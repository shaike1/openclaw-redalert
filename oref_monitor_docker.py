#!/usr/bin/env python3
"""
🚨 ORef Alerts Monitor - OpenClaw Smart Edition
פיקוד העורף - מערכת התרעות חכמה

סוגי התרעות:
  cat=1  🚀 ירי רקטות וטילים       → כנס למרחב מוגן!
  cat=2  ✈️  חדירת כלי טיס עוין     → כנס למרחב מוגן!
  cat=10 🔴 חדירת מחבלים           → נעל דלתות!
  cat=13 ✅ סיום אירוע / יציאה       → ניתן לצאת
  cat=14 ⚠️  התרעה מקדימה           → התכוננו!

ערוצי התרעה:
  1. 📱 WhatsApp (תמיד)
  2. 🔊 TTS קולי ברמקול HA (אם מוגדר)
  3. 📞 חיוג דרך openclaw-3cx (אופציונלי)
"""

import requests
import subprocess
import time
import logging
import os
from datetime import datetime

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# הגדרות
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OREF_API      = os.getenv("OREF_API_URL", "http://localhost:9001/current")
OREF_HISTORY  = os.getenv("OREF_API_URL", "http://localhost:9001").replace("/current","") + "/history"
POLL_INTERVAL = int(os.getenv("OREF_POLL_INTERVAL", "5"))
COOLDOWN_SEC  = int(os.getenv("OREF_COOLDOWN", "60"))

# מיקוד לפי אזורים (ריק = כל הארץ)
MONITORED_AREAS = [a.strip() for a in os.getenv("MONITORED_AREAS", "").split(",") if a.strip()]

# WhatsApp
WHATSAPP_GROUP = os.getenv("WHATSAPP_GROUP_JID", "")
WHATSAPP_OWNER = os.getenv("WHATSAPP_OWNER", "")

# Home Assistant
HA_URL         = os.getenv("HASS_SERVER", "")
HA_TOKEN       = os.getenv("HASS_TOKEN", "")
HA_TTS_SPEAKER = os.getenv("HA_TTS_SPEAKER", "media_player.home_assistant_voice_09a069")
HA_LIGHTS      = [l.strip() for l in os.getenv("HA_ALERT_LIGHTS", "").split(",") if l.strip()]
HA_ENABLED     = bool(HA_URL and HA_TOKEN)

# 3CX
PHONE_CALL_ENABLED = os.getenv("OREF_PHONE_CALL", "false").lower() == "true"
PHONE_NUMBERS      = [n.strip() for n in os.getenv("PHONE_ALERT_NUMBERS", "").split(",") if n.strip()]
CX3_GATEWAY_URL    = os.getenv("CX3_GATEWAY_URL", "http://localhost:8090")
CX3_EXTENSION      = os.getenv("CX3_EXTENSION", "")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# קטגוריות התרעה חכמה
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALERT_TYPES = {
    "1":  {
        "emoji": "🚀", "level": "CRITICAL",
        "action": "כנסו למרחב המוגן מיד! יש לכם 90 שניות!",
        "tts": "התרעה! ירי רקטות וטילים! כנסו למרחב המוגן מיד!",
        "flash": True, "call": True
    },
    "2":  {
        "emoji": "✈️", "level": "CRITICAL",
        "action": "כנסו למרחב המוגן מיד!",
        "tts": "התרעה! חדירת כלי טיס עוין! כנסו למרחב המוגן מיד!",
        "flash": True, "call": True
    },
    "10": {
        "emoji": "🔴", "level": "CRITICAL",
        "action": "נעלו דלתות וחלונות! אל תצאו!",
        "tts": "התרעת חדירת מחבלים! נעלו דלתות! אל תצאו החוצה!",
        "flash": True, "call": True
    },
    "13": {
        "emoji": "✅", "level": "ALL_CLEAR",
        "action": "ניתן לצאת מהמרחב המוגן.",
        "tts": "האירוע הסתיים. ניתן לצאת מהמרחב המוגן.",
        "flash": False, "call": False
    },
    "14": {
        "emoji": "⚠️", "level": "WARNING",
        "action": "התכוננו! צפויות התרעות בקרוב!",
        "tts": "שימו לב! בדקות הקרובות צפויות התרעות באזורכם. התכוננו!",
        "flash": False, "call": False
    },
}
DEFAULT_TYPE = {
    "emoji": "🚨", "level": "UNKNOWN",
    "action": "עיקבו אחר הוראות פיקוד העורף.",
    "tts": "התרעת פיקוד העורף. עיקבו אחר ההוראות.",
    "flash": True, "call": False
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("/var/log/oref_monitor.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("oref")

# State
last_alert_id     = None
alert_sent_at     = None
all_clear_sent    = False   # מניע שליחת "ניתן לצאת" כפולה


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WhatsApp
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def send_whatsapp(target: str, message: str):
    if not target:
        return
    # Support env-override for WA binary path (default: wacli)
    wa_bin = os.getenv("WA_BIN", "wacli")
    try:
        r = subprocess.run(
            [wa_bin, "send", "text", "--to", target, "--message", message],
            capture_output=True, text=True, timeout=15
        )
        log.info(f"✅ WhatsApp → {target}") if r.returncode == 0 else log.error(f"❌ WA ({r.returncode}): {r.stderr[:120]}")
    except Exception as e:
        log.error(f"❌ WA failed: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Home Assistant
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def ha_post(endpoint: str, payload: dict) -> bool:
    if not HA_ENABLED:
        return False
    try:
        r = requests.post(
            f"{HA_URL}/api/{endpoint}",
            headers={"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"},
            json=payload, timeout=8
        )
        ok = r.status_code in (200, 201)
        log.info(f"✅ HA {endpoint}") if ok else log.warning(f"⚠️ HA {endpoint} {r.status_code}")
        return ok
    except Exception as e:
        log.warning(f"⚠️ HA: {e}")
        return False


def ha_tts(text: str):
    ha_post("services/tts/speak", {
        "entity_id": HA_TTS_SPEAKER,
        "message": text,
        "language": "he"
    })


def ha_lights(color: str, flash: bool = False):
    if not HA_LIGHTS:
        return
    payload = {"entity_id": HA_LIGHTS, "color_name": color, "brightness": 255}
    if flash:
        payload["flash"] = "long"
    ha_post("services/light/turn_on", payload)


def ha_lights_off():
    if not HA_LIGHTS:
        return
    ha_post("services/light/turn_off", {"entity_id": HA_LIGHTS})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3CX
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def make_phone_call(text: str):
    if not PHONE_CALL_ENABLED or not PHONE_NUMBERS:
        return
    for number in PHONE_NUMBERS:
        try:
            r = requests.post(
                f"{CX3_GATEWAY_URL}/api/call/outbound",
                json={"to": number, "message": text, "language": "he", "extension": CX3_EXTENSION},
                timeout=10
            )
            log.info(f"📞 Call → {number}") if r.status_code == 200 else log.warning(f"⚠️ Call {number}: {r.status_code}")
        except Exception as e:
            log.warning(f"⚠️ 3CX: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# בניית הודעה לפי סוג התרעה
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_messages(data: dict) -> tuple[str, str, dict]:
    """מחזיר (whatsapp_text, tts_text, alert_type_config)"""
    current = data.get("current", {})
    cat     = str(current.get("cat", "1"))
    title   = current.get("title", "התרעה")
    areas   = current.get("data", []) or []
    desc    = current.get("desc", "")

    atype   = ALERT_TYPES.get(cat, DEFAULT_TYPE)
    emoji   = atype["emoji"]
    action  = atype["action"]
    now     = datetime.now().strftime("%H:%M:%S")

    # סינון לפי אזורים - הצג רק אזורים רלוונטיים
    if MONITORED_AREAS and areas:
        matched = [a for a in areas if any(m in a for m in MONITORED_AREAS)]
        areas_to_show = matched if matched else areas[:8]
    else:
        areas_to_show = areas[:8]
    areas_str = f"\n📍 {', '.join(areas_to_show)}" if areas_to_show else ""

    desc_str = f"\n📋 {desc}" if desc else ""

    wa_msg = (
        f"{emoji} *{title}* {emoji}\n\n"
        f"⏰ {now}\n"
        f"⚡ {action}"
        f"{areas_str}{desc_str}"
    )

    tts_text = atype["tts"]
    if areas:
        tts_text += f" אזורים מושפעים: {', '.join(areas[:3])}."

    return wa_msg, tts_text, atype


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# שליחת התרעה
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def dispatch_alert(data: dict):
    wa_msg, tts_text, atype = build_messages(data)
    level = atype["level"]

    log.info(f"🚨 [{level}] Dispatching alert")

    # 1️⃣ WhatsApp (תמיד)
    send_whatsapp(WHATSAPP_GROUP, wa_msg)
    send_whatsapp(WHATSAPP_OWNER, wa_msg)

    # 2️⃣ TTS + אורות
    ha_tts(tts_text)
    if atype["flash"]:
        ha_lights("red", flash=True)
    elif level == "ALL_CLEAR":
        ha_lights("green", flash=False)
        time.sleep(5)
        ha_lights_off()
    elif level == "WARNING":
        ha_lights("orange", flash=False)

    # 3️⃣ חיוג (רק לרמה CRITICAL)
    if atype["call"]:
        make_phone_call(tts_text)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# בדיקה ראשית
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def check_alert():
    global last_alert_id, alert_sent_at, all_clear_sent

    try:
        resp = requests.get(OREF_API, timeout=5)
        data = resp.json()
    except Exception as e:
        log.warning(f"⚠️ API: {e}")
        return

    is_alert = data.get("alert", False)
    current  = data.get("current", {})
    cat      = str(current.get("cat", ""))
    alert_id = current.get("id", "")

    # אין התרעה פעילה
    if not is_alert:
        if last_alert_id:
            log.info("✅ Alert cleared")
            last_alert_id = None
            all_clear_sent = False
        return

    # cat=13 = יציאה מהמרחב (שלח פעם אחת)
    if cat == "13":
        if not all_clear_sent:
            all_clear_sent = True
            dispatch_alert(data)
        return

    # סינון לפי אזורים מנוטרים (אם מוגדרים)
    if MONITORED_AREAS:
        areas_in_alert = current.get("data", []) or []
        matched = [a for a in areas_in_alert if any(m in a or a in m for m in MONITORED_AREAS)]
        if not matched:
            log.debug(f"⏭️ Alert in {areas_in_alert} - not in monitored areas, skipping")
            return

    # מנע ספאם
    if alert_id == last_alert_id:
        return
    now = time.time()
    if alert_sent_at and (now - alert_sent_at) < COOLDOWN_SEC:
        return

    last_alert_id  = alert_id
    alert_sent_at  = now
    all_clear_sent = False

    dispatch_alert(data)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    log.info("🚀 ORef Smart Monitor v2 started")
    log.info(f"📡 API: {OREF_API} | poll: {POLL_INTERVAL}s")
    log.info(f"📱 WhatsApp group: {WHATSAPP_GROUP or '❌ not set'}")
    log.info(f"🏠 HA TTS: {'✅ ' + HA_URL if HA_ENABLED else '❌ disabled'}")
    log.info(f"📞 Phone: {'✅ ' + str(PHONE_NUMBERS) if PHONE_CALL_ENABLED else '❌ disabled'}")
    log.info(f"📍 Monitored areas: {MONITORED_AREAS or 'כל הארץ'}")
    log.info("━" * 50)
    log.info("Alert levels: 🚀cat=1 ✈️cat=2 🔴cat=10 | ⚠️cat=14 pre-alert | ✅cat=13 all-clear")

    while True:
        try:
            check_alert()
        except Exception as e:
            log.error(f"❌ Error: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()

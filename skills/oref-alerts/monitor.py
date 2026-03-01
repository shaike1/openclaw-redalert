#!/usr/bin/env python3
"""
🚨 ORef Alerts Monitor - OpenClaw
פיקוד העורף - מערכת התרעות אדומות

שולח התראות דרך:
  1. 📱 WhatsApp (תמיד)
  2. 🔊 TTS קולי ברמקול HA (חובה אם HA מוגדר)
  3. 📞 חיוג טלפוני דרך openclaw-3cx (אופציונלי)
"""

import requests
import subprocess
import time
import logging
import os
from datetime import datetime

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# הגדרות ראשיות
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OREF_API       = os.getenv("OREF_API_URL", "http://localhost:9001/current")
POLL_INTERVAL  = int(os.getenv("OREF_POLL_INTERVAL", "5"))
COOLDOWN_SEC   = int(os.getenv("OREF_COOLDOWN", "60"))

# WhatsApp
WHATSAPP_GROUP = os.getenv("WHATSAPP_GROUP_JID", "")
WHATSAPP_OWNER = os.getenv("WHATSAPP_OWNER", "")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Home Assistant (אופציונלי)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HA_URL         = os.getenv("HASS_SERVER", "")
HA_TOKEN       = os.getenv("HASS_TOKEN", "")
HA_TTS_SPEAKER = os.getenv("HA_TTS_SPEAKER", "media_player.home_assistant_voice_09a069")
HA_LIGHTS      = [l.strip() for l in os.getenv("HA_ALERT_LIGHTS", "").split(",") if l.strip()]
HA_ENABLED     = bool(HA_URL and HA_TOKEN)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3CX חיוג טלפוני (אופציונלי)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHONE_CALL_ENABLED = os.getenv("OREF_PHONE_CALL", "false").lower() == "true"
PHONE_NUMBERS      = [n.strip() for n in os.getenv("PHONE_ALERT_NUMBERS", "").split(",") if n.strip()]
CX3_GATEWAY_URL    = os.getenv("CX3_GATEWAY_URL", "http://localhost:8090")
CX3_EXTENSION      = os.getenv("CX3_EXTENSION", "")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Logging
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
last_alert_id = None
alert_sent_at = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WhatsApp
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def send_whatsapp(target: str, message: str):
    if not target:
        return
    try:
        result = subprocess.run(
            ["openclaw", "message", "send",
             "--channel", "whatsapp",
             "--target", target,
             "--message", message],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            log.info(f"✅ WhatsApp → {target}")
        else:
            log.error(f"❌ WhatsApp error: {result.stderr[:100]}")
    except Exception as e:
        log.error(f"❌ WhatsApp failed: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Home Assistant
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def ha_call(endpoint: str, payload: dict) -> bool:
    if not HA_ENABLED:
        return False
    try:
        r = requests.post(
            f"{HA_URL}/api/{endpoint}",
            headers={"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"},
            json=payload, timeout=8
        )
        ok = r.status_code in (200, 201)
        if ok:
            log.info(f"✅ HA {endpoint}")
        else:
            log.warning(f"⚠️ HA {endpoint} → {r.status_code}")
        return ok
    except Exception as e:
        log.warning(f"⚠️ HA unreachable: {e}")
        return False


def ha_tts(text: str):
    """🔊 הכרזה קולית ברמקול (חובה אם HA מוגדר)"""
    if not HA_ENABLED:
        log.warning("⚠️ HA not configured — voice alert skipped!")
        return
    ha_call("services/tts/speak", {
        "entity_id": HA_TTS_SPEAKER,
        "message": text,
        "language": "he"
    })


def ha_flash_lights():
    """💡 הבהוב אורות אדומים"""
    if not HA_LIGHTS:
        return
    ha_call("services/light/turn_on", {
        "entity_id": HA_LIGHTS,
        "color_name": "red",
        "brightness": 255,
        "flash": "long"
    })


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3CX חיוג
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def make_phone_call(text: str):
    """📞 חיוג דרך openclaw-3cx (אופציונלי)"""
    if not PHONE_CALL_ENABLED or not PHONE_NUMBERS:
        return
    for number in PHONE_NUMBERS:
        try:
            resp = requests.post(
                f"{CX3_GATEWAY_URL}/api/call/outbound",
                json={
                    "to": number,
                    "message": text,
                    "language": "he",
                    "extension": CX3_EXTENSION
                },
                timeout=10
            )
            if resp.status_code == 200:
                log.info(f"📞 Call → {number}")
            else:
                log.warning(f"⚠️ Call failed {number}: {resp.status_code}")
        except Exception as e:
            log.warning(f"⚠️ 3CX unavailable: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# בניית הודעה
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CATEGORY_EMOJI = {
    "1": "🚀", "2": "🚀", "3": "✈️",
    "4": "💣", "6": "🌋", "13": "☢️"
}

def format_alert(data: dict) -> tuple[str, str]:
    """מחזיר (whatsapp_msg, tts_text)"""
    current = data.get("current", {})
    title   = current.get("title", "התרעה")
    areas   = current.get("data", []) or []
    desc    = current.get("desc", "")
    cat     = str(current.get("cat", "1"))
    emoji   = CATEGORY_EMOJI.get(cat, "🚨")
    now     = datetime.now().strftime("%H:%M:%S")

    areas_str = "\n" + "\n".join(f"  • {a}" for a in areas[:10]) if areas else ""
    desc_str  = f"\n📋 {desc}" if desc else ""

    wa_msg = (
        f"{emoji} *התרעת פיקוד העורף* {emoji}\n\n"
        f"⏰ {now}\n"
        f"🔔 {title}{areas_str}{desc_str}\n\n"
        f"⚠️ היכנסו למרחב המוגן מיד!"
    )

    tts_text = (
        f"התרעה! {title}. "
        f"{', '.join(areas[:3])}. " if areas else ""
        f"היכנסו למרחב המוגן מיד!"
    )

    return wa_msg, tts_text


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# לולאה ראשית
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def check_alert():
    global last_alert_id, alert_sent_at

    try:
        resp = requests.get(OREF_API, timeout=5)
        data = resp.json()
    except Exception as e:
        log.warning(f"⚠️ API error: {e}")
        return

    if not data.get("alert", False):
        if last_alert_id:
            log.info("✅ Alert cleared")
            last_alert_id = None
        return

    current  = data.get("current", {})
    alert_id = current.get("id", "unknown")

    if alert_id == last_alert_id:
        return
    now = time.time()
    if alert_sent_at and (now - alert_sent_at) < COOLDOWN_SEC:
        return

    last_alert_id = alert_id
    alert_sent_at = now

    wa_msg, tts_text = format_alert(data)
    log.info(f"🚨 ALERT! id={alert_id}")

    # 1️⃣ WhatsApp (תמיד)
    send_whatsapp(WHATSAPP_GROUP, wa_msg)
    send_whatsapp(WHATSAPP_OWNER, wa_msg)

    # 2️⃣ TTS + אורות (חובה אם HA מוגדר)
    ha_tts(tts_text)
    ha_flash_lights()

    # 3️⃣ חיוג (אופציונלי)
    make_phone_call(tts_text)


def main():
    log.info("🚀 ORef Monitor started")
    log.info(f"📡 API: {OREF_API} | interval: {POLL_INTERVAL}s")
    log.info(f"📱 WhatsApp group: {WHATSAPP_GROUP or 'not set'}")
    log.info(f"🏠 Home Assistant: {'✅ ' + HA_URL if HA_ENABLED else '❌ not configured'}")
    log.info(f"📞 Phone calls: {'✅ enabled → ' + str(PHONE_NUMBERS) if PHONE_CALL_ENABLED else '❌ disabled'}")

    while True:
        try:
            check_alert()
        except Exception as e:
            log.error(f"❌ Unexpected error: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()

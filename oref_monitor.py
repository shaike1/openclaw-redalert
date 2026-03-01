#!/usr/bin/env python3
"""
🚨 ORef Alerts Monitor - OpenClaw
מאזין ל-API של פיקוד העורף ושולח:
  1. WhatsApp (תמיד)
  2. TTS קולי ברמקול (חובה - דרך HA)
  3. חיוג טלפוני (אופציונלי - אם ENABLE_PHONE_CALL=true)
"""

import requests
import subprocess
import time
import json
import logging
import os
from datetime import datetime

# הגדרות
OREF_API = "http://localhost:9001/current"
POLL_INTERVAL = 5  # שניות
WHATSAPP_GROUP = os.getenv("WHATSAPP_GROUP_JID", "")
WHATSAPP_OWNER = os.getenv("WHATSAPP_OWNER", "")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# פילטר אזורים - רק ההתרעות האלה יישלחו!
# רשימה ריקה = שלח הכל (ברירת מחדל ישנה)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILTER_AREAS = [
    "הרצליה - גליל ים ומרכז",
    "הרצליה - שיכון עמידר",
    "הרצליה",
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Home Assistant (אופציונלי - השאר None אם לא צריך)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HA_URL   = os.getenv("HASS_SERVER", "")
HA_TOKEN = os.getenv("HASS_TOKEN", "")
HA_TTS_SPEAKER  = "media_player.home_assistant_voice_09a069"
HA_ALERT_LIGHTS = ["light.living_room", "light.kids_room"]  # אורות להבהב (אופציונלי)
HA_ENABLED = True  # שנה ל-False כדי לכבות לגמרי

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# חיוג טלפוני דרך 3CX (אופציונלי)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ENABLE_PHONE_CALL = os.getenv("OREF_PHONE_CALL", "false").lower() == "true"
PHONE_NUMBERS     = ["+972525173322"]   # מספרים לחייג בהתראה קריטית
CX3_GATEWAY_URL   = os.getenv("CX3_GATEWAY_URL", "http://localhost:8090")  # openclaw-3cx gateway

# מניעת ספאם - שלח רק פעם אחת לכל התרעה
last_alert_id = None
alert_sent_at = None
COOLDOWN_SECONDS = 60  # המתן דקה בין התראות לאותו אזור

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("/var/log/oref_monitor.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("oref")


def send_whatsapp(target: str, message: str):
    """שלח הודעת WhatsApp דרך OpenClaw CLI"""
    try:
        result = subprocess.run(
            [
                "openclaw", "message", "send",
                "--channel", "whatsapp",
                "--target", target,
                "--message", message
            ],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            log.info(f"✅ WhatsApp sent to {target}")
        else:
            log.error(f"❌ WhatsApp error: {result.stderr}")
    except Exception as e:
        log.error(f"❌ Failed to send WhatsApp: {e}")


def ha_call(endpoint: str, payload: dict):
    """קריאה ל-Home Assistant API (אופציונלי)"""
    if not HA_ENABLED or not HA_URL or not HA_TOKEN:
        return
    try:
        r = requests.post(
            f"{HA_URL}/api/{endpoint}",
            headers={"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"},
            json=payload,
            timeout=8
        )
        if r.status_code in (200, 201):
            log.info(f"✅ HA {endpoint} OK")
        else:
            log.warning(f"⚠️ HA {endpoint} → {r.status_code}: {r.text[:80]}")
    except Exception as e:
        log.warning(f"⚠️ HA not reachable ({e}) — continuing without HA")


def ha_tts(text: str):
    """🔊 הכרזה ברמקול דרך Home Assistant (חובה!)"""
    if not HA_ENABLED or not HA_URL or not HA_TOKEN:
        log.warning("⚠️ HA not configured - TTS skipped!")
        return
    # נסה tts/speak קודם, fallback ל-notify
    success = ha_call("services/tts/speak", {
        "entity_id": HA_TTS_SPEAKER,
        "message": text,
        "language": "he"
    })
    if not success:
        ha_call("services/notify/alexa_media_" + HA_TTS_SPEAKER.replace(".", "_"), {
            "message": text,
            "data": {"type": "announce"}
        })


def make_phone_call(text: str):
    """📞 חיוג טלפוני דרך openclaw-3cx (אופציונלי)"""
    if not ENABLE_PHONE_CALL:
        return
    for number in PHONE_NUMBERS:
        try:
            resp = requests.post(
                f"{CX3_GATEWAY_URL}/api/call/outbound",
                json={"to": number, "message": text, "language": "he"},
                timeout=10
            )
            if resp.status_code == 200:
                log.info(f"📞 Call initiated to {number}")
            else:
                log.warning(f"⚠️ Call failed {number}: {resp.status_code}")
        except Exception as e:
            log.warning(f"⚠️ 3CX gateway not available ({e}) — skipping call")


def ha_flash_lights():
    """הבהב אורות אדומים בזמן התרעה"""
    if not HA_ALERT_LIGHTS:
        return
    ha_call("services/light/turn_on", {
        "entity_id": HA_ALERT_LIGHTS,
        "color_name": "red",
        "brightness": 255,
        "flash": "long"
    })


def format_alert_message(data: dict) -> str:
    """צור הודעת התראה מעוצבת"""
    current = data.get("current", {})
    title = current.get("title", "התרעה")
    areas = current.get("data", [])
    desc = current.get("desc", "")
    cat = current.get("cat", "")

    # בחר אמוג'י לפי קטגוריה
    emoji = "🚨"
    if cat == "1":
        emoji = "🚀"  # ירי רקטות
    elif cat == "3":
        emoji = "✈️"  # חדירת כלי טיס
    elif cat == "4":
        emoji = "💣"  # חפץ חשוד
    elif cat == "6":
        emoji = "🌋"  # רעידת אדמה
    elif cat == "13":
        emoji = "☢️"  # חומרים מסוכנים

    areas_str = ""
    if areas:
        areas_str = "\n📍 אזורים:\n" + "\n".join(f"  • {a}" for a in areas[:10])

    desc_str = f"\n📋 {desc}" if desc else ""

    now = datetime.now().strftime("%H:%M:%S")
    return f"""{emoji} *התרעת פיקוד העורף* {emoji}

⏰ {now}
🔔 {title}{areas_str}{desc_str}

⚠️ היכנסו למרחב המוגן!"""


def check_alert():
    """בדוק ה-API ושלח התראה אם צריך"""
    global last_alert_id, alert_sent_at

    try:
        resp = requests.get(OREF_API, timeout=5)
        data = resp.json()
    except Exception as e:
        log.warning(f"⚠️ API error: {e}")
        return

    is_alert = data.get("alert", False)

    if not is_alert:
        if last_alert_id:
            log.info("✅ Alert cleared")
            last_alert_id = None
        return

    current = data.get("current", {})
    alert_id = current.get("id", "")

    # מנע ספאם
    if alert_id == last_alert_id:
        return

    now = time.time()
    if alert_sent_at and (now - alert_sent_at) < COOLDOWN_SECONDS:
        return

    # פילטר אזורים - בדוק שיש לפחות אזור אחד מהרשימה
    areas = current.get("data", [])
    if FILTER_AREAS:
        matched = [a for a in areas if any(f in a for f in FILTER_AREAS)]
        if not matched:
            log.info(f"⏭️ Alert skipped (not in filter): {areas}")
            return

    # שלח התראה!
    last_alert_id = alert_id
    alert_sent_at = now

    message = format_alert_message(data)
    log.info(f"🚨 ALERT! ID={alert_id}, sending notifications...")

    # 1️⃣ WhatsApp (תמיד)
    send_whatsapp(WHATSAPP_GROUP, message)
    send_whatsapp(WHATSAPP_OWNER, message)

    # 2️⃣ TTS קולי (חובה!)
    areas = matched if FILTER_AREAS else current.get("data", [])
    tts_text = f"התרעה! {current.get('title', '')}. {', '.join(areas[:3]) if areas else ''}. היכנסו למרחב המוגן מיד!"
    ha_tts(tts_text)
    ha_flash_lights()

    # 3️⃣ חיוג טלפוני (אופציונלי - OREF_PHONE_CALL=true)
    make_phone_call(tts_text)


def main():
    log.info("🚀 ORef Monitor started (OpenClaw-only mode)")
    log.info(f"📡 Polling: {OREF_API} every {POLL_INTERVAL}s")

    while True:
        try:
            check_alert()
        except Exception as e:
            log.error(f"❌ Unexpected error: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()

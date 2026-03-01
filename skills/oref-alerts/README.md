# 🚨 ORef Alerts Monitor - פיקוד העורף

מערכת התרעות חכמה לפיקוד העורף - מנוטרת לפי אזורים, ללא כפילויות, עם WhatsApp + HA TTS.

---

## ארכיטקטורה

```
Pikud Ha-Oref API (oref.org.il)
        ↓
Docker: dmatik/oref-alerts  (:49000)
        ↓
systemd: oref-monitor.service  (monitor.py)
        ↓  ↓  ↓
   📱 WA  🔊 TTS  💡 Lights
```

| רכיב | תפקיד | ניהול |
|------|-------|-------|
| `oref-alerts` | Proxy → Pikud Ha-Oref API, פורט 49000 | Docker |
| `oref-monitor.service` | Python monitor + dispatch | systemd |

> **WhatsApp נשלח דרך `wa-send.sh`** — wrapper ל-`openclaw message send`.
> wacli לא נדרש (ולא צריך אימות QR).

---

## התקנה מהירה (Deploy)

### דרישות מוקדמות
```bash
# Docker (עבור oref-alerts API proxy)
apt install docker.io -y

# OpenClaw (כבר מותקן — לשליחת WhatsApp)
which openclaw
```

### פריסה

```bash
cd /root/.openclaw/workspace/skills/oref-alerts

# 1. הפעל oref-alerts (proxy API)
docker run -d \
  --name oref-alerts \
  --restart unless-stopped \
  -p 49000:9001 \
  -e TZ="Asia/Jerusalem" \
  dmatik/oref-alerts:latest

# 2. הגדר .env (העתק מ-.env.example ומלא ערכים)
cp .env.example .env
nano .env

# 3. הפעל systemd service
systemctl daemon-reload
systemctl enable oref-monitor
systemctl start oref-monitor
```

---

## משתני סביבה

מוגדרים בקובץ `.env` (הקובץ **מחוץ ל-git**, ראה `.gitignore`):

| משתנה | ברירת מחדל | תיאור |
|-------|-----------|-------|
| `OREF_API_URL` | `http://localhost:49000/current` | כתובת proxy API (host) |
| `MONITORED_AREAS` | ריק = כל הארץ | אזורים לניטור, מופרדים בפסיק |
| `OREF_POLL_INTERVAL` | `5` | שניות בין בדיקות |
| `OREF_COOLDOWN` | `60` | שניות צינון בין התרעות |
| `WHATSAPP_GROUP_JID` | - | JID של קבוצת WhatsApp |
| `WHATSAPP_OWNER` | - | מספר WhatsApp אישי |
| `HASS_SERVER` | - | כתובת Home Assistant |
| `HASS_TOKEN` | - | HA Long-Lived Token |
| `HA_TTS_SPEAKER` | `media_player.home_assistant_voice_09a069` | רמקול TTS |
| `HA_ALERT_LIGHTS` | - | אורות להבהוב (entity_id מופרדים בפסיק) |
| `WA_BIN` | `wacli` | נתיב לסקריפט שליחת WhatsApp (ראה wa-send.sh) |

---

## שליחת WhatsApp דרך OpenClaw

המוניטור משתמש ב-`wa-send.sh` (מוגדר ב-service כ-`WA_BIN`):

```bash
# wa-send.sh מתרגם את הפרמטרים של wacli:
#   wacli send text --to <target> --message <msg>
# → openclaw message send --channel whatsapp --target <target> --message <msg>
```

ה-service מגדיר אוטומטית:
```
Environment=WA_BIN=/root/.openclaw/workspace/skills/oref-alerts/wa-send.sh
```

---

## בדיקה (Testing)

### בדוק ה-API ישירות
```bash
curl -s http://localhost:49000/current | python3 -m json.tool

# פלט לדוגמה (אין התרעה):
# {"alert": false, "current": {}}

# פלט לדוגמה (יש התרעה):
# {"alert": true, "current": {"cat": "1", "title": "ירי רקטות", "data": ["הרצליה - גליל ים ומרכז"]}}
```

### בדוק סטטוס
```bash
# systemd service
systemctl status oref-monitor

# Docker API proxy
docker ps | grep oref-alerts
# → oref-alerts   Up X minutes   0.0.0.0:49000->9001/tcp
```

### בדוק לוגים
```bash
# מוניטור — בזמן אמת
tail -f /var/log/oref-monitor.log
# או:
journalctl -u oref-monitor -f

# API proxy
docker logs oref-alerts --tail 20
```

### הפעל מצב TEST (התרעת דמה בהרצליה)
```bash
docker stop oref-alerts && docker rm oref-alerts

docker run -d \
  --name oref-alerts \
  -p 49000:9001 \
  -e TZ="Asia/Jerusalem" \
  -e CURRENT_ALERT_TEST_MODE=TRUE \
  -e CURRENT_ALERT_TEST_MODE_LOC="הרצליה - גליל ים ומרכז" \
  dmatik/oref-alerts:latest

# המתן 10 שניות ובדוק:
tail -f /var/log/oref-monitor.log

# אחרי הבדיקה - החזר לרגיל:
docker stop oref-alerts && docker rm oref-alerts
docker run -d --name oref-alerts --restart unless-stopped \
  -p 49000:9001 -e TZ="Asia/Jerusalem" dmatik/oref-alerts:latest
```

---

## סינון אזורים (ללא כפילויות)

המערכת כוללת מנגנון חכם למניעת כפילויות:

1. **Alert ID** - כל התרעה מקבלת ID ייחודי → לא נשלחת פעמיים
2. **Cooldown** - 60 שניות מינימום בין התרעות
3. **סינון אזורי** - בדיקה לפני שליחה → רק התרעות באזורך

```
התרעה ב: נערן, שדה בר
MONITORED_AREAS: הרצליה
→ לא מתאים → מדלג ✅

התרעה ב: הרצליה - גליל ים ומרכז, נתניה
MONITORED_AREAS: הרצליה
→ מתאים → שולח התרעה 🚨
```

---

## סוגי התרעות

| קטגוריה | סוג | WhatsApp | רמקול TTS | אורות |
|---------|-----|----------|-----------|-------|
| cat=1 | 🚀 ירי רקטות וטילים | ✅ | ✅ | 🔴 אדום |
| cat=2 | ✈️ חדירת כלי טיס | ✅ | ✅ | 🔴 אדום |
| cat=10 | 🔴 חדירת מחבלים | ✅ | ✅ | 🔴 אדום |
| cat=13 | ✅ סיום אירוע | ❌ רמקול בלבד | ✅ | 🟢 ירוק |
| cat=14 | ⚠️ התרעה מוקדמת | ❌ רמקול בלבד | ✅ | 🟠 כתום |

> **הגיון:** סיום אירוע והתרעה מוקדמת הן פחות דחופות - רמקול מספיק, בלי להטריד ב-WhatsApp.

---

## הפעלה מחדש

```bash
# הפעל מחדש מוניטור
systemctl restart oref-monitor

# הפעל מחדש API proxy
docker restart oref-alerts

# עצור הכל
systemctl stop oref-monitor
docker stop oref-alerts

# שנוי בקוד monitor.py → רק restart לservice
systemctl restart oref-monitor
```

---

## קבצים

```
oref-alerts/
├── monitor.py          ← מוניטור Python (הקוד הראשי)
├── wa-send.sh          ← wrapper: openclaw message send (במקום wacli ישיר)
├── .env                ← משתני סביבה (מחוץ ל-git!)
├── .env.example        ← תבנית ל-.env
├── Dockerfile          ← קונטיינר Docker (לא בשימוש ב-production)
├── docker-compose.yml  ← הגדרות Docker Compose (לא בשימוש ב-production)
├── README.md           ← המסמך הזה
├── SKILL.md            ← תיעוד Skill ל-OpenClaw
├── ha_config.yaml      ← קונפיג Home Assistant (אופציונלי)
└── scripts/
    ├── deploy.sh           ← סקריפט פריסה
    ├── standalone_monitor.py ← גרסה ישירה (ללא Docker)
    └── whatsapp-notify.sh  ← עוזר WhatsApp
```

### systemd service
```
/etc/systemd/system/oref-monitor.service
```
מוגדר עם `EnvironmentFile=.env` ו-`WA_BIN=wa-send.sh`. מופעל אוטומטית עם הפעלת המערכת.

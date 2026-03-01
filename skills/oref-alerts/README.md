# 🚨 ORef Alerts Monitor - פיקוד העורף

מערכת התרעות חכמה לפיקוד העורף - מנוטרת לפי אזורים, ללא כפילויות, עם WhatsApp + HA TTS.

---

## ארכיטקטורה

```
Pikud Ha-Oref API (oref.org.il)
        ↓
Docker: dmatik/oref-alerts  (:49000)
        ↓
Docker: oref-monitor (Python)
        ↓  ↓  ↓
   📱 WA  🔊 TTS  💡 Lights
```

| קונטיינר | תפקיד | פורט |
|----------|-------|------|
| `oref-alerts` | Proxy → Pikud Ha-Oref API | 49000 |
| `oref-monitor` | Monitor + dispatch | internal |

---

## התקנה מהירה (Deploy)

### דרישות מוקדמות
```bash
# Docker
apt install docker.io -y

# wacli (שליחת WhatsApp)
go install github.com/steipete/wacli/cmd/wacli@latest
# ואז: wacli auth  ← סרוק QR
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

# 2. בנה oref-monitor
docker build -t oref-monitor .

# 3. הפעל oref-monitor
docker run -d \
  --name oref-monitor \
  --restart unless-stopped \
  --link oref-alerts:oref-alerts \
  -v /root/go/bin/wacli:/usr/local/bin/wacli:ro \
  -v /root/.wacli:/root/.wacli:ro \
  -e OREF_API_URL="http://oref-alerts:9001/current" \
  -e MONITORED_AREAS="הרצליה,הרצליה - גליל ים ומרכז" \
  -e WHATSAPP_GROUP_JID="120363417492964228@g.us" \
  -e WHATSAPP_OWNER="+972525173322" \
  -e HASS_SERVER="https://ha.right-api.com" \
  -e HASS_TOKEN="YOUR_HA_LONG_LIVED_TOKEN" \
  -e HA_TTS_SPEAKER="media_player.home_assistant_voice_09a069" \
  oref-monitor
```

---

## משתני סביבה

| משתנה | ברירת מחדל | תיאור |
|-------|-----------|-------|
| `OREF_API_URL` | `http://localhost:9001/current` | כתובת proxy API |
| `MONITORED_AREAS` | ריק = כל הארץ | אזורים לניטור, מופרדים בפסיק |
| `OREF_POLL_INTERVAL` | `5` | שניות בין בדיקות |
| `OREF_COOLDOWN` | `60` | שניות צינון בין התרעות |
| `WHATSAPP_GROUP_JID` | - | JID של קבוצת WhatsApp |
| `WHATSAPP_OWNER` | - | מספר WhatsApp אישי |
| `HASS_SERVER` | - | כתובת Home Assistant |
| `HASS_TOKEN` | - | HA Long-Lived Token |
| `HA_TTS_SPEAKER` | `media_player.home_assistant_voice_09a069` | רמקול TTS |
| `HA_ALERT_LIGHTS` | - | אורות להבהוב (entity_id מופרדים בפסיק) |
| `WA_BIN` | `wacli` | נתיב לבינארי wacli |

---

## בדיקה (Testing)

### בדוק ה-API ישירות
```bash
# כל התרעות פעילות
curl -s http://localhost:49000/current | python3 -m json.tool

# פלט לדוגמה (אין התרעה):
# {"alert": false, "current": {}}

# פלט לדוגמה (יש התרעה):
# {"alert": true, "current": {"cat": "1", "title": "ירי רקטות", "data": ["הרצליה - גליל ים ומרכז"]}}
```

### בדוק סטטוס קונטיינרים
```bash
docker ps | grep oref
# → oref-alerts   Up X minutes   0.0.0.0:49000->9001/tcp
# → oref-monitor  Up X minutes
```

### בדוק לוגים
```bash
# מוניטור (מה קורה בזמן אמת)
docker logs oref-monitor -f --tail 30

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
docker logs oref-monitor --tail 20

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
→ לא מתאים → מדלג ✅ (ללא כפילות)

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
| cat=13 | ✅ סיום אירוע | ✅ | ✅ | 🟢 ירוק |
| cat=14 | ⚠️ התרעה מוקדמת | ❌ רמקול בלבד | ✅ | 🟠 כתום |

> **הגיון:** סיום אירוע והתרעה מוקדמת הן פחות דחופות - רמקול מספיק, בלי להטריד ב-WhatsApp.

---

## הפעלה מחדש

```bash
# הפעל מחדש הכל
docker restart oref-alerts oref-monitor

# עצור הכל
docker stop oref-alerts oref-monitor

# בנה מחדש (אחרי שינוי בקוד)
docker stop oref-monitor && docker rm oref-monitor
docker build -t oref-monitor /root/.openclaw/workspace/skills/oref-alerts/
# ואז הרץ שוב את פקודת docker run מלמעלה
```

---

## ⚠️ שגיאה נפוצה - שני מוניטורים במקביל

**בעיה:** אם `skills/oref-alerts/monitor.py` רץ **ישירות** (לא דרך Docker), הוא שולח התרעות מ**כל הארץ** כי הוא לא מקבל את ה-env variables עם `MONITORED_AREAS`.

**איבחון:**
```bash
ps aux | grep monitor.py | grep -v grep
# אם רואים שני תהליכים → בעיה!
```

**פתרון:**
```bash
# הרוג את התהליך הישיר (שאינו Docker)
kill $(ps aux | grep "skills/oref-alerts/monitor.py" | grep -v grep | awk '{print $2}')

# רק ה-Docker container צריך לרוץ:
docker ps | grep oref-monitor
```

**הכלל:** רק ה-Docker `oref-monitor` אמור לרוץ. **לעולם אל תפעיל את monitor.py ישירות.**

---

## קבצים

```
oref-alerts/
├── monitor.py          ← מוניטור Python (הקוד הראשי)
├── Dockerfile          ← קונטיינר oref-monitor
├── docker-compose.yml  ← הגדרות Docker Compose
├── README.md           ← המסמך הזה
├── SKILL.md            ← תיעוד Skill ל-OpenClaw
├── ha_config.yaml      ← קונפיג Home Assistant (אופציונלי)
└── scripts/
    ├── deploy.sh           ← סקריפט פריסה
    ├── standalone_monitor.py ← גרסה ישירה (ללא Docker)
    └── whatsapp-notify.sh  ← עוזר WhatsApp
```

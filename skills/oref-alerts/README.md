# 🚨 ORef Alerts - OpenClaw Integration
## מערכת התרעות פיקוד העורף - אינטגרציית OpenClaw

> מערכת עצמאית לקבלת התרעות אדומות מפיקוד העורף  
> **אין תלות ב-Home Assistant** — עובד לבד דרך OpenClaw

---

## 🏗️ ארכיטקטורה

```
📡 Pikud Ha-Oref API (כל 5 שניות)
              ↓
    🖥️ OpenClaw VPS (ליבה)
              ↓
   ┌──────────┼─────────────┐
   │          │             │
📱 WhatsApp  🔊 TTS קולי  📞 חיוג
  (תמיד)    (אם HA מוגדר) (3CX, אופציונלי)
```

---

## 📦 מה כלול

| קובץ | תיאור |
|------|-------|
| `monitor.py` | סקריפט הניטור הראשי |
| `scripts/deploy.sh` | סקריפט דיפלוי אינטראקטיבי |
| `docker-compose.yml` | Docker Compose לcontainer פיקוד העורף |
| `.env.example` | קובץ הגדרות לדוגמה |
| `references/api.md` | תיעוד ה-API של פיקוד העורף |
| `references/home-assistant.md` | מדריך אינטגרציית Home Assistant |

---

## 🚀 התקנה מהירה (מומלץ)

```bash
git clone https://github.com/shaike1/openclaw-redalert
cd openclaw-redalert
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

הסקריפט ישאל אותך שלב אחר שלב על:
1. הגדרות WhatsApp
2. Home Assistant (אופציונלי)
3. חיוג 3CX (אופציונלי)

---

## ⚙️ אפשרויות התקנה

### 🥉 מינימלי — WhatsApp בלבד

```bash
WHATSAPP_GROUP_JID=120363417492964228@g.us
WHATSAPP_OWNER=+972525173322
```

✅ קבל התרעות WhatsApp  
❌ ללא קול  
❌ ללא חיוג

---

### 🥈 מומלץ — WhatsApp + TTS קולי

```bash
WHATSAPP_GROUP_JID=120363417492964228@g.us
WHATSAPP_OWNER=+972525173322
HASS_SERVER=https://your-ha.example.com
HASS_TOKEN=your_long_lived_token
HA_TTS_SPEAKER=media_player.home_assistant_voice_09a069
HA_ALERT_LIGHTS=light.living_room,light.kids_room
```

✅ WhatsApp  
✅ הכרזה קולית ברמקול  
✅ הבהוב אורות אדומים  
❌ ללא חיוג

---

### 🥇 מלא — WhatsApp + TTS + חיוג טלפוני

```bash
WHATSAPP_GROUP_JID=120363417492964228@g.us
WHATSAPP_OWNER=+972525173322
HASS_SERVER=https://your-ha.example.com
HASS_TOKEN=your_long_lived_token
HA_TTS_SPEAKER=media_player.home_assistant_voice_09a069
HA_ALERT_LIGHTS=light.living_room,light.kids_room
OREF_PHONE_CALL=true
PHONE_ALERT_NUMBERS=+972525173322,+972545000000
CX3_GATEWAY_URL=http://localhost:8090
CX3_EXTENSION=100
```

✅ WhatsApp  
✅ הכרזה קולית  
✅ אורות  
✅ חיוג אוטומטי לכל המספרים

---

## 🔧 משתני סביבה

### ORef API
| משתנה | ברירת מחדל | תיאור |
|-------|-----------|-------|
| `OREF_API_URL` | `http://localhost:9001/current` | כתובת API |
| `OREF_POLL_INTERVAL` | `5` | שניות בין בדיקות |
| `OREF_COOLDOWN` | `60` | שניות בין התרעות חוזרות |

### WhatsApp
| משתנה | תיאור |
|-------|-------|
| `WHATSAPP_GROUP_JID` | JID של קבוצת WhatsApp (לדוגמה: `120363...@g.us`) |
| `WHATSAPP_OWNER` | מספר אישי (לדוגמה: `+972525173322`) |

### Home Assistant
| משתנה | ברירת מחדל | תיאור |
|-------|-----------|-------|
| `HASS_SERVER` | ריק | כתובת HA (לדוגמה: `https://ha.example.com`) |
| `HASS_TOKEN` | ריק | Long-Lived Access Token |
| `HA_TTS_SPEAKER` | `media_player.home_assistant_voice_09a069` | entity_id רמקול |
| `HA_ALERT_LIGHTS` | ריק | entity_ids אורות (מופרדים בפסיק) |

### 3CX חיוג
| משתנה | ברירת מחדל | תיאור |
|-------|-----------|-------|
| `OREF_PHONE_CALL` | `false` | הפעלת חיוג (`true`/`false`) |
| `CX3_GATEWAY_URL` | `http://localhost:8090` | כתובת openclaw-3cx gateway |
| `CX3_EXTENSION` | ריק | מספר שלוחה |
| `PHONE_ALERT_NUMBERS` | ריק | מספרי טלפון (מופרדים בפסיק) |

---

## 📋 פקודות שימושיות

```bash
# סטטוס השירות
systemctl status oref-monitor-openclaw

# לוגים חיים
journalctl -u oref-monitor-openclaw -f

# הפעלה מחדש
systemctl restart oref-monitor-openclaw

# עצירה
systemctl stop oref-monitor-openclaw

# בדיקת API
curl -s http://localhost:9001/current | python3 -m json.tool

# בדיקת container
docker ps | grep oref-alerts
docker logs oref-alerts --tail 20
```

---

## 🔄 עדכון הגדרות

```bash
# ערוך הגדרות
nano /root/.openclaw/workspace/skills/oref-alerts/.env

# הפעל מחדש
systemctl restart oref-monitor-openclaw
```

---

## 🐛 פתרון בעיות

### API לא מגיב
```bash
docker ps | grep oref-alerts
docker restart oref-alerts
curl -s http://localhost:9001/current
```

### WhatsApp לא שולח
```bash
openclaw status
journalctl -u oref-monitor-openclaw -n 20
```

### HA TTS לא עובד
```bash
curl -H "Authorization: Bearer $HASS_TOKEN" $HASS_SERVER/api/
```

---

## 📄 רישיון

MIT License — עשה בחופשיות!

---

*Made with ❤️ by OpenClaw Community*

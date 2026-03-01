# 🚨 ORef Alerts Monitor - פיקוד העורף

מערכת התרעות חכמה לפיקוד העורף — מנוטרת לפי אזורים, ללא כפילויות, עם WhatsApp + HA TTS.

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

---

## מסמכים

- **[skills/oref-alerts/README.md](skills/oref-alerts/README.md)** — הוראות התקנה, משתני סביבה, בדיקות ותפעול

---

## סוגי התרעות

| קטגוריה | סוג | WhatsApp | רמקול TTS |
|---------|-----|----------|-----------|
| cat=1 | 🚀 ירי רקטות וטילים | ✅ | ✅ |
| cat=2 | ✈️ חדירת כלי טיס | ✅ | ✅ |
| cat=10 | 🔴 חדירת מחבלים | ✅ | ✅ |
| cat=13 | ✅ סיום אירוע | ❌ רמקול בלבד | ✅ |
| cat=14 | ⚠️ התרעה מוקדמת | ❌ רמקול בלבד | ✅ |

---

## מצב מהיר

```bash
# סטטוס
systemctl status oref-monitor
docker ps | grep oref-alerts

# לוגים
tail -f /var/log/oref-monitor.log

# API
curl -s http://localhost:49000/current
```

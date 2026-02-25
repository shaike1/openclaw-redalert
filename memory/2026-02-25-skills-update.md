# PyWebtop Skill Update - 2026-02-25

## 🎉 New Feature: Event Reminders!

### What's New:
Added automatic event detection and reminders to the daily WhatsApp message.

### How It Works:
1. Fetches messages from Webtop inbox
2. Parses dates from Hebrew message subjects
3. Checks if any events are scheduled for today
4. Adds reminder section to morning WhatsApp message

### Supported Date Formats:
- `DD.MM` (18.2)
- `DD/MM/YY` (1/3/26)
- `DD/MM/YYYY` (1/3/2026)

### Event Types Detected:
- 🎭 תהלוכות (Parades)
- 🏛️ מוזיאונים (Museums)
- 🚸 טיולים (Trips)
- 📝 מבחנים (Exams)
- 🏊 שיעורי שחייה (Swimming lessons)
- Any message with a date in the subject

### Example Output:
```
📚 שיעורי הבית - 01/03/2026
⏰ 06:00

👦 יובל לוקוב (כיתה 2-5)
...

⚠️ תזכורת מיוחדת להיום:
🔔 תהלוכת פורים- פארק הפיראטים

---
🤖 Luky Bot
```

### Technical Details:
- Script: `webtop_homework_fetcher.py`
- Function: `parse_date_from_message()`
- API calls: `get_messages_inbox()`
- No Playwright needed (uses direct API)

---

## Files Updated:
- ✅ `SKILL.md` - Added Event Reminders section
- ✅ `webtop_homework_fetcher.py` - Added event detection logic
- ✅ `README-AUTOMATION.md` - Complete automation guide
- ✅ `messages_to_calendar.py` - Standalone event parser

---

## Testing:
```bash
cd /root/.openclaw/skills/pywebtop-skill
python3 webtop_homework_fetcher.py
python3 messages_to_calendar.py
```

---

## GitHub Push:
Ready to push to: https://github.com/openclaw/skills

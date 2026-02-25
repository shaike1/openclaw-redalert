# MEMORY.md - Luky Bot Memory

## Latest Updates
- **2026-02-25**: OpenClaw upgraded to v2026.2.23 ✅
  - Cleaned up duplicate Webtop skills
  - Kept only: pywebtop-skill (working)
  - Removed: webtop-homework, webtop-skill, webtop-script (outdated)

- **2026-02-24**: Webtop automation working ✅
  - Daily homework fetching at 6:00 AM
  - WhatsApp group: 120363417492964228@g.us
  - Children: Yuval (2-5), Shira (4-3)

- **2026-02-22**: Automated backup system installed
  - Daily backups at 3am UTC
  - Local: `/root/openclaw-backups/`
  - 7-day retention + weekly backups
  - Backup script: `/root/.openclaw/backup/backup-local.sh`

- **2026-02-22**: Bot configuration restored
  - Identity: Luky Bot (לוקי בוט)
  - Skills installed (after cleanup): ~44 skills
  - WhatsApp: +972527497367
  - Group "בוטים": 120363425850729867@g.us (no @mention needed)

---

## System Access
- **WhatsApp**: +972527497367 (luky bot)
- **Home Assistant**: https://ha.right-api.com (token configured)
- **Spotify**: OAuth configured
- **Discord**: @luky

---

## 🔐 Secure Credentials Location

**ALL credentials stored in:** `/root/.openclaw/workspace/.env/secrets.env`
- 🔒 **Permissions:** 600 (owner read/write only)
- 🔒 **Directory:** 700 (owner access only)
- ✅ **Secured with proper permissions**

### 📚 Webtop Credentials (SmartSchool)
**Parent Account:** שי שמעון לוקוב
- **Username:** USXD88
- **Password:** usx88usx88
- **Data Key:** makhVV2GVc7e99mbVW16PQ==
- **School:** נעמי שמר
- **Children:** יובל (2-5), שירה (4-3)

**Working Script:** `/root/.openclaw/skills/pywebtop-skill/webtop_homework_fetcher.py`
**Status:** ✅ Tested and working (2026-02-25)
**Method:** API direct (NOT Playwright - avoids CAPTCHA)

---

## User Preferences
- **Voice Messages**: Always respond with voice (Hebrew TTS via google-speech)
- **Language**: Hebrew (עברית) and English only
- **Communication Style**: Helpful, friendly, efficient

---

## Previous Memory (2026-01-30)
- Backup System - Duplicacy Web with Google Drive
- Lior (+972545889456) - Limited access user
- Google Calendar - School events added
- Identity change from "Claw" to "Luky Bot"

---

## Important Commands
```bash
# Run backup manually
/root/.openclaw/backup/backup-local.sh

# Check backup log
tail -f /root/.openclaw/backup/backup.log

# List backups
ls -lh /root/openclaw-backups/

# Restore backup
cd /root/.openclaw-backups
tar xzf luky-bot-YYYYMMDD-HHMMSS.tar.gz
cp -r openclaw-backup/* /root/.openclaw/
```

## Cross-Channel Messaging Fix (2026-02-22)

**Issue:** Bot was trying to send WhatsApp responses when receiving Discord messages
- Error: "Cross-context messaging denied: action=send target provider 'whatsapp' while bound to 'discord'"

**Solution:** Added rule to SOUL.md:
- ALWAYS respond to the SAME channel where the message was received
- NEVER hard-code channel in message tool calls
- Let system auto-route to correct channel

**Both bots have this fix:**
- luky bot (100.64.0.7) - WhatsApp + Discord
- sh.ai bot (100.64.0.12) - WhatsApp + Discord


# MEMORY.md - Luky Bot Memory

## Latest Updates
- **2026-02-22**: Automated backup system installed
  - Daily backups at 3am UTC
  - Local: `/root/openclaw-backups/`
  - 7-day retention + weekly backups
  - Backup script: `/root/.openclaw/backup/backup-local.sh`

- **2026-02-22**: Bot configuration restored after troubleshooting
  - Identity: Luky Bot (לוקי בוט)
  - 47 skills installed (google-speech, home-assistant-manager, model-router, etc.)
  - WhatsApp: +972527497367
  - Group "בוטים": 120363425850729867@g.us (no @mention needed)

- **2026-02-22**: Model configuration updated
  - Primary: zai/glm-4.7 (Z.ai GLM 4.7)
  - API: anthropic-messages
  - Provider: Z.ai

---

## System Access
- **WhatsApp**: +972527497367 (luky bot)
- **Home Assistant**: https://ha.right-api.com (token configured)
- **Spotify**: OAuth configured
- **Discord**: @luky

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


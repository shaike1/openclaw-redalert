#!/bin/bash
# One-time reminder for Shira's English lesson with Katie
# Date: March 2, 2026 at 15:00

WHATSAPP_GROUP="120363417492964228@g.us"
MESSAGE="⏰ *תזכורת לשירה*

שיעור אנגלית עם קייטי ב-15:30 📚

🤖 Luky Bot"

# Save message to file
echo "$MESSAGE" > /tmp/katies_reminder_message.txt

# Try to send via OpenClaw
openclaw message send \
    --channel whatsapp \
    --target "$WHATSAPP_GROUP" \
    --message "$MESSAGE" \
    >> /var/log/katies_reminder.log 2>&1

echo "Reminder sent at $(date)" >> /var/log/katies_reminder.log

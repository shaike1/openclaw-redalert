#!/bin/bash
# שולח עדכון שיעורי בית לקבוצת WhatsApp

WHATSAPP_GROUP="https://chat.whatsapp.com/HBcEOuyl1WU9NZ0LAhRSlS"
MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
    echo "Usage: $0 <message>"
    exit 1
fi

# שליחה דרך clawdbot message tool
# הקבוצה תזוהה אוטומטית מה-URL

echo "📤 שולח הודעה לקבוצה..."
echo "$MESSAGE"

# כרגע רק מדפיס - צריך להשתמש ב-message tool
# message --channel whatsapp --target "$WHATSAPP_GROUP" --message "$MESSAGE"

exit 0

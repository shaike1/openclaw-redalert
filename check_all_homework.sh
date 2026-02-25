#!/bin/bash
# Check homework for both kids and send to WhatsApp group

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_DIR="/tmp/webtop_homework_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TEMP_DIR"

# GENERIC_STUDENT_2
echo "🔍 בודק שיעורי בית לGENERIC_STUDENT_2..."
cd "$SCRIPT_DIR"
python3 get_homework.py REDACTED_STUDENT_2 REDACTED_PASSWORD_2 > "$TEMP_DIR/yuval.txt" 2>&1
YUVAL_JSON="/tmp/webtop_homework_REDACTED_STUDENT_2.json"

# GENERIC_STUDENT_1
echo "🔍 בודק שיעורי בית לGENERIC_STUDENT_1..."
cd "$SCRIPT_DIR"
python3 get_homework.py REDACTED_STUDENT_1 REDACTED_PASSWORD_1 > "$TEMP_DIR/shira.txt" 2>&1
SHIRA_JSON="/tmp/webtop_homework_REDACTED_STUDENT_1.json"

# יצירת הודעה מסכמת
MESSAGE="📚 *סיכום שיעורי בית* - $(date '+%d/%m/%Y %H:%M')

"

# עיבוד GENERIC_STUDENT_2
if [ -f "$YUVAL_JSON" ]; then
    YUVAL_SUCCESS=$(jq -r '.success' "$YUVAL_JSON" 2>/dev/null)
    if [ "$YUVAL_SUCCESS" = "true" ]; then
        YUVAL_NAME=$(jq -r '.student_name // "GENERIC_STUDENT_2"' "$YUVAL_JSON")
        YUVAL_SCHOOL=$(jq -r '.school // "לא ידוע"' "$YUVAL_JSON")
        YUVAL_COUNT=$(jq -r '.homework | length' "$YUVAL_JSON")
        
        MESSAGE+="👤 *$YUVAL_NAME*
🏫 $YUVAL_SCHOOL
"
        
        if [ "$YUVAL_COUNT" -gt 0 ]; then
            MESSAGE+="📖 שיעורי בית: $YUVAL_COUNT
"
            # הוספת פרטי שיעורי הבית
            HOMEWORK=$(jq -r '.homework[] | "- \(.subject // "ללא נושא"): \(.content // .raw_text // "אין תוכן")"' "$YUVAL_JSON" 2>/dev/null)
            MESSAGE+="$HOMEWORK
"
        else
            MESSAGE+="✅ אין שיעורי בית
"
        fi
    else
        MESSAGE+="👤 *GENERIC_STUDENT_2*
❌ שגיאה בחיבור
"
    fi
else
    MESSAGE+="👤 *GENERIC_STUDENT_2*
❌ לא נמצא קובץ נתונים
"
fi

MESSAGE+="
---

"

# עיבוד GENERIC_STUDENT_1
if [ -f "$SHIRA_JSON" ]; then
    SHIRA_SUCCESS=$(jq -r '.success' "$SHIRA_JSON" 2>/dev/null)
    if [ "$SHIRA_SUCCESS" = "true" ]; then
        SHIRA_NAME=$(jq -r '.student_name // "GENERIC_STUDENT_1"' "$SHIRA_JSON")
        SHIRA_SCHOOL=$(jq -r '.school // "לא ידוע"' "$SHIRA_JSON")
        SHIRA_COUNT=$(jq -r '.homework | length' "$SHIRA_JSON")
        
        MESSAGE+="👤 *$SHIRA_NAME*
🏫 $SHIRA_SCHOOL
"
        
        if [ "$SHIRA_COUNT" -gt 0 ]; then
            MESSAGE+="📖 שיעורי בית: $SHIRA_COUNT
"
            # הוספת פרטי שיעורי הבית
            HOMEWORK=$(jq -r '.homework[] | "- \(.subject // "ללא נושא"): \(.content // .raw_text // "אין תוכן")"' "$SHIRA_JSON" 2>/dev/null)
            MESSAGE+="$HOMEWORK
"
        else
            MESSAGE+="✅ אין שיעורי בית
"
        fi
    else
        MESSAGE+="👤 *GENERIC_STUDENT_1*
❌ שגיאה בחיבור
"
    fi
else
    MESSAGE+="👤 *GENERIC_STUDENT_1*
❌ לא נמצא קובץ נתונים
"
fi

# שמירת ההודעה לקובץ
echo "$MESSAGE" > "$TEMP_DIR/message.txt"

# הדפסת ההודעה למסך
echo "$MESSAGE"

# ניקוי
# rm -rf "$TEMP_DIR"

echo "✅ בדיקה הושלמה!"

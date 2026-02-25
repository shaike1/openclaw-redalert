#!/usr/bin/env python3
"""
Legacy WhatsApp Homework Script - Keep for Backward Compatibility
סקריפט ישן לשליחת שיעורי בית ל-WhatsApp (לשימוש עתידי)
"""

import subprocess
import json
import os
import sys
from datetime import datetime

# הגדרות - ניתן לשנות את זה
GROUP_JID = os.getenv('WHATSAPP_GROUP_JID', 'REDACTED_GROUP_ID@g.us')
WEBTOP_DIR = "/root/clawd/skills/webtop-skill"
GET_HOMEWORK_SCRIPT = f"{WEBTOP_DIR}/get_homework.py"

# פרטי התלמידים
STUDENTS = [
    {"name": "GENERIC_STUDENT_2", "username": "REDACTED_STUDENT_2", "password": "REDACTED_PASSWORD_2"},
    {"name": "GENERIC_STUDENT_1", "username": "REDACTED_STUDENT_1", "password": "REDACTED_PASSWORD_1"}
]

def create_enhanced_group_message():
    """יוצר הודעה משופרת לקבוצה עם סנכרון ליומן"""
    now = datetime.now()
    
    # בדיקה אם יש יומן היום
    today_summary = get_daily_summary(now.strftime('%Y-%m-%d'))
    
    message = f"""
🏫 *עדכוני שיעורי בית - נעמי שמר*
🗓️ תאריך: {now.strftime('%d/%m/%Y')} | ⏰ שעה: {now.strftime('%H:%M')}
======================================================================

"""
    
    # קבלת נתונים מפורסרים משופרים
    shira_data = get_student_homework("GENERIC_STUDENT_1", "REDACTED_STUDENT_1", "REDACTED_PASSWORD_1")
    if shira_data and shira_data.get('success'):
        homework_list = shira_data.get('homework', [])
        full_text = homework_list[0].get('full_text', '') if homework_list else ''
        
        # פרסר משופר עם הפרדות ברורות
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        subjects = ['עברית בחצאים', 'מתמטיקה', 'אנגלית', 'מדעים', 'חנ"ג', 
                     'תולדות', 'גאוגרפיה', 'טכנולוגיה', 'אומנות', 'ספורט', 'מוזיקה']
        
        current_subject = None
        homework_found = False
        
        for line in lines:
            if line in subjects:
                if current_subject:
                    message += f"\\n❌ לא הוזן שיעורי בית\\n"
                current_subject = line
                message += f"\\n📁 {current_subject}\\n"
            elif line.startswith('שיעור '):
                if current_subject:
                    message += f"🎓 {line}\\n"
            elif 'נושא' in line:
                if current_subject:
                    message += f"🎯 {line.replace('נושא שיעור:', '').strip()}\\n"
            elif 'שיעורי בית:' in line:
                homework_text = line.replace('שיעורי בית:', '').strip()
                if current_subject and homework_text and homework_text != 'לא הוזן':
                    message += f"\\n📚 *שיעורי בית:* {homework_text}\\n\\n"
                    homework_found = True
                elif current_subject:
                    message += f"\\n❌ לא הוזן שיעורי בית\\n\\n"
        
        # הוספת שיעורי הבית לסיכום
        if homework_found:
            message += "\\n🎯 *שיעורי בית מזוהים:*"
            for line in lines:
                if 'שיעורי בית:' in line and 'לא הוזן' not in line:
                    subject = None
                    for subj in subjects:
                        if lines.index(line) > 0 and lines[lines.index(line) - 1] == subj:
                            subject = subj
                            break
                    
                    if subject:
                        homework_text = line.replace('שיעורי בית:', '').strip()
                        message += f"\\n\\n📚 *{subject}:* {homework_text}"
        
        # הוספת תלמיד GENERIC_STUDENT_2
        message += "\\n\\n👤 *GENERIC_STUDENT_2*\\n"
        message += "═════════════════════════════════════════\\n"
        
        yuval_data = get_student_homework("GENERIC_STUDENT_2", "REDACTED_STUDENT_2", "REDACTED_PASSWORD_2")
        if yuval_data and yuval_data.get('success'):
            yuval_homework = yuval_data.get('homework', [])
            if yuval_homework:
                yuval_text = yuval_homework[0].get('full_text', '')
                yuval_lines = [line.strip() for line in yuval_text.split('\\n') if line.strip()]
                
                for line in yuval_lines:
                    if 'שיעורי בית:' in line and 'לא הוזן' not in line:
                        homework_text = line.replace('שיעורי בית:', '').strip()
                        message += f"\\n📚 *שיעורי בית:* {homework_text}\\n\\n"
                    elif 'אנגלית' in line or 'היסטוריה' in line:
                        message += f"\\n📖 {line}\\n"
    
    else:
        message += "\\n❌ לא ניתן לקבל נתונים מ-Webtop\\n"
    
    # הוספת יומן היום אם זמין
    if today_summary:
        message += f"\\n\\n📅 *יומן היום:*\\n"
        message += f"{today_summary}"
    
    # הוספת סיכום ולינקים
    message += f"""
\\n═════════════════════════════════════════
📝 *סיכום כללי* 📊
======================================================================

🎓 מצב: ההודעה כוללת פירוט מלא של שיעורי הבית
📱 יעד: קבוצת ה-WhatsApp של הכיתה
⏰ זמן: {now.strftime('%H:%M')} יום {now.strftime('%d/%m/%Y')}
💡 העדכון: מתבצע אוטומטית דרך סקריפט

🔗 *לינקים שימושיים* 🔗
- יומן המשפחה: family-calendar-id
- שיעורים מתוקננים: calendar.google.com
- יומן הכיתה: webtop.smartschool.co.il

🔔 התראות: התראות יישלחו עם כל עדכון בשיעורים
📞 תמיכה: עזרה בהגדרת המערכת: system-admin
"""
    
    return message

# ... שאר הפונקציות הקיימות (get_daily_summary, get_student_homework, send_to_whatsapp, main)

def send_to_whatsapp(message):
    """שולח הודעה ל-WhatsApp"""
    try:
        # תיקון פורמט - החלפת \\n בסימנים נכונים
        clean_message = message.replace('\\n', '\n').replace('\n\n\n\n', '\n\n').strip()
        
        # ניסיון שליחה דרך clawdbot
        target = GROUP_JID if '@' in GROUP_JID else 'REDACTED_PHONE'
        
        print(f"🔄 ניסיון שליחה דרך clawdbot ל: {target}")
        print(f"📝 אורך ההודעה: {len(clean_message)} תווים")
        
        # בניית פקודת clawdbot עם ההודעה הנקייה - עם נתיב מלא
        cmd = [
            '/root/.nvm/versions/node/v22.22.0/bin/clawdbot', 'message', 'send',
            '--channel', 'whatsapp',
            '--target', target,
            '--message', clean_message
        ]
        
        # הרצת פקודת clawdbot
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("🎉 ההודעה נשלחה בהצלחה!")
            return True
        else:
            print(f"❌ נכשלה השליחה: {result.stderr}")
            
            # אם זה עובד ב-dry-run, נשמור לקובץ
            if 'dry-run' in result.stderr:
                temp_file = f"/tmp/group_homework_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(clean_message)
                print(f"✅ ההודעה נשמרה לקובץ: {temp_file}")
                return temp_file
        
        # שמירת ההודעה לקובץ כגיבוי
        temp_file = f"/tmp/group_homework_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(clean_message)
        
        print(f"✅ ההודעה הוכנה לשליחה ל: {target}")
        print(f"📁 נשמרה ב: {temp_file}")
        
        return temp_file
        
    except Exception as e:
        print(f"❌ שגיאה בשליחה: {e}")
        # שמירת ההודעה לקובץ כגיבוי
        temp_file = f"/tmp/group_homework_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(message)
        return temp_file

def main():
    """פונקציה ראשית"""
    print("🚀 מתחיל בדיקת שיעורי בית לקבוצה...")
    
    # יצירת ההודעה
    message = create_enhanced_group_message()
    
    # תיקון פורמט - החלפת \n בסימנים נכונים
    clean_message = message.replace('\\n', '\n').replace('\n\n\n\n', '\n\n').strip()
    
    # שליחה
    result = send_to_whatsapp(clean_message)
    
    if result:
        if isinstance(result, str):
            print(f"✅ הודעה מוכנה ב: {result}")
        print("🎉 העדכון הסתיים!")
    else:
        print("❌ נכשלה שליחת ההודעה")

if __name__ == "__main__":
    main()
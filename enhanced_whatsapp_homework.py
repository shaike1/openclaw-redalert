#!/usr/bin/env python3
"""
Enhanced WhatsApp Homework Automation with Icons & Student Formatting
אוטומציית WhatsApp משופרת עם אייקונים ופורמט תלמיד-מקצוע
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
    {"name": "GENERIC_STUDENT_1", "username": "REDACTED_STUDENT_1", "password": "REDACTED_PASSWORD_1"},
    {"name": "GENERIC_STUDENT_2", "username": "REDACTED_STUDENT_2", "password": "REDACTED_PASSWORD_2"}
]

def get_student_homework(student_name, username, password):
    """מקבל את נתוני השיעורים לתלמיד בפורמט משופר"""
    try:
        result = subprocess.run(
            ["python3", GET_HOMEWORK_SCRIPT, username, password],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=WEBTOP_DIR
        )
        
        if result.returncode == 0:
            json_file = f"/tmp/webtop_homework_{username}.json"
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
    except Exception as e:
        print(f"שגיאה בקבלת שיעורים עבור {student_name}: {e}")
    
    return None

def create_enhanced_whatsapp_message():
    """יוצר הודעת WhatsApp משופרת עם אייקונים ופורמט תלמיד-מקצוע"""
    now = datetime.now()
    
    # כותרת ראשית עם אייקון מושך
    message = f"""
🎓 *עדכוני שיעורי בית יומיים* 📚
🏫 בית ספר: נעמי שמר
🗓️ תאריך: {now.strftime('%d/%m/%Y')} ({get_hebrew_day_name(now.strftime('%Y-%m-%d'))})
⏰ שעה: {now.strftime('%H:%M')}
═════════════════════════════════════════

"""
    
    homework_count = 0
    
    # עיבוד שיעורי בית לכל תלמיד
    for student in STUDENTS:
        student_name = student['name']
        username = student['username']
        password = student['password']
        
        student_data = get_student_homework(student_name, username, password)
        
        if student_data and student_data.get('success'):
            homework_list = student_data.get('homework', [])
            
            if homework_list:
                message += f"\\n👤 *{student_name}* 🎯\\n"
                message += f"═════════════════════════════\\n"
                
                for homework in homework_list:
                    subject = homework.get('subject', 'לא צוין')
                    content = homework.get('content', 'לא צוין')
                    due_date = homework.get('due_date', 'לא צוין')
                    
                    # פורמט משופר עם אייקון
                    message += f"\\n📚 *{subject}*\\n"
                    message += f"📝 תוכן: {content}\\n"
                    message += f"📅 יעד: {format_date(due_date)}\\n"
                    message += f"━━━━━━━━━━━━━━━━━━━━━━━━━━─\\n"
                    
                    homework_count += 1
            else:
                message += f"\\n👤 *{student_name}*\\n"
                message += f"═════════════════════════════\\n"
                message += f"❌ אין שיעורי בית חדשים\\n"
                message += f"━━━━━━━━━━━━━━━━━━━━━━━━━━─\\n"
        else:
            message += f"\\n👤 *{student_name}*\\n"
            message += f"═════════════════════════════\\n"
            message += f"❌ לא ניתן לקבל נתונים\\n"
            message += f"━━━━━━━━━━━━━━━━━━━━━━━━━━─\\n"
    
    # סיכום כללי עם אייקונים
    message += f"""
\\n📊 *סיכום יומי* 📈
═════════════════════════════
🎯 סה"כ מטלות: {homework_count}
⏰ זמן עדכון: {now.strftime('%H:%M')}
📱 מקור: סקריפט אוטומטי

💡 טיפ: עדכון זה נשלח אוטומטית מדי יום בשעה 18:00!
🔔 התראות נשלחות עם כל שינוי בשיעורי הבית.
"""
    
    # הוספת לינק לפרטים נוספים
    message += f"""
\\n📚 *לפרטים נוספים* 🔗
═════════════════════════════
🔗 צפה בשיעורים ב-Google Calendar
🔗 יומן משפחה: family-calendar-id
📱 שאלות? 📩 צור קשר עם המערכת.
"""
    
    return message

def get_hebrew_day_name(date_str):
    """מחזיר את שם היום בעברית"""
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        hebrew_days = ["יום ראשון", "יום שני", "יום שלישי", "יום רביעי", "יום חמישי", "יום שישי", "יום שבת"]
        return hebrew_days[date_obj.weekday()]
    except:
        return ''

def format_date(date_str):
    """מעצב תאריך בפורמט ישראלי"""
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except:
        return date_str

def send_enhanced_whatsapp_message():
    """שולח הודעת WhatsApp משופרת"""
    try:
        # יצירת ההודעה המשופרת
        message = create_enhanced_whatsapp_message()
        
        # ניקוי ההודעה מסימנים מיותרים
        clean_message = message.replace('\\n', '\n').strip()
        
        # הגדרת היעד
        target = GROUP_JID if '@' in GROUP_JID else 'REDACTED_PHONE'
        
        print(f"🔄 שולח הודעה משופרת ל: {target}")
        print(f"📝 אורך ההודעה: {len(clean_message)} תווים")
        
        # בניית פקודת clawdbot
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
            print("🎉 הודעת WhatsApp נשלחה בהצלחה!")
            print("✅ ההודעה כוללת:")
            print("   • אייקונים מסודרים")
            print("   • פורמט תלמיד-מקצוע ברור")
            print("   • הפרדות ויזואליות")
            print("   • סיכום יומי")
            return True
        else:
            print(f"❌ נכשלה השליחה: {result.stderr}")
            
            # שמירת ההודעה לקובץ
            temp_file = f"/tmp/enhanced_whatsapp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(clean_message)
            print(f"✅ ההודעה נשמרה לקובץ: {temp_file}")
            return temp_file
            
    except Exception as e:
        print(f"❌ שגיאה בשליחה: {e}")
        return None

def main():
    """פונקציה ראשית"""
    print("🚀 מתחיל בשליחת הודעת WhatsApp משופרת...")
    print("🎯 כולל אייקונים, פורמט תלמיד-מקצוע, וסטייל משופר!")
    
    # שליחת ההודעה
    result = send_enhanced_whatsapp_message()
    
    if result:
        if isinstance(result, str):
            print(f"✅ הודעה מוכנה ב: {result}")
        print("🎉 העדכון המשופר הסתיים!")
        print("📱 ההודעה תכלול את אותו הפירוט עם אייקונים כמו ביומן!")
    else:
        print("❌ נכשלה שליחת ההודעה")

if __name__ == "__main__":
    main()
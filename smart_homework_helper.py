#!/usr/bin/env python3
"""
עוזר שיעורי בית חכם - שולח הודעות מדויקות ושימושיות
"""

import subprocess
import json
import os
import sys
from datetime import datetime

# הגדרות
WEBTOP_DIR = "/root/clawd/skills/webtop-skill"
GET_HOMEWORK_SCRIPT = f"{WEBTOP_DIR}/get_homework.py"
TARGET_PHONE = "REDACTED_PHONE"  # מספר שלך - כעת נשלח אליך ותעביר לקבוצה

# פרטי התלמידים
STUDENTS = [
    {"name": "GENERIC_STUDENT_2", "username": "REDACTED_STUDENT_2", "password": "REDACTED_PASSWORD_2"},
    {"name": "GENERIC_STUDENT_1", "username": "REDACTED_STUDENT_1", "password": "REDACTED_PASSWORD_1"}
]

def get_student_homework(student_name, username, password):
    """מקבל את נתוני השיעורים לתלמיד"""
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
        print(f"❌ שגיאה ב-{student_name}: {e}")
    
    return None

def extract_homework_info(data):
    """מחלץ מידע מפורט על שיעורי הבית"""
    if not data or not data.get('success'):
        return None
    
    homework_list = data.get('homework', [])
    if not homework_list:
        return None
    
    full_text = homework_list[0].get('full_text', '')
    if not full_text:
        return None
    
    lines = [line.strip() for line in full_text.split('\n') if line.strip()]
    homework_info = []
    
    subjects = ['עברית בחצאים', 'מתמטיקה', 'אנגלית', 'מדעים', 'חנ"ג', 
                 'תולדות', 'גאוגרפיה', 'טכנולוגיה', 'אומנות', 'ספורט', 'מוזיקה']
    
    current_subject = None
    
    for line in lines:
        if line in subjects:
            if current_subject and current_subject.get('homework'):
                homework_info.append(current_subject)
            current_subject = {
                'subject': line,
                'homework': None,
                'teachers': [],
                'lessons': [],
                'topics': []
            }
        elif current_subject:
            if line.startswith('שיעור '):
                current_subject['lessons'].append(line)
            elif 'נושא' in line:
                current_subject['topics'].append(line.replace('נושא שיעור:', '').strip())
            elif 'שיעורי בית:' in line:
                homework_text = line.replace('שיעורי בית:', '').strip()
                if homework_text and homework_text != 'לא הוזן':
                    current_subject['homework'] = homework_text
    
    # הוספת הנושא האחרון
    if current_subject and current_subject.get('homework'):
        homework_info.append(current_subject)
    
    return homework_info

def create_quick_summary():
    """יוצר סיכום מהיר"""
    now = datetime.now()
    
    message = f"📱 *סיכום מהיר שיעורי בית*\n"
    message += f"🗓️ {now.strftime('%d/%m/%Y')} | ⏰ {now.strftime('%H:%M')}\n"
    message += "=" * 50 + "\n\n"
    
    for student in STUDENTS:
        data = get_student_homework(student['name'], student['username'], student['password'])
        
        if data and data.get('success'):
            homework_count = len(data.get('homework', []))
            homework_info = extract_homework_info(data)
            
            message += f"👤 *{student['name']}*\n"
            if homework_count > 0:
                message += f"   ✅ שיעורי בית: {homework_count}\n"
                
                if homework_info:
                    message += "   📚 פרטים:\n"
                    for hw in homework_info:
                        message += f"      • {hw['subject']}: {hw['homework']}\n"
            else:
                message += "   ❌ אין שיעורי בית\n"
        else:
            message += f"👤 *{student['name']}*\n"
            message += "   ❌ בעית חיבור\n"
        
        message += "\n"
    
    message += f"📡 סנכרון: {now.strftime('%d/%m/%Y %H:%M')}\n"
    message += f"🤖 בדיקה מהירה"
    
    return message

def create_detailed_report():
    """יוצר דוח מפורט"""
    now = datetime.now()
    
    message = f"📊 *דוח מפורט - שיעורי בית נעמי שמר*\n"
    message += f"🗓️ {now.strftime('%d/%m/%Y')} | ⏰ {now.strftime('%H:%M')}\n"
    message += "=" * 70 + "\n\n"
    
    for student in STUDENTS:
        message += f"👤 *{student['name']}*\n"
        message += f"🏫 {data.get('school', 'נעמי שמר')}\n"
        message += "-" * 50 + "\n"
        
        data = get_student_homework(student['name'], student['username'], student['password'])
        
        if data and data.get('success'):
            homework_count = len(data.get('homework', []))
            homework_info = extract_homework_info(data)
            
            message += f"✅ חיבור: מוצלח\n"
            message += f"📚 שיעורי בית: {homework_count}\n"
            
            if homework_info:
                message += f"\n📝 פירוט שיעורי בית:\n"
                for hw in homework_info:
                    message += f"   *{hw['subject']}*:\n"
                    message += f"      📖 {hw['homework']}\n"
            
            # מבנה היום
            full_text = data.get('homework', [{}])[0].get('full_text', '')
            if full_text:
                lines = full_text.split('\n')[:10]  # 10 השורות הראשונות
                message += f"\n📅 מבנה היום (ראשונים):\n"
                for line in lines:
                    line = line.strip()
                    if line:
                        message += f"   • {line}\n"
        else:
            message += f"❌ חיבור: נכשל\n"
        
        message += "\n" + "=" * 70 + "\n\n"
    
    message += f"🤖 ניתוח מדויק | שלוח ל: {TARGET_PHONE}"
    
    return message

def create_reminder_check():
    """בודק תזכורות"""
    now = datetime.now()
    message = f"⏰ *בדיקת תזכורות שיעורי בית*\n"
    message += f"🗓️ {now.strftime('%d/%m/%Y')} | ⏰ {now.strftime('%H:%M')}\n"
    message += "=" * 50 + "\n\n"
    
    # בדיקת תאריכים
    for student in STUDENTS:
        data = get_student_homework(student['name'], student['username'], student['password'])
        
        if data and data.get('success'):
            full_text = data.get('homework', [{}])[0].get('full_text', '')
            lines = full_text.split('\n')
            
            # חיפוש תאריכים
            import re
            date_pattern = r'(\d{1,2})[/.-](\d{1,2})'
            dates_found = []
            
            for line in lines:
                matches = re.findall(date_pattern, line)
                for match in matches:
                    day, month = map(int, match)
                    try:
                        check_date = datetime(now.year, month, day)
                        days_until = (check_date - now).days
                        if 1 <= days_until <= 7:
                            dates_found.append(check_date.strftime('%d/%m'))
                    except:
                        continue
            
            if dates_found:
                message += f"👤 *{student['name']}* - תאריכים קרובים:\n"
                message += f"   📅 {', '.join(dates_found)}\n"
            else:
                message += f"👤 *{student['name']}* - אין תאריכים קרובים\n"
        else:
            message += f"👤 *{student['name']}* - לא ניתן לבדוק\n"
        
        message += "\n"
    
    message += f"💡 טיפ: בדוק תאריכים קרובים בתוך 7 ימים"
    
    return message

def send_message(message, phone_number=TARGET_PHONE):
    """שולח הודעה"""
    try:
        temp_file = f"/tmp/urgent_homework_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(message)
        
        print(f"📤 ההודעה הוכנה ב: {temp_file}")
        return temp_file
    except Exception as e:
        print(f"❌ שגיאה בשליחה: {e}")
        return None

def main():
    """פונקציה ראשית"""
    if len(sys.argv) < 2:
        print("❌ צריך לציין סוג דוח")
        print("אפשרויות: quick, detailed, reminder")
        return
    
    report_type = sys.argv[1]
    
    print(f"🚀 מכין {report_type} דוח...")
    
    if report_type == "quick":
        message = create_quick_summary()
    elif report_type == "detailed":
        message = create_detailed_report()
    elif report_type == "reminder":
        message = create_reminder_check()
    else:
        print("❌ סוג דוח לא ידוע")
        return
    
    result = send_message(message)
    
    if result:
        print(f"✅ הדוח מוכן!")
        print("=" * 60)
        print(message)
        print("=" * 60)
    else:
        print("❌ נכשלה הכנת הדוח")

if __name__ == "__main__":
    main()
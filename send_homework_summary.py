#!/usr/bin/env python3
"""
שליחת סיכום שיעורי בית ל-WhatsApp
"""

import subprocess
import json
import os
from datetime import datetime

# הגדרת נתיבים
WEBTOP_DIR = "/root/clawd/skills/webtop-skill"
GET_HOMEWORK_SCRIPT = f"{WEBTOP_DIR}/get_homework.py"

# פרטי התלמידים
STUDENTS = [
    {
        "name": "GENERIC_STUDENT_2",
        "username": "REDACTED_STUDENT_2",
        "password": "REDACTED_PASSWORD_2",
        "json_file": "/tmp/webtop_homework_REDACTED_STUDENT_2.json"
    },
    {
        "name": "GENERIC_STUDENT_1",
        "username": "REDACTED_STUDENT_1",
        "password": "REDACTED_PASSWORD_1",
        "json_file": "/tmp/webtop_homework_REDACTED_STUDENT_1.json"
    }
]

def get_homework_for_student(student):
    """מריץ את הסקריפט לקבלת שיעורי בית"""
    print(f"🔍 בודק שיעורי בית ל{student['name']}...")
    
    try:
        result = subprocess.run(
            ["python3", GET_HOMEWORK_SCRIPT, student['username'], student['password']],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=WEBTOP_DIR
        )
        
        if result.returncode == 0:
            # קריאת הקובץ JSON
            if os.path.exists(student['json_file']):
                with open(student['json_file'], 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        return None
    
    except Exception as e:
        print(f"❌ שגיאה ב{student['name']}: {e}")
        return None

def format_homework_message():
    """יוצר הודעה מעוצבת של שיעורי הבית"""
    now = datetime.now()
    message = f"📚 *סיכום שיעורי בית* - {now.strftime('%d/%m/%Y %H:%M')}\n\n"
    
    for student in STUDENTS:
        data = get_homework_for_student(student)
        
        if data and data.get('success'):
            student_name = data.get('student_name') or student['name']
            school = data.get('school') or 'לא ידוע'
            homework_list = data.get('homework', [])
            
            message += f"👤 *{student_name}*\n"
            message += f"🏫 {school}\n"
            
            if homework_list:
                message += f"📖 שיעורי בית: {len(homework_list)}\n\n"
                
                for i, hw in enumerate(homework_list, 1):
                    subject = hw.get('subject', 'ללא נושא')
                    content = hw.get('content') or hw.get('raw_text', 'אין תוכן')
                    
                    # חיתוך תוכן ארוך מדי
                    if len(content) > 200:
                        content = content[:197] + "..."
                    
                    message += f"{i}. *{subject}*\n"
                    message += f"   {content}\n\n"
            else:
                message += "✅ אין שיעורי בית\n\n"
        else:
            message += f"👤 *{student['name']}*\n"
            message += "❌ שגיאה בחיבור\n\n"
        
        message += "---\n\n"
    
    return message.strip()

def send_to_whatsapp(message, group_id=None):
    """שולח הודעה ל-WhatsApp"""
    print("📤 שולח הודעה ל-WhatsApp...")
    
    # TODO: הוסף את מזהה הקבוצה שלך כאן
    # אם לא מוגדר, ההודעה תישלח אליך
    target = group_id or "REDACTED_PHONE"
    
    # שמירת ההודעה לקובץ זמני
    temp_file = f"/tmp/homework_message_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(message)
    
    print(f"💾 ההודעה נשמרה ב: {temp_file}")
    print("\n" + "="*60)
    print(message)
    print("="*60 + "\n")
    
    return temp_file

def main():
    """פונקציה ראשית"""
    print("🚀 מתחיל בדיקת שיעורי בית...")
    print("="*60 + "\n")
    
    # יצירת ההודעה
    message = format_homework_message()
    
    # שליחה ל-WhatsApp
    message_file = send_to_whatsapp(message)
    
    print(f"\n✅ הבדיקה הושלמה!")
    print(f"📄 ההודעה נשמרה ב: {message_file}")

if __name__ == "__main__":
    main()

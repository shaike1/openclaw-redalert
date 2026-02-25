#!/usr/bin/env python3
"""
מערכת פשוטה לניטור שיעורי בית
"""

import subprocess
import json
import os
from datetime import datetime

WEBTOP_DIR = "/root/clawd/skills/webtop-skill"
GET_HOMEWORK_SCRIPT = f"{WEBTOP_DIR}/get_homework.py"

STUDENTS = [
    {"name": "GENERIC_STUDENT_2", "username": "REDACTED_STUDENT_2", "password": "REDACTED_PASSWORD_2"},
    {"name": "GENERIC_STUDENT_1", "username": "REDACTED_STUDENT_1", "password": "REDACTED_PASSWORD_1"}
]

def check_student(student_name, username, password):
    """בודק שיעורי בית לתלמיד"""
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
                    if data.get('success'):
                        homework_count = len(data.get('homework', []))
                        return {
                            'name': student_name,
                            'success': True,
                            'count': homework_count,
                            'data': data
                        }
        
        return {'name': student_name, 'success': False, 'count': 0}
    
    except Exception as e:
        return {'name': student_name, 'success': False, 'count': 0, 'error': str(e)}

def main():
    print("מתחיל בדיקת שיעורי בית...")
    print("=" * 60)
    
    total_students = 0
    total_homework = 0
    results = []
    
    # בדוק כל תלמיד
    for student in STUDENTS:
        total_students += 1
        result = check_student(student['name'], student['username'], student['password'])
        results.append(result)
        
        if result['success']:
            total_homework += result['count']
            
            print(f"תלמיד: {student['name']}")
            print(f"   חיבור מוצלח")
            print(f"   שיעורי בית: {result['count']}")
            
            if result['count'] > 0:
                print("   פרטי השיעורים:")
                homework_list = result['data'].get('homework', [])
                for i, hw in enumerate(homework_list, 1):
                    subject = hw.get('subject', 'ללא נושא')
                    content = hw.get('content') or hw.get('raw_text', 'אין תוכן')[:100]
                    print(f"      {i}. {subject}: {content}")
        else:
            print(f"תלמיד: {student['name']}")
            print(f"   שגיאה בחיבור")
        
        print("   " + "-" * 40)
    
    # תוצאות סופיות
    print(f"\nסיכום:")
    print(f"   תלמידים נבדקים: {total_students}")
    print(f"   תלמידים מחוברים: {sum(1 for r in results if r['success'])}")
    print(f"   סהכ שיעורי בית: {total_homework}")
    
    # שלח התראה אם יש שיעורי בית
    if total_homework > 0:
        message = f"שיעורי בית חדשים - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        
        for result in results:
            if result['success'] and result['count'] > 0:
                message += f"{result['name']}: {result['count']} שיעורים\n"
        
        # יצירת קובץ לשליחה
        temp_file = f"/tmp/homework_notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(message)
        
        print(f"\nהתראה נשלחת ל: {temp_file}")
    
    print(f"\nהבדיקה הושלמה!")

if __name__ == "__main__":
    main()
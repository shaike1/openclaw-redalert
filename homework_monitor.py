#!/usr/bin/env python3
"""
מערכת התראות חכמה לשיעורי בית
בודק כל שעה בשעות הלימודים ושולח הודעה רק כשיש שיעורים חדשים
"""

import subprocess
import json
import os
import sys
from datetime import datetime, time
from typing import Dict, List, Optional

# הגדרות
WEBTOP_DIR = "/root/clawd/skills/webtop-skill"
GET_HOMEWORK_SCRIPT = f"{WEBTOP_DIR}/get_homework.py"
CONFIG_FILE = f"{WEBTOP_DIR}/homework_state.json"
LOG_FILE = f"{WEBTOP_DIR}/homework_monitor.log"

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

def log_message(message: str):
    """רשום ללוג"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def load_state() -> Dict:
    """טען את מצב הקודם מקובץ ההגדרות"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "last_check": None,
        "last_homework": {},
        "sent_notifications": []
    }

def save_state(state: Dict):
    """שמור את מצב המערכת"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def is_school_day() -> bool:
    """בודק אם היום הוא יום לימודים (סוף שבות, חגים וכו')"""
    # בודק שהיום לא שבת (5)
    weekday = datetime.now().weekday()
    return weekday < 5  # 0-4 = ראשון-שישי

def is_school_hours() -> bool:
    """בודק אם השעה הנוכחית בשעות הלימודים"""
    now = datetime.now().time()
    # בין 8:00 ל-15:00
    return time(8, 0) <= now <= time(15, 0)

def get_homework_for_student(student: Dict) -> Optional[Dict]:
    """מקבל שיעורי בית לתלמיד"""
    log_message(f"בודק שיעורי בית ל{student['name']}...")
    
    try:
        result = subprocess.run(
            ["python3", GET_HOMEWORK_SCRIPT, student['username'], student['password']],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=WEBTOP_DIR
        )
        
        if result.returncode == 0:
            if os.path.exists(student['json_file']):
                with open(student['json_file'], 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        return None
    
    except Exception as e:
        log_message(f"❌ שגיאה ב{student['name']}: {e}")
        return None

def format_homework_notification(data: Dict, student_name: str) -> str:
    """יוצר הודעה מסודרת כשיש שיעורי בית"""
    school = data.get('school') or 'לא ידוע'
    homework_list = data.get('homework', [])
    
    message = f"📚 *שיעורי בית חדשים!* - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    message += f"👤 *{student_name}*\n"
    message += f"🏫 {school}\n\n"
    
    if homework_list:
        message += f"📖 נמצאו {len(homework_list)} שיעורי בית:\n\n"
        
        for i, hw in enumerate(homework_list, 1):
            subject = hw.get('subject', 'ללא נושא')
            content = hw.get('content') or hw.get('raw_text', 'אין תוכן')
            
            # חיתוך תוכן ארוך
            if len(content) > 150:
                content = content[:147] + "..."
            
            message += f"{i}. *{subject}*\n"
            message += f"   {content}\n\n"
    else:
        message += "✅ לא נמצאו שיעורי בית חדשים\n"
    
    return message

def check_and_notify():
    """פונקציה ראשית - בודק ומודיע אם יש שיעורי בית"""
    state = load_state()
    
    # בדוק אם הזמן מתאים (שעות לימודים + יום לימודים)
    if not is_school_day():
        log_message("❌ לא יום לימודים (סוף שבות/חג)")
        return
    
    if not is_school_hours():
        log_message("❌ מחוץ לשעות הלימודים")
        return
    
    log_message("🔄 בודק שיעורי בית...")
    
    total_homework = 0
    notifications_to_send = []
    
    # בדוק לכל תלמיד
    for student in STUDENTS:
        data = get_homework_for_student(student)
        
        if data and data.get('success'):
            student_name = data.get('student_name') or student['name']
            homework_list = data.get('homework', [])
            
            # שמור את המצב הנוכחי
            state['last_homework'][student['name']] = {
                'count': len(homework_list),
                'last_check': datetime.now().isoformat(),
                'homework': homework_list
            }
            
            if homework_list:
                total_homework += len(homework_list)
                
                # בדוק אם יש שיעורים חדשים מהפעם האחרונה
                last_count = state['last_homework'].get(student['name'], {}).get('count', 0)
                
                if len(homework_list) > last_count:
                    message = format_homework_notification(data, student_name)
                    notifications_to_send.append(message)
                    log_message(f"📩 מצאתי שיעורים חדשים עבור {student_name}: {len(homework_list)}")
                else:
                    log_message(f"✅ אין שיעורים חדשים עבור {student_name}")
    
    # שמור את המצב
    save_state(state)
    
    # שלח התראות אם יש כאלה
    if notifications_to_send:
        log_message(f"🔔 מצאתי {len(notifications_to_send)} התראות לשליחה")
        
        # שלח את כל ההתראות
        for notification in notifications_to_send:
            send_notification(notification)
    else:
        log_message("✅ אין שיעורי בית חדשים להתראה")

def send_notification(message: str):
    """שולח הודעה ל-WhatsApp"""
    try:
        # ייצוא ההודעה לקובץ כדי ש-Clawdbot יוכל לשלוח אותה
        temp_file = f"/tmp/homework_notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(message)
        
        log_message(f"💾 ההודעה הוכנה לשליחה: {temp_file}")
        
        # המתן שיגיעה הודעה מסוג זה לשיחה
        return True
        
    except Exception as e:
        log_message(f"❌ שגיאה בשליחה: {e}")
        return False

if __name__ == "__main__":
    try:
        log_message("🚀 מתחיל בדיקה מערכתית...")
        check_and_notify()
        log_message("✅ הבדיקה הושלמה!")
    except Exception as e:
        log_message(f"❌ שגיאה כללית: {e}")
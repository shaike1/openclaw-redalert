#!/usr/bin/env python3
"""
Webtop Homework Monitor - מערכת ניטור שיעורי בית
בודק שינויים בשיעורי בית ושולח התראות לWhatsApp
"""

import json
import os
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import hashlib

# הגדרות
WHATSAPP_GROUP = "https://chat.whatsapp.com/HBcEOuyl1WU9NZ0LAhRSlS"
STATE_FILE = "/home/node/clawd/skills/webtop-skill/homework_state.json"

# פרטי התלמידים
STUDENTS = {
    "shira": {
        "name": "GENERIC_STUDENT_1",
        "username": "REDACTED_STUDENT_1",
        "password": "REDACTED_PASSWORD_1"
    },
    "yuval": {
        "name": "GENERIC_STUDENT_2", 
        "username": "REDACTED_STUDENT_2",
        "password": "REDACTED_PASSWORD_2"
    }
}


def get_homework(username, password):
    """מושך שיעורי בית מWebtop"""
    result = {
        "success": False,
        "student_name": None,
        "homework_text": None,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            page = browser.new_page()
            
            # התחברות
            page.goto("https://www.webtop.co.il/applications/loginMOENew/default.aspx", timeout=30000)
            time.sleep(3)
            
            page.click('#userName')
            page.fill('#userName', username)
            page.click('#password')
            time.sleep(0.5)
            page.fill('#password', password)
            time.sleep(1)
            page.click('button[type="submit"]')
            time.sleep(10)
            
            # שליפת נתונים
            body_text = page.inner_text('body')
            
            # שם תלמיד
            if 'צהריים טובים' in body_text or 'בוקר טוב' in body_text or 'ערב טוב' in body_text:
                lines = body_text.split('\n')
                for line in lines:
                    if 'טובים' in line or 'טוב' in line:
                        name = line.replace('צהריים טובים,', '').replace('בוקר טוב,', '').replace('ערב טוב,', '').strip()
                        if name and len(name) > 3:
                            result["student_name"] = name
                            break
            
            # שיעורי בית
            if 'שיעורי בית' in body_text.lower():
                # מציאת החלק הרלוונטי
                start = body_text.lower().find('שיעורי בית')
                end = body_text.find('התחברות משרד החינוך', start)
                if end == -1:
                    end = start + 1000
                
                homework_section = body_text[start:end]
                result["homework_text"] = homework_section
                result["success"] = True
            
            browser.close()
            
    except Exception as e:
        result["error"] = str(e)
        print(f"❌ שגיאה: {e}")
    
    return result


def parse_homework(homework_text):
    """מפרסר טקסט שיעורי בית למבנה מסודר"""
    if not homework_text:
        return []
    
    lines = homework_text.split('\n')
    lessons = []
    i = 1  # דילוג על "שיעורי בית"
    
    while i < len(lines):
        line = lines[i].strip()
        
        # בדיקה אם השורה הבאה היא "שיעור X"
        if i + 1 < len(lines) and lines[i + 1].strip().startswith('שיעור '):
            subject = line
            i += 1
            lesson_line = lines[i].strip()
            
            lesson = {
                "subject": subject,
                "lesson_num": lesson_line,
                "teacher": None,
                "topic": None,
                "homework": None
            }
            
            # מורה
            if i + 1 < len(lines):
                i += 1
                teacher = lines[i].strip()
                if teacher != 'התקיים':
                    lesson["teacher"] = teacher
            
            # דילוג על "התקיים"
            while i < len(lines) and 'התקיים' not in lines[i]:
                i += 1
            
            # נושא ושיעורי בית
            while i < len(lines):
                i += 1
                if i >= len(lines):
                    break
                if 'נושא שיעור:' in lines[i]:
                    lesson["topic"] = lines[i].replace('נושא שיעור:', '').strip()
                elif 'שיעורי בית:' in lines[i]:
                    hw = lines[i].replace('שיעורי בית:', '').strip()
                    if hw and hw != 'לא הוזן':
                        lesson["homework"] = hw
                    break
            
            lessons.append(lesson)
        else:
            i += 1
    
    return lessons


def get_homework_hash(homework_text):
    """יוצר hash של שיעורי הבית לזיהוי שינויים"""
    if not homework_text:
        return None
    return hashlib.md5(homework_text.encode()).hexdigest()


def load_state():
    """טוען מצב קודם"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_state(state):
    """שומר מצב"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def format_homework_message(student_name, lessons):
    """מעצב הודעה על שיעורי בית"""
    if not lessons:
        return f"📚 עדכון: ל{student_name} אין שיעורי בית להיום ✅"
    
    msg = f"📚 *שיעורי בית חדשים ל{student_name}!*\n\n"
    
    for i, lesson in enumerate(lessons, 1):
        msg += f"*{i}. {lesson['subject']}*\n"
        if lesson.get('teacher'):
            msg += f"👨‍🏫 {lesson['teacher']}\n"
        if lesson.get('topic'):
            msg += f"📝 {lesson['topic']}\n"
        if lesson.get('homework'):
            msg += f"✏️ *שיעורי בית:* {lesson['homework']}\n"
        else:
            msg += f"ℹ️ לא הוזן שיעורי בית\n"
        msg += "\n"
    
    msg += f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    
    return msg


def send_whatsapp_message(message):
    """שולח הודעה לקבוצת WhatsApp"""
    # השתמש ב-message tool של Clawdbot
    import subprocess
    
    # כתיבת ההודעה לקובץ זמני
    msg_file = "/tmp/homework_message.txt"
    with open(msg_file, 'w', encoding='utf-8') as f:
        f.write(message)
    
    print(f"📤 שולח הודעה לWhatsApp...")
    print(f"   קבוצה: {WHATSAPP_GROUP}")
    print(f"   תוכן: {message[:100]}...")
    
    # הודעה תישלח דרך Clawdbot
    # כרגע רק מדפיס - נצטרך להפעיל דרך message tool
    return True


def check_updates():
    """בודק עדכונים בשיעורי בית"""
    print("="*60)
    print(f"🔍 בדיקת שיעורי בית - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    state = load_state()
    updates = []
    
    for student_id, student in STUDENTS.items():
        print(f"\n📖 בודק {student['name']}...")
        
        result = get_homework(student['username'], student['password'])
        
        if result["success"]:
            current_hash = get_homework_hash(result["homework_text"])
            previous_hash = state.get(student_id, {}).get("hash")
            
            if current_hash != previous_hash:
                print(f"   🆕 יש שינוי!")
                
                lessons = parse_homework(result["homework_text"])
                message = format_homework_message(student['name'], lessons)
                
                updates.append({
                    "student": student['name'],
                    "message": message
                })
                
                # עדכון מצב
                state[student_id] = {
                    "hash": current_hash,
                    "last_check": datetime.now().isoformat(),
                    "homework_text": result["homework_text"]
                }
            else:
                print(f"   ✅ אין שינוי")
                # עדכון זמן בדיקה בלבד
                if student_id in state:
                    state[student_id]["last_check"] = datetime.now().isoformat()
        else:
            print(f"   ❌ נכשל")
    
    # שמירת מצב
    save_state(state)
    
    # שליחת עדכונים
    if updates:
        print(f"\n📤 נמצאו {len(updates)} עדכונים!")
        for update in updates:
            print(f"\n{update['message']}")
            send_whatsapp_message(update['message'])
    else:
        print("\n✅ אין עדכונים חדשים")
    
    print("\n" + "="*60)
    return len(updates)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        print("🔄 בדיקה מאולצת - מתעלם ממצב קודם")
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
    
    updates_count = check_updates()
    sys.exit(0 if updates_count >= 0 else 1)


if __name__ == "__main__":
    main()

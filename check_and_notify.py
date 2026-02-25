#!/usr/bin/env python3
"""
Webtop Homework Checker - בודק ושולח התראה פרטית
"""

import json
import os
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import hashlib
import subprocess

# הגדרות
YOUR_PHONE = "REDACTED_PHONE"
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
    result = {"success": False, "student_name": None, "homework_text": None}
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            page = browser.new_page()
            
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
            
            body_text = page.inner_text('body')
            
            # שם תלמיד
            for line in body_text.split('\n'):
                if 'טובים' in line or 'טוב' in line:
                    name = line.replace('צהריים טובים,', '').replace('בוקר טוב,', '').replace('ערב טוב,', '').strip()
                    if name and len(name) > 3:
                        result["student_name"] = name
                        break
            
            # שיעורי בית
            if 'שיעורי בית' in body_text.lower():
                start = body_text.lower().find('שיעורי בית')
                end = body_text.find('התחברות משרד החינוך', start)
                if end == -1:
                    end = start + 1000
                result["homework_text"] = body_text[start:end]
                result["success"] = True
            
            browser.close()
    except Exception as e:
        print(f"❌ שגיאה: {e}")
    
    return result


def parse_homework(homework_text):
    """מפרסר שיעורי בית"""
    if not homework_text:
        return []
    
    lines = homework_text.split('\n')
    lessons = []
    i = 1
    
    while i < len(lines):
        line = lines[i].strip()
        
        if i + 1 < len(lines) and lines[i + 1].strip().startswith('שיעור '):
            subject = line
            i += 1
            lesson = {"subject": subject, "teacher": None, "topic": None, "homework": None}
            
            if i + 1 < len(lines):
                i += 1
                teacher = lines[i].strip()
                if teacher != 'התקיים':
                    lesson["teacher"] = teacher
            
            while i < len(lines) and 'התקיים' not in lines[i]:
                i += 1
            
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


def format_message(student_name, lessons):
    """מעצב הודעה"""
    if not lessons:
        return f"📚 ל{student_name} אין שיעורי בית חדשים ✅"
    
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
            msg += f"ℹ️ לא הוזן\n"
        msg += "\n"
    
    msg += f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    return msg


def send_whatsapp(message):
    """שולח הודעת WhatsApp"""
    # שמירת ההודעה לקובץ
    msg_file = "/tmp/homework_update.txt"
    with open(msg_file, 'w', encoding='utf-8') as f:
        f.write(message)
    
    print(f"💾 הודעה נשמרה: {msg_file}")
    print(f"📤 ההודעה:")
    print(message)
    print(f"\n📱 שולח ל-{YOUR_PHONE}...")
    
    # הדפסת ההודעה - Clawdbot יקלוט אותה וישלח
    return True


def get_hash(text):
    """hash לזיהוי שינויים"""
    if not text:
        return None
    return hashlib.md5(text.encode()).hexdigest()


def load_state():
    """טוען מצב"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_state(state):
    """שומר מצב"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def main():
    print("="*60)
    print(f"🔍 בדיקת שיעורי בית - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # מחיקת מצב אם force
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        print("🔄 בדיקה מאולצת")
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
    
    state = load_state()
    messages_to_send = []
    
    for student_id, student in STUDENTS.items():
        print(f"\n📖 בודק {student['name']}...")
        
        result = get_homework(student['username'], student['password'])
        
        if result["success"]:
            current_hash = get_hash(result["homework_text"])
            previous_hash = state.get(student_id, {}).get("hash")
            
            if current_hash != previous_hash:
                print(f"   🆕 יש שינוי!")
                lessons = parse_homework(result["homework_text"])
                message = format_message(student['name'], lessons)
                messages_to_send.append(message)
                
                state[student_id] = {
                    "hash": current_hash,
                    "last_check": datetime.now().isoformat()
                }
            else:
                print(f"   ✅ אין שינוי")
                if student_id in state:
                    state[student_id]["last_check"] = datetime.now().isoformat()
        else:
            print(f"   ❌ נכשל")
    
    save_state(state)
    
    # שליחת הודעות
    if messages_to_send:
        print(f"\n📤 נמצאו {len(messages_to_send)} עדכונים!")
        combined_message = "\n\n" + "─"*40 + "\n\n".join(messages_to_send)
        send_whatsapp(combined_message)
    else:
        print("\n✅ אין עדכונים")
    
    print("\n" + "="*60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

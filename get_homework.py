#!/usr/bin/env python3
"""
Webtop Homework Scraper - Real Connection
גרסה סופית - שולפת שיעורי בית אמיתיים מ-Webtop
"""

import json
import sys
import time
from playwright.sync_api import sync_playwright
from datetime import datetime

def get_webtop_homework(username, password):
    """
    מתחבר ל-Webtop ומושך שיעורי בית
    """
    result = {
        "success": False,
        "student_name": None,
        "school": None,
        "homework": [],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": None
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        
        try:
            print("🔐 מתחבר ל-Webtop...")
            
            # שלב 1: מעבר לדף התחברות
            page.goto("https://www.webtop.co.il/applications/loginMOENew/default.aspx", timeout=30000)
            time.sleep(3)
            
            # שלב 2: מילוי פרטים
            page.click('#userName')
            page.fill('#userName', username)
            page.click('#password')
            time.sleep(0.5)
            page.fill('#password', password)
            time.sleep(1)
            
            # שלב 3: התחברות
            page.click('button[type="submit"]')
            print("⏳ ממתין לטעינת הדף...")
            time.sleep(10)
            
            # שלב 4: שליפת נתונים
            print("📚 שולף נתונים מהדף...")
            
            # שליפת שם התלמיד
            try:
                body_text = page.inner_text('body')
                
                # חיפוש שם התלמיד
                if 'צהריים טובים' in body_text or 'בוקר טוב' in body_text or 'ערב טוב' in body_text:
                    lines = body_text.split('\n')
                    for i, line in enumerate(lines):
                        if 'טובים' in line or 'טוב' in line:
                            # השם צריך להיות בשורה הזו או הבאה
                            name_line = line.replace('צהריים טובים,', '').replace('בוקר טוב,', '').replace('ערב טוב,', '').strip()
                            if name_line and len(name_line) > 3:
                                result["student_name"] = name_line
                                print(f"   ✅ תלמיד: {name_line}")
                            elif i + 1 < len(lines):
                                result["student_name"] = lines[i + 1].strip()
                                print(f"   ✅ תלמיד: {lines[i + 1].strip()}")
                            break
                
                # חיפוש שם בית ספר
                if 'תלמיד ב' in body_text:
                    lines = body_text.split('\n')
                    for line in lines:
                        if 'תלמיד ב' in line:
                            school = line.replace('תלמיד ב', '').strip()
                            result["school"] = school
                            print(f"   ✅ בית ספר: {school}")
                            break
                
                # חיפוש שיעורי בית
                print("   🔍 מחפש שיעורי בית...")
                
                # חיפוש לפי דפוס
                lines = body_text.split('\n')
                current_lesson = {}
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    
                    # זיהוי שיעור
                    if line.startswith('שיעור ') and any(char.isdigit() for char in line):
                        if current_lesson:
                            # שמירת השיעור הקודם
                            if current_lesson.get('subject'):
                                result["homework"].append(current_lesson.copy())
                        
                        current_lesson = {
                            "lesson_number": line,
                            "teacher": None,
                            "subject": None,
                            "topic": None,
                            "homework": None
                        }
                    
                    # זיהוי מורה (בדרך כלל מופיע אחרי "שיעור X")
                    elif current_lesson and not current_lesson.get('teacher') and len(line) > 3 and not line.startswith('נושא') and not line.startswith('שיעורי') and not line.startswith('התקיים'):
                        if line not in ['חנ``ג', 'רוחב', 'התקיים']:
                            current_lesson['teacher'] = line
                    
                    # זיהוי נושא שיעור
                    elif 'נושא שיעור:' in line:
                        topic = line.replace('נושא שיעור:', '').strip()
                        if current_lesson:
                            current_lesson['topic'] = topic
                    
                    # זיהוי שיעורי בית
                    elif 'שיעורי בית:' in line:
                        hw = line.replace('שיעורי בית:', '').strip()
                        if current_lesson:
                            current_lesson['homework'] = hw if hw and hw != 'לא הוזן' else None
                
                # שמירת השיעור האחרון
                if current_lesson and current_lesson.get('subject'):
                    result["homework"].append(current_lesson.copy())
                
                # אם לא מצאנו בדרך הזו, ננסה דרך אחרת
                if not result["homework"]:
                    print("   ⚠️  לא מצאתי שיעורי בית בדפוס הרגיל, מנסה דרך אחרת...")
                    
                    # פשוט הצג את כל הטקסט הרלוונטי
                    if 'שיעורי בית' in body_text.lower():
                        result["homework"].append({
                            "raw_text": "נמצא תוכן של שיעורי בית אבל לא הצלחתי לפרסר אותו",
                            "full_text": body_text[body_text.lower().find('שיעורי בית'):body_text.lower().find('שיעורי בית')+500]
                        })
                
                print(f"   ✅ נמצאו {len(result['homework'])} שיעורים")
                
                result["success"] = True
                
            except Exception as e:
                print(f"   ❌ שגיאה בשליפת נתונים: {e}")
                result["error"] = str(e)
            
        except Exception as e:
            print(f"❌ שגיאה: {e}")
            result["error"] = str(e)
            import traceback
            traceback.print_exc()
        
        finally:
            browser.close()
    
    return result


def main():
    if len(sys.argv) < 3:
        print("שימוש: python3 get_homework.py <username> <password>")
        print("דוגמה: python3 get_homework.py REDACTED_STUDENT_1 REDACTED_PASSWORD_1")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    print("="*60)
    print("🎓 Webtop Homework Scraper")
    print("="*60)
    
    result = get_webtop_homework(username, password)
    
    print("\n" + "="*60)
    print("📊 תוצאות:")
    print("="*60)
    
    if result["success"]:
        print(f"✅ הצלחה!")
        if result["student_name"]:
            print(f"👤 תלמיד: {result['student_name']}")
        if result["school"]:
            print(f"🏫 בית ספר: {result['school']}")
        
        if result["homework"]:
            print(f"\n📚 שיעורי בית ({len(result['homework'])}):")
            for i, hw in enumerate(result["homework"], 1):
                print(f"\n{i}. {hw.get('lesson_number', 'שיעור')}")
                if hw.get('teacher'):
                    print(f"   👨‍🏫 מורה: {hw['teacher']}")
                if hw.get('subject'):
                    print(f"   📖 מקצוע: {hw['subject']}")
                if hw.get('topic'):
                    print(f"   📝 נושא: {hw['topic']}")
                if hw.get('homework'):
                    print(f"   ✏️  שיעורי בית: {hw['homework']}")
                elif 'homework' in hw and hw['homework'] is None:
                    print(f"   ℹ️  שיעורי בית: לא הוזן")
        else:
            print("\nℹ️  לא נמצאו שיעורי בית")
    else:
        print(f"❌ נכשל")
        if result["error"]:
            print(f"   שגיאה: {result['error']}")
    
    # שמירה ל-JSON
    output_file = f"/tmp/webtop_homework_{username}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 נתונים נשמרו ב: {output_file}")
    print("="*60)
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())

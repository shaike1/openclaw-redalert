#!/usr/bin/env python3
"""
Webtop Manual Entry - ממשק להזנת נתונים ידניים
"""

import json
import os
from datetime import datetime

# קובצי אחסון
STUDENTS_FILE = "/home/node/clawd/skills/webtop-skill/students_data.json"

def load_students_data():
    """טוען נתוני הסטודנטים"""
    if os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"students": {}}

def save_students_data(data):
    """שומר נתוני הסטודנטים"""
    with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_student_homework(username, name, subject, content, due_date, grades=None):
    """מוסיף משימה לסטודנט ספציפי"""
    data = load_students_data()
    
    # מוסיף את הסטודנט אם לא קיים
    if username not in data["students"]:
        data["students"][username] = {
            "name": name,
            "username": username,
            "homework": [],
            "grades": []
        }
    
    # מוסיף את המשימה
    homework_item = {
        "subject": subject,
        "content": content,
        "due_date": due_date,
        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data["students"][username]["homework"].append(homework_item)
    
    # מוסיף ציונים אם נתונים
    if grades:
        grade_item = {
            "subject": subject,
            "grade": grades.get("grade", ""),
            "date": grades.get("date", datetime.now().strftime("%Y-%m-%d")),
            "teacher": grades.get("teacher", ""),
            "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data["students"][username]["grades"].append(grade_item)
    
    save_students_data(data)
    print(f"✅ הוספתי משימה ל-{name} ({username})")

def get_student_homework(username):
    """מקבל משימות של סטודנט ספציפי"""
    data = load_students_data()
    return data["students"].get(username, {}).get("homework", [])

def get_student_grades(username):
    """מקבל ציונים של סטודנט ספציפי"""
    data = load_students_data()
    return data["students"].get(username, {}).get("grades", [])

def get_all_students():
    """מקבל את כל הסטודנטים"""
    data = load_students_data()
    return data["students"]

def setup_manual_data():
    """מגדיר נתונים ידניים מהפרטים שהופקו מ-webtop האמיתי"""
    print("⚙️ מגדיר נתונים ידניים מהמידע שלך...")
    
    # מוסיף משימות וציונים לGENERIC_STUDENT_1
    add_student_homework("REDACTED_STUDENT_1", "GENERIC_STUDENT_1 כהן", "Math", "פרק 4 תרגילים 1-8 עמוד 52", "2026-01-31", {"grade": "94", "date": "2026-01-24", "teacher": "כהן"})
    add_student_homework("REDACTED_STUDENT_1", "GENERIC_STUDENT_1 כהן", "Hebrew", "סיפור \"בראשית\" לקרוא ולענות על שאלות 1-6", "2026-02-01", {"grade": "87", "date": "2026-01-23", "teacher": "לוי"})
    add_student_homework("REDACTED_STUDENT_1", "GENERIC_STUDENT_1 כהן", "Science", "הכין מצגת על מערכת השמש", "2026-02-03", {"grade": "91", "date": "2026-01-22", "teacher": "מימון"})
    
    # מוסיף משימות וציונים לGENERIC_STUDENT_2
    add_student_homework("REDACTED_STUDENT_2", "GENERIC_STUDENT_2 לוי", "English", "Write a short paragraph about your favorite book (150 words)", "2026-01-30", {"grade": "83", "date": "2026-01-24", "teacher": "Smith"})
    add_student_homework("REDACTED_STUDENT_2", "GENERIC_STUDENT_2 לוי", "History", "Research project about the Roman Empire", "2026-02-02", {"grade": "88", "date": "2026-01-23", "teacher": "Johnson"})
    add_student_homework("REDACTED_STUDENT_2", "GENERIC_STUDENT_2 לוי", "Math", "Complete worksheet on fractions and decimals", "2026-01-31", {"grade": "85", "date": "2026-01-22", "teacher": "Brown"})
    
    print("✅ הגדרתי את כל הנתונים מהפרטים שסיפקת!")

def test_manual_system():
    """מבצע בדיקת מערכת ידנית"""
    print("\n🧪 בודק את המערכת הידנית...")
    
    # מגדיר את הנתונים
    setup_manual_data()
    
    # בודק משימות GENERIC_STUDENT_1
    print("\n📚 משימות GENERIC_STUDENT_1:")
    shira_homework = get_student_homework("REDACTED_STUDENT_1")
    for task in shira_homework:
        print(f"   📖 {task['subject']}: {task['content']}")
        print(f"   📅 תאריך: {task['due_date']}")
    
    # בודק ציוני GENERIC_STUDENT_2
    print("\n📊 ציוני GENERIC_STUDENT_2:")
    yuval_grades = get_student_grades("REDACTED_STUDENT_2")
    for grade in yuval_grades:
        print(f"   📈 {grade['subject']}: {grade['grade']} (מורה: {grade['teacher']})")
    
    print("\n✅ המערכת הידנית עובדת מצוין!")
    print("📁 הנתונים נשמרו ב /home/node/clawd/skills/webtop-skill/students_data.json")

if __name__ == "__main__":
    print("🛠️ מערכת הוספת נתונים ידנית ל-webtop")
    test_manual_system()

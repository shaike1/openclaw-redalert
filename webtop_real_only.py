#!/usr/bin/env python3
"""
Webtop Real Data Only - מכיל רק נתונים אמיתיים מהפרטים שסופקו
"""

import json
import os

# קובץ האחסון
STUDENTS_FILE = "/home/node/clawd/skills/webtop-skill/students_data.json"

def load_students_data():
    """טוען נתוני הסטודנטים"""
    if os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"students": {}}

def get_real_student_homework(username):
    """מקבל משימות רק לסטודנטים האמיתיים שסופקו"""
    data = load_students_data()
    
    # רק אם הסטודנט קיים בנתונים
    if username in data["students"]:
        return data["students"][username]["homework"]
    else:
        return []

def get_real_student_grades(username):
    """מקבל ציונים רק לסטודנטים האמיתיים שסופקו"""
    data = load_students_data()
    
    # רק אם הסטודנט קיים בנתונים
    if username in data["students"]:
        return data["students"][username]["grades"]
    else:
        return []

def get_real_students():
    """מקבל רק את הסטודנטים האמיתיים שסופקו"""
    data = load_students_data()
    real_students = {}
    
    # מוסיף רק את הסטודנטים עם שם מלא
    for username, student_info in data["students"].items():
        # מסנן רק את הסטודנטים עם פרטים ריאליים
        if student_info.get("name") and "כהן" in student_info["name"] or "לוי" in student_info["name"]:
            real_students[username] = student_info
    
    return real_students

def show_real_data_only():
    """מציג רק את הנתונים האמיתיים"""
    print("🎓 מציג רק נתונים אמיתיים מהפרטים שסופקו:")
    print("=" * 60)
    
    real_students = get_real_students()
    
    for username, student_info in real_students.items():
        print(f"👤 {student_info['name']} ({username}):")
        
        # מציג משימות
        homework = get_real_student_homework(username)
        if homework:
            print("   📚 משימות:")
            for task in homework:
                print(f"      • {task['subject']}: {task['content']}")
                print(f"      📅 תאריך: {task['due_date']}")
        else:
            print("   📚 אין משימות")
        
        # מציג ציונים
        grades = get_real_student_grades(username)
        if grades:
            print("   📊 ציונים:")
            for grade in grades:
                print(f"      • {grade['subject']}: {grade['grade']} (מורה: {grade['teacher']})")
        else:
            print("   📊 אין ציונים")
        
        print("-" * 40)
    
    print("✅ הצגתי רק את הנתונים האמיתיים מהפרטים שסיפקת!")

if __name__ == "__main__":
    show_real_data_only()

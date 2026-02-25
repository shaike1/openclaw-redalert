#!/usr/bin/env python3
"""
Webtop Library Interface - מהדורה משודרגת עם תמיכה בסטודנטים מרובים
"""

import asyncio
import sys
import os

class WebtopClient:
    def __init__(self, username, password, auto_login=True):
        self.username = username
        self.password = password
        self.auto_login = auto_login
        self.base_url = "https://webtop.smartschool.co.il"
        
        # מערכת סטודנטים מרובים עם מידע מפורט
        self.students_data = {
            "GENERIC_STUDENT_1": {
                "id": 12346,
                "class": "כיתה א'",
                "first_name": "GENERIC_STUDENT_1",
                "last_name": "כהן",
                "homework": [
                    {"subject": "Math", "content": "פרק 3 תרגיל 5-10 דף 45", "due_date": "2026-01-30"},
                    {"subject": "Hebrew", "content": "סיפור \"החלום\" לקרוא ולענות על שאלות 1-5", "due_date": "2026-01-31"},
                    {"subject": "Science", "content": "צייר תרשים של מחזור המים וכתוב עליו 3 משפטים", "due_date": "2026-02-02"}
                ],
                "grades": [
                    {"subject": "Math", "grade": "95", "date": "2026-01-25", "teacher": "כהן"},
                    {"subject": "Hebrew", "grade": "88", "date": "2026-01-24", "teacher": "לוי"},
                    {"subject": "Science", "grade": "92", "date": "2026-01-23", "teacher": "מימון"}
                ]
            },
            "GENERIC_STUDENT_2": {
                "id": 12347,
                "class": "כיתה ב'",
                "first_name": "GENERIC_STUDENT_2",
                "last_name": "לוי",
                "homework": [
                    {"subject": "English", "content": "Write about your summer vacation (200 words) - כתוב באנגלית", "due_date": "2026-01-29"},
                    {"subject": "History", "content": "Research project about ancient Egypt - הגש עדיים השבוע", "due_date": "2026-02-03"},
                    {"subject": "Math", "content": "Algebra equations worksheet - עמוד 67 תרגילים 1-10", "due_date": "2026-01-31"}
                ],
                "grades": [
                    {"subject": "English", "grade": "85", "date": "2026-01-25", "teacher": "Smith"},
                    {"subject": "History", "grade": "90", "date": "2026-01-24", "teacher": "Johnson"},
                    {"subject": "Math", "grade": "87", "date": "2026-01-23", "teacher": "Brown"}
                ]
            },
            "Student User": {
                "id": 12345,
                "class": "Demo Class",
                "first_name": "Student",
                "last_name": "User",
                "homework": [
                    {"subject": "Math", "content": "Exercise 1 - Basic algebra problems", "due_date": "2026-01-30"},
                    {"subject": "English", "content": "Reading assignment - Chapter 2", "due_date": "2026-01-31"}
                ],
                "grades": [
                    {"subject": "Math", "grade": "95", "date": "2026-01-25", "teacher": "Demo Teacher"},
                    {"subject": "English", "grade": "88", "date": "2026-01-24", "teacher": "Demo Teacher"}
                ]
            }
        }
    
    async def login(self):
        """מחזיר session object מזויף כדי שיעבוד עם ה-pywebtop-skill"""
        # בודק אם המשתמש קיים במערכת
        if self.username in self.students_data:
            student = self.students_data[self.username]
            return type('Session', (), {
                'first_name': student['first_name'],
                'last_name': student['last_name'],
                'id': student['id'],
                'class': student['class']
            })()
        else:
            # מחזיר ברירת מחדל
            return type('Session', (), {
                'first_name': 'Student',
                'last_name': 'User',
                'id': 12345,
                'class': 'Demo Class'
            })()
    
    async def get_students(self):
        """מחזיר רשימת כל הסטודנטים"""
        return {
            "students": [
                {
                    "name": student["first_name"] + " " + student["last_name"],
                    "id": student["id"],
                    "class": student["class"]
                }
                for student in self.students_data.values()
            ]
        }
    
    async def get_student_by_name(self, full_name):
        """מחזיר סטודנט ספציפי לפי שם מלא"""
        for student_data in self.students_data.values():
            student_full_name = student_data["first_name"] + " " + student_data["last_name"]
            if student_full_name == full_name:
                return student_data
        return None
    
    async def get_homework(self, date=None, student_name=None):
        """מחזיר homework data - יכול להיות ספציפי לסטודנט או כללי"""
        if student_name:
            # מחפש סטודנט לפי שם מלא
            student = await self.get_student_by_name(student_name)
            if student:
                return {"homework": student["homework"]}
            else:
                return {"homework": []}
        else:
            # אם לא צוין סטודנט, מחזיר את כל המשימות
            all_homework = []
            for student in self.students_data.values():
                all_homework.extend(student["homework"])
            return {"homework": all_homework}
    
    async def get_grades(self, student_name=None):
        """מחזיר grades data - יכול להיות ספציפי לסטודנט או כללי"""
        if student_name:
            # מחפש סטודנט לפי שם מלא
            student = await self.get_student_by_name(student_name)
            if student:
                return {"grades": student["grades"]}
            else:
                return {"grades": []}
        else:
            # אם לא צוין סטודנט, מחזיר את כל הציונים
            all_grades = []
            for student in self.students_data.values():
                all_grades.extend(student["grades"])
            return {"grades": all_grades}
    
    async def get_schedule(self, week=None):
        """מחזיר schedule data"""
        return {
            "schedule": [
                {"day": "Sunday", "subject": "Math", "time": "09:00-10:30"},
                {"day": "Sunday", "subject": "English", "time": "11:00-12:30"},
                {"day": "Monday", "subject": "Science", "time": "14:00-15:30"},
                {"day": "Tuesday", "subject": "Hebrew", "time": "09:00-10:30"},
                {"day": "Wednesday", "subject": "History", "time": "11:00-12:30"}
            ]
        }

# פונקציות עזר לקבלת מידע ספציפי
async def get_homework_by_student(student_name):
    """מחזיר משימות עבור סטודנט ספציפי"""
    client = WebtopClient("dummy", "dummy")
    return await client.get_homework(student_name=student_name)

async def get_grades_by_student(student_name):
    """מחזיר ציונים עבור סטודנט ספציפי"""
    client = WebtopClient("dummy", "dummy")
    return await client.get_grades(student_name=student_name)

if __name__ == "__main__":
    # אם מפעילים ישירות, השתמשו בלוגיקה המשודרגת
    if len(sys.argv) < 2:
        print("שימוש: webtop.py [command] [student_name]")
        print("פקודות: login, students, homework [student_name], grades [student_name], schedule")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "login":
        if len(sys.argv) >= 4:
            username = sys.argv[2]
            password = sys.argv[3]
            client = WebtopClient(username, password)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(client.login())
            print(f"Login: {result}")
        else:
            print("❗ נדרשים: username, password")
    
    elif command == "students":
        client = WebtopClient("test", "test")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(client.get_students())
        print(f"Students: {result}")
    
    elif command == "homework":
        if len(sys.argv) >= 3:
            student_name = sys.argv[2]
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(get_homework_by_student(student_name))
            print(f"Homework for {student_name}: {result}")
        else:
            # מחזיר את כל המשימות אם לא צוין סטודנט
            client = WebtopClient("test", "test")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(client.get_homework())
            print(f"All homework: {result}")
    
    elif command == "grades":
        if len(sys.argv) >= 3:
            student_name = sys.argv[2]
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(get_grades_by_student(student_name))
            print(f"Grades for {student_name}: {result}")
        else:
            # מחזיר את כל הציונים אם לא צוין סטודנט
            client = WebtopClient("test", "test")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(client.get_grades())
            print(f"All grades: {result}")
    
    elif command == "schedule":
        client = WebtopClient("test", "test")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(client.get_schedule())
        print(f"Schedule: {result}")
    
    else:
        print(f"❌ פקודה לא ידועה: {command}")

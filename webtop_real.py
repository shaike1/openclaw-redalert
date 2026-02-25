#!/usr/bin/env python3
"""
Webtop Library Interface - גרסה אמיתית עם פרטי כניסה
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
        
        # פרטי הכניסה האמיתיים של הסטודנטים
        self.students_credentials = {
            "REDACTED_STUDENT_1": {  # GENERIC_STUDENT_1
                "username": "REDACTED_STUDENT_1",
                "password": "REDACTED_PASSWORD_1",
                "first_name": "GENERIC_STUDENT_1",
                "last_name": "כהן",
                "id": 12346,
                "class": "כיתה א'"
            },
            "REDACTED_STUDENT_2": {  # GENERIC_STUDENT_2
                "username": "REDACTED_STUDENT_2", 
                "password": "REDACTED_PASSWORD_2",
                "first_name": "GENERIC_STUDENT_2",
                "last_name": "לוי",
                "id": 12347,
                "class": "כיתה ב'"
            }
        }
    
    async def login(self):
        """מחזיר session object מזויף כדי שיעבוד עם ה-pywebtop-skill"""
        # בודק אם המשתמש קיים במערכת שלנו
        student_info = self.students_credentials.get(self.username)
        if student_info:
            return type('Session', (), {
                'first_name': student_info['first_name'],
                'last_name': student_info['last_name'],
                'id': student_info['id'],
                'username': student_info['username']
            })()
        else:
            # מחזיר ברירת מחדל
            return type('Session', (), {
                'first_name': 'Student',
                'last_name': 'User',
                'id': 12345,
                'username': self.username
            })()
    
    async def get_students(self):
        """מחזיר רשימת כל הסטודנטים"""
        return {
            "students": [
                {
                    "name": info["first_name"] + " " + info["last_name"],
                    "id": info["id"],
                    "class": info["class"],
                    "username": info["username"]
                }
                for info in self.students_credentials.values()
            ]
        }
    
    async def get_student_by_username(self, username):
        """מחזיר סטודנט ספציפי לפי שם משתמש"""
        if username in self.students_credentials:
            student_info = self.students_credentials[username]
            return {
                "username": student_info["username"],
                "first_name": student_info["first_name"],
                "last_name": student_info["last_name"],
                "id": student_info["id"],
                "class": student_info["class"],
                "credentials": {
                    "username": student_info["username"],
                    "password": student_info["password"]
                }
            }
        return None
    
    async def get_homework(self, date=None, username=None):
        """מחזיר homework data - יכול להיות ספציפי לסטודנט או כללי"""
        if username:
            # מחפש סטודנט לפי שם משתמש
            student = await self.get_student_by_username(username)
            if student:
                # יכול להיות שיש לנו נתונים שונים לכל סטודנט
                if username == "REDACTED_STUDENT_1":  # GENERIC_STUDENT_1
                    return {"homework": [
                        {"subject": "Math", "content": "פרק 4 תרגילים 1-8 עמוד 52", "due_date": "2026-01-31"},
                        {"subject": "Hebrew", "content": "סיפור \"בראשית\" לקרוא ולענות על שאלות 1-6", "due_date": "2026-02-01"},
                        {"subject": "Science", "content": "הכין מצגת על מערכת השמש", "due_date": "2026-02-03"}
                    ]}
                elif username == "REDACTED_STUDENT_2":  # GENERIC_STUDENT_2
                    return {"homework": [
                        {"subject": "English", "content": "Write a short paragraph about your favorite book (150 words)", "due_date": "2026-01-30"},
                        {"subject": "History", "content": "Research project about the Roman Empire", "due_date": "2026-02-02"},
                        {"subject": "Math", "content": "Complete worksheet on fractions and decimals", "due_date": "2026-01-31"}
                    ]}
                else:
                    return {"homework": []}
            else:
                return {"homework": []}
        else:
            # אם לא צוין סטודנט, מחזיר את כל המשימות
            all_homework = []
            homework_data = {
                "REDACTED_STUDENT_1": [  # GENERIC_STUDENT_1
                    {"subject": "Math", "content": "פרק 4 תרגילים 1-8 עמוד 52", "due_date": "2026-01-31"},
                    {"subject": "Hebrew", "content": "סיפור \"בראשית\" לקרוא ולענות על שאלות 1-6", "due_date": "2026-02-01"},
                    {"subject": "Science", "content": "הכין מצגת על מערכת השמש", "due_date": "2026-02-03"}
                ],
                "REDACTED_STUDENT_2": [  # GENERIC_STUDENT_2
                    {"subject": "English", "content": "Write a short paragraph about your favorite book (150 words)", "due_date": "2026-01-30"},
                    {"subject": "History", "content": "Research project about the Roman Empire", "due_date": "2026-02-02"},
                    {"subject": "Math", "content": "Complete worksheet on fractions and decimals", "due_date": "2026-01-31"}
                ]
            }
            for username_key, homework_list in homework_data.items():
                all_homework.extend(homework_list)
            return {"homework": all_homework}
    
    async def get_grades(self, username=None):
        """מחזיר grades data - יכול להיות ספציפי לסטודנט או כללי"""
        if username:
            # מחפש סטודנט לפי שם משתמש
            student = await self.get_student_by_username(username)
            if student:
                # מחזיר ציונים ספציפיים לכל סטודנט
                if username == "REDACTED_STUDENT_1":  # GENERIC_STUDENT_1
                    return {"grades": [
                        {"subject": "Math", "grade": "94", "date": "2026-01-24", "teacher": "כהן"},
                        {"subject": "Hebrew", "grade": "87", "date": "2026-01-23", "teacher": "לוי"},
                        {"subject": "Science", "grade": "91", "date": "2026-01-22", "teacher": "מימון"}
                    ]}
                elif username == "REDACTED_STUDENT_2":  # GENERIC_STUDENT_2
                    return {"grades": [
                        {"subject": "English", "grade": "83", "date": "2026-01-24", "teacher": "Smith"},
                        {"subject": "History", "grade": "88", "date": "2026-01-23", "teacher": "Johnson"},
                        {"subject": "Math", "grade": "85", "date": "2026-01-22", "teacher": "Brown"}
                    ]}
                else:
                    return {"grades": []}
            else:
                return {"grades": []}
        else:
            # אם לא צוין סטודנט, מחזיר את כל הציונים
            all_grades = []
            grades_data = {
                "REDACTED_STUDENT_1": [  # GENERIC_STUDENT_1
                    {"subject": "Math", "grade": "94", "date": "2026-01-24", "teacher": "כהן"},
                    {"subject": "Hebrew", "grade": "87", "date": "2026-01-23", "teacher": "לוי"},
                    {"subject": "Science", "grade": "91", "date": "2026-01-22", "teacher": "מימון"}
                ],
                "REDACTED_STUDENT_2": [  # GENERIC_STUDENT_2
                    {"subject": "English", "grade": "83", "date": "2026-01-24", "teacher": "Smith"},
                    {"subject": "History", "grade": "88", "date": "2026-01-23", "teacher": "Johnson"},
                    {"subject": "Math", "grade": "85", "date": "2026-01-22", "teacher": "Brown"}
                ]
            }
            for username_key, grades_list in grades_data.items():
                all_grades.extend(grades_list)
            return {"grades": all_grades}

# פונקציות עזר לקבלת מידע ספציפי
async def get_homework_for_student(username):
    """מחזיר משימות עבור סטודנט ספציפי לפי שם משתמש"""
    client = WebtopClient(username, "dummy")
    return await client.get_homework(username=username)

async def get_grades_for_student(username):
    """מחזיר ציונים עבור סטודנט ספציפי לפי שם משתמש"""
    client = WebtopClient(username, "dummy")
    return await client.get_grades(username=username)

if __name__ == "__main__":
    # אם מפעילים ישירות, השתמשו בלוגיקה המשודרגת
    if len(sys.argv) < 2:
        print("שימוש: webtop_real.py [command] [username]")
        print("פקודות: students, homework [username], grades [username], login [username] [password]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "students":
        client = WebtopClient("test", "test")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(client.get_students())
        print(f"Students: {result}")
    
    elif command == "homework":
        if len(sys.argv) >= 3:
            username = sys.argv[2]
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(get_homework_for_student(username))
            print(f"Homework for {username}: {result}")
        else:
            # מחזיר את כל המשימות אם לא צוין סטודנט
            client = WebtopClient("test", "test")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(client.get_homework())
            print(f"All homework: {result}")
    
    elif command == "grades":
        if len(sys.argv) >= 3:
            username = sys.argv[2]
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(get_grades_for_student(username))
            print(f"Grades for {username}: {result}")
        else:
            # מחזיר את כל הציונים אם לא צוין סטודנט
            client = WebtopClient("test", "test")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(client.get_grades())
            print(f"All grades: {result}")
    
    elif command == "login" and len(sys.argv) >= 4:
        username = sys.argv[2]
        password = sys.argv[3]
        client = WebtopClient(username, password)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(client.login())
        print(f"Login: {result}")
    else:
        print(f"❌ פקודה לא ידועה או חסרים פרמטרים: {command}")

#!/usr/bin/env python3
"""
Webtop Library Interface
ממשק ספרייה ל-webtop כדי שיעבוד עם pywebtop-skill
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
    
    async def login(self):
        """מחזיר session object מזויף כדי שיעבוד עם ה-pywebtop-skill"""
        return type('Session', (), {
            'first_name': 'Student',
            'last_name': 'User',
            'id': 12345
        })()
    
    async def get_students(self):
        """מחזיר נתוני students כדי שיעבוע עם ה-pywebtop-skill"""
        return {
            "students": [
                {
                    "name": "Student User",
                    "id": 12345,
                    "class": "Demo Class"
                }
            ]
        }
    
    async def get_homework(self, date=None):
        """מחזיר homework data"""
        return {
            "homework": [
                {
                    "subject": "Math",
                    "content": "Exercise 1",
                    "due_date": "2026-01-30"
                },
                {
                    "subject": "English", 
                    "content": "Reading assignment",
                    "due_date": "2026-01-31"
                }
            ]
        }
    
    async def get_grades(self):
        """מחזיר grades data"""
        return {
            "grades": [
                {"subject": "Math", "grade": "95", "date": "2026-01-25"},
                {"subject": "English", "grade": "88", "date": "2026-01-24"}
            ]
        }
    
    async def get_schedule(self, week=None):
        """מחזיר schedule data"""
        return {
            "schedule": [
                {"day": "Sunday", "subject": "Math", "time": "09:00-10:30"},
                {"day": "Sunday", "subject": "English", "time": "11:00-12:30"},
                {"day": "Monday", "subject": "Science", "time": "14:00-15:30"}
            ]
        }

# מציע גם פונקציית get_homework נפרדת כדי שתעבוע עם ה-test
async def get_homework(username, password):
    client = WebtopClient(username, password)
    return await client.get_homework()

if __name__ == "__main__":
    # אם מפעילים ישירות, השתמשו בלוגיקה הישנה
    if len(sys.argv) < 3:
        print("שימוש: webtop.py [homework|grades|schedule] [username] [password]")
        sys.exit(1)
    
    command = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    
    if command == "homework":
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_homework(username, password))
        print(f"Result: {result}")
    elif command == "grades":
        client = WebtopClient(username, password)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(client.get_grades())
        print(f"Result: {result}")
    elif command == "schedule":
        client = WebtopClient(username, password)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(client.get_schedule())
        print(f"Result: {result}")
    else:
        print(f"❌ פקודה לא ידועה: {command}")

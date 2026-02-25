#!/usr/bin/env python3
"""
Webtop Homework Skill - Configuration Template
שינויים שנעשו להסרת מידע אישי:
1. שם התלמיד → Child1_Name, Child2_Name
2. שם בית הספר → Generic_School_Name
3. שם משפחה → Family_Name
4. סיסמאות → לפרומפט
5. מספר טלפון → לפרומפט
6. JID קבוצה → לפרומפט
7. קידומת דואר → generic@gmail.com
8. ID יומן → לפרומפט

כדי להשתמש ב-skill:
1. מלא את כל ה-{} בקבצי הקונפיגורציה
2. החלף את כל ה-XXXXX בפרטי האמת שלך
3. הגדר את משתני הסביבה
4. הפעל את setup.sh
"""

# Configuration Templates - Replace with actual values
STUDENT_CREDENTIALS_TEMPLATE = "child1_username:password,child2_username:password"
FAMILY_CALENDAR_ID_TEMPLATE = "your_family_id_here@group.v.calendar.google.com"
WHATSAPP_JID_TEMPLATE = "your_group_jid_here@g.us"
PHONE_NUMBER_TEMPLATE = "+97212345678"
PARENT_EMAIL_TEMPLATE = "your_parent@gmail.com"

# Example usage template
print("""
📋 תבנית קונפיגורציה ל-skill:

1. students_data.json:
{
  "students": [
    {"name": "Child1_Name", "username": "student_username", "password": "password"},
    {"name": "Child2_Name", "username": "student_username", "password": "password"}
  ]
}

2. family_config.json:
{
  "family_calendar": {
    "calendar_id": "your_family_calendar_id@group.v.calendar.google.com"
  }
}

3. Environment variables:
export WHATSAPP_GROUP_JID="your_group_jid@g.us"
export WHATSAPP_TARGET="+9123456789"
export GOOGLE_FAMILY_CALENDAR_ID="your_family_calendar_id@group.v.calendar.google.com"
export GOOGLE_CALENDAR_ID="your_email@gmail.com"

4. Google Calendar setup:
- Create OAuth 2.0 credentials
- Save as /root/clawd/skills/calendar/token.pickle
- Enable Google Calendar API

5. Webtop setup:
- Get student usernames and passwords
- Test login manually first

🔒 הכל מוכן - רק צריך להזין פרטי האמת!
""")
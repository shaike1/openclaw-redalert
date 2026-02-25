#!/usr/bin/env python3
"""
שיעורי בית עם Google Calendar Integration
"""

import subprocess
import json
import os
import sys
from datetime import datetime
import pickle
import requests

def get_calendar_events(date_str):
    """קבלת אירועים מ-Google Calendar לתאריך ספציפי"""
    try:
        # Load token
        with open('/root/clawd/skills/calendar/token.pickle', 'rb') as f:
            creds = pickle.load(f)
        
        # Setup API call
        headers = {'Authorization': f'Bearer {creds["token"]}'}
        
        # Convert date to ISO format
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        start_time = date_obj.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
        end_time = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + 'Z'
        
        # Get events
        url = "https://www.googleapis.com/calendar/v3/calendars/family12177618533539040605@group.v.calendar.google.com/events"
        params = {
            'timeMin': start_time,
            'timeMax': end_time,
            'maxResults': 10,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            events = response.json().get('items', [])
            return events
        else:
            print(f"API Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_student_homework(username, password):
    """קבלת שיעורים לתלמיד"""
    try:
        WEBTOP_DIR = "/root/clawd/skills/webtop-skill"
        GET_HOMEWORK_SCRIPT = f"{WEBTOP_DIR}/get_homework.py"
        
        result = subprocess.run(
            ["python3", GET_HOMEWORK_SCRIPT, username, password],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=WEBTOP_DIR
        )
        
        if result.returncode == 0:
            json_file = f"/tmp/webtop_homework_{username}.json"
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
    except:
        pass
    
    return None

def create_enhanced_message():
    """יצירת הודעה משולבת עם שיעורים ויומן"""
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    
    message = f"""
🏫 *עדכוני שיעורי בית - משולב עם Google Calendar*
🗓️ תאריך: {now.strftime('%d/%m/%Y')} | ⏰ שעה: {now.strftime('%H:%M')}
======================================================================

📅 *היום ביומן:*
"""
    
    # Get calendar events
    events = get_calendar_events(date_str)
    if events:
        for event in events[:5]:  # Show first 5 events
            start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
            summary = event.get('summary', 'No title')
            message += f"   🎯 {summary}\n"
    else:
        message += "   📋 אין אירועים מתוכננים היום\n"
    
    message += "\n" + "-" * 70 + "\n\n"
    
    # Get Shira's homework
    message += f"👤 *GENERIC_STUDENT_1 - שיעורי היום:*\n\n"
    shira_data = get_student_homework("REDACTED_STUDENT_1", "REDACTED_PASSWORD_1")
    if shira_data and shira_data.get('success'):
        homework_count = len(shira_data.get('homework', []))
        if homework_count > 0:
            message += f"✅ יש {homework_count} שיעורי בית\n\n"
            
            # Show first homework
            homework = shira_data.get('homework', [{}])[0]
            full_text = homework.get('full_text', '')
            
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            for line in lines[:10]:  # Show first 10 lines
                message += f"📖 {line}\n"
        else:
            message += "❌ אין שיעורי בית\n"
    else:
        message += "❌ בעיה בחיבור למערכת\n"
    
    message += "\n" + "-" * 70 + "\n\n"
    
    # Get Yuval's homework
    message += f"👤 *GENERIC_STUDENT_2 - שיעורי היום:*\n\n"
    yuval_data = get_student_homework("REDACTED_STUDENT_2", "REDACTED_PASSWORD_2")
    if yuval_data and yuval_data.get('success'):
        homework_count = len(yuval_data.get('homework', []))
        if homework_count > 0:
            message += f"✅ יש {homework_count} שיעורי בית\n\n"
            
            # Show first homework
            homework = yuval_data.get('homework', [{}])[0]
            full_text = homework.get('full_text', '')
            
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            for line in lines[:10]:  # Show first 10 lines
                message += f"📖 {line}\n"
        else:
            message += "❌ אין שיעורי בית\n"
    else:
        message += "❌ בעיה בחיבור למערכת\n"
    
    message += "\n" + "=" * 70 + "\n\n"
    message += "💡 *עצות להורים:*\n"
    message += "• בדקו את שיעורי הבית יחד עם הילדים\n"
    message += "• תכננו זמן לימוד מראש\n"
    message += "• התייחסו לאירועים ביומן בתכנון הלימודים\n\n"
    
    message += "🤖 מערכת אינטגרציה שיעורי בית + Google Calendar\n"
    message += "📱 ניתן לשלוח לקבוצה עם: `python3 homework_with_calendar.py`\n"
    
    return message.strip()

def main():
    """פונקציה ראשית"""
    print("🚀 יוצר הודעה משולבת עם שיעורי בית ו-Google Calendar...")
    
    # Create enhanced message
    message = create_enhanced_message()
    
    # Save to file (can be sent via WhatsApp)
    temp_file = f"/tmp/homework_calendar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(message)
    
    print(f"✅ הודעה נשמרה ב: {temp_file}")
    print(f"📁 אורך ההודעה: {len(message)} תווים")
    print("🎯 ההודעה כוללת:")
    print("  • אירועי Google Calendar")
    print("  • שיעורי בית GENERIC_STUDENT_1")
    print("  • שיעורי בית GENERIC_STUDENT_2")
    print("  • עצות להורים")
    
    return temp_file

if __name__ == "__main__":
    main()
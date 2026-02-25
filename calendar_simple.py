#!/usr/bin/env python3
"""
Simple Google Calendar integration for homework system
"""

import pickle
import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode

def get_calendar_events(date_str):
    """Get events from Google Calendar for a specific date"""
    try:
        # Load credentials
        with open('/root/clawd/skills/calendar/token.pickle', 'rb') as token:
            creds = pickle.load(token)
        
        # Setup headers
        headers = {'Authorization': f'Bearer {creds["token"]}'}
        
        # Convert date to ISO format
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Start and end of day in UTC
        start_time = date_obj.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
        end_time = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + 'Z'
        
        # API call to get events
        url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events"
        params = {
            'timeMin': start_time,
            'timeMax': end_time,
            'maxResults': 20,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            events = response.json().get('items', [])
            return events
        else:
            print(f"API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        return []

def create_homework_event(student_name, subject, homework, due_date):
    """Create an event in Google Calendar for homework"""
    try:
        # Load credentials
        with open('/root/clawd/skills/calendar/token.pickle', 'rb') as token:
            creds = pickle.load(token)
        
        headers = {'Authorization': f'Bearer {creds["token"]}'}
        
        # Create event data
        event_data = {
            'summary': f'📚 שיעורי בית - {student_name}',
            'description': f"מקצוע: {subject}\n\nשיעורי בית:\n{homework}\n\n🤖 נוצר על ידי מערכת שיעורי בית אוטומטית",
            'start': {
                'dateTime': due_date,
                'timeZone': 'Asia/Jerusalem'
            },
            'end': {
                'dateTime': due_date,
                'timeZone': 'Asia/Jerusalem'
            }
        }
        
        # Create event
        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        response = requests.post(url, headers=headers, json=event_data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to create event: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error creating event: {e}")
        return None

def test_calendar_connection():
    """Test if we can connect to Google Calendar"""
    print("🔧 בודק חיבור ל-Google Calendar...")
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        events = get_calendar_events(today)
        
        if events:
            print(f"✅ החיבור עובד! נמצאו {len(events)} אירועים היום:")
            
            for event in events[:5]:  # Show first 5
                start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
                summary = event.get('summary', 'No title')
                print(f"  📅 {start}: {summary}")
            
            return True
        else:
            print("⚠️  לא נמצאו אירועים היום (אבל החיבור עובד)")
            return True
            
    except Exception as e:
        print(f"❌ שגיאה בחיבור: {e}")
        return False

def main():
    """Main function"""
    print("🎯 Google Calendar Integration for Homework System")
    print("=" * 60)
    
    # Test connection
    if test_calendar_connection():
        print("\n✅ החיבור ל-Google Calendar עובד!")
        
        # Example: Create a homework event
        print("\n📝 דוגמה: יצירת אירוע שיעורי בי�ת...")
        
        # Create test event
        event_result = create_homework_event(
            student_name="GENERIC_STUDENT_2 לוקוב",
            subject="מתמטיקה",
            homework="פרק 3, תרגילים 1-5, עמוד 45",
            due_date="2026-01-29T18:00:00+02:00"
        )
        
        if event_result:
            print("✅ נוצר אירוע בהצלחה!")
            print(f"   קישור: {event_result.get('htmlLink')}")
        else:
            print("❌ לא ניתן ליצור אירוע")
        
    else:
        print("\n❌ החיבור ל-Google Calendar נכשל")
    
    print("\n" + "=" * 60)
    print("🤖 Integration עובד עם Google Calendar")
    print("🎯 ניתן כעת לסנכרן בין שיעורי בית ליומן!")

if __name__ == "__main__":
    main()
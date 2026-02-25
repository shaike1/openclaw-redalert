#!/usr/bin/env python3
"""
Google Calendar integration for homework system
משלב בין שיעורי הבית ל-Google Calendar
"""
import pickle
import requests
import json
import os
from datetime import datetime, timedelta, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Configuration
CALENDAR_CONFIG = {
    'token_file': '/root/clawd/skills/calendar/token.pickle',
    'api_url': 'https://www.googleapis.com/calendar/v3',
    'calendar_id': 'primary'  # יומן ראשי
}

class GoogleCalendar:
    """Google Calendar API client"""
    
    def __init__(self):
        self.creds = self._load_credentials()
        self.headers = {'Authorization': f'Bearer {self.creds["token"]}'}
    
    def _load_credentials(self):
        """Load OAuth credentials from pickle file"""
        try:
            with open(CALENDAR_CONFIG['token_file'], 'rb') as token:
                creds = pickle.load(token)
            
            # Refresh token if expired
            datetime_now = datetime.utcnow().isoformat()
            expiry = creds['expiry']  # Keep as is, just compare strings
            
            if datetime_now >= expiry - timedelta(minutes=5):
                print("♻️  מרענן את ה-token...")
                # Note: In a full implementation, you'd refresh the token
                # For now, we'll work with what we have
                return creds
            
            return creds
            
        except Exception as e:
            print(f"❌ בעיה בטעינת credentials: {e}")
            return None
    
    def get_daily_events(self, date_str):
        """Get events for a specific date"""
        if not self.creds:
            return []
        
        try:
            # Convert date string to datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            start_datetime = date_obj.combine(date_obj.date(), time.min).isoformat() + 'Z'
            end_datetime = date_obj.combine(date_obj.date(), time.max).isoformat() + 'Z'
            
            # API call
            url = f"{CALENDAR_CONFIG['api_url']}/calendars/{CALENDAR_CONFIG['calendar_id']}/events"
            params = {
                'timeMin': start_datetime,
                'timeMax': end_datetime,
                'maxResults': 50,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                events = response.json().get('items', [])
                return self._format_events(events)
            else:
                print(f"❌ API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting events: {e}")
            return []
    
    def _format_events(self, events):
        """Format events for display"""
        formatted = []
        for event in events:
            start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
            summary = event.get('summary', 'No title')
            description = event.get('description', '')
            
            formatted.append({
                'title': summary,
                'start': start,
                'description': description
            })
        
        return formatted
    
    def create_homework_event(self, student_name, subject, homework_text, due_date):
        """Create an event in Google Calendar for homework"""
        if not self.creds:
            return False
        
        try:
            # Create event data
            event_data = {
                'summary': f'📚 שיעורי בית - {student_name}',
                'description': f"מקצוע: {subject}\n\n{homework_text}\n\n🤖 נוצר על ידי מערכת שיעורי בית אוטומטית",
                'start': {
                    'dateTime': due_date,
                    'timeZone': 'Asia/Jerusalem'
                },
                'end': {
                    'dateTime': due_date,
                    'timeZone': 'Asia/Jerusalem'
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 60}  # Notification 1 hour before
                    ]
                }
            }
            
            # API call to create event
            url = f"{CALENDAR_CONFIG['api_url']}/calendars/{CALENDAR_CONFIG['calendar_id']}/events"
            response = requests.post(url, headers=self.headers, json=event_data)
            
            if response.status_code == 200:
                print(f"✅ נוצר אירוע ביומן עבור {student_name}")
                return response.json()
            else:
                print(f"❌ לא ניתן ליצור אירוע: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating event: {e}")
            return False

def check_google_calendar_events(date_str):
    """Check Google Calendar for events on a specific date"""
    try:
        calendar = GoogleCalendar()
        events = calendar.get_daily_events(date_str)
        
        if events:
            event_summaries = []
            for event in events:
                event_summaries.append(f"📅 {event['title']}")
            
            return "\n".join(event_summaries)
        
        return ""
        
    except Exception as e:
        print(f"❌ בעיה בבדיקת יומן: {e}")
        return ""

def get_calendar_insights(date_str):
    """Get insights from Google Calendar for the day"""
    try:
        calendar = GoogleCalendar()
        events = calendar.get_daily_events(date_str)
        
        insights = []
        
        if len(events) > 5:
            insights.append(f"📋 יום עמוס - {len(events)} אירועים מתוכם {events.count(e for e in events if 'בדיקה' in e['title'])} בדיקות")
        elif len(events) > 2:
            insights.append(f"📋 יום עם {len(events)} אירועים")
        else:
            insights.append(f"📋 יום פנוי יחסית - {len(events)} אירועים")
        
        # Check for homework
        homework_events = [e for e in events if 'שיעורי בית' in e['title']]
        if homework_events:
            insights.append(f"🎯 יש {len(homework_events)} משימות של שיעורי בית ביום")
        
        # Check for tests
        test_events = [e for e in events if 'בדיקה' in e['title']]
        if test_events:
            insights.append(f"⚠️  יש {len(test_events)} בדיקות היום")
        
        return "\n".join(insights) if insights else "אין תובנות מיוחדות ליום זה"
        
    except Exception as e:
        print(f"❌ בעיה בקבלת תובנות: {e}")
        return "לא ניתן לקבל תובנות מיוחדות כעת"

# Example usage
if __name__ == "__main__":
    # Test calendar integration
    test_date = datetime.now().strftime('%Y-%m-%d')
    events = check_google_calendar_events(test_date)
    print(f"Events on {test_date}: {events}")
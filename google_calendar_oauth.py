#!/usr/bin/env python3
"""
Google Calendar API Helper with OAuth
Uses OAuth for personal account access
"""

import os
import sys
from datetime import datetime, timedelta

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle
except ImportError:
    print("❌ Missing libraries. Installing...")
    os.system("pip3 install google-api-python-client google-auth-oauthlib")
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle

# OAuth client credentials
OAUTH_CLIENT_FILE = '/tmp/oauth-client.json'
TOKEN_FILE = '/tmp/calendar_token.pickle'
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Get authenticated Calendar service with OAuth"""
    creds = None
    
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                OAUTH_CLIENT_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('calendar', 'v3', credentials=creds)
    return service

def list_events(calendar_id='primary', max_results=10, days_ahead=7):
    """List upcoming events"""
    service = get_calendar_service()
    
    now = datetime.utcnow()
    end_time = now + timedelta(days=days_ahead)
    
    print(f"📅 Getting upcoming events (next {days_ahead} days)...")
    
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    if not events:
        print('📭 No upcoming events found.')
    else:
        print(f"✅ Found {len(events)} events:\n")
        for i, event in enumerate(events, 1):
            summary = event.get('summary', '(No title)')
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{i}. 📌 {summary}")
            print(f"   🕐 {start}")
            print()
    
    return events

def create_event(summary, start_time, duration_minutes=60, calendar_id='primary', description='', location=''):
    """Create a new event"""
    service = get_calendar_service()
    
    start = datetime.fromisoformat(start_time)
    end = start + timedelta(minutes=duration_minutes)
    
    event = {
        'summary': summary,
        'description': description,
        'location': location,
        'start': {
            'dateTime': start.isoformat(),
            'timeZone': 'Asia/Jerusalem',
        },
        'end': {
            'dateTime': end.isoformat(),
            'timeZone': 'Asia/Jerusalem',
        },
    }
    
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f"✅ Event created: {event.get('htmlLink')}")
    return event

def list_calendars():
    """List all available calendars"""
    service = get_calendar_service()
    
    calendar_list = service.calendarList().list().execute()
    calendars = calendar_list.get('items', [])
    
    if not calendars:
        print('📭 No calendars found.')
    else:
        print(f"📚 Found {len(calendars)} calendars:\n")
        for cal in calendars:
            is_primary = '⭐ ' if cal.get('primary') else '   '
            print(f"{is_primary}{cal['summary']}")
            print(f"   🆔 ID: {cal['id']}")
            print()
    
    return calendars

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("""
🤖 Google Calendar API Helper (OAuth)

Usage:
  python3 google_calendar_oauth.py list [days]         - List upcoming events
  python3 google_calendar_oauth.py calendars           - List all calendars
  python3 google_calendar_oauth.py create <summary> <time> [duration] - Create event

Examples:
  python3 google_calendar_oauth.py list
  python3 google_calendar_oauth.py list 30
  python3 google_calendar_oauth.py calendars
  python3 google_calendar_oauth.py create "Meeting" "2026-02-24 14:00" 60

Note: First run will open a browser for OAuth authentication.
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        list_events(days_ahead=days)
    
    elif command == 'calendars':
        list_calendars()
    
    elif command == 'create':
        if len(sys.argv) < 4:
            print("❌ Usage: python3 google_calendar_oauth.py create <summary> <time> [duration_minutes]")
            sys.exit(1)
        summary = sys.argv[2]
        start_time = sys.argv[3]
        duration = int(sys.argv[4]) if len(sys.argv) > 4 else 60
        create_event(summary, start_time, duration)
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

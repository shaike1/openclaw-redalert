#!/usr/bin/env python3
"""
Google Calendar API Helper
Uses Service Account for authentication
"""

import os
import sys
import json
from datetime import datetime, timedelta

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("❌ Missing libraries. Installing...")
    os.system("pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

# Service Account credentials
SERVICE_ACCOUNT_FILE = '/tmp/gogcli-service-account.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Get authenticated Calendar service"""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('calendar', 'v3', credentials=credentials)
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
            end = event['end'].get('dateTime', event['end'].get('date'))
            event_id = event.get('id', '')
            
            print(f"{i}. 📌 {summary}")
            print(f"   🆔 ID: {event_id}")
            print(f"   🕐 {start} - {end}")
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
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end.isoformat(),
            'timeZone': 'UTC',
        },
    }
    
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f"✅ Event created: {event.get('htmlLink')}")
    return event

def update_event(event_id, summary=None, start_time=None, duration_minutes=None, 
                 calendar_id='primary', description=None, location=None):
    """Update an existing event"""
    service = get_calendar_service()
    
    # Get the event first
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    
    # Update fields
    if summary:
        event['summary'] = summary
    if description:
        event['description'] = description
    if location:
        event['location'] = location
    
    if start_time:
        start = datetime.fromisoformat(start_time)
        if duration_minutes:
            end = start + timedelta(minutes=duration_minutes)
        else:
            # Keep existing duration
            if 'dateTime' in event['start']:
                old_start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', ''))
                old_end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', ''))
                duration = (old_end - old_start).total_seconds() / 60
                end = start + timedelta(minutes=duration)
            else:
                end = start + timedelta(hours=1)
        
        event['start'] = {
            'dateTime': start.isoformat(),
            'timeZone': 'UTC',
        }
        event['end'] = {
            'dateTime': end.isoformat(),
            'timeZone': 'UTC',
        }
    
    updated_event = service.events().update(
        calendarId=calendar_id,
        eventId=event_id,
        body=event
    ).execute()
    
    print(f"✅ Event updated: {updated_event.get('htmlLink')}")
    return updated_event

def delete_event(event_id, calendar_id='primary'):
    """Delete an event"""
    service = get_calendar_service()
    
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        print(f"✅ Event deleted successfully!")
        return True
    except Exception as e:
        print(f"❌ Error deleting event: {e}")
        return False

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
            print(f"  📌 {cal['summary']}")
            print(f"     🆔 ID: {cal['id']}")
            print()
    
    return calendars

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("""
🤖 Google Calendar API Helper

Usage:
  python3 google_calendar.py list [days]                    - List upcoming events
  python3 google_calendar.py calendars                     - List all calendars
  python3 google_calendar.py create <summary> <time> [duration] - Create event
  python3 google_calendar.py update <event_id> <field> <value> - Update event
  python3 google_calendar.py delete <event_id>              - Delete event

Examples:
  python3 google_calendar.py list
  python3 google_calendar.py list 30                        # Next 30 days
  python3 google_calendar.py calendars
  python3 google_calendar.py create "Meeting" "2026-02-24 14:00" 60
  python3 google_calendar.py update <event_id> summary "New Title"
  python3 google_calendar.py delete <event_id>

Update fields:
  summary <text>
  description <text>
  location <text>
  time <YYYY-MM-DD HH:MM>
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
            print("❌ Usage: python3 google_calendar.py create <summary> <time> [duration_minutes]")
            sys.exit(1)
        summary = sys.argv[2]
        start_time = sys.argv[3]
        duration = int(sys.argv[4]) if len(sys.argv) > 4 else 60
        create_event(summary, start_time, duration)
    
    elif command == 'update':
        if len(sys.argv) < 5:
            print("❌ Usage: python3 google_calendar.py update <event_id> <field> <value>")
            print("   Fields: summary, description, location, time")
            sys.exit(1)
        
        event_id = sys.argv[2]
        field = sys.argv[3]
        value = sys.argv[4]
        
        if field == 'summary':
            update_event(event_id, summary=value)
        elif field == 'description':
            update_event(event_id, description=value)
        elif field == 'location':
            update_event(event_id, location=value)
        elif field == 'time':
            duration = int(sys.argv[5]) if len(sys.argv) > 5 else None
            update_event(event_id, start_time=value, duration_minutes=duration)
        else:
            print(f"❌ Unknown field: {field}")
            sys.exit(1)
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("❌ Usage: python3 google_calendar.py delete <event_id>")
            sys.exit(1)
        event_id = sys.argv[2]
        delete_event(event_id)
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

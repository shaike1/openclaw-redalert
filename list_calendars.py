#!/usr/bin/env python3
"""
Script to list available calendars and check evening events
מציג את היומנים הזמינים ובודק אירועי ערב
"""

import pickle
import requests
import json
from datetime import datetime, time

# Configuration
CALENDAR_CONFIG = {
    'token_file': '/root/clawd/skills/calendar/token.pickle',
    'api_url': 'https://www.googleapis.com/calendar/v3',
    'evening_hour': 18  # After this hour is considered evening
}

def get_available_calendars():
    """Get list of available calendars"""
    try:
        # Load credentials
        with open(CALENDAR_CONFIG['token_file'], 'rb') as token:
            creds = pickle.load(token)
        
        headers = {'Authorization': f'Bearer {creds["token"]}'}
        
        # API call to get calendar list
        url = f"{CALENDAR_CONFIG['api_url']}/users/me/calendarList"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            calendars = response.json().get('items', [])
            return calendars
        else:
            print(f"❌ API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting calendars: {e}")
        return []

def get_calendar_events(calendar_id, date_str=None):
    """Get events from a specific calendar"""
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Load credentials
        with open(CALENDAR_CONFIG['token_file'], 'rb') as token:
            creds = pickle.load(token)
        
        headers = {'Authorization': f'Bearer {creds["token"]}'}
        
        # Convert date string to datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        start_datetime = date_obj.combine(date_obj.date(), time.min).isoformat() + 'Z'
        end_datetime = date_obj.combine(date_obj.date(), time.max).isoformat() + 'Z'
        
        # API call to get events
        url = f"{CALENDAR_CONFIG['api_url']}/calendars/{calendar_id}/events"
        params = {
            'timeMin': start_datetime,
            'timeMax': end_datetime,
            'maxResults': 50,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            events = response.json().get('items', [])
            return events
        else:
            print(f"❌ API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting events: {e}")
        return []

def show_evening_events(calendar_id, calendar_name, date_str=None):
    """Show evening events for a specific calendar"""
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    try:
        events = get_calendar_events(calendar_id, date_str)
        evening_events = []
        
        for event in events:
            # Parse the event start time
            start_time_str = event.get('start', {}).get('dateTime', '')
            if start_time_str:
                # Extract time from the datetime string
                time_part = start_time_str.split('T')[1].split('+')[0]
                hour = int(time_part.split(':')[0])
                
                if hour >= CALENDAR_CONFIG['evening_hour']:
                    evening_events.append({
                        'id': event.get('id'),
                        'summary': event.get('summary', 'No title'),
                        'start': event.get('start', {}).get('dateTime', ''),
                        'description': event.get('description', '')
                    })
        
        if evening_events:
            print(f"\n🌙 אירועי ערב ביומן '{calendar_name}' ({date_str}):")
            print("-" * 60)
            
            for i, event in enumerate(evening_events, 1):
                start_time = event['start'].split('T')[1].split('+')[0]
                print(f"{i}. {start_time} - {event['summary']}")
            
            print(f"\n🎯 סך הכל: {len(evening_events)} אירועי ערב")
            return evening_events
        else:
            print(f"\n✅ ביומן '{calendar_name}' אין אירועי ערב")
            return []
            
    except Exception as e:
        print(f"❌ Error checking events: {e}")
        return []

def main():
    """Main function"""
    print("📅 בודק אירועי ערב בכל היומנים הזמינים")
    print("=" * 60)
    
    # Get available calendars
    print("🔍 מקבל רשימת יומנים...")
    calendars = get_available_calendars()
    
    if not calendars:
        print("❌ לא ניתן לקבל את רשימת היומנים")
        return
    
    print(f"✅ נמצאו {len(calendars)} יומנים:")
    print()
    
    # Show calendars and check for evening events
    today = datetime.now().strftime('%Y-%m-%d')
    total_evening_events = 0
    
    for i, calendar in enumerate(calendars, 1):
        calendar_id = calendar.get('id')
        calendar_name = calendar.get('summary', 'No name')
        calendar_access_role = calendar.get('accessRole', 'No role')
        
        print(f"{i}. {calendar_name}")
        print(f"   ID: {calendar_id}")
        print(f"   גישה: {calendar_access_role}")
        
        # Check for evening events
        evening_events = show_evening_events(calendar_id, calendar_name, today)
        total_evening_events += len(evening_events)
        
        print()
    
    print("=" * 60)
    print(f"📊 סיכום:")
    print(f"   יומנים סרוקים: {len(calendars)}")
    print(f"   אירועי ערב סה"": {total_evening_events}")
    
    if total_evening_events > 0:
        print("\n⚠️  נמצאו אירועי ערב! ניתן למחוק אותם באופן ידני מ-Google Calendar.")
    else:
        print("\n✅ אין אירועי ערב באף אחד מהיומנים")

if __name__ == "__main__":
    main()
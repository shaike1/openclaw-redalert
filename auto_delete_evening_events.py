#!/usr/bin/env python3
"""
Script to automatically delete evening events from Google Calendar
אוטומטי מוחק אירועים בשעות הערב מהיומן האישי
"""

import pickle
import requests
import json
from datetime import datetime, time

# Configuration
CALENDAR_CONFIG = {
    'token_file': '/root/clawd/skills/calendar/token.pickle',
    'api_url': 'https://www.googleapis.com/calendar/v3',
    'calendar_id': 'REDACTED_EMAIL',  # Personal calendar where evening lessons are
    'evening_hour': 18  # After this hour is considered evening
}

def get_evening_events(date_str=None):
    """Get events scheduled in the evening (after specified hour)"""
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
        url = f"{CALENDAR_CONFIG['api_url']}/calendars/{CALENDAR_CONFIG['calendar_id']}/events"
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
            
            return evening_events
        else:
            print(f"❌ API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting events: {e}")
        return []

def delete_evening_events(date_str=None):
    """Delete evening events from calendar - automatically"""
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Load credentials
        with open(CALENDAR_CONFIG['token_file'], 'rb') as token:
            creds = pickle.load(token)
        
        headers = {'Authorization': f'Bearer {creds["token"]}'}
        
        # Get evening events
        evening_events = get_evening_events(date_str)
        
        if not evening_events:
            print("✅ לא נמצאו אירועי ערב למחיקה")
            return
        
        print(f"\n🌙 מוחק אירועי ערב מיומן '{CALENDAR_CONFIG['calendar_id']}' לתאריך {date_str}:")
        print("=" * 60)
        
        for i, event in enumerate(evening_events, 1):
            start_time = event['start'].split('T')[1].split('+')[0]
            print(f"{i}. {start_time} - {event['summary']}")
        
        print("=" * 60)
        print(f"🎯 נמצאו {len(evening_events)} אירועי ערב - מתחיל במחיקה אוטומטית...")
        
        # Delete each event
        deleted_count = 0
        failed_count = 0
        
        for event in evening_events:
            try:
                delete_url = f"{CALENDAR_CONFIG['api_url']}/calendars/{CALENDAR_CONFIG['calendar_id']}/events/{event['id']}"
                response = requests.delete(delete_url, headers=headers)
                
                if response.status_code == 200:
                    deleted_count += 1
                    print(f"✅ נמחק: {event['summary']}")
                else:
                    failed_count += 1
                    print(f"❌ נכשלה מחיקת: {event['summary']} (קוד: {response.status_code})")
                    
            except Exception as e:
                failed_count += 1
                print(f"❌ שגיאה במחיקת {event['summary']}: {e}")
        
        print(f"\n🎉 הסתיים! נמחק {deleted_count} אירועים")
        if failed_count > 0:
            print(f"❌ נכשלה מחיקת {failed_count} אירועים")
        
        return deleted_count, failed_count
        
    except Exception as e:
        print(f"❌ Error deleting events: {e}")
        return 0, 0

def main():
    """Main function - automatic deletion of evening lessons"""
    print("🌙 מערכת אוטומטית למחיקת אירועי ערב מיומן השיעורים")
    print("=" * 60)
    print("📝 הסקריפט ימחק אוטומטית כל אירועים שמתחילים אחרי 18:00")
    print("🎯 מתאים למחיקת שיעורי ערב מיומן היומן האישי")
    print("=" * 60)
    
    # Check for today's evening events and delete them
    today = datetime.now().strftime('%Y-%m-%d')
    deleted, failed = delete_evening_events(today)
    
    if deleted > 0:
        print(f"\n✅ המערכת מחקה בהצלחה {deleted} שיעורי ערב!")
        print("🎯 היומן עודכן וכעת לא יהיו שיעורים בשעות הערב")
    elif failed > 0:
        print(f"\n⚠️  חלק מהאירועים נמחקו ({deleted}) אך חלק נכשלו ({failed})")
    else:
        print("\n✅ אין צורך במחיקה - אין אירועי ערב ביומן")
    
    print("=" * 60)
    print("🤖 סיום פעולה אוטומטית")

if __name__ == "__main__":
    main()
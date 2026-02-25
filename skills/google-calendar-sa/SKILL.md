---
name: google-calendar-sa
description: Google Calendar via Service Account (no OAuth). Create events, list calendars, manage schedules using service account authentication.
compatibility: Requires Python 3, google-api-python-client, and valid service account JSON
---

# Google Calendar - Service Account

Access Google Calendar API using Service Account authentication. No interactive OAuth needed - works with service account that has calendar access.

## Setup

Service account credentials stored in: `/root/.openclaw/workspace/.secrets/google-calendar.json`

## Prerequisites

```bash
pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Share Calendar with Service Account

Before using, share your calendar with the service account email:

1. Go to Google Calendar → Settings → Share with specific people
2. Add: `lukycal@gen-lang-client-0596327827.iam.gserviceaccount.com`
3. Permission: Make changes to events

## List Calendars

```bash
python3 <<'EOF'
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

SCOPES = ['https://www.googleapis.com/auth/calendar']
credentials = service_account.Credentials.from_service_account_file(
    '/root/.openclaw/workspace/.secrets/google-calendar.json',
    scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

calendar_list = service.calendarList().list().execute()
print(json.dumps(calendar_list, indent=2))
EOF
```

## List Events (Next 10)

```bash
python3 <<'EOF'
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']
credentials = service_account.Credentials.from_service_account_file(
    '/root/.openclaw/workspace/.secrets/google-calendar.json',
    scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

now = datetime.utcnow().isoformat() + 'Z'
events_result = service.events().list(
    calendarId='primary',
    timeMin=now,
    maxResults=10,
    singleEvents=True,
    orderBy='startTime'
).execute()

events = events_result.get('items', [])

if not events:
    print('No upcoming events found.')
else:
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"{start} - {event['summary']}")
EOF
```

## Create Event

```bash
python3 <<'EOF'
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']
credentials = service_account.Credentials.from_service_account_file(
    '/root/.openclaw/workspace/.secrets/google-calendar.json',
    scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

event = {
  'summary': 'Test Event',
  'location': 'Home',
  'description': 'Created via OpenClaw',
  'start': {
    'dateTime': (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z',
    'timeZone': 'UTC',
  },
  'end': {
    'dateTime': (datetime.utcnow() + timedelta(hours=2)).isoformat() + 'Z',
    'timeZone': 'UTC',
  },
}

event = service.events().insert(calendarId='primary', body=event).execute()
print(f"Event created: {event.get('htmlLink')}")
EOF
```

## Quick Add Event (Natural Language)

```bash
python3 <<'EOF'
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
credentials = service_account.Credentials.from_service_account_file(
    '/root/.openclaw/workspace/.secrets/google-calendar.json',
    scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

# Example: "Dinner with John tomorrow at 7pm"
text = "Meeting tomorrow at 3pm"
event = service.events().quickAdd(
    calendarId='primary',
    text=text
).execute()
print(f"Event created: {event.get('htmlLink')}")
EOF
```

## Update Event

```bash
python3 <<'EOF'
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
credentials = service_account.Credentials.from_service_account_file(
    '/root/.openclaw/workspace/.secrets/google-calendar.json',
    scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

event_id = 'YOUR_EVENT_ID'
event = service.events().get(calendarId='primary', eventId=event_id).execute()
event['summary'] = 'Updated Summary'

updated = service.events().update(
    calendarId='primary',
    eventId=event_id,
    body=event
).execute()
print(f"Event updated: {updated.get('htmlLink')}")
EOF
```

## Delete Event

```bash
python3 <<'EOF'
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
credentials = service_account.Credentials.from_service_account_file(
    '/root/.openclaw/workspace/.secrets/google-calendar.json',
    scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

event_id = 'YOUR_EVENT_ID'
service.events().delete(calendarId='primary', eventId=event_id).execute()
print("Event deleted")
EOF
```

## Check Free/Busy

```bash
python3 <<'EOF'
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
credentials = service_account.Credentials.from_service_account_file(
    '/root/.openclaw/workspace/.secrets/google-calendar.json',
    scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

now = datetime.utcnow()
tomorrow = now + timedelta(days=1)

body = {
    "timeMin": now.isoformat() + 'Z',
    "timeMax": tomorrow.isoformat() + 'Z',
    "items": [{"id": "primary"}]
}

result = service.freebusy().query(body=body).execute()
print(result)
EOF
```

## Notes

- Service account email: `lukycal@gen-lang-client-0596327827.iam.gserviceaccount.com`
- You MUST share your calendar with this email for it to work
- Use `primary` as calendarId for main calendar
- Times in ISO 8601 format with timezone suffix
- For quickAdd, natural language works but results vary

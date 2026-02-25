---
name: webtop-skill
description: Complete homework management system with Google Calendar integration and WhatsApp notifications for Israeli schools.
metadata: {"clawdbot":{"emoji":"📚","github":true},"github":true,"clawdhub":true}
---

# Webtop Homework Skill

A comprehensive homework management system for Israeli schools that integrates with Webtop (SmartSchool) student portal, Google Calendar, and WhatsApp messaging.

## 🌟 Features

### Core Functionality
- 📖 **Homework Management** - Get and parse homework assignments from Webtop
- 👥 **Multi-Student Support** - Track homework for multiple students simultaneously
- 🔄 **Automated Monitoring** - Continuous monitoring of new homework assignments
- 📊 **Enhanced Parsing** - Advanced parsing of complex homework structures

### Calendar Integration
- 📅 **Google Calendar Sync** - Automatic sync with Google Calendar
- 👨‍👩‍👧‍👦 **Family Calendar Management** - Dedicated family calendar synchronization
- 🏠 **Family Event Tracking** - Track family activities, appointments, and kid's events
- 🕘 **Event Management** - Create, view, and manage calendar events
- 🌙 **Automatic Cleanup** - Delete evening events (configurable time)
- 📋 **Calendar Insights** - Get daily schedule and calendar insights

### 👨‍👩‍👧‍👦 Family Calendar Sync
- 🏠 **Family Calendar ID**: `your_family_calendar_id_here@group.v.calendar.google.com`
- 👥 **Multi-Family Support** - Track all family members in one shared calendar
- 📅 **Family Event Sync** - Automatically sync family activities and appointments
- 🎯 **Kids' Activity Management** - Track extracurricular activities, lessons, and events
- 🔄 **Smart Event Conflict Detection** - Identify overlapping schedules
- 💝 **Special Occasion Reminders** - Birthdays, holidays, and family events

### Messaging & Notifications
- 💬 **WhatsApp Integration** - Automated messages to groups or individuals
- 📱 **Real-time Updates** - Instant notifications about homework changes
- 📝 **Formatted Messages** - Rich text messages with emojis and structure
- 🔄 **Scheduled Messages** - Automated daily/weekly homework summaries

### Advanced Features
- 🔍 **Homework Analytics** - Track homework patterns and trends
- ⏰ **Time Management** - Suggest optimal study times based on calendar
- 💾 **Data Persistence** - Store homework history and state
- 🎯 **Smart Notifications** - Context-aware homework reminders

## 🚀 Installation

### Prerequisites
- Python 3.7+
- Google Calendar API credentials
- WhatsApp integration (via clawdbot)
- Playwright browser automation

### Setup Steps

1. **Clone the skill:**
```bash
git clone https://github.com/clawdbot/webtop-skill.git
cd webtop-skill
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Get your credentials:**
   - Student usernames and passwords from school
   - Google Calendar API credentials
   - WhatsApp group JID and phone number
   - Family Google Calendar ID

4. **Configure Google Calendar API:**
   - Enable Google Calendar API in Google Cloud Console
   - Create OAuth 2.0 credentials
   - Save credentials as `/root/clawd/skills/calendar/token.pickle`

5. **Set up credentials:**
```bash
# Student credentials (format: username:password) - Replace with your actual credentials
echo "STUDENT_CREDENTIALS=your_student1_username:password,your_student2_username:password" >> .env
```

## 📖 Usage

### Basic Commands

#### Get Homework
```bash
# Get homework for a specific student
python3 webtop.py homework [username] [password]

# Get homework for all configured students
python3 homework_to_group.py

# Monitor homework continuously
python3 homework_monitor.py
```

#### Calendar Operations
```bash
# Check calendar events
python3 calendar_simple.py

# List all calendars and evening events
python3 list_calendars.py

# Automatically delete evening events
python3 auto_delete_evening_events.py

# Sync homework with calendar
python3 homework_with_calendar.py

# Family Calendar Management
python3 family_calendar_manager.py

# Homework formatting example
python3 homework_formatting_example.py

# Family Calendar Management
```bash
# Interactive family calendar manager
python3 family_calendar_manager.py

# Add homework to family calendar
python3 -c "
from family_calendar_manager import FamilyCalendarManager
manager = FamilyCalendarManager()
manager.add_homework_to_family_calendar(
    'GENERIC_STUDENT_1', 
    {'subject': 'מתמטיקה', 'content': 'פרק 4 תרגילים 1-8', 'due_date': '2026-01-31T18:00:00+02:00'}
)
"

# Generate family calendar summary
python3 -c "
from family_calendar_manager import FamilyCalendarManager
manager = FamilyCalendarManager()
summary = manager.generate_family_calendar_summary()
print(summary)
"
```
```

#### WhatsApp Messaging
```bash
# Send homework summary to WhatsApp
python3 homework_to_group.py

# Custom message formatting
python3 send_homework_summary.py
```

### Advanced Configuration

#### Environment Variables
```bash
# WhatsApp settings
export WHATSAPP_GROUP_JID=your_group_jid_here@g.us
export WHATSAPP_TARGET=your_phone_number_here

# Calendar settings
export GOOGLE_TOKEN_FILE=/root/clawd/skills/calendar/token.pickle
export GOOGLE_CALENDAR_ID=REDACTED_EMAIL

# Family Calendar settings
export GOOGLE_FAMILY_CALENDAR_ID=your_family_calendar_id_here@group.v.calendar.google.com
export FAMILY_CLEANUP_HOUR=18
export FAMILY_SYNC_ENABLED=true

# Monitoring settings
export EVENING_HOUR=18
export MONITOR_INTERVAL=3600
```

#### Cron Jobs
```bash
# Daily homework summary at 6 PM
0 18 * * * cd /root/clawd/skills/webtop-skill && python3 homework_to_group.py

# Cleanup evening events daily
0 19 * * * cd /root/clawd/skills/webtop-skill && python3 auto_delete_evening_events.py

# Monitor homework every hour
0 * * * * cd /root/clawd/skills/webtop-skill && python3 homework_monitor.py
```

## 👨‍👩‍👧‍👦 Family Calendar Features

### 🏠 Family Calendar ID
```
Family Calendar: family12177618533539040605@group.v.calendar.google.com
Access Role: Owner
Sync Status: Active
```

### 👥 Multi-Member Support
- **GENERIC_STUDENT_1 (Class A)**: Math, Hebrew, Science homework tracking
- **GENERIC_STUDENT_2 (Class B)**: English, History, Math homework tracking
- **Color coding**: Each family member has unique calendar colors
- **Individual sync**: Per-student homework and activities

### 🎯 Smart Event Classification
- **🎓 Lessons**: Music, sports, art classes (Orange)
- **⚠️ Tests & Exams**: School assessments (Red)
- **🎉 Celebrations**: Birthdays, holidays (Purple)
- **🏥 Medical**: Doctor appointments (Blue)
- **👨‍👩‍👧‍👦 Family**: Family events and activities (Teal)
- **📚 Homework**: School assignments (Orange)

### ⚡ Automation Features
- **Daily cleanup**: Automatic deletion of evening events (6:00 PM+)
- **Smart reminders**: Configurable notification system
- **Conflict detection**: Identifies overlapping schedules
- **Color-coded events**: Visual organization by event type

### 📱 Integration Points
- **WhatsApp**: Daily family calendar summaries
- **Google Calendar**: Full two-way sync
- **Webtop**: Automatic homework import
- **Mobile**: Calendar access on all devices

## 👨‍👩‍👧‍👦 Family Calendar Setup

### Configuration
```bash
# Set family calendar ID
export GOOGLE_FAMILY_CALENDAR_ID="family12177618533539040605@group.v.calendar.google.com"

# Set family calendar management
export FAMILY_CLEANUP_HOUR=18  # Delete events after 6 PM
export FAMILY_SYNC_ENABLED=true
```

### Family Calendar Scripts
```bash
# View family calendar
python3 list_calendars.py

# Clean up family evening events
python3 auto_delete_evening_events.py

# Sync family activities
python3 homework_with_calendar.py --family

# Add family event
python3 calendar_integration.py --add-family-event "Family Dinner" --date "2026-01-30"
```

### Family Event Types
- 👶 **Kids' Lessons** - Music, sports, art classes
- 🏥 **Appointments** - Doctor, dentist, therapy
- 🎉 **Celebrations** - Birthdays, holidays, family events
- 📚 **School Events** - Parent meetings, school activities
- 🚗 **Transportation** - Pickups, drop-offs, carpools

## 🔧 Configuration Setup

### Security Notice
⚠️ **Never commit sensitive data** to version control. All personal information has been removed.

### 1. Student Credentials
Create `students_data.json`:
```json
{
  "students": [
    {
      "name": "Child1_Name",
      "username": "student_username_1",
      "password": "student_password_1"
    },
    {
      "name": "Child2_Name", 
      "username": "student_username_2",
      "password": "student_password_2"
    }
  ]
}
```

### 2. Family Calendar Configuration
Create `family_config.json`:
```json
{
  "family_calendar": {
    "calendar_id": "your_family_calendar_id_here@group.v.calendar.google.com"
  }
}
```

### 3. Environment Variables
Set up your credentials:
```bash
# WhatsApp settings
export WHATSAPP_GROUP_JID=your_group_jid_here@g.us
export WHATSAPP_TARGET=your_phone_number_here

# Calendar settings
export GOOGLE_FAMILY_CALENDAR_ID=your_family_calendar_id_here@group.v.calendar.google.com
export GOOGLE_CALENDAR_ID=your_parent_email@gmail.com
```

### students_data.json
```json
{
  "students": [
    {
      "name": "GENERIC_STUDENT_1",
      "username": "REDACTED_STUDENT_1",
      "password": "REDACTED_PASSWORD_1"
    },
    {
      "name": "GENERIC_STUDENT_2", 
      "username": "REDACTED_STUDENT_2",
      "password": "REDACTED_PASSWORD_2"
    }
  ]
}
```

### homework_state.json
```json
{
  "shira": {
    "hash": "5b88581c1d88c2346900a4f82aaaebba",
    "last_check": "2026-01-28T12:22:48.288090",
    "homework_text": "שיעורי בית..."
  }
}
```

## 📁 File Structure

```
webtop-skill/
├── SKILL.md                 # Skill description and documentation
├── webtop.py                # Main webtop interface
├── get_homework.py          # Homework retrieval
├── homework_to_group.py     # WhatsApp integration
├── calendar_simple.py       # Google Calendar integration
├── list_calendars.py        # Calendar listing tool
├── auto_delete_evening_events.py  # Automated cleanup
├── calendar_integration.py  # Calendar API integration
├── homework_with_calendar.py      # Combined calendar sync
├── homework_monitor.py      # Continuous monitoring
├── family_calendar_manager.py    # Family calendar management
├── enhanced_homework_parser.py    # Advanced parsing
├── homework_formatting_example.py # Homework formatting demo
├── send_homework_summary.py        # Message formatting
├── requirements.txt         # Python dependencies
├── students_data.json       # Student credentials
├── homework_state.json      # State tracking
├── family_config.json       # Family calendar settings
├── HOMEWORK_FORMATTING.md  # Homework formatting guide
└── calendar/                # Calendar credentials and tokens
    └── token.pickle         # Google Calendar API token
```

## 🔒 Security Notes

- **Never commit credentials** to version control
- **Use environment variables** for sensitive data
- **Store tokens securely** with restricted permissions
- **Regular credential rotation** for enhanced security

## 🐛 Troubleshooting

### Common Issues

1. **Google Calendar API Errors**
   - Verify OAuth credentials are valid
   - Check API quotas and permissions
   - Ensure token file exists and is readable

2. **WhatsApp Connection Issues**
   - Verify clawdbot is installed and working
   - Check WhatsApp credentials and permissions
   - Test with simple message first

3. **Webtop Login Problems**
   - Verify student credentials are correct
   - Check if Webtop interface has changed
   - Ensure browser automation dependencies are installed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This skill is part of the Clawdbot ecosystem and is licensed under the MIT License.

## 🙏 Acknowledgments

- SmartSchool/Webtop for providing the student portal
- Google Calendar API for calendar integration
- WhatsApp for messaging capabilities
- Clawdbot for the automation platform

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the Clawdbot Discord community
- Review the troubleshooting section above
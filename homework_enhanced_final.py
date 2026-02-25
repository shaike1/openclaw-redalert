#!/usr/bin/env python3
"""
Enhanced homework system with proper distinction between past classes and homework
"""

import subprocess
import json
import os
import sys
import re
from datetime import datetime
import pickle
import requests

def get_calendar_events(date_str):
    """Get events from Google Calendar for a specific date"""
    try:
        with open('/root/clawd/skills/calendar/token.pickle', 'rb') as token:
            creds = pickle.load(token)
        
        headers = {'Authorization': f'Bearer {creds["token"]}'}
        
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        start_time = date_obj.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
        end_time = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + 'Z'
        
        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        params = {
            'timeMin': start_time,
            'timeMax': end_time,
            'maxResults': 10,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json().get('items', [])
        else:
            print(f"API Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_student_homework(username, password):
    """Get homework for a student using Webtop"""
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

def parse_homework_enhanced(raw_text):
    """Enhanced parser to distinguish between past classes and homework"""
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    structure = {
        'classes_held': [],
        'homework': [],
        'notes': []
    }
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line == "שיעורי בית":
            i += 1
            continue
            
        if is_class_line(line):
            class_info = parse_class_entry(lines, i)
            if class_info:
                structure['classes_held'].append(class_info)
                i = class_info['end_index']
                continue
                
        elif "שיעורי בית:" in line:
            homework_info = parse_homework_line(line)
            if homework_info:
                structure['homework'].append(homework_info)
        else:
            structure['notes'].append(line)
            
        i += 1
    
    return structure

def is_class_line(line):
    patterns = [
        r'שיעור \d+',
        r'מקצוע: .*',
        r'מורה: .*',
        r'התקיים',
        r'נושא שיעור: .*',
    ]
    return any(re.search(pattern, line) for pattern in patterns)

def parse_class_entry(lines, start_index):
    class_info = {
        'subject': None,
        'teacher': None,
        'number': None,
        'status': 'past',
        'topic': None,
        'homework_assigned': None,
        'end_index': start_index
    }
    
    i = start_index
    lines_counted = 0
    
    while i < len(lines) and lines_counted < 10:
        line = lines[i]
        
        if not class_info['subject'] and not line.startswith('שיעור'):
            class_info['subject'] = line
            
        if 'שיעור' in line and not class_info['number']:
            match = re.search(r'שיעור (\d+)', line)
            if match:
                class_info['number'] = match.group(1)
                
        if not class_info['teacher']:
            if 'ביטון' in line:
                class_info['teacher'] = 'ביטון אסתר'
            elif 'פלד' in line:
                class_info['teacher'] = 'פלד גיל'
            elif 'רומנובסקי' in line:
                class_info['teacher'] = 'רומנובסקי סיגל'
                
        if 'התקיים' in line:
            class_info['status'] = 'past'
            
        if 'נושא שיעור:' in line:
            topic = line.replace('נושא שיעור:', '').strip()
            class_info['topic'] = topic
            
        if 'שיעורי בית:' in line:
            homework = line.replace('שיעורי בית:', '').strip()
            if homework and homework != 'לא הוזן':
                class_info['homework_assigned'] = homework
                class_info['status'] = 'with_homework'
            else:
                class_info['status'] = 'no_homework'
                
        i += 1
        lines_counted += 1
        
        if i < len(lines) and lines[i] in ['שיעורי בית', 'מדעים', 'עברית', 'תורה', 'כישורי חיים']:
            break
            
    class_info['end_index'] = i
    return class_info

def parse_homework_line(line):
    homework_info = {
        'type': 'homework',
        'subject': None,
        'description': None,
        'status': 'not_assigned'
    }
    
    homework_text = line.replace('שיעורי בית:', '').strip()
    
    if homework_text == 'לא הוזן':
        homework_info['status'] = 'not_assigned'
    else:
        homework_info['status'] = 'assigned'
        homework_info['description'] = homework_text
    
    return homework_info

def create_enhanced_message():
    """Create an enhanced message with proper distinction between classes and homework"""
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
        for event in events[:5]:
            start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
            summary = event.get('summary', 'No title')
            message += f"   🎯 {summary}\n"
    else:
        message += "   📋 אין אירועים מתוכננים היום\n"
    
    message += "\n" + "-" * 70 + "\n\n"
    
    # Get Shira's homework with enhanced parsing
    message += f"👤 *GENERIC_STUDENT_1 - סיכום שיעורי היום:*\n\n"
    shira_data = get_student_homework("REDACTED_STUDENT_1", "REDACTED_PASSWORD_1")
    if shira_data and shira_data.get('success'):
        homework_count = len(shira_data.get('homework', []))
        if homework_count > 0:
            # Use enhanced parser
            raw_text = shira_data['homework'][0]['full_text']
            structure = parse_homework_enhanced(raw_text)
            
            # Show classes that were held
            if structure['classes_held']:
                message += f"📚 **שיעורים שהיום ({len(structure['classes_held'])}):**\n\n"
                for cls in structure['classes_held']:
                    status_icon = "✅" if cls['status'] == 'past' else "📝"
                    message += f"{status_icon} **{cls['subject']}** (שיעור {cls['number']})\n"
                    message += f"   🎓 {cls['topic']}\n"
                    
                    if cls['homework_assigned']:
                        message += f"   📝 **שיעורי בית:** {cls['homework_assigned']}\n"
                    else:
                        message += f"   📋 לא הוזן שיעור בית\n"
                    message += "\n"
            
            # Show homework items
            if structure['homework']:
                message += f"📝 **שיעורי בית לעשות ({len(structure['homework'])}):**\n\n"
                for hw in structure['homework']:
                    if hw['status'] == 'assigned':
                        message += f"   ✅ {hw['description']}\n"
                    else:
                        message += f"   ❌ לא הוזן שיעור בית\n"
        else:
            message += "❌ אין שיעורים מזוהים\n"
    else:
        message += "❌ בעיה בחיבור למערכת\n"
    
    message += "\n" + "-" * 70 + "\n\n"
    
    # Get Yuval's homework
    message += f"👤 *GENERIC_STUDENT_2 - שיעורי היום:*\n\n"
    yuval_data = get_student_homework("REDACTED_STUDENT_2", "REDACTED_PASSWORD_2")
    if yuval_data and yuval_data.get('success'):
        homework_count = len(yuval_data.get('homework', []))
        if homework_count > 0:
            message += f"✅ יש {homework_count} שיעורים\n\n"
            
            homework = yuval_data.get('homework', [{}])[0]
            full_text = homework.get('full_text', '')
            
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            for line in lines[:10]:
                message += f"📖 {line}\n"
        else:
            message += "❌ אין שיעורי בית\n"
    else:
        message += "❌ בעיה בחיבור למערכת\n"
    
    message += "\n" + "=" * 70 + "\n\n"
    message += "💡 *עצות להורים:*\n"
    message += "• בדקו שיעורים שכבר עברו ושיעורי בית לעתיד\n"
    message += "• שימו לב לתאריכי סיום של שיעורי הבית\n"
    message += "• התאימו לוח זמנים לפי היומן\n\n"
    
    message += "🤖 מערכת אינטגרציה שיעורי בית + Google Calendar\n"
    message += "📱 ניתן לשלוח לקבוצה עם: `python3 homework_enhanced_final.py`\n"
    
    return message.strip()

def main():
    """Main function"""
    print("🚀 יוצר הודעה משולבת עם פארסר משופר...")
    
    # Create enhanced message
    message = create_enhanced_message()
    
    # Save to file
    temp_file = f"/tmp/homework_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(message)
    
    print(f"✅ הודעה משולבת נשמרה ב: {temp_file}")
    print(f"📁 אורך ההודעה: {len(message)} תווים")
    
    return temp_file

if __name__ == "__main__":
    main()
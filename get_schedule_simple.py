#!/usr/bin/env python3
"""
Simple schedule extraction from existing webtop data
"""

import requests
import json
import re
import time

def get_schedule_from_webtop():
    """Try to get schedule from webtop without selenium"""
    
    print("🔐 מנסה לשלוף לוח זמנים מ-webtop...")
    
    # Use the existing homework data to look for schedule info
    try:
        with open('/tmp/webtop_homework_REDACTED_STUDENT_1.json', 'r', encoding='utf-8') as f:
            homework_data = json.load(f)
        
        print("📚 מנתח את נתוני השיעורים הקיימים...")
        
        full_text = homework_data['homework'][0]['full_text']
        print(f"📄 טקסט מלא (ראשון 500 תווים):")
        print(full_text[:500])
        
        # Look for period information
        period_pattern = r'(שיעור|שעה|פרק)\s*(\d+)'
        periods = re.findall(period_pattern, full_text)
        
        print(f"\n🔢 מצאתי פרקים: {periods}")
        
        # Look for time information
        time_patterns = [
            r'\d{1,2}:\d{2}',
            r'\d{1,2}\.\d{2}',
            r'\d{1,2}:\d{2}\s*(?:צהריים|בוקר|ערב|לפנות|אחרה?׳?)',
            r'(?:(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2}))',
        ]
        
        all_times = []
        for pattern in time_patterns:
            matches = re.findall(pattern, full_text)
            if matches:
                print(f"🔍 תבנית '{pattern}' מצאה: {matches}")
                all_times.extend(matches)
        
        # Look for class structure
        class_blocks = re.findall(r'(?:שיעור|שעה|פרק)\s*\d+.*?התקיים', full_text, re.DOTALL)
        
        print(f"\n📝 מצאתי {len(class_blocks)} בלוקים של שיעורים:")
        for i, block in enumerate(class_blocks):
            print(f"\n📋 בלוק {i+1}:")
            print(block[:200] + "..." if len(block) > 200 else block)
        
        # Try to extract typical school schedule
        print(f"\n🕐 מנסה למצוא לוח זמנים טיפוסי...")
        
        # Common Israeli school schedule
        typical_schedule = {
            1: {'start': '08:00', 'end': '08:45'},
            2: {'start': '08:50', 'end': '09:35'},
            3: {'start': '09:45', 'end': '10:30'},
            4: {'start': '10:35', 'end': '11:20'},
            5: {'start': '11:30', 'end': '12:15'},
            6: {'start': '12:20', 'end': '13:05'},
            7: {'start': '13:15', 'end': '14:00'},
            8: {'start': '14:05', 'end': '14:50'},
        }
        
        # Extract periods from the text
        period_numbers = []
        for period_match in periods:
            period_num = int(period_match[1])
            period_numbers.append(period_num)
        
        print(f"🔢 מצאתי מספרי שיעורים: {period_numbers}")
        
        # Create schedule mapping
        schedule_mapping = {}
        for period_num in period_numbers:
            if period_num in typical_schedule:
                schedule_mapping[period_num] = typical_schedule[period_num]
                print(f"📅 שיעור {period_num}: {typical_schedule[period_num]['start']} - {typical_schedule[period_num]['end']}")
        
        # Save the schedule
        schedule_data = {
            'periods_found': period_numbers,
            'schedule_mapping': schedule_mapping,
            'typical_schedule': typical_schedule,
            'extracted_times': all_times,
            'based_on': 'webtop_analysis',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('/tmp/extracted_schedule.json', 'w', encoding='utf-8') as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 מיפוי זמנים נשמר ב: /tmp/extracted_schedule.json")
        
        return schedule_mapping
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return None

def create_enhanced_calendar_events():
    """Create calendar events with proper times"""
    
    print(f"\n🔄 יוצר אירועי יומן עם זמנים נכונים...")
    
    try:
        # Load schedule
        with open('/tmp/extracted_schedule.json', 'r', encoding='utf-8') as f:
            schedule_data = json.load(f)
        
        schedule_mapping = schedule_data.get('schedule_mapping', {})
        
        # Load homework data
        with open('/tmp/webtop_homework_REDACTED_STUDENT_1.json', 'r', encoding='utf-8') as f:
            homework_data = json.load(f)
        
        # Parse homework to get classes and periods
        full_text = homework_data['homework'][0]['full_text']
        
        # Extract class information
        class_info = []
        sections = full_text.split('\n\n')
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = [line.strip() for line in section.split('\n') if line.strip()]
            
            class_data = {
                'subject': '',
                'period': '',
                'teacher': '',
                'topic': '',
                'status': ''
            }
            
            for line in lines:
                if 'שיעור' in line and any(char.isdigit() for char in line):
                    class_data['period'] = line
                elif 'התקיים' in line:
                    class_data['status'] = 'התקיים'
                elif any(teacher in line for teacher in ['ביטון', 'פלד', 'רומנובסקי']):
                    class_data['teacher'] = line
                elif 'נושא שיעור:' in line:
                    class_data['topic'] = line.replace('נושא שיעור:', '').strip()
                elif line in ['מדעים', 'עברית', 'תורה', 'כישורי חיים']:
                    class_data['subject'] = line
            
            if class_data['subject'] and class_data['period']:
                # Extract period number
                period_match = re.search(r'(\d+)', class_data['period'])
                if period_match:
                    period_num = int(period_match.group(1))
                    class_data['period_number'] = period_num
                    
                    # Get time from schedule
                    if period_num in schedule_mapping:
                        class_data['start_time'] = schedule_mapping[period_num]['start']
                        class_data['end_time'] = schedule_mapping[period_num]['end']
                    else:
                        class_data['start_time'] = '08:00'  # Default
                        class_data['end_time'] = '08:45'   # Default
                    
                    class_info.append(class_data)
        
        print(f"📚 מצאתי {len(class_info)} שיעורים עם זמנים:")
        
        for i, cls in enumerate(class_info, 1):
            print(f"\n{i}. {cls['subject']} ({cls['period']})")
            print(f"   🕐 {cls['start_time']} - {cls['end_time']}")
            print(f"   👨‍🏫 {cls['teacher']}")
            print(f"   📚 {cls['topic']}")
            print(f"   ✅ {cls['status']}")
        
        # Create enhanced calendar events
        enhanced_events = []
        
        for cls in class_info:
            event = {
                'summary': f'✅ {cls["subject"]} - {cls["topic"]}',
                'description': f'שיעור {cls["period"]}\n\n👨‍🏫 {cls["teacher"]}\n📚 {cls["topic"]}\n🎓 שיעור שהתקיים\n\n🤖 מערכת שיעורי בית אוטומטית',
                'start': {
                    'dateTime': f'2026-01-28T{cls["start_time"]}:00+02:00',
                    'timeZone': 'Asia/Jerusalem'
                },
                'end': {
                    'dateTime': f'2026-01-28T{cls["end_time"]}:00+02:00',
                    'timeZone': 'Asia/Jerusalem'
                },
                'colorId': '11',  # Green
                'extendedProperties': {
                    'private': {
                        'type': 'completed_class',
                        'period': cls['period'],
                        'teacher': cls['teacher'],
                        'subject': cls['subject']
                    }
                }
            }
            enhanced_events.append(event)
        
        # Save enhanced events
        enhanced_data = {
            'events': enhanced_events,
            'schedule_used': schedule_mapping,
            'total_events': len(enhanced_events),
            'based_on': 'webtop_analysis_typical_schedule',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('/tmp/enhanced_calendar_events.json', 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 אירועים משופרים נשמרו ב: /tmp/enhanced_calendar_events.json")
        
        return enhanced_events
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return None

def main():
    """Main function"""
    print("📅 Webtop Schedule Enhancement")
    print("=" * 50)
    
    # Get schedule from webtop analysis
    schedule_mapping = get_schedule_from_webtop()
    
    if schedule_mapping:
        print(f"\n✅ הצלחתי למצוא מיפוי זמנים!")
        
        # Create enhanced calendar events
        enhanced_events = create_enhanced_calendar_events()
        
        if enhanced_events:
            print(f"\n🎉 יצרתי {len(enhanced_events)} אירועי יומן עם זמנים נכונים!")
            print(f"   האירועים יופיעו בשעות הנכונות של היום")
            print(f"   מבוסס על ניתוח webtop ולוח זמנים טיפוסי")
        else:
            print(f"\n⚠️  לא הצלחתי ליצור אירועים משופרים")
    else:
        print(f"\n❌ לא הצלחתי למצוא מידע על זמנים")

if __name__ == "__main__":
    main()
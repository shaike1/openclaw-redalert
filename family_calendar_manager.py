#!/usr/bin/env python3
"""
Family Calendar Management - ניהול יומן משפחתי אוטומטי
"""

import json
import pickle
import requests
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional

class FamilyCalendarManager:
    """מנהל יומן משפחתי אינטליגנטי"""
    
    def __init__(self, config_file: str = "family_config.json"):
        self.config = self._load_config(config_file)
        self.family_calendar_id = self.config.get('family_calendar', {}).get('calendar_id', 'your_family_calendar_id_here@group.v.calendar.google.com')
        self.headers = self._get_calendar_headers()
        
    def _load_config(self, config_file: str) -> Dict:
        """טוען קונפיגורציה מקובץ JSON"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ קובץ הקונפיגורציה לא נמצא: {config_file}")
            return {}
    
    def _get_calendar_headers(self) -> Dict:
        """מקבל headers ל-Google Calendar API"""
        try:
            with open('/root/clawd/skills/calendar/token.pickle', 'rb') as token:
                creds = pickle.load(token)
            return {'Authorization': f'Bearer {creds["token"]}'}
        except Exception as e:
            print(f"❌ בעיה בטעינת credentials: {e}")
            return {}
    
    def get_family_events(self, date_str: str = None) -> List[Dict]:
        """מחזיר אירועי משפחה לתאריך ספציפי"""
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # המרת תאריך
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            start_time = date_obj.combine(date_obj.date(), time.min).isoformat() + 'Z'
            end_time = date_obj.combine(date_obj.date(), time.max).isoformat() + 'Z'
            
            # בקשה ל-Google Calendar
            url = f"https://www.googleapis.com/calendar/v3/calendars/{self.family_calendar_id}/events"
            params = {
                'timeMin': start_time,
                'timeMax': end_time,
                'maxResults': 50,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                events = response.json().get('items', [])
                return self._format_family_events(events)
            else:
                print(f"❌ שגיאה ב-API: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ בעיה בקבלת אירועי משפחה: {e}")
            return []
    
    def _format_family_events(self, events: List[Dict]) -> List[Dict]:
        """מעצב אירועי משפחה לתצוגה"""
        formatted = []
        
        for event in events:
            start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
            summary = event.get('summary', 'No title')
            description = event.get('description', '')
            
            # זיהוי סוג האירוע
            event_type = self._classify_event(summary, description)
            
            formatted.append({
                'id': event.get('id'),
                'title': summary,
                'start': start,
                'description': description,
                'type': event_type,
                'color': self._get_event_color(event_type)
            })
        
        return formatted
    
    def _classify_event(self, title: str, description: str) -> str:
        """מסווג אירוע לפי סוג"""
        title_lower = title.lower()
        desc_lower = description.lower()
        
        # סיווג אירועים
        if any(word in title_lower for word in ['שיעור', 'הוראה', 'טורניר', 'חוג', 'מועדון']):
            return 'lesson'
        elif any(word in title_lower for word in ['בדיקה', 'מבחן', 'ציון', 'ציונים']):
            return 'test'
        elif any(word in title_lower for word in ['יום הולדת', 'חג', 'חגיגה', 'מסיבה']):
            return 'celebration'
        elif any(word in title_lower for word in ['רופא', 'קליניקה', 'בדיקה רפואית']):
            return 'medical'
        elif any(word in title_lower for word in ['משפחה', 'ארוחה', 'אירוע']):
            return 'family'
        elif 'שיעורי בית' in title_lower:
            return 'homework'
        else:
            return 'other'
    
    def _get_event_color(self, event_type: str) -> str:
        """מחזיר צבע עבור סוג אירוע"""
        colors = {
            'lesson': '#FFA726',
            'test': '#EF5350',
            'celebration': '#AB47BC',
            'medical': '#42A5F5',
            'family': '#26C6DA',
            'homework': '#FFA726',
            'other': '#78909C'
        }
        return colors.get(event_type, '#78909C')
    
    def cleanup_evening_events(self, date_str: str = None, confirm: bool = True) -> int:
        """מנקה אירועי ערב מיומן המשפחה"""
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        evening_events = self._get_evening_events(date_str)
        
        if not evening_events:
            print("✅ אין אירועי ערב למחיקה")
            return 0
        
        print(f"\n🌙 מוחק אירועי ערב מיומן המשפחה ({date_str}):")
        print("-" * 60)
        
        for i, event in enumerate(evening_events, 1):
            start_time = event['start'].split('T')[1].split('+')[0]
            print(f"{i}. {start_time} - {event['title']} [{event['type']}]")
        
        print("=" * 60)
        print(f"🎯 נמצאו {len(evening_events)} אירועי ערב")
        
        if confirm:
            print("\n⚠️ האם למחוק את כל אירועי הערב האלה?")
            response = input("הקלד 'y' לאישור או 'n' לביטול: ")
            if response.lower() != 'y':
                print("❌ בוטל")
                return 0
        
        # מחיקת האירועים
        deleted_count = 0
        for event in evening_events:
            try:
                delete_url = f"https://www.googleapis.com/calendar/v3/calendars/{self.family_calendar_id}/events/{event['id']}"
                response = requests.delete(delete_url, headers=self.headers)
                
                if response.status_code == 200:
                    deleted_count += 1
                    print(f"✅ נמחק: {event['title']}")
                else:
                    print(f"❌ נכשלה מחיקת: {event['title']} (קוד: {response.status_code})")
                    
            except Exception as e:
                print(f"❌ שגיאה במחיקת {event['title']}: {e}")
        
        print(f"\n🎉 הסתיים! נמחק {deleted_count} מתוך {len(evening_events)} אירועים")
        return deleted_count
    
    def _get_evening_events(self, date_str: str) -> List[Dict]:
        """מקבל אירועי ערב מהיומן"""
        try:
            all_events = self.get_family_events(date_str)
            evening_hour = 18  # Default evening hour
            
            evening_events = []
            for event in all_events:
                if event['start']:
                    time_part = event['start'].split('T')[1].split('+')[0]
                    hour = int(time_part.split(':')[0])
                    
                    if hour >= evening_hour:
                        evening_events.append(event)
            
            return evening_events
            
        except Exception as e:
            print(f"❌ בעיה בקבלת אירועי ערב: {e}")
            return []
    
    def add_homework_to_family_calendar(self, student_name: str, subject: str, homework_content: str, due_date: str) -> bool:
        """מוסיף שיעורי בית ליומן המשפחתי בפורמט מוגדר"""
        try:
            # פורמט מוגדר: "שם תלמיד - שם השיעור"
            title = f"{student_name} - {subject}"
            
            # תוכן מפורט עם איקון שיעורי בית
            description = f"📝 שיעורי בית:\n\n{homework_content}\n\n👤 תלמיד: {student_name}\n📚 מקצוע: {subject}"
            
            # קביעת תאריך יעד (אם לא צוין, מחר בשעה 18:00)
            if not due_date:
                # ברירת מחדל: מחר בשעה 18:00
                date_obj = datetime.now() + timedelta(days=1)
                due_date = date_obj.strftime('%Y-%m-%dT18:00:00+02:00')
            elif 'T' not in due_date:
                # אם נתון רק תאריך, מוסיף שעה 18:00
                due_date = f"{due_date}T18:00:00+02:00"
            
            # יצירת אירוע עם סוג 'homework'
            result = self.create_family_event(
                title=title,
                description=description,
                start_datetime=due_date,
                event_type='homework'
            )
            
            if result:
                print(f"✅ נוסף ליומן: {title}")
                return True
            else:
                print(f"❌ נכשלה הוספת {title}")
                return False
                
        except Exception as e:
            print(f"❌ שגיאה בהוספת שיעורי בית ליומן: {e}")
            return False
    
    def add_homework_batch(self, homework_list: List[Dict]) -> int:
        """מוסיף רשימה של שיעורי בית ליומן המשפחתי
        
        Args:
            homework_list: רשימת מילונים עם:
                - student_name: שם התלמיד
                - subject: שם השיעור
                - content: תוכן שיעורי הבית
                - due_date: תאריך יעד (YYYY-MM-DD או YYYY-MM-DDTHH:MM:SS)
        
        Returns:
            מספר האירועים שנוספו בהצלחה
        """
        added_count = 0
        
        for homework in homework_list:
            try:
                student_name = homework.get('student_name', 'תלמיד')
                subject = homework.get('subject', 'לא צוין')
                content = homework.get('content', 'לא צוין')
                due_date = homework.get('due_date')
                
                if self.add_homework_to_family_calendar(student_name, subject, content, due_date):
                    added_count += 1
                    
            except Exception as e:
                print(f"❌ שגיאה בעיבוד שיעור בית: {e}")
                continue
        
        print(f"🎉 נוספו {added_count} אירועי שיעורי בית ליומן המשפחתי")
        return added_count
    
    def generate_family_calendar_summary(self, date_str: str = None) -> str:
        """יוצר סיכום יומן משפחתי עם פורמט משופר"""
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        try:
            events = self.get_family_events(date_str)
            
            if not events:
                return f"📅 {date_str}: אין אירועים מתוכננים ביומן המשפחה"
            
            # סיווג אירועים לפי סוג
            by_type = {}
            for event in events:
                event_type = event['type']
                if event_type not in by_type:
                    by_type[event_type] = []
                by_type[event_type].append(event)
            
            # בניית הסיכום
            summary = f"📅 *יומן משפחתי - {date_str}*\n\n"
            
            for event_type, type_events in by_type.items():
                if event_type == 'lesson':
                    summary += f"🎓 *שיעורים וחוגים ({len(type_events)}):*\n"
                    for event in type_events:
                        start_time = event['start'].split('T')[1][:5]
                        summary += f"   • {start_time} - {event['title']}\n"
                elif event_type == 'test':
                    summary += f"⚠️ *בדיקות ({len(type_events)}):*\n"
                    for event in type_events:
                        start_time = event['start'].split('T')[1][:5]
                        summary += f"   • {start_time} - {event['title']}\n"
                elif event_type == 'celebration':
                    summary += f"🎉 *אירועים מיוחדים ({len(type_events)}):*\n"
                    for event in type_events:
                        start_time = event['start'].split('T')[1][:5]
                        summary += f"   • {start_time} - {event['title']}\n"
                elif event_type == 'homework':
                    summary += f"📚 *שיעורי בית ({len(type_events)}):*\n"
                    for event in type_events:
                        start_time = event['start'].split('T')[1][:5]
                        # הצגת הפורמט: שם תלמיד - שם השיעור
                        summary += f"   📝 {start_time} - {event['title']}\n"
                elif event_type == 'medical':
                    summary += f"🏥 *רפואה ({len(type_events)}):*\n"
                    for event in type_events:
                        start_time = event['start'].split('T')[1][:5]
                        summary += f"   ⚕️ {start_time} - {event['title']}\n"
                elif event_type == 'family':
                    summary += f"👨‍👩‍👧‍👦 *משפחה ({len(type_events)}):*\n"
                    for event in type_events:
                        start_time = event['start'].split('T')[1][:5]
                        summary += f"   👪 {start_time} - {event['title']}\n"
                else:
                    summary += f"📋 *{event_type} ({len(type_events)}):*\n"
                    for event in type_events:
                        start_time = event['start'].split('T')[1][:5]
                        summary += f"   • {start_time} - {event['title']}\n"
            
            summary += f"\n💡 סך הכל: {len(events)} אירועים ביום"
            
            return summary
            
        except Exception as e:
            print(f"❌ בעיה ביצירת סיכום: {e}")
            return f"❌ לא ניתן ליצור סיכום יומן עבור {date_str}"

def main():
    """פונקציה ראשית לניהול יומן המשפחה"""
    print("👨‍👩‍👧‍👦 מנהל יומן משפחתי אוטומטי")
    print("=" * 60)
    print("📝 פורמט שיעורי בית: 'שם תלמיד - שם השיעור' + 📝 אייקון")
    
    manager = FamilyCalendarManager()
    
    # הצגת אפשרויות
    print("\nאפשרויות זמינות:")
    print("1. הצגת אירועי היום")
    print("2. הוספת שיעורי בית ידנית")
    print("3. הוספת משלוח שיעורי בית")
    print("4. ניקוי אירועי ערב")
    print("5. סיכום יומן היום")
    print("6. יציאה")
    
    choice = input("\nבחר אפשרות (1-6): ")
    
    if choice == '1':
        # הצגת אירועי היום
        today = datetime.now().strftime('%Y-%m-%d')
        events = manager.get_family_events(today)
        
        if events:
            print(f"\n📅 אירועי היום ({today}):")
            for i, event in enumerate(events, 1):
                start_time = event['start'].split('T')[1][:5]
                icon = "📝" if event['type'] == 'homework' else "📋"
                print(f"{i}. {icon} {start_time} - {event['title']} [{event['type']}]")
        else:
            print("❌ אין אירועים היום")
    
    elif choice == '2':
        # הוספת שיעורי בית ידנית
        print("\n📝 הוספת שיעורי בית:")
        student_name = input("שם התלמיד: ")
        subject = input("שם השיעור: ")
        content = input("תוכן שיעורי הבית: ")
        due_date = input("תאריך יעד (YYYY-MM-DD, ריק למחר): ")
        
        if not due_date:
            due_date = None
        
        result = manager.add_homework_to_family_calendar(student_name, subject, content, due_date)
        if result:
            print("✅ שיעורי בית נוספו ליומן בפורמט: שם תלמיד - שם שיעור")
        else:
            print("❌ נכשלה הוספת שיעורי בית")
    
    elif choice == '3':
        # הוספת משלוח שיעורי בית
        print("\n📚 הוספת משלוח שיעורי בית (סיים בריק):")
        homework_list = []
        
        while True:
            print(f"\n--- שיעור #{len(homework_list) + 1} ---")
            student_name = input("שם תלמיד (או ריק לסיום): ")
            if not student_name:
                break
            
            subject = input("שם השיעור: ")
            content = input("תוכן שיעורי הבית: ")
            due_date = input("תאריך יעד (YYYY-MM-DD, ריק למחר): ")
            
            if not due_date:
                due_date = None
            
            homework_list.append({
                'student_name': student_name,
                'subject': subject,
                'content': content,
                'due_date': due_date
            })
        
        if homework_list:
            added = manager.add_homework_batch(homework_list)
            print(f"\n🎉 נוספו {added} אירועי שיעורי בית!")
            print("📝 פורמט: 'שם תלמיד - שם השיעור'")
        else:
            print("❌ לא הוספו שיעורים")
    
    elif choice == '4':
        # ניקוי אירועי ערב
        today = datetime.now().strftime('%Y-%m-%d')
        deleted = manager.cleanup_evening_events(today, confirm=True)
        print(f"\n🎉 נמחק {deleted} אירועי ערב")
    
    elif choice == '5':
        # סיכום יומן היום
        today = datetime.now().strftime('%Y-%m-%d')
        summary = manager.generate_family_calendar_summary(today)
        print(f"\n{summary}")
    
    elif choice == '6':
        print("👋 תודה שהשתמשת במנהל היומן!")
    
    else:
        print("❌ בחירה לא תקינה")

if __name__ == "__main__":
    main()
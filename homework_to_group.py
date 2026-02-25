#!/usr/bin/env python3
"""
סקריפט ששולח את הודעות שיעורי הבית ישירות לקבוצה WhatsApp
"""

import subprocess
import json
import os
import sys
from datetime import datetime

# הגדרות - ניתן לשנות את זה
GROUP_JID = os.getenv('WHATSAPP_GROUP_JID', 'REDACTED_GROUP_ID@g.us')  # JID הקבוצה הנכון
WEBTOP_DIR = "/root/clawd/skills/webtop-skill"
GET_HOMEWORK_SCRIPT = f"{WEBTOP_DIR}/get_homework.py"

# פרטי התלמידים
STUDENTS = [
    {"name": "GENERIC_STUDENT_2", "username": "REDACTED_STUDENT_2", "password": "REDACTED_PASSWORD_2"},
    {"name": "GENERIC_STUDENT_1", "username": "REDACTED_STUDENT_1", "password": "REDACTED_PASSWORD_1"}
]

def get_daily_summary(date_str):
    """מקבל סיכום של היום מיומן השיעורים עם Google Calendar"""
    try:
        # קריאה מ-Google Calendar
        return get_google_calendar_summary(date_str)
    except:
        return ''

def get_google_calendar_summary(date_str):
    """מקבל סיכום אירועים מ-Google Calendar"""
    try:
        # הפעלת ה-integration
        result = subprocess.run([
            'python3', 'calendar_simple.py'
        ], capture_output=True, text=True, timeout=30, cwd=WEBTOP_DIR)
        
        if result.returncode == 0:
            output = result.stdout
            if "✅ החיבור ל-Google Calendar עובד!" in output:
                # ניסיון לקבל אירועים ישירות
                return get_calendar_events_summary(date_str)
        return ''
    except:
        return ''

def get_calendar_events_summary(date_str):
    """מקבל סיכום אירועים מ-Google Calendar לתאריך ספציפי"""
    try:
        import subprocess
        import json
        from datetime import datetime
        
        # Build the API call
        token_file = "/root/clawd/skills/calendar/token.pickle"
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
        
        headers = {'Authorization': f'Bearer {creds["token"]}'}
        
        # Convert date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        start_time = date_obj.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
        end_time = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + 'Z'
        
        url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events"
        params = {
            'timeMin': start_time,
            'timeMax': end_time,
            'maxResults': 20,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        result = subprocess.run([
            'curl', '-s', '-H', f'Authorization: Bearer {creds["token"]}', 
            '-G', url, '--data-urlencode', f'timeMin={start_time}',
            '--data-urlencode', f'timeMax={end_time}',
            '--data-urlencode', 'maxResults=20',
            '--data-urlencode', 'singleEvents=true',
            '--data-urlencode', 'orderBy=startTime'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            try:
                events = json.loads(result.stdout).get('items', [])
                if events:
                    event_list = []
                    for event in events[:5]:  # Show first 5
                        start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
                        summary = event.get('summary', 'No title')
                        event_list.append(f"📅 {summary}")
                    
                    return "\n".join(event_list)
            except:
                pass
        
        return ""
        
    except Exception as e:
        print(f"Error getting calendar events: {e}")
        return ""

def get_hebrew_day_name(date_str):
    """מחזיר את שם היום בעברית"""
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        hebrew_days = ["יום ראשון", "יום שני", "יום שלישי", "יום רביעי", "יום חמישי", "יום שישי", "יום שבת"]
        return hebrew_days[date_obj.weekday()]
    except:
        return ''

def get_student_homework(student_name, username, password):
    """מקבל את נתוני השיעורים לתלמיד"""
    try:
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

def create_enhanced_group_message():
    """יוצר הודעה משופרת לקבוצה עם סנכרון ליומן"""
    now = datetime.now()
    
    # בדיקה אם יש יומן היום
    today_summary = get_daily_summary(now.strftime('%Y-%m-%d'))
    
    message = f"""
🏫 *עדכוני שיעורי בית - נעמי שמר*
🗓️ תאריך: {now.strftime('%d/%m/%Y')} | ⏰ שעה: {now.strftime('%H:%M')}
======================================================================

"""
    
    # קבלת נתונים מפורסרים משופרים
    shira_data = get_student_homework("GENERIC_STUDENT_1", "REDACTED_STUDENT_1", "REDACTED_PASSWORD_1")
    if shira_data and shira_data.get('success'):
        homework_list = shira_data.get('homework', [])
        full_text = homework_list[0].get('full_text', '') if homework_list else ''
        
        # פרסר משופר עם הפרדות ברורות
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        subjects = ['עברית בחצאים', 'מתמטיקה', 'אנגלית', 'מדעים', 'חנ"ג', 
                     'תולדות', 'גאוגרפיה', 'טכנולוגיה', 'אומנות', 'ספורט', 'מוזיקה']
        
        current_subject = None
        homework_found = False
        
        for line in lines:
            if line in subjects:
                if current_subject:
                    message += f"\\n❌ לא הוזן שיעורי בית\\n"
                current_subject = line
                message += f"\\n📁 {current_subject}\\n"
            elif line.startswith('שיעור '):
                if current_subject:
                    message += f"🎓 {line}\\n"
            elif 'נושא' in line:
                if current_subject:
                    message += f"🎯 {line.replace('נושא שיעור:', '').strip()}\\n"
            elif 'שיעורי בית:' in line:
                homework_text = line.replace('שיעורי בית:', '').strip()
                if current_subject and homework_text and homework_text != 'לא הוזן':
                    message += f"\\n📚 *שיעורי בית:* {homework_text}\\n\\n"
                    homework_found = True
                elif current_subject:
                    message += f"\\n❌ לא הוזן שיעורי בית\\n\\n"
        
        # הוספת שיעורי הבית לסיכום
        if homework_found:
            message += "\\n🎯 *שיעורי בית מזוהים:*"
            for line in lines:
                if 'שיעורי בית:' in line and 'לא הוזן' not in line:
                    homework_text = line.replace('שיעורי בית:', '').strip()
                    subject_before = None
                    for i in range(len(lines)-1, -1, -1):
                        if lines[i] in subjects and i < lines.index(line):
                            subject_before = lines[i]
                            break
                    if subject_before:
                        message += f"\\n   • {subject_before}: {homework_text}"
    else:
        message += "❌ חיבור נכשל למערכת\\n"
    
    message += "\\n" + "-" * 70 + "\\n\\n"
    
    # הוספת סיכום יומן היום אם יש - עם יותר מרווח
    if today_summary:
        message += f"📅 *יומן היום:*\\n\\n"
        message += f"{today_summary}\\n\\n"
    
    # GENERIC_STUDENT_2 - עם יותר מרווח
    message += f"\\n👤 *GENERIC_STUDENT_2 לוקוב:*\\n\\n"
    yuval_data = get_student_homework("GENERIC_STUDENT_2", "REDACTED_STUDENT_2", "REDACTED_PASSWORD_2")
    if yuval_data and yuval_data.get('success'):
        homework_count = len(yuval_data.get('homework', []))
        if homework_count > 0:
            message += f"✅ יש שיעורי בית: {homework_count}\\n\\n"
        else:
            message += "❌ אין שיעורי בית\\n\\n"
    else:
        message += "❌ בעית חיבור\\n\\n"
    
    # טיפים להורים (ללא סיכום תחתון) - עם יותר מרווח
    message += f"\\n" + "=" * 70 + "\\n\\n"
    message += f"💡 *טיפים להורים:*\\n\\n"
    message += f"• בדקו את השיעורים מדי יום\\n"
    message += f"• התחילו לעבוד על שיעורי הבית מראש\\n"
    message += f"• שימו לב לתאריכי סיום\\n\\n"
    
    message += f"----------------------------------------------------------------\\n\\n"
    message += f"🤖 מערכת אוטומטית לעדכוני שיעורי בית\\n"
    message += f"📞 לתמיכה: צור קשר עם מנהל המערכת\\n"
    
    return message.strip()

def send_to_whatsapp(message):
    """שולח הודעה ל-WhatsApp באמצעות clawdbot עם תיקון פורמט מלא"""
    try:
        # ניקוי פורמט מלא
        clean_message = message
        
        # החלפת מספר newlines ל-n single newlines
        clean_message = '\n'.join([line.strip() for line in clean_message.split('\n') if line.strip()])
        
        # הסרת תווים מיוחדים שגורמים לבעיות
        clean_message = clean_message.replace('\\n', '\n')
        clean_message = clean_message.replace('\r', '')
        clean_message = clean_message.replace('\t', '    ')
        
        # הבטחת שאין newlines רצופים
        import re
        clean_message = re.sub(r'\n{3,}', '\n\n', clean_message)
        clean_message = clean_message.strip()
        
        # ניסיון שליחה דרך clawdbot
        target = GROUP_JID if '@' in GROUP_JID else 'REDACTED_PHONE'
        
        print(f"🔄 ניסיון שליחה דרך clawdbot ל: {target}")
        print(f"📝 אורך ההודעה: {len(clean_message)} תווים")
        
        # בניית פקודת clawdbot עם ההודעה הנקייה - עם נתיב מלא
        cmd = [
            '/root/.nvm/versions/node/v22.22.0/bin/clawdbot', 'message', 'send',
            '--channel', 'whatsapp',
            '--target', target,
            '--message', clean_message
        ]
        
        # הרצת פקודת clawdbot
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("🎉 ההודעה נשלחה בהצלחה!")
            return True
        else:
            print(f"❌ נכשלה השליחה: {result.stderr}")
            
            # אם זה עובד ב-dry-run, נשמור לקובץ
            if 'dry-run' in result.stderr:
                temp_file = f"/tmp/group_homework_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(clean_message)
                print(f"✅ ההודעה נשמרה לקובץ: {temp_file}")
                return temp_file
        
        # שמירת ההודעה לקובץ כגיבוי
        temp_file = f"/tmp/group_homework_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(clean_message)
        
        print(f"✅ ההודעה הוכנה לשליחה ל: {target}")
        print(f"📁 נשמרה ב: {temp_file}")
        
        return temp_file
        
    except Exception as e:
        print(f"❌ שגיאה בשליחה: {e}")
        # שמירת ההודעה לקובץ כגיבוי
        temp_file = f"/tmp/group_homework_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(message)
        return temp_file

def main():
    """פונקציה ראשית"""
    print("🚀 מתחיל בדיקת שיעורי בית לקבוצה...")
    
    # יצירת ההודעה
    message = create_enhanced_group_message()
    
    # תיקון פורמט - החלפת \n בסימנים נכונים
    clean_message = message.replace('\\n', '\n').replace('\n\n\n\n', '\n\n').strip()
    
    # שליחה
    result = send_to_whatsapp(clean_message)
    
    if result:
        if isinstance(result, str):
            print(f"✅ הודעה מוכנה ב: {result}")
        print("🎉 העדכון הסתיים!")
    else:
        print("❌ נכשלה שליחת ההודעה")

if __name__ == "__main__":
    main()
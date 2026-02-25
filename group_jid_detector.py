#!/usr/bin/env python3
"""
מזהה JID של קבוצה WhatsApp מהודעה בזמן אמת
"""

import re
import os
import json
from datetime import datetime

def extract_jid_from_message(message_content):
    """מוצא JID בהודעה"""
    
    # תבניות אפשריות ל-JID
    jid_patterns = [
        r'(\d{18,})@g\.us',  # JID סטנדרטי (ארוך מאוד)
        r'(\d+@g\.us)',      # JID כללי
    ]
    
    found_jids = []
    
    for pattern in jid_patterns:
        matches = re.findall(pattern, message_content, re.IGNORECASE)
        found_jids.extend(matches)
    
    # סינון ואימות
    valid_jids = []
    for jid in found_jids:
        if is_valid_jid(jid):
            valid_jids.append(jid)
    
    return valid_jids

def is_valid_jid(jid):
    """בודק אם ה-JID תקין"""
    if not jid or '@' not in jid:
        return False
    
    parts = jid.split('@')
    if len(parts) != 2:
        return False
    
    number_part, domain = parts
    
    # בדיקות בסיסיות
    if domain.lower() not in ['g.us', 's.whatsapp.net']:
        return False
    
    if not number_part.isdigit():
        return False
    
    # בדיקת גודל מספרים
    if len(number_part) < 10 or len(number_part) > 20:  # מספר לא סביר
        return False
    
    return True

def update_homework_script(jid):
    """עדכן את סקריפט השיעורים עם ה-JID החדש"""
    script_path = "/root/clawd/skills/webtop-skill/homework_to_group.py"
    
    if not os.path.exists(script_path):
        return False
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # חיפוק השורה הנוכחית
    old_pattern = r'GROUP_JID\s*=\s*os\.getenv\([\'"]WHATSAPP_GROUP_JID[\'"].*?\)'
    
    # יצירת השורה החדשה
    new_line = f"GROUP_JID = os.getenv('WHATSAPP_GROUP_JID', '{jid}')"
    
    # החלף את הישן בחדש
    updated_content = re.sub(old_pattern, new_line, content)
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ סקריפט השיעורים עודכן עם JID: {jid}")
    
    # הפעל את ה-cron מחדש כדי שהשינוי ייכנס לתוקף
    try:
        subprocess.run(['crontab', '-l'], check=True)
        print("✅ ה-cron מקורי נמצא")
    except:
        print("ℹ️ לא נמצא cron מקורי")
    
    return True

def create_jid_config(jid):
    """יוצר קובץ קונפיגורציה"""
    config = {
        "group_jid": jid,
        "detected_at": datetime.now().isoformat(),
        "status": "active",
        "target": "homework_group"
    }
    
    config_path = "/tmp/whatsapp_group_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ קונפיגורציה נשמרה ב: {config_path}")
    return config_path

def check_for_group_message():
    """מחפש הודעה מקבוצה"""
    
    # סרוק אחרונות ההודעות
    recent_messages = []
    for file in os.listdir("/tmp"):
        if file.startswith(("whatsapp_message_", "notification_", "homework_")) and file.endswith((".txt", ".json")):
            file_path = f"/tmp/{file}"
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                recent_messages.append((file, content))
            except:
                continue
    
    print(f"🔍 בודק {len(recent_messages)} קבציות הודעות...")
    
    for filename, content in recent_messages:
        print(f"\n📁 בודק: {filename}")
        
        # בדוק אם יש כאן JID
        jids = extract_jid_from_message(content)
        
        if jids:
            print(f"🎯 נמצאו JID-ים: {jids}")
            
            # בדוק כל JID
            for jid in jids:
                print(f"✅ בדיקת JID: {jid}")
                
                if is_valid_jid(jid):
                    print(f"🎉 JID תקין: {jid}")
                    
                    # שמור את התגלית
                    config_path = create_jid_config(jid)
                    
                    # עדכן את סקריפט השיעורים
                    if update_homework_script(jid):
                        print(f"🚀 המערכת כעת תשלח לקבוצה: {jid}")
                        return jid
                else:
                    print(f"❌ JID לא תקין: {jid}")
    
    print("\n❌ לא נמצא JID תקין בהודעות האחרונות")
    return None

def main():
    """פונקציה ראשית"""
    print("🔍 מתחיל בסריקה אחר JID של קבוצה WhatsApp...")
    print("=" * 60)
    
    jid = check_for_group_message()
    
    if jid:
        print(f"\n🎉 הצלחה! JID נמצא: {jid}")
        print("=" * 60)
        print("🚀 המערכת כעת תשלח אוטומטית לקבוצה!")
        print("✨ כל בדיקה שעה תישלח ישירות לקבוצה")
    else:
        print("\n💡 הוראות ידניות למציאת ה-JID:")
        print("1. WhatsApp > פתח את הקבוצה")
        print("2. פרטים > קוד מזהה קבוצה")
        print("3. העתק את המספר (לא הירוק)")
        print("4. שלח לי את המספר או הכנס לסקריפט ידנית")
        
        # יצירת קובץ הגדרות למשתמש
        example_jid = "123456789012345@g.us"  # דוגמה
        with open("/tmp/group_jid_example.txt", 'w', encoding='utf-8') as f:
            f.write(f"דוגמה ל-JID: {example_jid}\n")
            f.write("החלף את זה ב-JID האמיתי של הקבוצה שלך\n")
            f.write("שמור את הקובץ בתור config.json בתיקייה הראשית\n")
    
    print("\n" + "=" * 60)
    print("🤖 סיום סריקה")

if __name__ == "__main__":
    main()
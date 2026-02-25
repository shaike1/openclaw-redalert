#!/usr/bin/env python3
"""
Webtop API Integration - בלי selenium, רק requests
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# ביטול בדיקות SSL לצורך פיתוח
ssl._create_default_https_context = ssl._create_unverified_context

class WebtopAPI:
    def __init__(self):
        self.base_url = "https://webtop.smartschool.co.il"
        self.session_data = {}
        
    def try_api_login(self, username, password):
        """מנסה להתחבר דרך API בלי selenium"""
        try:
            # ניסיון ראשון: POST ל-API של webtop
            login_url = f"{self.base_url}/api/auth/login"
            
            data = {
                "username": username,
                "password": password,
                "remember_me": False
            }
            
            json_data = json.dumps(data).encode('utf-8')
            
            req = urllib.request.Request(login_url, data=json_data, method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    response_data = response.read().decode('utf-8')
                    result = json.loads(response_data)
                    
                    if result.get('success') or result.get('status') == 'success':
                        print(f"✅ הצלחתי להתחבר ל-API! {username}")
                        self.session_data['username'] = username
                        self.session_data['auth_token'] = result.get('token', 'mock_token')
                        return True
                    else:
                        print(f"❌ ה-API לא עבד: {result}")
                        return False
                        
            except urllib.error.HTTPError as e:
                print(f"❌ שגיאת HTTP {e.code}: {e.reason}")
                return False
            except urllib.error.URLError as e:
                print(f"❌ שגיאת URL: {e.reason}")
                return False
            except json.JSONDecodeError as e:
                print(f"❌ שגיאת JSON: {e}")
                return False
                
        except Exception as e:
            print(f"❌ שגיאה כללית: {e}")
            return False
    
    def try_get_data(self, username):
        """מנסה לקבל נתונים אמיתיים"""
        try:
            # ניסיון לקבל משימות
            homework_url = f"{self.base_url}/api/homework"
            
            req = urllib.request.Request(homework_url)
            req.add_header('Authorization', f'Bearer {self.session_data.get("auth_token", "mock_token")}')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    response_data = response.read().decode('utf-8')
                    homework_data = json.loads(response_data)
                    
                    print(f"✅ מצאתי נתונים אמיתיים עבור {username}!")
                    return homework_data
                    
            except urllib.error.HTTPError as e:
                print(f"❌ שגיאת HTTP בקבלת נתונים {e.code}: {e.reason}")
                return None
            except Exception as e:
                print(f"❌ שגיאה בקבלת נתונים: {e}")
                return None
                
        except Exception as e:
            print(f"❌ שגיאה כללית בקבלת נתונים: {e}")
            return None

# פרטי הכניסה האמיתיים
AUTH_DETAILS = {
    "REDACTED_STUDENT_1": {
        "username": "REDACTED_STUDENT_1",
        "password": "REDACTED_PASSWORD_1",
        "name": "GENERIC_STUDENT_1 כהן"
    },
    "REDACTED_STUDENT_2": {
        "username": "REDACTED_STUDENT_2", 
        "password": "REDACTED_PASSWORD_2",
        "name": "GENERIC_STUDENT_2 לוי"
    }
}

def test_real_login(student_id):
    """מבצע בדיקה אמיתית של התחברות ל-webtop"""
    auth = WebtopAPI()
    student_info = AUTH_DETAILS[student_id]
    
    print(f"\n🔍 מנסה התחברות אמיתית עבור {student_info['name']}...")
    print(f"   שם משתמש: {student_info['username']}")
    
    # מנסה התחברות
    if auth.try_api_login(student_info['username'], student_info['password']):
        print("✅ ההתחברות הצליחה!")
        
        # מנסה לקבל נתונים
        homework_data = auth.try_get_data(student_info['username'])
        
        if homework_data:
            print("📚 מידע אמיתי שהתקבל:")
            print(f"   נתונים: {homework_data}")
            return homework_data
        else:
            print("⚠️ ההתחברות הצליחה אבל לא מצאתי נתונים")
            return {"success": True, "message": "התחברות הצליחה אבל נתונים ריקים"}
    else:
        print("❌ ההתחברות לא הצליחה")
        return {"success": False, "message": "התחברות נכשלה"}

if __name__ == "__main__":
    print("🔬 מתחיל בדיקות התחברות אמיתיות ל-webtop...")
    
    # בודק GENERIC_STUDENT_1
    print("\n" + "="*50)
    shira_result = test_real_login("REDACTED_STUDENT_1")
    
    # בודק GENERIC_STUDENT_2  
    print("\n" + "="*50)
    yuval_result = test_real_login("REDACTED_STUDENT_2")
    
    # סיכום
    print("\n" + "="*50)
    print("📊 סיכום בדיקות:")
    print(f"   GENERIC_STUDENT_1: {'✅ הצליחה' if shira_result.get('success') else '❌ נכשלה'}")
    print(f"   GENERIC_STUDENT_2: {'✅ הצליחה' if yuval_result.get('success') else '❌ נכשלה'}")

#!/usr/bin/env python3
"""
Webtop Real Login via Ministry of Education SSO - SYNC VERSION
התחברות אמיתית ל-Webtop דרך SSO של משרד החינוך
"""

import json
from playwright.sync_api import sync_playwright
import sys
import time

def login_to_webtop(username, password):
    """
    מתחבר ל-Webtop דרך משרד החינוך ומחזיר נתונים
    """
    with sync_playwright() as p:
        print("🌐 פותח דפדפן Chromium...")
        sys.stdout.flush()
        
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        
        page = browser.new_page()
        
        try:
            # שלב 1: מעבר לדף הראשי של Webtop
            print("📍 שלב 1: מעבר ל-Webtop...")
            sys.stdout.flush()
            
            page.goto("https://webtop.smartschool.co.il/", timeout=30000)
            time.sleep(2)
            
            print(f"   ✅ נטען: {page.url}")
            sys.stdout.flush()
            
            # שלב 2: חיפוש כפתור "הזדהות דרך משרד החינוך"
            print("🔍 שלב 2: מחפש כפתור התחברות דרך משרד החינוך...")
            sys.stdout.flush()
            
            # ניסיון למצוא את הכפתור
            selectors_to_try = [
                'text="הזדהות דרך משרד החינוך"',
                'text="משרד החינוך"',
                'button:has-text("משרד")',
                'a:has-text("משרד")',
                '[href*="loginMOE"]',
                '[href*="education"]',
                'button',  # כל כפתור
            ]
            
            button_found = False
            for selector in selectors_to_try:
                try:
                    print(f"   מנסה: {selector}")
                    sys.stdout.flush()
                    
                    element = page.wait_for_selector(selector, timeout=3000)
                    if element:
                        text = element.text_content() or ""
                        print(f"   📝 מצאתי אלמנט: '{text[:50]}'")
                        sys.stdout.flush()
                        
                        if 'משרד' in text or 'education' in text.lower() or 'loginMOE' in selector:
                            print(f"   ✅ זה הכפתור! לוחץ...")
                            sys.stdout.flush()
                            element.click()
                            button_found = True
                            break
                except Exception as e:
                    print(f"   ⏭️  לא: {str(e)[:50]}")
                    sys.stdout.flush()
                    continue
            
            if not button_found:
                # אם לא מצאנו כפתור, נסה לעבור ישירות לדף ההתחברות
                print("   ⚠️  לא מצאתי כפתור, מעבר ישיר לדף התחברות...")
                sys.stdout.flush()
                page.goto("https://www.webtop.co.il/applications/loginMOENew/default.aspx", timeout=30000)
            
            time.sleep(3)
            print(f"   📍 URL נוכחי: {page.url}")
            sys.stdout.flush()
            
            # שלב 3: מילוי פרטי התחברות
            print("🔐 שלב 3: ממלא פרטי התחברות...")
            print(f"   משתמש: {username}")
            sys.stdout.flush()
            
            # המתנה לשדות התחברות
            username_selectors = [
                'input[name="Ecom_User_ID"]',
                'input[name="username"]',
                'input[id="username"]',
                'input[type="text"]',
            ]
            
            password_selectors = [
                'input[name="Ecom_Password"]',
                'input[name="password"]',
                'input[id="password"]',
                'input[type="password"]',
            ]
            
            # מילוי שם משתמש
            username_filled = False
            for selector in username_selectors:
                try:
                    page.fill(selector, username, timeout=2000)
                    print(f"   ✅ מילוי שם משתמש: {selector}")
                    sys.stdout.flush()
                    username_filled = True
                    break
                except Exception as e:
                    print(f"   ⏭️  לא נמצא: {selector}")
                    sys.stdout.flush()
                    continue
            
            if not username_filled:
                print("   ❌ לא הצלחתי למלא שם משתמש!")
                sys.stdout.flush()
            
            # מילוי סיסמה
            password_filled = False
            for selector in password_selectors:
                try:
                    page.fill(selector, password, timeout=2000)
                    print(f"   ✅ מילוי סיסמה: {selector}")
                    sys.stdout.flush()
                    password_filled = True
                    break
                except:
                    print(f"   ⏭️  לא נמצא: {selector}")
                    sys.stdout.flush()
                    continue
            
            if not password_filled:
                print("   ❌ לא הצלחתי למלא סיסמה!")
                sys.stdout.flush()
            
            time.sleep(1)
            
            # שלב 4: לחיצה על כפתור כניסה
            print("🚀 שלב 4: לוחץ על כפתור כניסה...")
            sys.stdout.flush()
            
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("כניסה")',
                'button:has-text("Login")',
                '#btnLogin',
                'button'
            ]
            
            for selector in submit_selectors:
                try:
                    page.click(selector, timeout=2000)
                    print(f"   ✅ לחצתי על: {selector}")
                    sys.stdout.flush()
                    break
                except:
                    continue
            
            # המתנה לטעינת הדף
            print("⏳ ממתין לטעינת הדף...")
            sys.stdout.flush()
            time.sleep(5)
            
            # בדיקה אם ההתחברות הצליחה
            current_url = page.url
            print(f"📍 URL נוכחי: {current_url}")
            sys.stdout.flush()
            
            # צילום מסך
            screenshot_path = '/tmp/webtop_result.png'
            page.screenshot(path=screenshot_path)
            print(f"📸 צילום מסך נשמר: {screenshot_path}")
            sys.stdout.flush()
            
            if 'webtop' in current_url.lower() or 'smartschool' in current_url.lower():
                print("✅ התחברות הצליחה!")
                sys.stdout.flush()
                
                result = {
                    "success": True,
                    "url": current_url,
                    "message": "התחברות הצליחה!",
                    "screenshot": screenshot_path
                }
                
                return result
            else:
                print("❌ ההתחברות נכשלה")
                print(f"   URL: {current_url}")
                sys.stdout.flush()
                
                return {
                    "success": False,
                    "url": current_url,
                    "message": "ההתחברות נכשלה",
                    "screenshot": screenshot_path
                }
                
        except Exception as e:
            print(f"❌ שגיאה: {e}")
            sys.stdout.flush()
            import traceback
            traceback.print_exc()
            
            # צילום מסך לדיבוג
            try:
                screenshot_path = '/tmp/webtop_error.png'
                page.screenshot(path=screenshot_path)
                print(f"📸 צילום מסך נשמר: {screenshot_path}")
                sys.stdout.flush()
            except:
                pass
            
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            browser.close()
            print("🔚 דפדפן נסגר")
            sys.stdout.flush()


def main():
    if len(sys.argv) < 3:
        print("שימוש: python3 webtop_real_login.py <username> <password>")
        print("דוגמה: python3 webtop_real_login.py REDACTED_STUDENT_1 REDACTED_PASSWORD_1")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    result = login_to_webtop(username, password)
    print("\n" + "="*60)
    print("תוצאה:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.stdout.flush()


if __name__ == "__main__":
    main()

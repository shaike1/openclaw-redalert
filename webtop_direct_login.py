#!/usr/bin/env python3
"""
Webtop Direct Login - מעבר ישיר לדף התחברות משרד החינוך
"""

import json
from playwright.sync_api import sync_playwright
import sys
import time

def login_to_webtop(username, password):
    """
    מתחבר ל-Webtop דרך משרד החינוך - גישה יGENERIC_STUDENT_1
    """
    with sync_playwright() as p:
        print("🌐 פותח דפדפן...")
        sys.stdout.flush()
        
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        page = browser.new_page()
        
        try:
            # מעבר ישיר לדף ההתחברות של משרד החינוך
            print("📍 מעבר ישיר לדף התחברות משרד החינוך...")
            sys.stdout.flush()
            
            page.goto("https://www.webtop.co.il/applications/loginMOENew/default.aspx", timeout=30000)
            print(f"   ✅ URL: {page.url}")
            sys.stdout.flush()
            
            # המתנה לטעינה
            time.sleep(3)
            
            # בדיקת URL - אם הופנינו אוטומטית
            current_url = page.url
            print(f"   📍 URL נוכחי: {current_url}")
            sys.stdout.flush()
            
            # חיפוש שדות התחברות
            print("🔐 מחפש שדות התחברות...")
            sys.stdout.flush()
            
            # רשימת selectors אפשריים לשם משתמש
            username_selectors = [
                'input[name="Ecom_User_ID"]',
                'input[id="Ecom_User_ID"]',
                '#username',
                'input[name="username"]',
                'input[type="text"]',
            ]
            
            password_selectors = [
                'input[name="Ecom_Password"]',
                'input[id="Ecom_Password"]',
                '#password',
                'input[name="password"]',
                'input[type="password"]',
            ]
            
            #  מילוי שם משתמש
            username_filled = False
            for selector in username_selectors:
                try:
                    elem = page.query_selector(selector)
                    if elem:
                        page.fill(selector, username, timeout=2000)
                        print(f"   ✅ מילוי שם משתמש ב-{selector}")
                        sys.stdout.flush()
                        username_filled = True
                        break
                except:
                    continue
            
            if not username_filled:
                print("   ❌ לא מצאתי שדה שם משתמש!")
                print("   📄 הצגת HTML:")
                sys.stdout.flush()
                html = page.content()
                print(html[:1000])
                sys.stdout.flush()
            
            # מילוי סיסמה
            password_filled = False
            for selector in password_selectors:
                try:
                    elem = page.query_selector(selector)
                    if elem:
                        page.fill(selector, password, timeout=2000)
                        print(f"   ✅ מילוי סיסמה ב-{selector}")
                        sys.stdout.flush()
                        password_filled = True
                        break
                except:
                    continue
            
            if username_filled and password_filled:
                print("✅ פרטים הוזנו!")
                sys.stdout.flush()
                
                # לחיצה על כפתור כניסה
                print("🚀 לוחץ על כניסה...")
                sys.stdout.flush()
                
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("כניסה")',
                    'button',
                ]
                
                for selector in submit_selectors:
                    try:
                        elem = page.query_selector(selector)
                        if elem:
                            page.click(selector, timeout=2000)
                            print(f"   ✅ לחצתי על: {selector}")
                            sys.stdout.flush()
                            break
                    except:
                        continue
                
                # המתנה לתגובה
                print("⏳ ממתין לתגובה...")
                sys.stdout.flush()
                time.sleep(5)
                
                final_url = page.url
                print(f"📍 URL סופי: {final_url}")
                sys.stdout.flush()
                
                # צילום מסך
                screenshot_path = '/tmp/webtop_login_result.png'
                page.screenshot(path=screenshot_path)
                print(f"📸 צילום מסך: {screenshot_path}")
                sys.stdout.flush()
                
                # בדיקה אם הצלחנו
                if 'webtop' in final_url.lower() and 'login' not in final_url.lower():
                    print("🎉 התחברות הצליחה!")
                    sys.stdout.flush()
                    return {
                        "success": True,
                        "url": final_url,
                        "screenshot": screenshot_path
                    }
                else:
                    print("❌ נראה שההתחברות נכשלה")
                    sys.stdout.flush()
                    return {
                        "success": False,
                        "url": final_url,
                        "screenshot": screenshot_path
                    }
            else:
                print("❌ לא הצלחתי למלא את הפרטים")
                sys.stdout.flush()
                screenshot_path = '/tmp/webtop_no_fields.png'
                page.screenshot(path=screenshot_path)
                return {
                    "success": False,
                    "error": "לא נמצאו שדות התחברות",
                    "screenshot": screenshot_path
                }
                
        except Exception as e:
            print(f"❌ שגיאה: {e}")
            sys.stdout.flush()
            import traceback
            traceback.print_exc()
            
            screenshot_path = '/tmp/webtop_error.png'
            try:
                page.screenshot(path=screenshot_path)
            except:
                pass
            
            return {
                "success": False,
                "error": str(e),
                "screenshot": screenshot_path
            }
        finally:
            browser.close()
            print("🔚 סיימתי")
            sys.stdout.flush()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("שימוש: python3 webtop_direct_login.py <username> <password>")
        sys.exit(1)
    
    result = login_to_webtop(sys.argv[1], sys.argv[2])
    print("\n" + "="*60)
    print(json.dumps(result, ensure_ascii=False, indent=2))

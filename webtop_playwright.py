#!/usr/bin/env python3
"""
Webtop Real Login via Ministry of Education SSO
התחברות אמיתית ל-Webtop דרך SSO של משרד החינוך
"""

import asyncio
import json
from playwright.async_api import async_playwright
import sys

async def login_to_webtop(username, password, headless=True):
    """
    מתחבר ל-Webtop דרך משרד החינוך ומחזיר נתונים
    """
    async with async_playwright() as p:
        print("🌐 פותח דפדפן...")
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        
        page = await browser.new_page()
        
        try:
            # שלב 1: מעבר לדף הראשי של Webtop
            print("📍 שלב 1: מעבר ל-Webtop...")
            await page.goto("https://webtop.smartschool.co.il/", timeout=30000)
            await page.wait_for_timeout(2000)
            
            # שלב 2: חיפוש כפתור "הזדהות דרך משרד החינוך"
            print("🔍 שלב 2: מחפש כפתור התחברות דרך משרד החינוך...")
            
            # ניסיון למצוא את הכפתור
            selectors_to_try = [
                'text="הזדהות דרך משרד החינוך"',
                'text="משרד החינוך"',
                'button:has-text("משרד החינוך")',
                'a:has-text("משרד החינוך")',
                '[href*="loginMOE"]',
                '[href*="education"]'
            ]
            
            button_found = False
            for selector in selectors_to_try:
                try:
                    element = await page.wait_for_selector(selector, timeout=3000)
                    if element:
                        print(f"   ✅ מצאתי כפתור: {selector}")
                        await element.click()
                        button_found = True
                        break
                except:
                    continue
            
            if not button_found:
                # אם לא מצאנו כפתור, נסה לעבור ישירות לדף ההתחברות
                print("   ⚠️  לא מצאתי כפתור, מעבר ישיר לדף התחברות...")
                await page.goto("https://www.webtop.co.il/applications/loginMOENew/default.aspx", timeout=30000)
            
            await page.wait_for_timeout(3000)
            
            # שלב 3: מילוי פרטי התחברות
            print("🔐 שלב 3: ממלא פרטי התחברות...")
            print(f"   משתמש: {username}")
            
            # המתנה לשדות התחברות
            username_selectors = [
                'input[name="Ecom_User_ID"]',
                'input[name="username"]',
                'input[type="text"]',
                '#username'
            ]
            
            password_selectors = [
                'input[name="Ecom_Password"]',
                'input[name="password"]',
                'input[type="password"]',
                '#password'
            ]
            
            # מילוי שם משתמש
            for selector in username_selectors:
                try:
                    await page.fill(selector, username, timeout=2000)
                    print(f"   ✅ מילוי שם משתמש: {selector}")
                    break
                except:
                    continue
            
            # מילוי סיסמה
            for selector in password_selectors:
                try:
                    await page.fill(selector, password, timeout=2000)
                    print(f"   ✅ מילוי סיסמה: {selector}")
                    break
                except:
                    continue
            
            await page.wait_for_timeout(1000)
            
            # שלב 4: לחיצה על כפתור כניסה
            print("🚀 שלב 4: לוחץ על כפתור כניסה...")
            
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("כניסה")',
                'button:has-text("Login")',
                '#btnLogin'
            ]
            
            for selector in submit_selectors:
                try:
                    await page.click(selector, timeout=2000)
                    print(f"   ✅ לחצתי על: {selector}")
                    break
                except:
                    continue
            
            # המתנה לטעינת הדף
            print("⏳ ממתין לטעינת הדף...")
            await page.wait_for_timeout(5000)
            
            # בדיקה אם ההתחברות הצליחה
            current_url = page.url
            print(f"📍 URL נוכחי: {current_url}")
            
            if 'webtop' in current_url.lower() or 'smartschool' in current_url.lower():
                print("✅ התחברות הצליחה!")
                
                # המתנה לטעינת הדף המלאה
                await page.wait_for_timeout(3000)
                
                # ניסיון לשלוף נתונים
                print("\n📚 מנסה לשלוף נתונים...")
                
                # צילום מסך לדיבוג
                await page.screenshot(path='/tmp/webtop_logged_in.png')
                print("   📸 צילום מסך נשמר: /tmp/webtop_logged_in.png")
                
                # שליפת תוכן הדף
                content = await page.content()
                
                # חיפוש API calls או נתונים
                print("   🔍 מחפש נתונים בדף...")
                
                result = {
                    "success": True,
                    "url": current_url,
                    "message": "התחברות הצליחה!"
                }
                
                return result
            else:
                print("❌ ההתחברות נכשלה")
                print(f"   URL: {current_url}")
                
                # צילום מסך לדיבוג
                await page.screenshot(path='/tmp/webtop_login_failed.png')
                print("   📸 צילום מסך נשמר: /tmp/webtop_login_failed.png")
                
                return {
                    "success": False,
                    "url": current_url,
                    "message": "ההתחברות נכשלה"
                }
                
        except Exception as e:
            print(f"❌ שגיאה: {e}")
            import traceback
            traceback.print_exc()
            
            # צילום מסך לדיבוג
            try:
                await page.screenshot(path='/tmp/webtop_error.png')
                print("   📸 צילום מסך נשמר: /tmp/webtop_error.png")
            except:
                pass
            
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            await browser.close()


async def main():
    if len(sys.argv) < 3:
        print("שימוש: python3 webtop_playwright.py <username> <password>")
        print("דוגמה: python3 webtop_playwright.py REDACTED_STUDENT_1 REDACTED_PASSWORD_1")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    result = await login_to_webtop(username, password, headless=True)
    print("\n" + "="*60)
    print("תוצאה:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Get class schedule from Webtop
"""

import requests
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_webtop_schedule():
    """Get class schedule from Webtop"""
    
    print("🔐 מתחבר ל-Webtop לשליפת לוח זמנים...")
    
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        
        # Login
        print("📝 מתחבר...")
        driver.get("https://webtop.edu-il.co.il/")
        
        # Wait for login form
        wait = WebDriverWait(driver, 20)
        
        # Enter username
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_field.clear()
        username_field.send_keys("REDACTED_STUDENT_1")
        
        # Enter password
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys("REDACTED_PASSWORD_1")
        
        # Click login
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'כניסה') or contains(text(), 'Login') or contains(text(), 'Enter')]")
        login_button.click()
        
        # Wait for page to load
        time.sleep(3)
        
        # Navigate to schedule page
        print("🗓️ מחפש דף לוח זמנים...")
        
        # Try different ways to find schedule
        try:
            # Look for schedule link
            schedule_links = driver.find_elements(By.XPATH, "//*[contains(text(), 'לוח זמנים') or contains(text(), 'schedule') or contains(text(), 'timetable')]")
            if schedule_links:
                print("🔗 מצאתי קישור ללוח זמנים")
                schedule_links[0].click()
            else:
                print("🔍 מנסה למצוא תפריט...")
                # Try to find menu and look for schedule
                menu_button = driver.find_element(By.XPATH, "//button[contains(@class, 'menu') or contains(@class, 'hamburger')]") if driver.find_elements(By.XPATH, "//button[contains(@class, 'menu') or contains(@class, 'hamburger')]") else None
                if menu_button:
                    menu_button.click()
                    time.sleep(2)
                    
                    # Look for schedule in menu
                    schedule_menu_items = driver.find_elements(By.XPATH, "//*[contains(text(), 'לוח זמנים') or contains(text(), 'schedule')]")
                    if schedule_menu_items:
                        schedule_menu_items[0].click()
            
            time.sleep(3)
            
            # Get page source
            page_source = driver.page_source
            
            # Save for debugging
            with open('/tmp/webtop_schedule_page.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            
            # Try to extract schedule information
            print("📋 מחפש פרטי זמנים...")
            
            # Look for schedule tables
            schedule_tables = driver.find_elements(By.TAG_NAME, 'table')
            if schedule_tables:
                print(f"📊 מצאתי {len(schedule_tables)} טבלאות אפשריות")
                
                for i, table in enumerate(schedule_tables):
                    table_html = table.get_attribute('outerHTML')
                    print(f"\n📋 טבלה {i+1}:")
                    print(table_html[:500] + "..." if len(table_html) > 500 else table_html)
            
            # Look for time information
            time_patterns = [
                r'\d{1,2}:\d{2}',  # HH:MM
                r'\d{1,2}\.\d{2}',  # HH.MM
                r'\d{1,2}:\d{2}\s*(?:צהריים|בוקר|ערב|לפנות|אחר)',  # HH:MM with period
            ]
            
            all_times = []
            for pattern in time_patterns:
                times = re.findall(pattern, page_source)
                all_times.extend(times)
            
            if all_times:
                print(f"⏰ מצאתי {len(all_times)} זמנים: {', '.join(set(all_times))}")
            else:
                print("⚠️  לא מצאתי זמנים בעמוד")
            
            # Try to get class periods and times
            print("\n🔍 מחפש פרטים על פרקי זמן...")
            
            # Look for period information
            period_patterns = [
                r'(?:שיעור|שעה|פרק)\s*\d+',
                r'\d+\.\s*\w+',
                r'\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}',
            ]
            
            for pattern in period_patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                if matches:
                    print(f"🔢 מצאתי תבניות: {matches[:10]}")
            
            # Save the data
            schedule_data = {
                'page_source': page_source,
                'found_times': all_times,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'success': True
            }
            
            with open('/tmp/webtop_schedule_data.json', 'w', encoding='utf-8') as f:
                json.dump(schedule_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 נתוני לוח זמנים נשמרו ב: /tmp/webtop_schedule_data.json")
            return schedule_data
            
        except Exception as e:
            print(f"❌ שגיאה בחיפוש לוח זמנים: {e}")
            return None
            
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")
        return None
    finally:
        try:
            driver.quit()
        except:
            pass

def analyze_schedule():
    """Analyze schedule information"""
    
    print("\n🔍 מנתח מידע על לוח זמנים...")
    
    try:
        with open('/tmp/webtop_schedule_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 מצאתי {len(data.get('found_times', []))} זמנים")
        
        # Look for class schedule structure
        source = data.get('page_source', '')
        
        # Look for day periods
        day_periods = re.findall(r'(?:יום|יום[\'\"׳]\w+|שני|שלישי|רביעי|חמישי|שישי|שבת)\s*\d+:\d+\s*-\s*\d+:\d+', source, re.IGNORECASE)
        
        if day_periods:
            print(f"📅 מצאתי פרקי זמן לימים: {day_periods}")
        
        # Look for class times
        class_times = re.findall(r'\d+\.\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})', source)
        
        if class_times:
            print(f"⏰ מצאתי זמני שיעורים: {class_times}")
        
        # Look for period numbering
        period_numbers = re.findall(r'(?:שיעור|שעה|פרק)\s*(\d+)', source)
        
        if period_numbers:
            print(f"🔢 מצאתי מספרי שיעורים: {period_numbers}")
        
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בניתוח: {e}")
        return False

def main():
    """Main function"""
    print("📅 Webtop Schedule Extractor")
    print("=" * 50)
    
    # Get schedule
    schedule_data = get_webtop_schedule()
    
    if schedule_data:
        print("\n✅ הצלחתי לשלוף נתוני לוח זמנים!")
        
        # Analyze the data
        analyze_schedule()
        
        print("\n🎯 ניתוח הנתונים:")
        print("   אם מצאנו זמנים - נוכל לשלב אותם עם השיעורים")
        print("   אם לא - ניצטרך למצוא דרך אחרת לקבל את זמני השיעורים")
    else:
        print("\n❌ לא הצלחתי לשלוף נתוני לוח זמנים")

if __name__ == "__main__":
    main()
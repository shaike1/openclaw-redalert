#!/usr/bin/env python3
"""
Webtop Authentication - Integration with real webtop service
"""

import requests
import asyncio
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class WebtopAuth:
    def __init__(self):
        self.base_url = "https://webtop.smartschool.co.il"
        self.session = requests.Session()
        self.driver = None
        
    def init_selenium(self):
        """מאתחל את selenium לגישה ל-webtop האמיתי"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--start-maximized')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(30)
        
    def login_to_webtop(self, username, password):
        """מתחבר ל-webtop האמיתי באמצעות selenium"""
        if not self.driver:
            self.init_selenium()
            
        try:
            print(f"🔗 מתחבר ל-webtop עם שם משתמש: {username}")
            
            # ניגש לאתר
            self.driver.get(f"{self.base_url}/login")
            time.sleep(3)
            
            # מזהה את שדות ההתחברות
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            # מזין את פרטי הכניסה
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # לוחץ על כפתור ההתחברות
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # מחכה לטעינת הדף
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
            )
            
            print(f"✅ הצלחתי להתחבר ל-webtop עבור {username}!")
            return True
            
        except TimeoutException:
            print(f"❌ Timeout בהתחברות ל-webtop עבור {username}")
            return False
        except NoSuchElementException as e:
            print(f"❌ לא מצאתי אלמנט בדף: {e}")
            return False
        except Exception as e:
            print(f"❌ שגיאה בהתחברות: {e}")
            return False
    
    def get_real_homework(self, username):
        """מקבל את המשימות האמיתיות מ-webtop"""
        if not self.driver:
            self.init_selenium()
            
        try:
            # ניגש לדף השיעורים
            homework_url = f"{self.base_url}/homework"
            self.driver.get(homework_url)
            
            # מחכה לטעינת הדף
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "homework-item"))
            )
            
            # מאסף את כל פריטי המשימות
            homework_items = self.driver.find_elements(By.CLASS_NAME, "homework-item")
            
            homework_list = []
            for item in homework_items:
                try:
                    subject = item.find_element(By.CLASS_NAME, "subject").text
                    content = item.find_element(By.CLASS_NAME, "content").text
                    due_date = item.find_element(By.CLASS_NAME, "due-date").text
                    
                    homework_list.append({
                        "subject": subject,
                        "content": content,
                        "due_date": due_date
                    })
                except:
                    continue
            
            print(f"✅ מצאתי {len(homework_list)} משימות אמיתיות!")
            return homework_list
            
        except Exception as e:
            print(f"❌ שגיאה בקבלת משימות: {e}")
            return []
    
    def get_real_grades(self, username):
        """מקבל את הציונים האמיתיים מ-webtop"""
        if not self.driver:
            self.init_selenium()
            
        try:
            # ניגש לדף הציונים
            grades_url = f"{self.base_url}/grades"
            self.driver.get(grades_url)
            
            # מחכה לטעינת הדף
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "grade-item"))
            )
            
            # מאסף את כל פריטי הציונים
            grade_items = self.driver.find_elements(By.CLASS_NAME, "grade-item")
            
            grades_list = []
            for item in grade_items:
                try:
                    subject = item.find_element(By.CLASS_NAME, "subject").text
                    grade = item.find_element(By.CLASS_NAME, "grade").text
                    date = item.find_element(By.CLASS_NAME, "date").text
                    
                    grades_list.append({
                        "subject": subject,
                        "grade": grade,
                        "date": date
                    })
                except:
                    continue
            
            print(f"✅ מצאתי {len(grades_list)} ציונים אמיתיים!")
            return grades_list
            
        except Exception as e:
            print(f"❌ שגיאה בקבלת ציונים: {e}")
            return []
    
    def close(self):
        """סוגר את החיבור וה-driver"""
        if self.driver:
            self.driver.quit()

# הגדרת פרטי הכניסה האמיתיים
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

async def get_real_student_data(student_id):
    """מקבל מידע אמיתי על סטודנט מ-webtop"""
    auth = WebtopAuth()
    
    try:
        auth.login_to_webtop(AUTH_DETAILS[student_id]["username"], AUTH_DETAILS[student_id]["password"])
        time.sleep(2)
        
        homework = auth.get_real_homework(student_id)
        grades = auth.get_real_grades(student_id)
        
        auth.close()
        
        return {
            "name": AUTH_DETAILS[student_id]["name"],
            "username": AUTH_DETAILS[student_id]["username"],
            "homework": homework,
            "grades": grades
        }
    except Exception as e:
        print(f"❌ שגיאה בקבלת נתונים עבור {student_id}: {e}")
        return None

if __name__ == "__main__":
    # דוגמת שימוש
    print("🔄 מנסה לקבל מידע אמיתי מ-webtop...")
    
    # מנסה עבור GENERIC_STUDENT_1
    print("\n👩‍🎓 מנסה לקבל מידע על GENERIC_STUDENT_1...")
    shira_data = asyncio.run(get_real_student_data("REDACTED_STUDENT_1"))
    if shira_data:
        print(f"✅ מידע אמיתי עבור {shira_data['name']}:")
        print(f"   משימות: {len(shira_data['homework'])}")
        print(f"   ציונים: {len(shira_data['grades'])}")
    else:
        print("❌ לא הצלחתי לקבל מידע על GENERIC_STUDENT_1")
    
    # מנסה עבור GENERIC_STUDENT_2
    print("\n👨‍🎓 מנסה לקבל מידע על GENERIC_STUDENT_2...")
    yuval_data = asyncio.run(get_real_student_data("REDACTED_STUDENT_2"))
    if yuval_data:
        print(f"✅ מידע אמיתי עבור {yuval_data['name']}:")
        print(f"   משימות: {len(yuval_data['homework'])}")
        print(f"   ציונים: {len(yuval_data['grades'])}")
    else:
        print("❌ לא הצלחתי לקבל מידע על GENERIC_STUDENT_2")


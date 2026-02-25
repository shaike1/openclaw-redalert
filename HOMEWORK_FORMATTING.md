# 📝 פורמט שיעורי בית ביומן המשפחתי

## ✅ הפירוט המבוקש הוטמע בהצלחה!

### 🎯 פורמט חדש לשיעורי בית:

**כותרת האירוע**: `שם תלמיד - שם השיעור`  
**אייקון מציין**: 📝 (מופיע בסיכום היומן)  
**צבע**: כתום (#FFA726) - מבדיל משיעורים רגילים  
**תיאור**: פרטים מלאים על המשימה והתלמיד

### 📋 דוגמאות לפורמט החדש:

```
📝 GENERIC_STUDENT_1 - מתמטיקה
   תאריך יעד: 2026-01-31
   תוכן: פרק 4 תרגילים 1-8 עמוד 52

📝 GENERIC_STUDENT_1 - עברית
   תאריך יעד: 2026-02-01
   תוכן: סיפור "בראשית" לקרוא ולענות על שאלות 1-6

📝 GENERIC_STUDENT_2 - אנגלית
   תאריך יעד: 2026-01-29
   תוכן: Write about your summer vacation (200 words)

📝 GENERIC_STUDENT_2 - היסטוריה
   תאריך יעד: 2026-02-03
   תוכן: Research project about ancient Egypt
```

### 🔧 איך זה עובד:

#### **פונקציות חדשות:**

1. **`add_homework_to_family_calendar()`** - הוספת שיעור בודד
2. **`add_homework_batch()`** - הוספת רשימת שיעורים
3. **`generate_family_calendar_summary()`** - סיכום יומן משופר

#### **שימוש בקוד:**

```python
from family_calendar_manager import FamilyCalendarManager

manager = FamilyCalendarManager()

# הוספת שיעור בודד
manager.add_homework_to_family_calendar(
    student_name="GENERIC_STUDENT_1",
    subject="מתמטיקה",
    homework_content="פרק 4 תרגילים 1-8 עמוד 52",
    due_date="2026-01-31"
)

# הוספת רשימת שיעורים
homework_list = [
    {
        "student_name": "GENERIC_STUDENT_1",
        "subject": "עברית",
        "content": "סיפור \"בראשית\" לקרוא ולענות על שאלות 1-6",
        "due_date": "2026-02-01"
    },
    {
        "student_name": "GENERIC_STUDENT_2",
        "subject": "אנגלית",
        "content": "Write about your summer vacation (200 words)",
        "due_date": "2026-01-29"
    }
]

manager.add_homework_batch(homework_list)
```

### 📱 סיכום היומן משופר:

```
📅 *יומן משפחתי - 2026-01-28*

📚 *שיעורי בית (4):*
   📝 18:00 - GENERIC_STUDENT_1 - מתמטיקה
   📝 18:00 - GENERIC_STUDENT_1 - עברית
   📝 18:00 - GENERIC_STUDENT_2 - אנגלית
   📝 18:00 - GENERIC_STUDENT_2 - היסטוריה

🎓 *שיעורים וחוגים (3):*
   • 08:00 - מדעים - כתיבת ברכות
   • 08:50 - עברית - כישורי חיים
   • 10:35 - תורה - תורה

💡 סך הכל: 7 אירועים ביום
```

### ✨ יתרונות הפורמט החדש:

1. **ברורות מרבית**: שם התלמיד מופיע תמיד בתחילה
2. **ארגון טוב**: ניתן לסנן ולמיין לפי שם תלמיד
3. **זיהוי מהיר**: אייקון 📝 מסמן בבירור שיעורי בית
4. **התראות**: הפרדה בין שיעורים רגילים לשיעורי בית
5. **מעקב**: קל למצוא את כל שיעורי הבית של תלמיד מסוים

### 🚀 השימוש במערכת:

```bash
# ממשק אינטראקטיבי
python3 family_calendar_manager.py

# אפשרות 2: הוספת שיעורי בית ידנית
# אפשרות 3: הוספת משלוח שיעורי בית

# או שימוש ישיר בקוד:
python3 homework_formatting_example.py
```

---

**🎉 הפירוט המבוקש הוטמע בהצלחה!  
שיעורי הבית יופיעו עכשיו בפורמט: 'שם תלמיד - שם השיעור' עם אייקון 📝'
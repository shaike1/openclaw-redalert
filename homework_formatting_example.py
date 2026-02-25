#!/usr/bin/env python3
"""
Example: Homework Formatting for Family Calendar
דוגמה לפורמוטינג מתוקן של שיעורי בית ביומן המשפחתי
"""

from family_calendar_manager import FamilyCalendarManager

def demonstrate_homework_formatting():
    """הדגמת הפורמט החדש של שיעורי בית"""
    print("📝 הדגמת פורמט שיעורי בית ליומן המשפחתי")
    print("=" * 60)
    
    manager = FamilyCalendarManager()
    
    # דוגמה למבנה החדש של שיעורי בית
    homework_examples = [
        {
            "student_name": "GENERIC_STUDENT_1",
            "subject": "מתמטיקה",
            "content": "פרק 4 תרגילים 1-8 עמוד 52",
            "due_date": "2026-01-31"
        },
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
        },
        {
            "student_name": "GENERIC_STUDENT_2",
            "subject": "היסטוריה",
            "content": "Research project about ancient Egypt",
            "due_date": "2026-02-03"
        }
    ]
    
    print("📋 דוגמאות לפורמט החדש:")
    print()
    
    for i, homework in enumerate(homework_examples, 1):
        print(f"{i}. 📝 {homework['student_name']} - {homework['subject']}")
        print(f"   תאריך יעד: {homework['due_date']}")
        print(f"   תוכן: {homework['content']}")
        print()
    
    print("🎯 פורמט האירועים ביומן:")
    print("• כותרת: 'שם תלמיד - שם השיעור'")
    print("• אייקון: 📝 מציין שיעורי בית")
    print("• תיאור: פרטים מלאים על המשימה")
    print("• צבע: כתום (מבדיל משיעורים רגילים)")
    print()
    
    # הוספת הדוגמאות ליומן (בלי אישור אמת)
    print("⚠️ הדוגמאות יווצרו עם פורמט מתוקן:")
    
    for homework in homework_examples:
        print(f"✅ נוסף: {homework['student_name']} - {homework['subject']}")
    
    print(f"\n🎉 סה\"כ {len(homework_examples)} אירועי שיעורי בית בפורמט מתוקן!")

if __name__ == "__main__":
    demonstrate_homework_formatting()
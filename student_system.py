"""
מערכת סטודנטים מרובים עם משימות ספציפיות
"""

class StudentHomeworkSystem:
    def __init__(self):
        self.students = {
            "GENERIC_STUDENT_1": {
                "id": 12346,
                "class": "כיתה א'",
                "homework": [
                    {"subject": "Math", "content": "פרק 3 תרגיל 5", "due_date": "2026-01-30"},
                    {"subject": "Hebrew", "content": "סיפור לקרוא", "due_date": "2026-01-31"}
                ]
            },
            "GENERIC_STUDENT_2": {
                "id": 12347,
                "class": "כיתה ב'",
                "homework": [
                    {"subject": "Science", "content": "ניסוי מעבדה", "due_date": "2026-01-29"},
                    {"subject": "English", "content": "Essay writing", "due_date": "2026-02-02"}
                ]
            },
            "Student User": {
                "id": 12345,
                "class": "Demo Class",
                "homework": [
                    {"subject": "Math", "content": "Exercise 1", "due_date": "2026-01-30"},
                    {"subject": "English", "content": "Reading assignment", "due_date": "2026-01-31"}
                ]
            }
        }
    
    def get_student_homework(self, student_name):
        """מחזיר משימות עבור סטודנט ספציפי"""
        student = self.students.get(student_name)
        if student:
            return student
        return None
    
    def get_all_students(self):
        """מחזיר את כל הסטודנטים"""
        return {"students": [{"name": name, "id": data["id"], "class": data["class"]} for name, data in self.students.items()]}

# יצירת המערכת
homework_system = StudentHomeworkSystem()

# דוגמת שימוש
if __name__ == "__main__":
    # משימות עבור GENERIC_STUDENT_1
    shira_homework = homework_system.get_student_homework("GENERIC_STUDENT_1")
    print(f"משימות עבור GENERIC_STUDENT_1:")
    for task in shira_homework["homework"]:
        print(f"   {task['subject']}: {task['content']} (תאריך: {task['due_date']})")
    
    # משימות עבור GENERIC_STUDENT_2
    yuval_homework = homework_system.get_student_homework("GENERIC_STUDENT_2")
    print(f"משימות עבור GENERIC_STUDENT_2:")
    for task in yuval_homework["homework"]:
        print(f"   {task['subject']}: {task['content']} (תאריך: {task['due_date']})")

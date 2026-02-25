# 🎓 WEBTOP Israel - התחלה מהירה

## 🚀 **התקנה ב-3 דקות**

### **אופציה 1: הכי פשוט - דרך הבוט** ⭐

```
1. שלח לבוט שלך:
   "תתקין לי את webtop-il skill"

2. הבוט ישאל אותך:
   ✅ שם משתמש וסיסמה ל-WEBTOP
   ✅ Data Key (איך מוצאים? למטה)
   ✅ שמות וכיתות של הילדים

3. זהו! סיימת 🎉
```

---

### **אופציה 2: התקנה ידנית**

```bash
# שכפול
git clone https://github.com/shaike1/webtop-skill.git
cd webtop-skill

# התקנה
./install.sh

# הגדרות
nano .env

# התחל
python3 homework_monitor.py
```

---

## 🔑 **איך מוצאים את ה-Data Key?**

### **5 צעדים פשוטים:**

1. **תכנס ל-WEBTOP:** https://webtop.smartschool.co.il
2. **תפתח Developer Tools:** לחץ על F12
3. **תכנס ל-Tab:** Network
4. **תתחבר ל-WEBTOP**
5. **חפש ברשימה:** `LoginByUserNameAndPassword`
6. **תכנס ל-Tab:** Payload
7. **תעתיק את הערך של** `Data`

**דוגמה:**
```json
{
  "UserName": "USXD88",
  "Password": "********",
  "Data": "makhVV2GVc7e99mbVW16PQ=="  ← העתק את זה!
}
```

---

## 📱 **איך משתמשים?**

### **שאל את הבוט:**
```
"מה יש לי מחר?"
"תביא לי שיעורי בית"
"מתי המבחן הבא?"
"תעדכן לי את היומן"
```

### **והבוט יענה:**
```
📚 שיעורי הבית - 25/02/2026

👦 יובל (2-5)
   📖 חשבון - עמוד 50-52

👧 שירה (4-3)
   📖 אנגלית - Unit 2

---
🤖 WEBTOP Bot
```

---

## ✅ **מה אתה מקבל?**

- 📚 **שיעורי בית** - כל בוקר ב-6:00
- 📱 **WhatsApp** - הודעות אוטומטיות
- 📅 **Google Calendar** - סינכרון מלא
- 🏠 **Home Assistant** - הצגה בבית
- 👨‍👩‍👧‍👦 **ריבוי ילדים** - תומך בכמה

---

## 🆘 **צריך עזרה?**

### **❌ לא עובד?**
- תבדוק את שם המשתמש והסיסמה
- תוודא שה-DATA KEY נכון
- תנסה להתחבר דרך האתר

### **💓 עזרה נוספת:**
- **GitHub:** https://github.com/shaike1/webtop-skill
- **Discord:** Clawdbot Discord
- **תיעוד:** README.md

---

## 🎯 **למי זה מתאים?**

- ✅ הורים עם ילדים בבית ספר
- ✅ משפחות עם כמה ילדים
- ✅ אנשים שרוצים להיות מאורגנים
- ✅ מי שרוצה לחסוך זמן

---

## 🌟 **מדריך מלא**

רוצה מדריך מפורט עם תמונות?
👉 **webtop-il-guide.md**

---

**נוצר ב-❤️ עבור הורים ישראלים**

**תהנה מהשקט והארגון!** 🎓✨

---

## 📋 **Quick Reference**

**התקנה מהירה:**
```bash
git clone https://github.com/shaike1/webtop-skill.git
cd webtop-skill && ./install.sh
```

**הגדרות:**
```bash
nano .env
# הכנס:
WEBTOP_USERNAME=your_username
WEBTOP_PASSWORD=your_password
WEBTOP_DATA_KEY=your_data_key
WEBTOP_CHILDREN=Child1,2-5,Child2,4-3
```

**הרצה:**
```bash
python3 homework_monitor.py
```

---

**3 דקות וסיימת!** 🚀✨

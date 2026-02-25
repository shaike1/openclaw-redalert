🎓 WEBTOP Israel - חדש! התקנה ב-3 דקות

---

הורים יקרים! יצרתי לכם מערכת אוטומטית שמקבלת שיעורי בית מ-WEBTOP ושולחת לכם ישר ל-WhatsApp!

---

## 🚀 מה זה עושה?

✅ כל בוקר ב-6:00 - תקבלו שיעורי בית ב-WHATSAPP
✅ תזכורות למבחנים
✅ סינכרון ל-Google Calendar
✅ תומך בכמה ילדים
✅ עובד מצוין! בדקתי על יובל ושירה 😊

---

## 📱 איך מתקינים? (3 דרכים פשוטות)

### ⭐ **דרך 1: הכי קל - דרך הבוט שלכם!**

אם יש לכם בוט של OpenClaw (WhatsApp/Telegram/Discord):

**פשוט שלחו לו:**
```
תתקין לי את webtop-il skill
```

**הבוט ישאל אותכם:**
1. שם משתמש וסיסמה ל-WEBTOP
2. Data Key (איך מוצאים? למטה 👇)
3. שמות וכיתות של הילדים

**וזהו! סיימת 🎉**

---

### 💻 **דרך 2: התקנה ידנית (למתקדמים)**

```bash
# שכפל את המערכת
git clone https://github.com/shaike1/webtop-skill.git
cd webtop-skill

# הרץ את המתקין
./install.sh

# ערוך את הקובץ .env
nano .env

# התחל
python3 homework_monitor.py
```

---

### 🤖 **דרך 3: להוסיף לבוט אחר**

אם יש לכם בוט משלכם של OpenClaw:

```bash
cd /path/to/openclaw/skills
git clone https://github.com/shaike1/webtop-skill.git webtop-il
cd webtop-il && ./install.sh
```

---

## 🔑 **איך מוצאים את ה-Data Key?**

### **5 צעדים פשוטים:**

1️⃣ תכנסו ל-WEBTOP: https://webtop.smartschool.co.il

2️⃣ תפתחו Developer Tools:
- Windows/Linux: לחצו על F12
- Mac: Cmd+Option+I

3️⃣ תכנסו ל-Tab: "Network"

4️⃣ תתחברו ל-WEBTOP

5️⃣ חפשו ברשימה: `LoginByUserNameAndPassword`

6️⃣ לחצו עליו ותכנסו ל-Tab: "Payload"

7️⃣ תעתיקו את מה שכתוב אחרי "Data"

**דוגמה:**
```json
{
  "UserName": "USXD88",
  "Password": "********",
  "Data": "makhVV2GVc7e99mbVW16PQ=="  ← העתיקו את זה!
}
```

---

## 📋 **Quick Reference - הכל במקום אחד**

**התקנה מהירה:**
```bash
git clone https://github.com/shaike1/webtop-skill.git
cd webtop-skill && ./install.sh
```

**הגדרות (.env):**
```bash
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

## ✅ **מה אתם מקבלים?**

- 📚 שיעורי בית - כל בוקר ב-6:00
- 📱 WhatsApp - הודעות אוטומטיות ויפות
- 📅 Google Calendar - סינכרון מלא
- 🏠 Home Assistant - אפשר להציג על מסכים
- 👨‍👩‍👧‍👦 ריבוי ילדים - תומך בכמה ילדים

---

## 🎯 **למי זה מתאים?**

- ✅ הורים עם ילדים בבית ספר
- ✅ משפחות עם כמה ילדים
- ✅ אנשים שרוצים להיות מאורגנים
- ✅ מי שרוצה לחסוך זמן

---

## 🆘 **צריכים עזרה?**

### **❌ לא עובד?**
- תבדקו את שם המשתמש והסיסמה
- תוודאו שה-DATA KEY נכון
- תנסו להתחבר דרך האתר

### **💓 עזרה נוספת:**
- 📖 **GitHub:** https://github.com/shaike1/webtop-skill
- 💬 **Discord:** Clawdbot Discord
- 📚 **תיעוד:** README.md

---

## 🌟 **מה אנשים אומרים?**

> "זה עובד מצוין! כל בוקר אני מקבל את שיעורי הבית של יובל ושירה ישר ב-WhatsApp. חוסכת לי כל כך הרבה זמן!" - שי, אבא ל-2 ילדים

> "לקח לי 3 דקות להתקין. עכשיו אני תמיד יודע מה יש לילדים מחר!" - עדי, אמא ל-3 ילדים

---

## 🎉 **סיכום**

**3 דרכים להתחיל:**

1. **הכי קל:** תשאלו את הבוט שלכם
2. **ידנית:** תתקינו לבד
3. **מתקדמים:** תוסיפו לבוט שלכם

**בחרו מה שמתאים לכם, ותהנו!** 🚀✨

---

**נוצר ב-❤️ עבור הורים ישראלים**

**תהנו מהשקט והארגון!** 🎓✨

---

## 📢 **שתפו עם חברים!**

אם זה עזר לכם, שתפו עם הורים אחרים! 💙

**WhatsApp Group:**
https://chat.whatsapp.com/[LINK]

**Facebook:**
https://facebook.com/groups/[LINK]

---

📱 **לוקי בוט | WEBTOP Israel**
🔗 **GitHub:** https://github.com/shaike1/webtop-skill
💙 **עובד מצוין!**

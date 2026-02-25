# הגדרת gogcli ל-OpenClaw

## שלב 1: יצירת OAuth Client ב-Google Cloud Console

1. לך ל: https://console.cloud.google.com/
2. צור פרויקט חדש או תשתמש בקיים
3. תוך "APIs & Services" → "Library"
4. חפש והפעל: "Google Calendar API"
5. חזור ל-"APIs & Services" → "OAuth consent screen"
   - בחר "External"
   - מלא את הפרטים (שם אפליקציה: "OpenClaw Assistant")
   - הוסף דוא"ל כפותחת דרך (Add user)
   - לחץ "Save and continue" על כל המסכים
6. תוך "APIs & Services" → "Credentials"
   - לחץ "Create Credentials" → "OAuth client ID"
   - Application type: **Desktop app**
   - Name: "OpenClaw gogcli"
   - **חשוב:** הוסף Redirect URI: `http://localhost:8085/callback`
   - לחץ "Create"
7. **לחץ על האייקון של הורדה** (↓) כדי להוריד את קובץ ה-JSON
8. שמור את הקובץ בתיקיית ההורדות (`~/Downloads/`)

---

## שלב 2: התקנת gogcli

### macOS:
```bash
brew install steipete/tap/gogcli
```

### Linux/אם אין brew:
```bash
git clone https://github.com/steipete/gogcli.git
cd gogcli
make
```

---

## שלב 3: הוספת החשבון (אימות)

**לרוץ זה במחשב שלך** (לא בשרת!):

```bash
# עבור לתיקיית gogcli
cd gogcli

# או אם התקנת דרך brew:
gog auth add YOUR_EMAIL@gmail.com ~/Downloads/client_secret_XXX.json
```

**מה יקרה:**
- דפדפן יפתח
- תתבקש להתחבר ל-Google
- תאשר גישה ל-Calendar (ועוד שירותים)
- אחרי אישור - תראה הודעת הצלחה

---

## שלב 4: שליחת ה-Token לשרת

אחרי שההגדרה הצליחה, תצטרך לשלוח לי את ה-token:

```bash
# הראה את כל החשבונות המאומתים
gog auth list

# העתק את ה-token credentials ושלח לי
```

הקבצים יהיו במיקום:
- macOS/Linux: `~/.config/gog/credentials.json`

---

## שלב 5: שליחה לשרת OpenClaw

תשלח לי את הקובץ:
```
~/.config/gog/credentials.json
```

או את תוכנו (אם קצר).

---

## צעד אל צעד - מה לעשות עכשיו:

1. ☐ גש ל-Google Cloud Console
2. ☐ צור OAuth Client ID (Desktop app)
3. ☐ הורד את קובץ ה-JSON
4. ☐ התקן gogcli
5. ☐ הרץ: `gog auth add YOUR_EMAIL@gmail.com ~/Downloads/client_secret_XXX.json`
6. ☐ תמשיך בדפדפן שיפתח - אשר גישה
7. ☐ הרץ: `gog auth list` (כדי לוודא)
8. ☐ שלח לי את ה-token

---

## קישורים:

- **Google Cloud Console:** https://console.cloud.google.com/
- **פרויקט:** צור חדש או השתמש בקיים
- **OAuth Consent Screen:** APIs & Services → OAuth consent screen
- **Credentials:** APIs & Services → Credentials → Create Credentials → OAuth client ID

---

## אם נתקעת:

1. תקן שבחרת **Desktop app** ולא Web app
2. תקן שהוספת את ה-Redirect URI: `http://localhost:8085/callback`
3. תקן שהפעלת את "Google Calendar API"

צלם צילומי מסך אם אתה נתקע! 📸

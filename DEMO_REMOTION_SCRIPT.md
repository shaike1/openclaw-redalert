# 🎬 סקריפט ליצירת סרטון הדגמה עם Remotion ו-Browser Agent

סקריפט זה יוצר סרטון הדגמה מקצועי שמראה את היכולות של ה-skill, כולל סימולציות של WhatsApp, Google Calendar, וממשק משתמש.

## 🛠️ דרישות מוקדמות

```bash
# התקנת Remotion
npm install remotion

# התקנת ספריות ל-browser automation
pip install playwright
playwright install

# התקנת FFmpeg (לעריכת וידאו)
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg
```

## 📁 מבנה הפרויקט

```
demo-remotion/
├── package.json
├── remotion.config.js
├── src/
│   ├── components/
│   │   ├── WhatsAppScene.js     # סצנת WhatsApp
│   │   ├── CalendarScene.js      # סצנת Google Calendar
│   │   ├── StudentsScene.js     # סצנת ניהול תלמידים
│   │   └── AnalyticsScene.js    # סצנת אנליטיקה
│   ├── scenes/
│   │   └── DemoSequence.js      # רצף ההדגמה
│   ├── hooks/
│   │   └── useWebtopData.js      # הוק לנתונים מה-skill
│   └── browser/
│       └── automation.js        # Browser Agent automation
└── public/
    └── assets/                  # אייקונים ותמונות
```

## 🎯 יצירת הסרטון

### 1. יצירת פרויקט Remotion

```bash
# יצירת פרויקט חדש
npx create-video-app demo-remotion
cd demo-remotion

# התקנת תלותים
npm install @remotion/cli @remotion/player
npm install playwright
playwright install chromium
```

### 2. קוד הסצנות

#### 🔧 `src/hooks/useWebtopData.js`
```javascript
import { useState, useEffect } from 'react';

export const useWebtopData = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    // שימוש בנתונים אמיתיים מה-skill או סימולציה
    const mockData = {
      students: [
        {
          name: "שירה",
          subjects: ["מתמטיקה", "עברית", "מדעים"],
          homework: [
            { subject: "מתמטיקה", content: "פרק 4 תרגילים 1-8", due: "2026-01-31" },
            { subject: "עברית", content: "סיפור 'בראשית'", due: "2026-02-01" }
          ]
        },
        {
          name: "יובל",
          subjects: ["אנגלית", "היסטוריה", "מתמטיקה"],
          homework: [
            { subject: "אנגלית", content: "Write about summer vacation", due: "2026-01-30" }
          ]
        }
      ],
      calendar: [
        { time: "08:00", subject: "מדעים", type: "lesson" },
        { time: "08:50", subject: "עברית", type: "lesson" },
        { time: "18:00", subject: "שיעורי בית", type: "homework" }
      ]
    };
    
    setData(mockData);
  }, []);
  
  return data;
};
```

#### 📱 `src/components/WhatsAppScene.js`
```javascript
import React, { useEffect, useRef } from 'react';
import { useWebtopData } from '../hooks/useWebtopData';

export const WhatsAppScene = ({ progress }) => {
  const { data } = useWebtopData();
  const messageRef = useRef(null);
  
  useEffect(() => {
    if (progress > 0.3 && messageRef.current) {
      messageRef.current.classList.add('show');
    }
  }, [progress]);
  
  if (!data) return null;
  
  return (
    <div className="whatsapp-scene">
      <div className="phone-mockup">
        <div className="whatsapp-header">
          <div className="group-info">
            <img src="group-icon.png" alt="Group" />
            <div>
              <div className="group-name">שיעורי בית - משפחה</div>
              <div className="group-time">לפני דקות</div>
            </div>
          </div>
        </div>
        
        <div ref={messageRef} className="message-container">
          <div className="message whatsapp">
            <div className="message-header">
              <span className="message-time">18:00</span>
            </div>
            <div className="message-content">
              <div className="message-title">
                🎓 *עדכוני שיעורי בית יומיים* 📚
              </div>
              <div className="message-body">
                <p>🏫 בית ספר: נעמי שמר</p>
                <p>🗓️ תאריך: 28/01/2026 (יום שלישי)</p>
                
                <div className="student-section">
                  <div className="student-title">👤 *שירה* 🎯</div>
                  <div className="homework-item">
                    <div className="homework-subject">📚 מתמטיקה</div>
                    <div className="homework-content">📝 תוכן: פרק 4 תרגילים 1-8 עמוד 52</div>
                    <div className="homework-date">📅 יעד: 31/01/2026</div>
                  </div>
                  
                  <div className="student-title">👤 *יובל* 🎯</div>
                  <div className="homework-item">
                    <div className="homework-subject">📚 אנגלית</div>
                    <div className="homework-content">📝 Write about your summer vacation</div>
                    <div className="homework-date">📅 יעד: 29/01/2026</div>
                  </div>
                </div>
                
                <div className="summary">
                  🎯 סה"כ מטלות: 2
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
```

#### 📅 `src/components/CalendarScene.js`
```javascript
import React from 'react';
import { useWebtopData } from '../hooks/useWebtopData';

export const CalendarScene = ({ progress }) => {
  const { data } = useWebtopData();
  
  if (!data) return null;
  
  return (
    <div className="calendar-scene">
      <div className="calendar-header">
        <h2>📅 לוח הזמנים המשפתי</h2>
        <div className="date-display">יום רביעי, 28/01/2026</div>
      </div>
      
      <div className="calendar-grid">
        {data.calendar.map((item, index) => (
          <div 
            key={index}
            className={`calendar-item ${item.type}`}
            style={{ opacity: Math.max(0, progress * 2 - index * 0.1) }}
          >
            <div className="time">{item.time}</div>
            <div className="subject">{item.subject}</div>
            <div className="type-icon">
              {item.type === 'lesson' ? '🎓' : '📚'}
            </div>
          </div>
        ))}
      </div>
      
      <div className="calendar-legend">
        <div className="legend-item">
          <div className="legend-color lesson"></div>
          <span>שיעורים</span>
        </div>
        <div className="legend-item">
          <div className="legend-color homework"></div>
          <span>שיעורי בית</span>
        </div>
      </div>
    </div>
  );
};
```

#### 🔧 `src/browser/automation.js`
```javascript
import { chromium } from 'playwright';

export async function createDemoVideo() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    // ניווט ל-Google Calendar
    await page.goto('https://calendar.google.com');
    
    // לכידת צילום מסך
    await page.screenshot({ 
      path: 'calendar-capture.png',
      fullPage: true 
    });
    
    // סימולציה של אינטראקציה
    await page.click('[data-testid="calendar-view-day"]');
    
    // לכידת וידאו
    await page.waitForTimeout(2000);
    await page.screenshot({ 
      path: 'calendar-day-view.png',
      fullPage: true 
    });
    
  } finally {
    await browser.close();
  }
}

// הפעלה אוטומטית
createDemoVideo().catch(console.error);
```

#### 🎬 `src/scenes/DemoSequence.js`
```javascript
import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  useVideoConfig,
} from 'remotion';
import { WhatsAppScene } from '../components/WhatsAppScene';
import { CalendarScene } from '../components/CalendarScene';

export const DemoSequence = ({ }) => {
  const { fps, durationInFrames } = useVideoConfig();
  
  return (
    <AbsoluteFill>
      {/* WhatsApp Scene (0-10 seconds) */}
      <WhatsAppScene progress={interpolate(frame, [0, 300], [0, 1])} />
      
      {/* Calendar Scene (10-20 seconds) */}
      <CalendarScene progress={interpolate(frame, [300, 600], [0, 1])} />
      
      {/* Students Management Scene (20-30 seconds) */}
      {/* Analytics Scene (30-40 seconds) */}
      
    </AbsoluteFill>
  );
};
```

### 3. יצירת הסרטון

```bash
# יצירת הווידאו
npx remotion render src/scenes/DemoSequence.js webtop-demo.mp4

# צפייה בפרויקט
npx remotion preview src/scenes/DemoSequence.js
```

## 🎥 תכולת הסרטון

### 1️⃣ **התראת WhatsApp** (0:00-0:10)
- סימולציה של מסך טלפון
- הודעת עדכון מסודרת עם אייקונים
- הצגת הפרדה בין שירה ליובל

### 2️⃣ **יומן Google Calendar** (0:10-0:20)
- הצגת לוח הזמנים עם צבעים
- מעבר בין תצוגות יום/שבוע/חודש
- הדגמת אירועים ושיעורי בית

### 3️⃣ **ניהול תלמידים** (0:20-0:30)
- מעבר בין שירה ליובל
- הצגת התקדמות של כל תלמיד
- סטטיסטיקות ויזואליות

### 4️⃣ **אנליטיקה** (0:30-0:40)
- גרפי התקדמות
- השוואה בין תלמידים
- דוחות חודשיים

## 🎯 עריכת הסוף

```bash
# חיבור פסקול
ffmpeg -i webtop-demo.mp4 -i background-music.mp3 -c:v copy -c:a aac final-demo.mp4

# הוספת כותרות
ffmpeg -i final-demo.mp4 -vf "drawtext=text=Webtop Homework Skill:x=(w-tw)/2:y=h-th-50:fontsize=24:fontcolor=white" final-with-title.mp4
```

## 📤 העלאה ליוטיוב/לינקדאין

```bash
# כיווץ לפורמט אופטימלי
ffmpeg -i final-with-title.mp4 -c:v libx264 -crf 23 -preset fast -c:a aac webtop-youtube.mp4

# העלאה ליוטיוב
youtube-upload --title="Webtop Homework Skill - הדגמה מלאה" --description="פתרון ממוחשב לניהול שיעורי בית" webtop-youtube.mp4
```

## 🎨 המלצות עיצוב

- **צבעים**: צבעים בהירים ומרצדים
- **פונט**: Inter (תמיכה בעברית)
- **אייקונים**: להשתמש ב- Font Awesome או סט אייקונים מודרני
- **אנימציות**: מעברים חלקים בין סצנות
- **פסקול**: מוזיקה קלילה ללא זכויות יוצרים

## 🚀 אופטימיזציה ללינקדאין

```bash
# יצירת גרסאות שונות
# גרסה מלאה (40 שניות) - לפוסט
# גרסה מקוצרת (15 שניות) - לתמונה נעה
# גרסה מינימלית (5 שניות) - לפרופיל
```

**הפרויקט מוכן ליצירת סרטון הדגמה מקצועי!** 🎬✨
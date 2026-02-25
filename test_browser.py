#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        print("🌐 פתיחת Chromium...")
        # נסה headless=False כדי לראות אם זה עוזר
        browser = await p.chromium.launch(
            headless=False,  # Full browser, not headless
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        
        page = await browser.new_page()
        
        try:
            print("🔗 גישה ל-Webtop...")
            await page.goto("https://webtop.smartschool.co.il", timeout=10000)
            print("✅ עמוד נטען!")
            
            # בדוק אם יש login form
            title = await page.title()
            print(f"   Title: {title}")
            
        except Exception as e:
            print(f"❌ שגיאה: {str(e)[:100]}")
        finally:
            await browser.close()

asyncio.run(test())

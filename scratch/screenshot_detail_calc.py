import sys
import os
from playwright.sync_api import sync_playwright

output_path = r"C:\Users\MUNNA\.gemini\antigravity\brain\7e18d46f-a07c-4bde-9cf7-ac324cac7605\detail_calc_verified.png"
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=chrome_path, headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 1100})
    page.goto("http://127.0.0.1:8055", wait_until="networkidle")
    
    # Click on the Detail Calculations tab
    page.evaluate("if (typeof switchTab === 'function') switchTab('sheet2-calc'); else if (typeof renderSheet2Calc === 'function') renderSheet2Calc();")
    
    page.wait_for_timeout(1000)
    page.screenshot(path=output_path, full_page=False)
    browser.close()

print(f"Screenshot saved to {output_path}")

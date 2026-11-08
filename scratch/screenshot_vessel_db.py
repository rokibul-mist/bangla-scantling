import os
from playwright.sync_api import sync_playwright

output_dir = r"C:\Users\MUNNA\.gemini\antigravity\brain\7e18d46f-a07c-4bde-9cf7-ac324cac7605"
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=chrome_path, headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 1050})
    page.goto("http://127.0.0.1:8055", wait_until="networkidle")

    # 1. Switch to Vessel Database tab
    page.evaluate("if (window.navigation) window.navigation.switchTab('vessel-db'); else if (typeof renderVesselDb === 'function') renderVesselDb();")
    page.wait_for_timeout(1000)
    page.screenshot(path=os.path.join(output_dir, "vessel_db_view.png"), full_page=False)
    print("Saved vessel_db_view.png")

    # 2. Open Save Vessel Modal
    page.evaluate("if (typeof openSaveVesselModal === 'function') openSaveVesselModal();")
    page.wait_for_timeout(500)
    page.screenshot(path=os.path.join(output_dir, "save_vessel_modal.png"), full_page=False)
    print("Saved save_vessel_modal.png")

    browser.close()

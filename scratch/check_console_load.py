from playwright.sync_api import sync_playwright

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=chrome_path, headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 1050})
    
    page.on("console", lambda msg: print(f"PAGE LOG: {msg.text}"))
    page.goto("http://127.0.0.1:8055", wait_until="networkidle")

    page.evaluate("if (typeof switchTab === 'function') switchTab('vessel-db');")
    page.wait_for_timeout(1000)

    load_btn = page.locator("button:has-text('Open in Calculator')").first
    load_btn.click()
    page.wait_for_timeout(1500)

    # Check which tab-content has hidden class
    dash_hidden = page.evaluate("document.getElementById('tab-content-dashboard').classList.contains('hidden')")
    db_hidden = page.evaluate("document.getElementById('tab-content-vessel-db').classList.contains('hidden')")
    print(f"tab-content-dashboard hidden: {dash_hidden}, tab-content-vessel-db hidden: {db_hidden}")

    page.screenshot(path=r"C:\Users\MUNNA\.gemini\antigravity\brain\7e18d46f-a07c-4bde-9cf7-ac324cac7605\loaded_dashboard_verified.png")
    browser.close()

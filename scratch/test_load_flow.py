from playwright.sync_api import sync_playwright

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=chrome_path, headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 1050})
    page.goto("http://127.0.0.1:8055", wait_until="networkidle")

    # 1. Switch to Vessel Database
    page.evaluate("if (window.navigation) window.navigation.switchTab('vessel-db');")
    page.wait_for_timeout(1000)

    # 2. Click "Open in Calculator" on first vessel
    load_btn = page.locator("button:has-text('Open in Calculator')").first
    load_btn.click()
    page.wait_for_timeout(1000)

    # 3. Verify top header
    header_text = page.locator("#top-vessel-name").inner_text()
    print("Top header after loading:", header_text)

    # 4. Check active tab
    active_tab = page.locator(".nav-tab.active").first.inner_text()
    print("Active tab after loading:", active_tab)

    # 5. Take screenshot of dashboard after loading
    page.screenshot(path=r"C:\Users\MUNNA\.gemini\antigravity\brain\7e18d46f-a07c-4bde-9cf7-ac324cac7605\loaded_vessel_dashboard.png", full_page=False)
    print("Saved loaded_vessel_dashboard.png")

    browser.close()

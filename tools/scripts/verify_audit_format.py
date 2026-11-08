import sys, json, urllib.request
from playwright.sync_api import sync_playwright

def verify_audit_format():
    print("=== Testing Statutory Audit Format (Web UI & PDF) ===")

    # 1. Test Application Form PDF endpoint
    print("Testing POST /api/export-pdf/application-form...")
    with open('app/saved_state.json', 'r', encoding='utf-8') as f:
        state = json.load(f)
    req = urllib.request.Request(
        "http://127.0.0.1:8055/api/export-pdf/application-form",
        data=json.dumps(state).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        pdf_data = resp.read()
        print(f"[PASS] PDF generated successfully: {len(pdf_data):,} bytes")

    # 2. Test Browser UI with Playwright
    console_errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 950})

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        print("Navigating to http://127.0.0.1:8055...")
        page.goto("http://127.0.0.1:8055", wait_until="networkidle")

        # Click on Application Form Tab
        print("Clicking Application Form tab...")
        page.click('button.nav-tab[data-tab="application-form"]')
        page.wait_for_timeout(1000)

        # Select Page 10 (Stem item)
        print("Selecting Page 10 in dropdown...")
        page.select_option("#app-form-page-select", "10")
        page.wait_for_timeout(800)

        # Check for Audit Table presence
        table_html = page.inner_html("#tab-content-application-form")
        assert "For office use only" in table_html, "Missing 'For office use only' header in audit table"
        assert "Complied with" in table_html, "Missing 'Complied with' header in audit table"
        assert "16. Stem" in table_html, "Missing '16. Stem' item row in audit table"
        assert "(rule-14)" in table_html, "Missing '(rule-14)' citation in audit table"
        assert "Requirement as per table - 7" in table_html, "Missing requirement text"
        assert "As per rule" in table_html, "Missing 'As per rule' label"
        assert "13.19" in table_html, "Missing rule value 13.19"
        assert "14" in table_html, "Missing drawing value 14"

        print("[PASS] Audit Table content on Page 10 verified successfully!")

        # Screenshot the Application Form Page 10
        out_png = r"C:\Users\MUNNA\.gemini\antigravity\brain\7e18d46f-a07c-4bde-9cf7-ac324cac7605\final_audit_format_web.png"
        page.screenshot(path=out_png)
        print(f"[PASS] Full web view screenshot saved to: {out_png}")

        # Crop the table specifically
        table_elem = page.locator("#tab-content-application-form table")
        if table_elem.count() > 0:
            table_crop = r"C:\Users\MUNNA\.gemini\antigravity\brain\7e18d46f-a07c-4bde-9cf7-ac324cac7605\final_audit_format_table_crop.png"
            table_elem.first.screenshot(path=table_crop)
            print(f"[PASS] Table crop screenshot saved to: {table_crop}")

        browser.close()

    if console_errors:
        print(f"[WARN] Console errors detected: {console_errors}")
    else:
        print("[PASS] 0 Console Errors encountered!")

    print("\nALL STATUTORY AUDIT FORMAT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_audit_format()

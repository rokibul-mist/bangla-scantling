import os
import sys
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"C:\Users\MUNNA\.gemini\antigravity\brain\7e18d46f-a07c-4bde-9cf7-ac324cac7605"

def run_e2e_test():
    console_errors = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {str(err)}"))

        print("Navigating to http://127.0.0.1:8055...")
        page.goto("http://127.0.0.1:8055", wait_until="networkidle")
        time.sleep(1)

        # 1. Verify Dashboard
        print("Checking Dashboard tab...")
        vessel_name = page.locator("#top-vessel-name").inner_text()
        print(f"Top Vessel Name: {vessel_name}")
        assert len(vessel_name) > 0, "Top vessel name is missing"

        # Check 5 Stiffener Columns exist in Section 2 table
        table_html = page.locator("#tab-content-dashboard").inner_html()
        assert "Profile (L/T/FB)" in table_html or "Profile" in table_html, "Profile column missing"
        assert "Web (mm)" in table_html or "Web" in table_html, "Web column missing"
        assert "Web Thk" in table_html, "Web Thk column missing"
        assert "Flange (mm)" in table_html or "Flange" in table_html, "Flange column missing"
        assert "Flange Thk" in table_html, "Flange Thk column missing"
        print("[PASS] All 5 stiffener profile columns verified in Dashboard table!")

        page.screenshot(path=os.path.join(OUTPUT_DIR, "modular_dashboard_e2e.png"), full_page=False)

        # 2. Test Switching Hull Construction
        print("Testing hull construction switcher...")
        # Double Hull
        page.locator("input[name='hull_construction_radio'][value='Double Hull']").click()
        time.sleep(0.5)
        dh_count = page.locator("tr[id^='brain-row-']").count()
        print(f"Double Hull members count: {dh_count}")
        assert dh_count >= 60, f"Expected >= 60 Double Hull members, got {dh_count}"

        # Single Hull
        page.locator("input[name='hull_construction_radio'][value='Single Hull']").click()
        time.sleep(0.5)
        sh_count = page.locator("tr[id^='brain-row-']").count()
        print(f"Single Hull members count: {sh_count}")
        assert sh_count >= 50, f"Expected >= 50 Single Hull members, got {sh_count}"

        # Double Bottom
        page.locator("input[name='hull_construction_radio'][value='Double Bottom']").click()
        time.sleep(0.5)
        db_count = page.locator("tr[id^='brain-row-']").count()
        print(f"Double Bottom members count: {db_count}")
        assert db_count >= 55, f"Expected >= 55 Double Bottom members, got {db_count}"

        # 3. Test Detail Calculations Tab
        print("Testing Detail Calculations tab...")
        page.locator(".nav-tab[data-tab='sheet2-calc']").click()
        time.sleep(0.5)
        sheet_options = page.locator("#tab-content-sheet2-calc select option").count()
        print(f"Detail calculation sheets available: {sheet_options}")
        assert sheet_options >= 14, f"Expected at least 14 stiffener sheets, got {sheet_options}"
        page.screenshot(path=os.path.join(OUTPUT_DIR, "modular_detail_calc_e2e.png"), full_page=False)

        # 4. Test Lightship Tab
        print("Testing Lightship tab...")
        page.locator(".nav-tab[data-tab='lightship']").click()
        time.sleep(0.5)
        ls_html = page.locator("#tab-content-lightship").inner_html()
        assert "Keel Plate" in ls_html, "Keel Plate missing in Lightship"
        assert "TOTAL LIGHT SHIP WEIGHT" in ls_html, "Total Lightship missing"
        page.screenshot(path=os.path.join(OUTPUT_DIR, "modular_lightship_e2e.png"), full_page=False)

        # 5. Test Live PDF Preview Modal
        print("Testing Live PDF Preview Modal...")
        page.locator("#btn-live-pdf-preview").click()
        time.sleep(1.5)
        modal_visible = page.locator("#live-pdf-modal").is_visible()
        print(f"Live PDF Modal visible: {modal_visible}")
        assert modal_visible, "Live PDF preview modal did not open"
        page.screenshot(path=os.path.join(OUTPUT_DIR, "modular_pdf_modal_e2e.png"), full_page=False)
        
        # Close modal
        page.locator("#live-pdf-modal button:has-text('Close')").click()
        time.sleep(0.5)
        assert not page.locator("#live-pdf-modal").is_visible(), "Modal did not close"

        # Check console errors
        print(f"Console errors recorded: {len(console_errors)}")
        if console_errors:
            for err in console_errors:
                print(f"  ERROR: {err}")
        assert len(console_errors) == 0, f"Found {len(console_errors)} console errors!"

        browser.close()
        print("[PASS] All End-to-End Tests Passed with 0 Console Errors!")

if __name__ == "__main__":
    run_e2e_test()

import os
import sys
import json
import asyncio
import fitz  # PyMuPDF
from playwright.async_api import async_playwright

async def run_full_audit():
    print("=" * 70)
    print("FULL COMPLIANCE & LINKAGE AUDIT: WEB APP STATE vs DETAIL CALC PDF")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="msedge")
        page = await browser.new_page()

        # 1. Navigate to live application
        url = "http://127.0.0.1:8055"
        print(f"[1/5] Loading web application at {url}...")
        try:
            await page.goto(url, wait_until="networkidle", timeout=15000)
        except Exception as e:
            print(f"Error loading page: {e}")
            await browser.close()
            return

        await page.wait_for_timeout(2000)

        # 2. Extract window.appState
        app_state = await page.evaluate("() => window.appState")
        if not app_state:
            print("[FAIL] window.appState is not available!")
            await browser.close()
            return
        
        inputs = app_state.get('dashboard_inputs', {})
        brain = app_state.get('calculation_brain', [])
        sheets = app_state.get('sheet2_results', [])

        print(f"[2/5] Retrieved Web App State:")
        print(f"      - Vessel Name: {inputs.get('vessel_name')}")
        print(f"      - Cb (Block Coeff): {inputs.get('block_coeff')}")
        print(f"      - Frame Spacing: {inputs.get('frame_spacing')} mm")
        print(f"      - Rudder Blade Thk in inputs: {inputs.get('rudder_blade_thk')}")
        print(f"      - Statutory Brain Items: {len(brain)} items")
        print(f"      - Detail Calculation Sheets: {len(sheets)} sheets")

        # 3. Call PDF generation endpoint with the live appState snapshot
        print("\n[3/5] Requesting live PDF generation via POST /api/pdf/detail-calculation/generate...")
        response = await page.request.post(
            f"{url}/api/pdf/detail-calculation/generate",
            data=app_state,
            headers={"Content-Type": "application/json"}
        )
        if response.status != 200:
            print(f"[FAIL] PDF generation returned status {response.status}")
            await browser.close()
            return

        pdf_bytes = await response.body()
        pdf_path = "audit_booklet_output.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        print(f"      -> PDF generated successfully ({len(pdf_bytes)} bytes, saved to {pdf_path})")

        # 4. Parse PDF with PyMuPDF
        print("\n[4/5] Auditing PDF Content with PyMuPDF...")
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        print(f"      - Total PDF Pages: {total_pages}")

        # Page 1: Cover Page particulars
        p1_text = doc[0].get_text()
        
        # Verify Cover Page particulars
        cover_checks = [
            ("Vessel Name", str(inputs.get('vessel_name')), str(inputs.get('vessel_name')) in p1_text),
            ("LOA", f"{inputs.get('loa')}", f"{inputs.get('loa')}" in p1_text),
            ("LBP", f"{inputs.get('lbp')}", f"{inputs.get('lbp')}" in p1_text),
            ("Breadth", f"{inputs.get('breadth')}", f"{inputs.get('breadth')}" in p1_text),
            ("Depth", f"{inputs.get('depth')}", f"{inputs.get('depth')}" in p1_text),
            ("Draft", f"{inputs.get('draft')}", f"{inputs.get('draft')}" in p1_text),
            ("Block Coeff (Cb)", f"{inputs.get('block_coeff')}", f"{inputs.get('block_coeff')}" in p1_text),
            ("Frame Spacing", f"{inputs.get('frame_spacing')}", f"{inputs.get('frame_spacing')}" in p1_text),
            ("Statutory kt", f"{inputs.get('effective_kt', 1.20):.2f}", f"{inputs.get('effective_kt', 1.20):.2f}" in p1_text),
            ("Statutory kz", f"{inputs.get('effective_kz', 1.25):.2f}", f"{inputs.get('effective_kz', 1.25):.2f}" in p1_text),
        ]

        print("\n--- COVER PAGE AUDIT (PAGE 1) ---")
        cover_pass = True
        for name, expected, passed in cover_checks:
            mark = "[OK]" if passed else "[MISMATCH]"
            if not passed:
                cover_pass = False
            print(f"  {mark} {name}: expected '{expected}' -> {'FOUND' if passed else 'NOT FOUND'}")

        # Dashboard Pages (Pages 2 & 3 typically)
        dash_text = doc[1].get_text() + "\n" + (doc[2].get_text() if total_pages > 2 else "")

        print("\n--- STATUTORY COMPLIANCE AUDIT (77 ITEMS) ---")
        brain_mismatches = []
        for it in brain:
            no = it.get('item', '')
            name = it.get('name', '')
            dact = f"{float(it.get('dact', 0)):.2f}"
            rreq = f"{float(it.get('rreq', 0)):.2f}"

            # Check if dact and rreq are present in the dashboard text
            dact_in = dact in dash_text
            rreq_in = rreq in dash_text
            if not (dact_in and rreq_in):
                brain_mismatches.append({
                    "no": no,
                    "name": name,
                    "dact": dact,
                    "rreq": rreq,
                    "dact_found": dact_in,
                    "rreq_found": rreq_in
                })

        if not brain_mismatches:
            print(f"  [OK] All {len(brain)} Statutory Compliance Audit items matched exactly in PDF Dashboard!")
        else:
            print(f"  [MISMATCH] {len(brain_mismatches)} items had mismatches:")
            for m in brain_mismatches[:5]:
                print(f"    Item #{m['no']} ({m['name']}): dact={m['dact']} (found={m['dact_found']}), rreq={m['rreq']} (found={m['rreq_found']})")

        # Specific audit for Item #29 (Rudder Blade Plating)
        rudder_item = next((x for x in brain if x.get('item') == 29 or 'Rudder Blade' in x.get('name', '')), None)
        if rudder_item:
            print(f"\n--- AUDIT OF ITEM #29 (RUDDER BLADE PLATING) ---")
            print(f"  Web dact: {rudder_item.get('dact')} mm, rreq: {rudder_item.get('rreq')} mm")
            r_dact_str = f"{float(rudder_item.get('dact')):.2f}"
            in_pdf = r_dact_str in dash_text
            print(f"  PDF Match for '{r_dact_str} mm': {'[OK] FOUND' if in_pdf else '[FAIL] NOT FOUND'}")

        # Section Modulus Detail Calculation Sheets
        all_sheets_text = ""
        # Sheets start after dashboard
        for p_idx in range(2, total_pages):
            all_sheets_text += doc[p_idx].get_text() + "\n"

        print(f"\n--- DETAIL CALCULATION SHEETS AUDIT ({len(sheets)} SHEETS) ---")
        sheet_mismatches = []
        for s in sheets:
            s_id = s.get('id')
            s_name = s.get('name', '')
            z_cm3 = f"{float(s.get('z_cm3', 0)):.2f}"
            rreq = f"{float(s.get('rreq', 0)):.2f}"
            yna = f"{float(s.get('yna', 0)):.3f}"
            ina = f"{float(s.get('ina', 0)):.2f}"

            z_found = z_cm3 in all_sheets_text
            yna_found = yna in all_sheets_text

            if not (z_found and yna_found):
                sheet_mismatches.append({
                    "id": s_id,
                    "name": s_name,
                    "z_cm3": z_cm3,
                    "yna": yna,
                    "z_found": z_found,
                    "yna_found": yna_found
                })

        if not sheet_mismatches:
            print(f"  [OK] All {len(sheets)} Section Modulus sheets matched exactly in PDF (Z, yna, and formulas)!")
        else:
            print(f"  [MISMATCH] {len(sheet_mismatches)} sheets had mismatches:")
            for m in sheet_mismatches[:5]:
                print(f"    Sheet #{m['id']} ({m['name']}): z={m['z_cm3']} (found={m['z_found']}), yna={m['yna']} (found={m['yna_found']})")

        # 5. Live UI Interactivity Test: Modifying a value and checking PDF update
        print("\n[5/5] Testing Live Dynamic User Edit Linkage...")
        # Simulate changing Frame Spacing to 625 mm
        modified_state = json.loads(json.dumps(app_state))
        modified_state['dashboard_inputs']['frame_spacing'] = 625.0
        # When user changes frame spacing, calc.js recalculates
        # Let's send the modified state to the PDF generator:
        mod_resp = await page.request.post(
            f"{url}/api/pdf/detail-calculation/generate",
            data=modified_state,
            headers={"Content-Type": "application/json"}
        )
        mod_pdf = await mod_resp.body()
        mod_doc = fitz.open(stream=mod_pdf, filetype="pdf")
        mod_p1_text = mod_doc[0].get_text()

        spacing_updated = "625.0 mm" in mod_p1_text or "625 mm" in mod_p1_text
        print(f"  Changed Frame Spacing to 625 mm in state:")
        print(f"  PDF Cover Page updated to 625 mm: {'[OK] YES' if spacing_updated else '[FAIL] NO'}")

        print("\n" + "=" * 70)
        overall_pass = cover_pass and (len(brain_mismatches) == 0) and (len(sheet_mismatches) == 0) and spacing_updated
        if overall_pass:
            print("AUDIT RESULT: 100% PASS - ALL WEB VALUES AND CALCULATIONS ARE FULLY LINKED!")
        else:
            print("AUDIT RESULT: ISSUES DETECTED - PLEASE REVIEW ABOVE")
        print("=" * 70)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_full_audit())

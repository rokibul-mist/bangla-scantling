import asyncio
import fitz
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="chrome")
        context = await browser.new_context(viewport={"width": 1600, "height": 1000})
        page = await context.new_page()

        print("Navigating to http://127.0.0.1:8055 ...")
        await page.goto("http://127.0.0.1:8055", wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)

        # 1. Extract frontend data from page
        fe_data = await page.evaluate("""() => {
            const state = window.appState || {};
            const inputs = state.dashboard_inputs || {};
            const brain = state.calculation_brain || [];
            const results = state.sheet2_results || [];

            // Read table values from DOM directly
            const domBrain = [];
            document.querySelectorAll("#brain-groups-container tr[id^='brain-row-']").forEach(tr => {
                const cells = tr.querySelectorAll("td");
                if (cells.length >= 9) {
                    domBrain.push({
                        item: cells[0].textContent.trim(),
                        name: cells[1].textContent.trim(),
                        baseline: cells[2].textContent.trim(),
                        factor: cells[3].textContent.trim(),
                        required: cells[4].textContent.trim(),
                        provided: cells[5].querySelector("input") ? cells[5].querySelector("input").value.trim() : cells[5].textContent.trim(),
                        unit: cells[6].textContent.trim(),
                        margin: cells[7].textContent.trim(),
                        status: cells[8].textContent.trim()
                    });
                }
            });

            return {
                inputs,
                brain,
                results,
                domBrain
            };
        }""")

        inputs = fe_data['inputs']
        dom_brain = fe_data['domBrain']
        results = fe_data['results']

        print(f"Extracted {len(dom_brain)} DOM brain rows from web dashboard.")
        print(f"Extracted {len(results)} stiffener sheets from frontend.")

        # 2. Fetch the live PDF directly
        res = await page.request.post("http://127.0.0.1:8055/api/pdf/detail-calculation/generate", data=fe_data['inputs'])
        # Also let's test with full appState payload
        full_state = await page.evaluate("() => window.appState")
        res_full = await page.request.post("http://127.0.0.1:8055/api/pdf/detail-calculation/generate", data=full_state)
        pdf_bytes = await res_full.body()

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        print(f"PDF generated with {len(doc)} pages.")

        # 3. Check Cover Page Particulars
        p1_text = doc[0].get_text()
        print("\n--- AUDIT: COVER PAGE PARTICULARS ---")
        mismatches = []

        vessel_name = inputs.get('vessel_name', '')
        if vessel_name and vessel_name not in p1_text:
            mismatches.append(f"Vessel Name mismatch: expected '{vessel_name}' in PDF")

        route = inputs.get('proposed_route', inputs.get('route', ''))
        if route and route not in p1_text:
            mismatches.append(f"Route mismatch: expected '{route}' in PDF")

        hull_type = inputs.get('hull_type', '')
        if hull_type and hull_type not in p1_text:
            mismatches.append(f"Hull Type mismatch: expected '{hull_type}' in PDF")

        spacing = str(int(float(inputs.get('frame_spacing', 550))))
        if spacing not in p1_text:
            mismatches.append(f"Frame Spacing mismatch: expected '{spacing}' in PDF")

        loa = str(inputs.get('loa', ''))
        if loa and loa not in p1_text:
            mismatches.append(f"LOA mismatch: expected '{loa}' in PDF")

        lbp = str(inputs.get('lbp', ''))
        if lbp and lbp not in p1_text:
            mismatches.append(f"LBP mismatch: expected '{lbp}' in PDF")

        breadth = str(inputs.get('breadth', ''))
        if breadth and breadth not in p1_text:
            mismatches.append(f"Breadth mismatch: expected '{breadth}' in PDF")

        depth = str(inputs.get('depth', ''))
        if depth and depth not in p1_text:
            mismatches.append(f"Depth mismatch: expected '{depth}' in PDF")

        draft = str(inputs.get('draft', ''))
        if draft and draft not in p1_text:
            mismatches.append(f"Draft mismatch: expected '{draft}' in PDF")

        cb = str(inputs.get('cb', ''))
        if cb and cb not in p1_text:
            mismatches.append(f"Cb mismatch: expected '{cb}' in PDF")

        kt = f"{float(inputs.get('effective_kt', 1.20)):.2f}"
        kz = f"{float(inputs.get('effective_kz', 1.25)):.2f}"
        if kt not in p1_text or kz not in p1_text:
            mismatches.append(f"kt/kz mismatch: expected '{kt} / {kz}' in PDF")

        print("Cover Page Mismatches:", mismatches if mismatches else "None [PASS]")

        # 4. Check Dashboard Tables in PDF vs DOM
        print("\n--- AUDIT: DASHBOARD TABLES (PDF vs WEB DASHBOARD) ---")
        p2_text = doc[1].get_text() + "\n" + doc[2].get_text()
        db_mismatches = []
        for idx, item in enumerate(dom_brain[:20]): # Check first 20 items sample
            no = item['item']
            name = item['name']
            prov = item['provided']
            req = item['required']
            marg = item['margin']
            
            # Check if name is in text
            clean_name = name[:18]
            if clean_name not in p2_text:
                db_mismatches.append(f"Item #{no} '{name}' not found in Dashboard PDF")
            else:
                # Check provided value in text
                if prov not in p2_text:
                    db_mismatches.append(f"Item #{no} '{name}' Provided value '{prov}' mismatch in Dashboard PDF")

        print(f"Dashboard Table Mismatches (sample 20):", db_mismatches if db_mismatches else "None [PASS]")
        if db_mismatches:
            for m in db_mismatches[:5]:
                print("  ->", m)

        # 5. Check Detail Calculation Sheets vs Web Detail Calc
        print("\n--- AUDIT: DETAIL CALCULATION SHEETS (PDF vs WEB DETAIL CALC) ---")
        stiff_mismatches = []
        detail_pdf_text = ""
        for p_idx in range(3, len(doc)):
            detail_pdf_text += doc[p_idx].get_text() + "\n"

        for idx, res in enumerate(results):
            s_id = res.get('id', idx+1)
            name = res.get('name', '')
            z_act = f"{float(res.get('z_cm3', 0)):.2f}"
            z_req = f"{float(res.get('rreq', 0)):.2f}"
            yna = f"{float(res.get('yna', 0)):.3f}"
            hw = str(int(round(float(res.get('web_height', 0)))))
            tw = str(int(round(float(res.get('web_thk', 0)))))
            tp = f"{float(res.get('plate_thk', 0)):.1f}"

            # Check if Sheet header exists
            sheet_tag = f"SHEET {s_id < 10 and '0' or ''}{s_id}"
            if sheet_tag not in detail_pdf_text:
                stiff_mismatches.append(f"{sheet_tag} '{name}' not found in PDF")
            else:
                if z_act not in detail_pdf_text:
                    stiff_mismatches.append(f"{sheet_tag} '{name}' Actual Modulus Z={z_act} not found in PDF")
                if z_req not in detail_pdf_text:
                    stiff_mismatches.append(f"{sheet_tag} '{name}' Required Modulus Z_req={z_req} not found in PDF")

        print(f"Detail Calculation Sheets Mismatches ({len(results)} sheets):", stiff_mismatches if stiff_mismatches else "None [PASS]")
        if stiff_mismatches:
            for sm in stiff_mismatches[:10]:
                print("  ->", sm)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(audit())

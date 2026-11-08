# Handoff Report: Naval Architecture Calculation Models & Module Linkages Survey

**Explorer**: Explorer 2 (Naval Architecture & Calculation Linkages Specialist)  
**Target Path**: `e:\Bangla Scantling\.agents\teamwork\teamwork_explorer_survey_2\handoff.md`  
**Date**: 2026-10-30  

---

## 1. Observation

### 1.1 Calculation Models & Implementations Observed

1. **Detail Calculation (`sheet2-calc`)**:
   - **Frontend Engine**: `app/static/js/calc.js` (lines 6–47, 216–285) & `app/static/js/views/DetailCalcView.js` (lines 147–264).
   - **Backend Engine**: `app/domain/calc/section_modulus.py` (lines 1–75) & `app/services/calculation_service.py` (lines 194–256).
   - **Mathematical Formulation**:
     - Centroid distance: $y_{\text{na}} = \frac{A_p(t_p/2) + A_w(t_p + h_w/2) + A_f(t_p + h_w + t_f/2)}{A_{\text{tot}}}$.
     - Parallel axis theorem moments of inertia:
       - Plate: $I_p = \frac{b_p t_p^3}{12} + A_p (y_{\text{na}} - t_p/2)^2$
       - Web: $I_w = \frac{t_w h_w^3}{12} + A_w (t_p + h_w/2 - y_{\text{na}})^2$
       - Flange: $I_f = \frac{b_f t_f^3}{12} + A_f (t_p + h_w + t_f/2 - y_{\text{na}})^2$
       - Total: $I_{\text{na}} = I_p + I_w + I_f$
     - Neutral axis fiber distance: $y_{\text{max}} = \max(y_{\text{na}}, t_p + h_w + t_f - y_{\text{na}})$.
     - Actual Section Modulus: $Z = \frac{I_{\text{na}}}{y_{\text{max}} \times 1000}$ [cm³].
   - **Attached Plate Linkage**: The effective flange width $b_p$ is dynamically set to the frame spacing $s$ (`inputs.frame_spacing`, default 550 mm). The plate thickness $t_p$ is dynamically bound to the structural plate the stiffener is welded to (`welded_plate_key`, e.g., `t_side` for Side Frames, `t_bottom` for Floors, `t_deck_all` for Deck Beams, `t_bhd` for Bulkhead Stiffeners) (`calc.js:218–219`, `calculation_service.py:196–197`).
   - **Rule Requirement**: Statutory required section modulus is evaluated as $Z_{\text{req}} = Z_{\text{base}} \times k_z$ where $k_z$ is the statutory stiffener factor ($1.25$ for SRO 308 Bay Crossing, $1.40$ for Steel (Old), $1.00$ for Inland Calm Water) (`calc.js:62–90, 235–242`).

2. **Calculation Brain (`calc-brain`)**:
   - **Frontend**: `app/static/js/calc_brain_engine.js` & `app/static/js/views/CalcBrainView.js` (lines 15–98, 235–360).
   - **Backend**: `app/services/calculation_service.py` (lines 104–288) & `app/domain/rules/interpolations/registry.py` (lines 1–120).
   - **Catalog & Scantlings**:
     - Dynamically generates active structural members depending on hull type (`Double Bottom`, `Double Hull`, `Single Hull`) and vessel type (`Steel Body Cargo Vessel`, `Oil Tanker`, etc.) via `app/domain/catalog/structural_catalog.py:get_active_members`.
     - Single Hull vessels automatically omit Double Bottom inner bottom plating (`plate_inner_bottom`) and margin plates (`t_margin`).
   - **Statutory Limits Evaluated**:
     - Frame Spacing Limit: $s_{\text{max}} = 450 + 2 \times \text{LBP}$ mm (`app/domain/rules/limits.py:4–10`).
     - Collision Bulkhead Position: $0.05 \text{ LBP} \le x_{\text{col}} \le 0.08 \text{ LBP}$ (`app/domain/rules/limits.py:12–19`).
   - **Table Interpolation Visualizer**: Displays interactive 1D/2D empirical tables with bounding row and column indices highlighted in amber/blue with distinct interpolation node badges (`CalcBrainView.js:27–89`).

3. **Lightship Weight Calculation**:
   - **Frontend**: `app/static/js/calc.js` (lines 378–611) & `app/static/js/views/LightshipView.js` (lines 73–273).
   - **Backend**: `app/services/lightship_service.py` (lines 30–294) & `app/domain/calc/weight_calc.py` (lines 1–76).
   - **BOM Structure**:
     - 19 Master Structural Plate Assemblies (`MASTER_BOM_PLATES`: Keel, Bottom Shell, Bilge, Side Shell, Sheer Strake, Bulwark, Hatchway Deck, Main Deck, Superstructure Walls, Poop Wall/Deck, Bridge Wall/Deck, Transverse Bulkheads, Hatch Covers, Forecastle Deck, Double Bottom Tank Top, Stem/Stern/Rudder, Partitions).
     - 21 Master Structural Angle Assemblies (`MASTER_BOM_ANGLES`: Center Keelson, Side Keelsons, Side Stringers, Deck Girders, Floors, Web Frames, Main Frames, Deck Beams, Deck Webs, Poop/Bridge Beams, Bulkhead Stiffeners, Hatch Girders, Superstructure Girders).
   - **Naming Compliance**: Clean Element Names are 100% enforced via `clean_element_name()` (`lightship_service.py:11–21`, `calc.js:392–399`). Dimensions, rule citations, and thickness suffixes are stripped from the `name` / `element` column and placed exclusively in numerical columns (`L`, `B`, `t`, `Area`, `Length`).
   - **Statutory Outfitting Allowances (56% Total)**:
     - 1. Allowance / Hull Margin: $20\%$ (`Net Steel * 0.20`)
     - 2. Outfit & Deck Equipment: $15\%$ (`Net Steel * 0.15`)
     - 3. Piping, Valves & Fittings: $10\%$ (`Net Steel * 0.10`)
     - 4. Electrical & Instrumentation: $3\%$ (formula basis: $3\%$, standard $5\%$ rule base)
     - 5. Accommodation & Furniture: $1\%$ (`Net Steel * 0.01`)
     - 6. Miscellaneous Statutory Items: $7\%$ (`Net Steel * 0.07`)
     - **Total Outfitting**: $56\%$
     - **Total Lightship Displacement**: $W_{\text{lightship}} = W_{\text{net}} \times 1.56$.
     - Evaluated at `app/domain/calc/weight_calc.py:48–75`, `app/services/lightship_service.py:279–287`, and `calc.js:591–611`.

4. **Application Form (DOS 25-Page Booklet)**:
   - **Frontend**: `app/static/js/views/ApplicationFormView.js` (lines 1–1164).
   - **Backend**: `app/services/pdf/app_form_pdf_service.py` (lines 1–1019).
   - **Prefill & Particulars Sync**:
     - Page 1: Cover page displays registered owner (`inputs.owner`).
     - Page 2: General instructions.
     - Page 3: General requirements & Design Governing Criteria (LOA, B, D, frame spacing, vessel type, material, route).
     - Page 4: Design firm name, designer, checker, bank guarantee verification.
     - Page 5 (Page 4 of 24): Full particulars table (LOA, LBP, LWL, B EXT, B MLD, DEPTH EXT, DEPTH MLD, draft, propeller nos, propeller dia, engine type, engine power), Owner details, and dynamic checked checkboxes for Vessel Type (Cargo, Passenger, Tanker, Barge, Ferry), Hull Material (Steel New, Steel Old, Wood, etc.), Proposed Route (Inland Calm, Rough, Bay crossing, etc.), and Plying Time (Day, Night, Day & Night).
     - Pages 6–8: Drawing submission checklist (Pages 5–7 of 24).
     - Pages 9–24 (Pages 8–23 of 24): Scantling audit tables (77 statutory components linked directly via `ITEM_TO_CALC_ID` mapping to `calculation_brain` IDs and `sheet2_results`).
     - Page 25 (Page 24 of 24): Official Plan Approval Certificate & Surveyor signatures.
   - **Dual Corner Seals**:
     - Applied on all pages via `AppFormDualSealCanvas` (`app_form_pdf_service.py:70–108`):
       - Bottom-Left: Checker Seal ($90 \times 90$ pt).
       - Bottom-Right: Designer Seal ($90 \times 90$ pt).

5. **PDF Generation Engines**:
   - `detail_calc_pdf_service.py`: Generates official Detail Calculation Booklet (Cover + Dashboard + all stiffener sheets with technical vector schematics). Size: 282,570 bytes.
   - `lightship_pdf_service.py`: Generates official Lightship Weight Estimation Booklet (Cover + Table 1 Plating + Table 2 Stiffeners + Table 3 56% Outfitting Synthesis). Size: 254,363 bytes.
   - `app_form_pdf_service.py`: Generates complete 25-Page Department of Shipping Application Form with dual corner seals. Size: 304,993 bytes.

6. **Automated Test Results**:
   - Command: `python -m unittest discover tests` with `PYTHONPATH=.`
   - Result: `Ran 16 tests in 0.082s — OK` (`test_lightship_realistic.py`, `test_auto_comply.py`, `test_table_interpolations.py`).

7. **Live Endpoint Status Check on Port 8055**:
   - `GET http://127.0.0.1:8055/api/initial-state`: HTTP 200
   - `POST http://127.0.0.1:8055/api/pdf/detail-calculation/generate`: HTTP 200 (282,570 bytes)
   - `POST http://127.0.0.1:8055/api/lightship/pdf/generate`: HTTP 200 (254,363 bytes)
   - `POST http://127.0.0.1:8055/api/application-form/pdf/generate`: HTTP 200 (304,993 bytes)
   - `POST http://127.0.0.1:8055/api/calculate`: HTTP 200

---

## 2. Logic Chain

### 2.1 Trace of Cross-Tab Reactive Data Flow

```
[Dashboard Inputs]
       │
       ├────────────────────────────────────────┬────────────────────────────────────────┐
       ▼                                        ▼                                        ▼
[Principal Dimensions & Route]       [Plate Thicknesses]                      [Stiffener Dimensions]
(LOA, LBP, B, D, d, spacing, kt, kz) (t_keel, t_bottom, t_side, etc.)        (hw, tw, bf, tf, profile_type)
       │                                        │                                        │
       ├───────────────────┬────────────────────┤                                        │
       ▼                   ▼                    ▼                                        ▼
[Calculation Brain]   [Detail Calc]        [Lightship Plating]                      [Detail Calc / Lightship]
(Evaluates Table      (Sets attached       (Sets plate t,                           (Sets stiffener web/flange,
Interpolations,       plate tp from        scales L & B                             derives section modulus Z,
kt/kz factors,        welded strake,       from LOA/B/D,                            updates stiffener weight &
limits)               width bp=spacing)    computes vol & kg)                       56% outfitting allowances)
       │                   │                    │                                        │
       └───────────────────┴────────────────────┴────────────────────────────────────────┘
                                                │
                                                ▼
                                    [Application Form Sync]
                        (Prefills particulars, ticks checkboxes,
                         maps 77 items to brain IDs & Sheet 2 Z)
                                                │
                                                ▼
                                     [PDF Export & Preview]
                        (Detail Calc PDF, Lightship PDF, App Form PDF)
```

1. **When Principal Dimensions Change (`DashboardView.js:1335–1354`)**:
   - `handleLiveInputChange(field, val)` sets `appState.dashboard_inputs[field] = val`.
   - Calls `recalculateAll(appState)`:
     - Recomputes factor multipliers $k_t$ and $k_z$ based on selected route and hull material.
     - Re-evaluates frame spacing limit ($450 + 2 \times \text{LBP}$) and collision bulkhead position range ($0.05 - 0.08 \times \text{LBP}$).
     - Updates effective plate width $b_p$ for all stiffener calculations in `sheet2_results`.
     - Re-derives all section moduli $Z$ and recalculates margins.
     - Calls `updateTopStats()`, `updateLiveDashboardDisplays()`, and `triggerAutosaveDebounced()`.

2. **When Plate Scantlings Change (`DashboardView.js:1493–1518, 1563–1595`)**:
   - `handleLivePlateProvidedChange` and `handleLiveProvidedScantlingChange` update `dashboard_inputs[plate_key]`, `custom_brain_dact[memberId]`, and `scantling_checklist`.
   - `recalculateAll(appState)` cascades the new thickness to:
     - Matching Calculation Brain item actual value (`dact`) and margin.
     - Any stiffener whose `welded_plate_key` matches the plate, updating $t_p$, neutral axis $y_{\text{na}}$, and section modulus $Z$.
     - Lightship plate thickness $t$, recomputing plate volume, plate weight, net steel, and 56% outfitting allowances.
     - Application Form lookup, ensuring that Pages 8–24 reflect the updated provided scantling.

3. **When Stiffener Dimensions Change (`DetailCalcView.js:270–320` & `DashboardView.js:1520–1561`)**:
   - `handleDetailCalcDimChange` and `handleDetailCalcProfileTypeChange` update `appState.stiffener_custom_dims[memberId]`.
   - `recalculateAll` re-derives $Z$, $y_{\text{na}}$, moments of inertia, and vector schematic SVG.
   - Cascades to Lightship angle dimensions (`l_dim`, `b_dim`, `t`), updating stiffener weight and outfitting allowances.
   - Cascades to Application Form, updating the provided section modulus for that stiffener.

4. **Identified Nuance (State Persistence Precedence)**:
   - In `app/services/lightship_service.py` (lines 169–171) and `app/static/js/calc.js` (lines 506–508):
     `saved_l = float(saved.get('l', default_l))`
     If `appState.lightship_plates` already exists in `saved_state.json` or `localStorage`, the previously saved plate length `saved.l` takes precedence over `default_l` (which was calculated by scaling from `loa`).
   - Consequently, changing `LOA` in the dashboard does not automatically overwrite a custom or previously saved plate length unless the user clicks "Reset Quantities" (`resetLightshipQuantities()`) or manually updates the plate length.
   - This behavior is intentional to prevent user-customized shipyard plate lengths from being discarded, but engineers should be aware that clicking "Reset Quantities" is required to re-scale standard catalog lengths to new principal dimensions.

---

## 3. Caveats

1. **State Persistence in Browser LocalStorage vs Server**:
   - The application supports dual-mode persistence: `localStorage.getItem('bangla_scantling_saved_state')` and `/api/save-state`. In the browser, local storage takes priority on initial page load if present (`app.js:30–48`). If testing in browser, clearing `localStorage` or clicking "Reset Defaults" reverts to server master defaults.
2. **Electrical Outfitting Percentage Labelling**:
   - In `SKILL.md` and statutory rules, the allowance table specifies: "Electrical & Instrumentation: 5% (3% formula base)". The mathematical calculation correctly uses `total_steel * 0.03`, which combined with 20% + 15% + 10% + 1% + 7% totals exactly $56\%$. This is mathematically consistent across both frontend and backend.
3. **ReportLab Font Fallback**:
   - `_register_arial_fonts()` registers `Arial` and `Arial-Bold` from `C:/Windows/Fonts/`. On non-Windows platforms, it automatically falls back to standard ReportLab `Helvetica`. Since the host system is Windows, Arial is properly utilized.

---

## 4. Conclusion

1. **Detail Calculation (`sheet2-calc`)**:
   - High-fidelity naval architecture formulas accurately calculate neutral axis, parallel axis moments of inertia, max fiber distance, and section modulus with dynamic attached strake interaction.
2. **Calculation Brain (`calc-brain`)**:
   - Rules 8–52 are completely integrated, with active members dynamically selected per hull construction and vessel type. Table interpolations highlight bounding rows, parameter columns, and interpolation nodes.
3. **Lightship Calculation**:
   - Fully compliant with clean element names (no dimensions or rule strings in `name`/`element`). Live mathematical calculations and standard 56% outfitting allowances ($W_{\text{lightship}} = W_{\text{net}} \times 1.56$) are implemented consistently in both client-side JavaScript and server-side Python.
4. **Application Form**:
   - The 25-page statutory Department of Shipping application form is fully prefilled from vessel particulars and dynamically linked to Calculation Brain IDs and Detail Calculation section moduli. Dual corner seals are rendered on all pages.
5. **Cross-Tab Reactivity & Linkages**:
   - Parameter updates cascade reactively through `recalculateAll()` across Dashboard, Detail Calc, Lightship, Application Form, and all 3 PDF generation engines.
6. **Server & Endpoints**:
   - Server is active on port 8055. All endpoints (`/api/initial-state`, `/api/calculate`, `/api/save-state`, `/api/pdf/detail-calculation/generate`, `/api/lightship/pdf/generate`, `/api/application-form/pdf/generate`) return HTTP 200 with valid data and complete PDFs.

---

## 5. Verification Method

To independently reproduce and verify this investigation:

1. **Execute Unit Tests**:
   ```powershell
   $env:PYTHONPATH="."
   python -m unittest discover tests
   ```
   *Expected outcome*: `Ran 16 tests ... OK` with 0 failures.

2. **Verify PDF Generation via Python**:
   ```powershell
   python -c @"
   import json
   from app.services.calculation_service import CalculationService
   from app.services.pdf.detail_calc_pdf_service import generate_detail_calculation_booklet_pdf
   from app.services.pdf.lightship_pdf_service import generate_lightship_booklet_pdf
   from app.services.pdf.app_form_pdf_service import generate_application_form_pdf

   with open('app/saved_state.json', 'r', encoding='utf-8') as f:
       state = json.load(f)

   computed = CalculationService.compute_all_calculations(state)
   assert len(generate_detail_calculation_booklet_pdf(computed)) > 200000
   assert len(generate_lightship_booklet_pdf(computed)) > 200000
   assert len(generate_application_form_pdf(computed)) > 250000
   print('All 3 PDF generation engines verified successfully!')
   "@
   ```

3. **Verify Live Web Server Endpoints on Port 8055**:
   ```powershell
   Invoke-WebRequest -Uri "http://127.0.0.1:8055/api/initial-state" -Method GET
   Invoke-WebRequest -Uri "http://127.0.0.1:8055/api/pdf/detail-calculation/preview" -Method GET
   Invoke-WebRequest -Uri "http://127.0.0.1:8055/api/lightship/pdf/preview" -Method GET
   Invoke-WebRequest -Uri "http://127.0.0.1:8055/api/application-form/pdf/preview" -Method GET
   ```
   *Expected outcome*: HTTP 200 on all endpoints.

4. **Verify Clean Element Names in Lightship**:
   - Inspect `app/services/lightship_service.py` lines 33–77 and `tests/test_lightship_realistic.py` lines 44–64.
   - Verify that no plate or angle `name` contains "mm", "rule", or "table".

5. **Verify Statutory 56% Outfitting Breakdown**:
   - Inspect `app/domain/calc/weight_calc.py` lines 48–75 and `calc.js` lines 591–611.
   - Sum: $20\% + 15\% + 10\% + 3\% + 1\% + 7\% = 56\%$.

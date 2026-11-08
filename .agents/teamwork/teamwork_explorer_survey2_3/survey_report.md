# Survey Report 2.3: Auto-Comply Optimizer, Test Suites, and Port 8055 Verification Setup

**Agent**: `teamwork_explorer_survey2_3`  
**Date**: 2026-10-30  
**Repository Working Directory**: `e:\Bangla Scantling`  
**Target Milestone**: Survey 2.3 — Auto-Comply Optimizer, Profile Selection, Test Suites & Port 8055 Verification

---

## 1. Executive Summary

This investigation surveys three tightly linked subsystems of the Bangladesh Scantling Statutory Compliance System:
1. **Auto-Comply Optimizer Architecture**: Backend optimizer (`ScantlingOptimizer`), coordinator service (`AutoComplyService`), and frontend UI integration (`AutoComplyModal.js`, `DetailCalcView.js`, `calc.js`).
2. **Profile Selection & Multi-Criterion Component Compliance**: How structural members (Center Keelson, Side Keelson, Frames, Girders) are currently evaluated, why candidate selection previously evaluated only Section Modulus ($Z_{\text{prov}} \ge Z_{\text{req}}$) ignoring component minimums ($t_w \ge t_{w,\text{req}}$, $b_f \ge b_{f,\text{req}}$, $A_f \ge A_{f,\text{req}}$), and the exact algorithmic upgrade required to guarantee simultaneous compliance of all physical criteria.
3. **Test Suites & Verification Framework**: Inventory of all existing unit, architecture, stress, and browser-driven regression tests, execution methods (noting Python 3.14 environment details without `pytest`), port 8055 monitoring, and deliverable validation criteria.

---

## 2. Auto-Comply Optimizer Implementation

### 2.1 Backend Architecture

The backend Auto-Comply framework resides under `app/services/auto_comply/` and `app/api/v1/`:

| Module Path | Primary Class / Function | Purpose & Responsibility |
|---|---|---|
| `app/services/auto_comply/optimizer.py` | `ScantlingOptimizer` | Mathematical optimizer for plate thickness increments and stiffener profile selection. |
| `app/services/auto_comply/service.py` | `AutoComplyService` | High-level orchestrator: runs calculation, detects non-compliant members, coordinates sizing, and formats previews. |
| `app/services/auto_comply/standard_profiles.py` | `STANDARD_ANGLES`, `STANDARD_TEES`, `STANDARD_FLAT_BARS`, `STANDARD_PLATE_THICKNESSES` | Standard shipbuilding catalogs (BS/EN/ISO rolled angles, built-up tees, flat bars, commercial plate thicknesses). |
| `app/api/v1/endpoints_auto_comply.py` | `preview_auto_comply`, `apply_auto_comply` | FastAPI endpoints exposed at `/api/auto-comply/preview` and `/api/auto-comply/apply`. |

#### Data Flow in Backend:
1. `POST /api/auto-comply/preview` receives `current_state` (JSON payload with `dashboard_inputs`, `custom_brain_dact`, `stiffener_custom_dims`).
2. `AutoComplyService.generate_compliance_preview(current_state)`:
   - Calls `CalculationService.compute_all_calculations(current_state)` to obtain authoritative rule values (`calculation_brain`, `sheet2_results`).
   - Filters items where `status != 'COMPLIANT'` or `margin < 0`.
   - For `plate` members: calls `ScantlingOptimizer.find_compliant_plate_thickness(rreq, dact)`.
   - For `stiffener` members: retrieves attached plate thickness $t_p$ from `welded_plate_key` and calls `ScantlingOptimizer.find_compliant_stiffener_profile(...)`.
   - Re-evaluates state with `CalculationService.compute_all_calculations` to verify 100% compliance.
   - Returns `{ status: 'success', old_compliant_count, new_compliant_count, items_updated_count, changes, proposed_state }`.
3. `POST /api/auto-comply/apply`:
   - Calls `apply_compliance(current_state)`, merges `proposed_state`, and returns the recomputed master state.

### 2.2 Frontend Implementation

| File Path | Component / Function | Role in Auto-Comply |
|---|---|---|
| `app/static/js/services/AutoComplyModal.js` | `AutoComplyModal` (`open`, `renderModal`, `apply`, `showSuccessToast`) | Modal dialog displaying preview scorecard, before/after table, and one-click "Apply All Compliant Scantlings" action. |
| `app/static/js/views/DetailCalcView.js` | `renderSheet2Calc`, `handleDetailCalcProfileTypeChange`, `handleDetailCalcDimChange` | Interactive profile selector (L, T, FB), dimension inputs ($h_w, t_w, b_f, t_f$), section properties, and SVG vector cross-section diagram. |
| `app/static/js/views/CalcBrainView.js` | `renderDerivationTable`, `toggleCalcBrainDerivation` | Calculation Brain drawer showing empirical statutory tables, bounding cells, and step-by-step formulas. |
| `app/static/js/views/DashboardView.js` | `renderDashboard`, `handleLiveBrainItemChange` | Executive compliance dashboard table showing provided, required, margin, and status badges. |
| `app/static/js/calc.js` | `calcStiffenerSection`, `recalculateAll` | Client-side section modulus engine and global recalculator. |

---

## 3. Current Profile Filtering, Evaluation & Sizing Mechanism

### 3.1 Current Code Analysis (`app/services/auto_comply/optimizer.py:46-173`)

In `ScantlingOptimizer.find_compliant_stiffener_profile`:
```python
@classmethod
def find_compliant_stiffener_profile(
    cls,
    rreq_z: float,
    spacing: float = 550.0,
    tp: float = 10.0,
    preferred_type: str = "L",
    current_hw: float = 0.0,
    current_tw: float = 0.0,
    current_bf: float = 0.0,
    current_tf: float = 0.0
) -> Dict[str, Any]:
```

#### Deficiencies in Existing Logic:
1. **Input Signature**:
   - Only accepts `rreq_z` (required section modulus in $\text{cm}^3$).
   - Completely lacks parameters for individual component minimums: `min_tw` (web thickness), `min_bf` (flange width), and `min_af` (flange sectional area).
2. **Premature Dimension Retention**:
   Lines 68-83:
   ```python
   if current_hw > 0:
       cur_res = calc_stiffener_section(
           spacing, tp, current_hw, current_tw, current_bf, current_tf, preferred_type
       )
       if cur_res['z_cm3'] >= rreq_z and rreq_z > 0:
           return { ... }
   ```
   If a user has an existing girder where $Z_{\text{prov}} \ge Z_{\text{req}}$, but $t_w < t_{w,\text{req}}$ or $b_f < b_{f,\text{req}}$, the optimizer falsely assumes the profile is compliant and leaves non-compliant component dimensions untouched!
3. **Candidate Catalog Filtering**:
   Lines 85-94:
   ```python
   candidates = []
   if preferred_type == "FB" and rreq_z <= 120.0:
       candidates.extend(STANDARD_FLAT_BARS)

   if rreq_z <= 450.0:
       candidates.extend(STANDARD_ANGLES)

   candidates.extend(STANDARD_TEES)
   ```
   - Does not filter out Flat Bars when $b_f > 0$ or $A_f > 0$ is required.
   - Does not check if angles can physically provide the required flange area or width (angles in `STANDARD_ANGLES` have max $b_f = 150\text{ mm}$ and max $A_f \approx 21\text{ cm}^2$).
4. **Candidate Evaluation Loop**:
   Lines 100-139:
   Evaluates each profile purely on:
   ```python
   if z_prov >= rreq_z:
       diff = z_prov - rreq_z
       if z_prov >= target_z and diff < best_diff: ...
   ```
   No checks for `prof["web_thk"] >= min_tw`, `prof["flange_width"] >= min_bf`, or `cand_af >= min_af`.
5. **Parametric Fallback Generator**:
   Lines 145-163:
   ```python
   hw = 600.0
   while hw <= 1500.0:
       tw = max(12.0, round(hw / 50.0))
       bf = max(200.0, round(hw * 0.4))
       tf = max(16.0, round(tw * 1.5))
       res = calc_stiffener_section(spacing, tp, hw, tw, bf, tf, "T")
       if res["z_cm3"] >= rreq_z * 1.05:
           return ...
       hw += 50.0
   ```
   - If $hw = 600\text{ mm}$, $tw$ is set to $\max(12, 12) = 12.0\text{ mm}$, and $bf$ is set to $\max(200, 240) = 240\text{ mm}$, $tf = 18\text{ mm}$.
   - For Table 16 Center Keelson ($L = 69.85\text{ m}, kt = 1.40$), the requirements are:
     - $t_{w,\text{req}} = 13.29\text{ mm}$
     - $b_{f,\text{req}} = 319.0\text{ mm}$
     - $A_{f,\text{req}} = 71.12\text{ cm}^2$
     - $Z_{\text{req}} = 1480.88\text{ cm}^3$
   - The fallback generator at $hw = 600$ generates $Z \approx 2200 \ge 1480.88$, but produces $t_w = 12.0 < 13.29\text{ mm}$, $b_f = 240 < 319.0\text{ mm}$, and $A_f = 43.2 < 71.12\text{ cm}^2$! Thus, the member fails 3 out of 4 criteria despite "passing" section modulus!

---

## 4. Required Optimizer Upgrade: Multi-Criterion Sizing Logic

To guarantee that candidate profiles satisfy BOTH Section Modulus ($Z \ge Z_{\text{req}}$) and all individual component minimums ($t_w \ge t_{w,\text{req}}$, $b_f \ge b_{f,\text{req}}$, $A_f \ge A_{f,\text{req}}$):

### 4.1 Upgraded Method Signature & Component Extraction

In `app/services/auto_comply/optimizer.py`:
```python
@classmethod
def find_compliant_stiffener_profile(
    cls,
    rreq_z: float,
    spacing: float = 550.0,
    tp: float = 10.0,
    preferred_type: str = "L",
    current_hw: float = 0.0,
    current_tw: float = 0.0,
    current_bf: float = 0.0,
    current_tf: float = 0.0,
    min_tw: float = 0.0,
    min_bf: float = 0.0,
    min_af: float = 0.0
) -> Dict[str, Any]:
```

In `app/services/auto_comply/service.py`:
When processing stiffener member `m`:
```python
# Extract statutory component minimums if present in member or derivation
comps = m.get("components") or m.get("derivation", {}).get("components") or []
min_tw = 0.0
min_bf = 0.0
min_af = 0.0

for comp in comps:
    param = comp.get("param")
    req_val = float(comp.get("rreq") or 0.0)
    if param == "web_thk":
        min_tw = max(min_tw, req_val)
    elif param == "face_width":
        min_bf = max(min_bf, req_val)
    elif param == "face_area":
        min_af = max(min_af, req_val)

opt_prof = ScantlingOptimizer.find_compliant_stiffener_profile(
    rreq_z=rreq,
    spacing=spacing,
    tp=tp,
    preferred_type=pref_type,
    current_hw=cur_hw,
    current_tw=cur_tw,
    current_bf=cur_bf,
    current_tf=cur_tf,
    min_tw=min_tw,
    min_bf=min_bf,
    min_af=min_af
)
```

### 4.2 Multi-Criterion Evaluation in `ScantlingOptimizer`

1. **Current Dimension Validation**:
   ```python
   if current_hw > 0:
       cur_res = calc_stiffener_section(
           spacing, tp, current_hw, current_tw, current_bf, current_tf, preferred_type
       )
       cur_af = (current_bf * current_tf) / 100.0 if preferred_type != "FB" else 0.0
       if (cur_res['z_cm3'] >= rreq_z and rreq_z > 0
           and current_tw >= min_tw
           and current_bf >= min_bf
           and cur_af >= min_af):
           return { ... }
   ```

2. **Candidate Profiling**:
   - If `min_bf > 0` or `min_af > 0`: exclude `STANDARD_FLAT_BARS` and force profile type to `T` or `L`.
   - If `min_bf > 150` or `min_af > 21.0`: exclude `STANDARD_ANGLES` and force profile type to `T`.
   - When iterating through `candidates`:
     ```python
     cand_af = (prof["flange_width"] * prof["flange_thk"]) / 100.0 if prof["profile_type"] != "FB" else 0.0
     if prof["web_thk"] < min_tw or prof["flange_width"] < min_bf or cand_af < min_af:
         continue
     ```

3. **Parametric Built-Up T Generator**:
   ```python
   hw = 600.0
   while hw <= 1500.0:
       tw = max(min_tw, 12.0, round(hw / 50.0))
       bf = max(min_bf, 200.0, round(hw * 0.4))
       tf = max(16.0, round(tw * 1.5))
       if min_af > 0 and (bf * tf) / 100.0 < min_af:
           tf = max(tf, math.ceil((min_af * 100.0) / bf))
       
       cand_af = (bf * tf) / 100.0
       res = calc_stiffener_section(spacing, tp, hw, tw, bf, tf, "T")
       if (res["z_cm3"] >= rreq_z * 1.05 
           and tw >= min_tw 
           and bf >= min_bf 
           and cand_af >= min_af):
           return {
               "profile_type": "T",
               "web_depth": hw,
               "web_thk": tw,
               "flange_width": bf,
               "flange_thk": tf,
               "prov_z": round(res["z_cm3"], 2),
               "margin": round(res["z_cm3"] - rreq_z, 2),
               "label": f"T {int(hw)}×{int(bf)}×{int(tw)}/{int(tf)}"
           }
       hw += 50.0
   ```

4. **Catalog Expansion**:
   Add built-up T profiles to `STANDARD_TEES` in `app/services/auto_comply/standard_profiles.py` that cater directly to heavy keelsons:
   ```python
   {"label": "T 600×350×14/25", "profile_type": "T", "web_depth": 600, "web_thk": 14, "flange_width": 350, "flange_thk": 25},
   {"label": "T 700×350×15/25", "profile_type": "T", "web_depth": 700, "web_thk": 15, "flange_width": 350, "flange_thk": 25},
   {"label": "T 800×350×16/28", "profile_type": "T", "web_depth": 800, "web_thk": 16, "flange_width": 350, "flange_thk": 28},
   ```
   For `T 600×350×14/25`:
   $t_w = 14.0 \ge 13.29\text{ mm}$, $b_f = 350.0 \ge 319.0\text{ mm}$, $A_f = 35.0 \times 2.5 = 87.5 \ge 71.12\text{ cm}^2$, and $Z \approx 3900 \ge 1480.88\text{ cm}^3$. All 4 statutory checks pass with positive margins.

---

## 5. Comprehensive Survey of Existing Test Suites

The codebase contains an extensive test framework spanning unit tests, architecture tests, adversarial live API tests, and Playwright browser integration tests.

### 5.1 Test Suite Inventory

| Test File | Suite Category | Tests Count | Scope & Assertions |
|---|---|---|---|
| `tests/test_auto_comply.py` | Unit | 4 | Commercial plate thickness rounding ($\ge +0.4\text{ mm}$ margin), stiffener profile selection, automatic upgrade of heavy sections to T, AutoComplyService preview generation. |
| `tests/test_table_interpolations.py` | Unit | 9 | Statutory table interpolators: Rule 8(1) min plate, Table 1 Keel Plate & Width, Table 2 Bottom Shell, Spacing correction for $s > 550\text{ mm}$, Table 13 Floors 3D surface, Table 17 Side Frames, Table 20 Deck Beams, Table 39 Rudder stock, `TableViewData` active rows/cols structure. |
| `tests/test_lightship_realistic.py` | Unit / Validation | 2 | Net steel realistic range ($400\text{t} - 650\text{t}$), lightship range ($650\text{t} - 1000\text{t}$), outfitting allowances exactly $56\%$ of net steel ($1.56\times$), clean element names without embedded dimensions or rule text. |
| `verify_modular_architecture.py` | Architecture / Service | 6 | Section modulus with attached plating, plate weight & $56\%$ lightship allowances, statutory factors ($kt=1.40, kz=1.40$ for Steel Old; $kt=1.20, kz=1.25$ for Bay Crossing), dynamic active member counts per hull type (DB: 88, DH: 93, SH: 77), in-memory generation of all 3 PDFs. |
| `tests/test_hardening_verification.py` | Integration / Hardening | 5 | 400 Bad Request rejection on non-dict payloads (`/api/calculate`, `/api/save-state`), null/negative dimension safety guards in `LightshipService`, non-dict saved state resilience, RFC 6266 / RFC 5987 Bengali vessel name content disposition headers on port 8055, deliverable PDF page counts and PNG sizes. |
| `tests/adversarial_endpoint_stress.py` | Adversarial / Live Port 8055 | 9 | Live port 8055 stress: PDF route aliases (GET/POST), CORS preflight, malformed/boundary payloads, thread pool concurrency, state persistence & rollback. |
| `audit_pdf_vs_web.py` | Playwright E2E | Script | Compares web dashboard DOM rows, Detail Calculation sheets (20 sheets), and generated PDF deliverables. |
| `verify_lightship_improvements.py` | Playwright E2E | Script | Interactive DOM manipulation on Lightship tab, live recalculations on plate/angle input edits, reset quantities button, PDF booklet generation. |

### 5.2 Environment & Execution Methodology

- **Python Environment**: Python 3.14 (64-bit) located at:  
  `C:\Users\MUNNA\AppData\Local\Python\pythoncore-3.14-64\python.exe`
- **Important Note on Pytest**: `pytest` is **NOT installed** in the active Python 3.14 environment. Attempting to invoke `pytest` or `python -m pytest` returns `CommandNotFoundException` / `No module named pytest`.
- **Authoritative Execution Commands**:
  ```powershell
  # 1. Run all unit test suites in tests/
  python -m unittest discover tests

  # 2. Run modular architecture tests
  python verify_modular_architecture.py

  # 3. Run hardening verification against live port 8055
  python -m unittest tests/test_hardening_verification.py

  # 4. Run adversarial stress test against live port 8055
  python tests/adversarial_endpoint_stress.py

  # 5. Run Playwright E2E audit
  python audit_pdf_vs_web.py
  ```

---

## 6. Port 8055 Verification & Deliverable Validation Setup

### 6.1 Port 8055 Monitoring

1. **Process Launch**:
   The web server is started via:
   ```powershell
   python run_server.py 8055
   # or start_app.bat
   ```
   Command executed by Uvicorn:
   `"C:\Users\MUNNA\AppData\Local\Python\bin\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8055`
2. **Liveness & Health Verification**:
   - PowerShell port check:
     `Get-NetTCPConnection -LocalPort 8055 -ErrorAction SilentlyContinue` (Verifies state `Listen`)
   - HTTP Health Check:
     `GET http://127.0.0.1:8055/api/initial-state` returns HTTP 200 with complete initial application state.
   - Browser navigation:
     When using Playwright scripts, use `await page.goto("http://127.0.0.1:8055", wait_until="domcontentloaded")` (recommended over `networkidle` which can exceed timeouts on websocket/font activity).

### 6.2 Deliverables Integrity & Page Specifications

The project maintains 4 mandatory deliverable artifacts in the project root:

| Deliverable File | Target Specification | Validation Method |
|---|---|---|
| `Detail_Calculation_Booklet.pdf` | Exactly **10 pages**, A4, Arial font, no running header/footer, designer corner seal stamped on pages 2–10. | PyMuPDF `doc = fitz.open('Detail_Calculation_Booklet.pdf')`; `assert len(doc) == 10`. |
| `Lightship.pdf` | Exactly **2 pages**, evaluated lightship weight calculation deliverable, 56% outfitting breakdown. | PyMuPDF `doc = fitz.open('Lightship.pdf')`; `assert len(doc) == 2`. |
| `Application_Form_Booklet.pdf` | Exactly **25 pages**, statutory Bangladesh scantlings application booklet. | PyMuPDF `doc = fitz.open('Application_Form_Booklet.pdf')`; `assert len(doc) == 25`. |
| `lightship_preview.png` | High-resolution visual preview of the Lightship synthesis table, file size $> 100\text{ KB}$. | `assert os.path.exists('lightship_preview.png') and os.path.getsize('lightship_preview.png') > 100000`. |

### 6.3 Live PDF Endpoint Validation

All three PDF documents are generated via dedicated HTTP endpoints that must return HTTP 200, valid uncorrupted PDF bytes, and compliant RFC 6266 headers:
1. **Detail Calculation Booklet**: `POST /api/pdf/detail-calculation/generate` or `POST /api/v1/pdf/detail-calc`
2. **Lightship Booklet**: `POST /api/lightship/pdf/generate` or `POST /api/v1/pdf/lightship`
3. **Application Form Booklet**: `POST /api/export-pdf/application-form` or `POST /api/v1/pdf/application-form`

---

## 7. Recommendations & Implementation Blueprint

For the implementer subagent executing Milestone 2:
1. **In `app/domain/rules/interpolations/base_interpolator.py`**:
   - Add `active_col_indices: List[int] = Field(default_factory=list)` to `TableViewData`.
   - Add `components: Optional[List[Dict[str, Any]]] = None` to `InterpolationResult`.
2. **In `app/domain/rules/interpolations/table_14_16_keelson.py`**:
   - Interpolate all 3 columns for Table 16: $t_w$, $A_f$, $b_f$.
   - Compute baseline equivalent $Z = 1057.77\text{ cm}^3$ and $Z_{\text{req}} = Z_{\text{base}} \times kz$.
   - Populate `components` list with 4 criteria: Web Plate Thickness, Face Plate Area, Face Plate Width, Girder Section Modulus.
   - Set `active_col_indices = [1, 2, 3]`.
3. **In `app/services/calculation_service.py`**:
   - Propagate `interp_res.components` to `m['components']`.
   - If `m['components']` exists, evaluate each component against provided profile dimensions ($t_w, b_f, A_f = (b_f \times t_f)/100, Z$).
   - Set `m['status'] = 'COMPLIANT'` if and only if Section Modulus AND all sub-components pass.
4. **In `app/services/auto_comply/optimizer.py` and `service.py`**:
   - Extract `min_tw`, `min_bf`, `min_af` from `m.get('components')`.
   - Pass them into `find_compliant_stiffener_profile`.
   - Filter candidates and configure the built-up T generator to enforce all physical minimums.
5. **In `app/static/js/`**:
   - In `CalcBrainView.js`: update `renderDerivationTable` to highlight all columns in `tv.active_col_indices`, and render the multi-part component comparison grid.
   - In `DashboardView.js`: render equivalent $Z$ on the main row and add multi-component breakdown tooltip on the status badge.
   - In `DetailCalcView.js`: render the structured Base $\to$ Factor $\to$ Req $\to$ Prov $\to$ Margin $\to$ Status component grid for multi-part members.
6. **Verification**:
   - Execute `python -m unittest discover tests`
   - Execute `python verify_modular_architecture.py`
   - Execute `python tests/adversarial_endpoint_stress.py`
   - Audit live UI on `http://127.0.0.1:8055` using Playwright (`domcontentloaded`).

# Strategy Report: PDF Deliverables & Output Verification

**Specialist**: Explorer M1-3 (PDF Deliverables & Output Strategy Specialist)  
**Target Recipient**: Orchestrator (ID: `862ff85e-a971-4f0d-8d8d-3a2a0b9e6aec`) & Worker  
**Date**: 2026-10-30  
**Working Directory**: `e:\Bangla Scantling\.agents\teamwork\teamwork_explorer_m1_3`  

---

## 1. Observation

### 1.1 Existing PDF Generation Engines & File Paths
Direct inspection of the codebase identified the three primary ReportLab PDF generation engines and their supporting modules:

1. **Detail Calculation Booklet Generator**:
   - **Path**: `app/services/pdf/detail_calc_pdf_service.py` (Lines 374–713: `generate_detail_calculation_booklet_pdf(state)`)
   - **Layout**:
     - Page 1: Formal Cover Page with vessel particulars, Designer & Checker stamps (Lines 468–547)
     - Pages 2–3: Executive Dashboard containing 12 groups, 77 statutory scantling items, formatted with `KeepTogether` on every group table (Lines 550–674)
     - Pages 4–10: 20 Section Modulus stiffener sheets (3 sheets per page on pages 4–9, 2 sheets on page 10), each featuring technical derivation tables, a pure vector cross-section diagram (height=180 pt), and a red dashed neutral axis line `y_na` (Lines 118–203, 676–698)
     - Canvas: `CleanCanvas` (Lines 90–116) stamps the 58x58 pt Designer Seal in the bottom-right corner (`x = 595.27 - 36.0 - 58.0`, `y = 10.0`) of all pages except Page 1.
   - **Standalone Output Test**:
     - Command: `python -c "from app.services.pdf.detail_calc_pdf_service import generate_detail_calculation_booklet_pdf; ..."`
     - Result: Exactly **10 pages**, **282,570 bytes**.

2. **Lightship Weight Estimation Booklet Generator**:
   - **Path**: `app/services/pdf/lightship_pdf_service.py` (Lines 47–499: `generate_lightship_booklet_pdf(state)`)
   - **Layout**:
     - Page 1: Clean Cover Page with vessel particulars and dual review stamp boxes (NO signature/date lines, Lines 170–268)
     - Page 2: Complete Calculation Page fitted onto ONE single page (Table 1 Plating Scantlings, Table 2 Stiffeners Geometry, Table 3 Statutory 56% Outfitting Synthesis, Lines 270–489)
     - Canvas: `LightshipCleanCanvas` (Lines 20–46) stamps the 2X enlarged Designer Seal (116x116 pt) in the bottom-right corner (`x = 595.27 - 26.0 - 116.0`, `y = 12.0`) of Page 2.
   - **Standalone Output Test**:
     - Result: Exactly **2 pages**, **254,363 bytes**.

3. **Application Form Booklet Generator**:
   - **Path**: `app/services/pdf/app_form_pdf_service.py` (Lines 800–1018: `generate_application_form_pdf(state)`)
   - **Layout**:
     - 25 official Department of Shipping submission form pages.
     - Pages 1–8: Form cover, instructions, criteria, prefilled particulars, drawing checklist.
     - Pages 9–24: 104 statutory audit items dynamically linked to Calculation Brain IDs and Dashboard inputs (`ITEM_TO_CALC_ID`, Lines 24–68, 122–200).
     - Page 25: Official Plan Approval Certificate & Surveyor Signatures (Lines 960–1004).
     - Canvas: `AppFormDualSealCanvas` (Lines 70–110) stamps dual 90x90 pt seals on the bottom two corners of ALL 25 pages (Bottom-Left: Checker Seal, Bottom-Right: Designer Seal).
   - **Standalone Output Test**:
     - Result: Exactly **25 pages**, **304,993 bytes**.

### 1.2 State of Workspace Deliverables
Execution of `python -c "import os; ..."` revealed the current presence of deliverable files in `e:\Bangla Scantling\`:
- `Lightship.pdf`: **Present** (2 pages, 254,363 bytes).
- `Detail_Calculation_Booklet.pdf`: **MISSING** (File does not exist in root).
- `Application_Form_Booklet.pdf`: **MISSING** (File does not exist in root).
- `lightship_preview.png`: **MISSING** (File does not exist in root).

### 1.3 API Router & Route Aliases Status
- In `app/main.py`:
  - Line 45: Only `app.include_router(api_router, prefix="/api")` is mounted. Prefix `/api/v1` is **NOT mounted**.
  - CORS middleware (`CORSMiddleware`) is **NOT configured** in `app/main.py`.
- In `app/api/v1/endpoints_pdf.py`:
  - Lines 48, 73, 98: Only `/detail-calculation/preview`, `/detail-calculation/export`, and `/detail-calculation/generate` exist.
  - Requested route aliases `/detail-calc`, `/lightship`, and `/application-form` are **MISSING**.
- In `app/api/v1/endpoints_lightship.py`:
  - Prefix is `/lightship`, exposing `/pdf/generate`, `/pdf/preview`, `/pdf/export`.
- In `app/api/v1/endpoints_app_form.py`:
  - Prefix is `/application-form`, exposing `/pdf/generate`, `/pdf/preview`, `/pdf/export`.

### 1.4 Test Framework & Environment Tooling
- Execution of `python -c "import httpx..."` failed with `ModuleNotFoundError: No module named 'httpx'`.
- Execution of `python -m pytest` failed with `No module named pytest`.
- Available libraries: `requests` (available), `urllib.request` (available), `playwright` (available), `fitz` / `pymupdf` (available).
- Execution of `python -m unittest discover -s tests -p "test_*.py"` ran **16 tests in 0.094s: OK**.

---

## 2. Logic Chain

1. **Deliverable Generation Requirement**:
   - The user request and PROJECT.md Feature 8 mandate 4 updated deliverable files in the workspace:
     1. `Lightship.pdf` (evaluated live PDF deliverable)
     2. `Detail_Calculation_Booklet.pdf` (10-page evaluated PDF booklet)
     3. `Application_Form_Booklet.pdf` (25-page evaluated DOS application form)
     4. `lightship_preview.png` (high-resolution table preview per user rules)
   - `StateRepository`, `StateService`, and `CalculationService` load `app/saved_state.json` and compute all 77 brain rules, 20 stiffener sheets, and 56% lightship synthesis.
   - Passing `computed_state` directly to `generate_detail_calculation_booklet_pdf`, `generate_lightship_booklet_pdf`, and `generate_application_form_pdf` yields the evaluated PDF bytes without requiring a running web server.
   - For `lightship_preview.png`, rendering Page 1 (0-indexed; the complete calculation tables page) of `Lightship.pdf` via PyMuPDF `doc[1].get_pixmap(dpi=200)` generates a crisp 1654x2339 px image matching the user rule's requirement for a "High-resolution table preview".

2. **Route Aliasing & Mounting Strategy**:
   - ORIGINAL_REQUEST.md lines 16–18 and PROJECT.md Feature 2 specify routes:
     - `/api/v1/pdf/detail-calc`
     - `/api/v1/pdf/lightship`
     - `/api/v1/pdf/application-form`
   - In `app/api/v1/endpoints_pdf.py`, adding routes `@router.get("/detail-calc")`, `@router.post("/detail-calc")`, `@router.get("/lightship")`, `@router.post("/lightship")`, `@router.get("/application-form")`, `@router.post("/application-form")` encapsulates all PDF endpoints within `endpoints_pdf.py`.
   - In `app/main.py`, adding:
     ```python
     app.include_router(api_router, prefix="/api")
     app.include_router(api_router, prefix="/api/v1")
     ```
     simultaneously exposes the new `/api/v1/pdf/*` routes, creates `/api/pdf/*` aliases, and preserves 100% backward compatibility for all existing frontend JavaScript calls (`PdfViewerModal.js`, `LightshipView.js`, `ApplicationFormView.js`).
   - Adding `CORSMiddleware` in `app/main.py` satisfies preflight `OPTIONS` requests and browser cross-origin requests.

3. **Verification Rigor (Page Count, Size, Clearance, Overlaps)**:
   - Programmatic verification with PyMuPDF (`fitz`) guarantees mathematical certainty:
     - **Page Count**: `len(doc)` must strictly match target counts (10, 2, 25).
     - **Byte Size**: Minimum size thresholds (>200 KB for Detail Calc, >150 KB for Lightship, >250 KB for App Form).
     - **Visual Clearance**: All bounding boxes `(x0, y0, x1, y1)` must reside within page bounds `[0, 0, 595.28, 841.89]`. Flowable elements must not collide with canvas seals.
     - **Absence of Text Overlaps**: Pairwise intersection check of word bounding boxes on the same page. If `(r1 & r2).get_area() > 0.40 * min(r1.area, r2.area)` for different words, an overlap error is raised. In our baseline test, this algorithm found **0 overlaps** across all 37 pages of generated documents.

4. **Testing Live Downloads via Live Server**:
   - Because `httpx` is not installed, the Worker must test against the running FastAPI server on port 8055 using Python's `requests` library.
   - The test script will assert HTTP status `200`, `Content-Type: application/pdf`, `Content-Disposition`, valid byte streams, and parse each downloaded stream with PyMuPDF.

---

## 3. Caveats

1. **Server Runtime Dependency for Endpoint Testing**:
   - Generating the standalone deliverable files does not require the server to be running.
   - However, verifying the live HTTP endpoints (`/api/v1/pdf/*`) requires the server to be running on port 8055 (`python run_server.py 8055`).
2. **Missing `httpx` and `pytest` Packages**:
   - Automated testing must use `requests` and `unittest` (`python -m unittest discover tests`). Do not attempt `pytest` or `TestClient` without installing `httpx`.
3. **Clean Element Names Rule**:
   - The user rule strictly prohibits dimensions or rule citations in the `ELEMENT` column of `Lightship.pdf`. `lightship_pdf_service.py` strips parenthetical dimensions, and tests must verify that strings like `(Rule` or `(12.0mm)` are absent.

---

## 4. Conclusion & Concrete Worker Action Plan

The Worker should execute the following 4-phase implementation plan:

### Phase 1: Implement Route Aliasing & CORS in `app/main.py` and `app/api/v1/endpoints_pdf.py`

#### A. In `app/main.py`:
1. Add CORSMiddleware:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
2. Mount both `/api` and `/api/v1`:
```python
app.include_router(api_router, prefix="/api")
app.include_router(api_router, prefix="/api/v1")
```

#### B. In `app/api/v1/endpoints_pdf.py`:
Import generators and helper state functions from `endpoints_lightship` and `endpoints_app_form`:
```python
from app.services.pdf.lightship_pdf_service import generate_lightship_booklet_pdf
from app.services.pdf.app_form_pdf_service import generate_application_form_pdf
from app.api.v1.endpoints_lightship import _get_computed_lightship_state
from app.api.v1.endpoints_app_form import _get_computed_app_form_state
```
Add endpoints:
```python
# --- Detail Calculation Route Aliases ---
@router.get("/detail-calc")
async def get_detail_calc_pdf(
    disposition: str = "inline",
    state_service: StateService = Depends(get_state_service)
):
    computed_state = _get_computed_state(state_service=state_service)
    pdf_bytes = generate_detail_calculation_booklet_pdf(computed_state)
    vessel_name = computed_state.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Detail_Calculation_Booklet.pdf"
    disp_type = "attachment" if disposition == "attachment" else "inline"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"{disp_type}; filename={filename}"}
    )

@router.post("/detail-calc")
async def post_detail_calc_pdf(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    computed_state = _get_computed_state(custom_state=body)
    pdf_bytes = generate_detail_calculation_booklet_pdf(computed_state)
    vessel_name = computed_state.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Detail_Calculation_Booklet.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

# --- Lightship Booklet Route Aliases ---
@router.get("/lightship")
async def get_lightship_pdf(
    disposition: str = "inline",
    state_service: StateService = Depends(get_state_service)
):
    computed_state = _get_computed_lightship_state(state_service=state_service)
    pdf_bytes = generate_lightship_booklet_pdf(computed_state)
    vessel_name = computed_state.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Lightship_Booklet.pdf"
    disp_type = "attachment" if disposition == "attachment" else "inline"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"{disp_type}; filename={filename}"}
    )

@router.post("/lightship")
async def post_lightship_pdf(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    computed_state = _get_computed_lightship_state(custom_state=body)
    pdf_bytes = generate_lightship_booklet_pdf(computed_state)
    vessel_name = computed_state.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Lightship_Booklet.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

# --- Application Form Booklet Route Aliases ---
@router.get("/application-form")
async def get_app_form_pdf(
    disposition: str = "inline",
    state_service: StateService = Depends(get_state_service)
):
    computed_state = _get_computed_app_form_state(state_service=state_service)
    pdf_bytes = generate_application_form_pdf(computed_state)
    vessel_name = computed_state.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Application_Form.pdf"
    disp_type = "attachment" if disposition == "attachment" else "inline"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"{disp_type}; filename={filename}"}
    )

@router.post("/application-form")
async def post_app_form_pdf(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    computed_state = _get_computed_app_form_state(custom_state=body)
    pdf_bytes = generate_application_form_pdf(computed_state)
    vessel_name = computed_state.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Application_Form.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )
```

---

### Phase 2: Generate Updated Deliverables in the Workspace Root
Create and run a generation script (e.g., `generate_deliverables.py`):
```python
import os
import fitz
from app.repositories.state_repository import StateRepository
from app.services.state_service import StateService
from app.services.calculation_service import CalculationService
from app.services.pdf.detail_calc_pdf_service import generate_detail_calculation_booklet_pdf
from app.services.pdf.lightship_pdf_service import generate_lightship_booklet_pdf
from app.services.pdf.app_form_pdf_service import generate_application_form_pdf

repo = StateRepository()
svc = StateService(repo)
state = svc.get_saved_state() or svc.get_initial_state()
computed = CalculationService.compute_all_calculations(state)

# 1. Detail_Calculation_Booklet.pdf
calc_pdf = generate_detail_calculation_booklet_pdf(computed)
with open("Detail_Calculation_Booklet.pdf", "wb") as f:
    f.write(calc_pdf)
print(f"Generated Detail_Calculation_Booklet.pdf: {len(calc_pdf)} bytes")

# 2. Lightship.pdf
ls_pdf = generate_lightship_booklet_pdf(computed)
with open("Lightship.pdf", "wb") as f:
    f.write(ls_pdf)
print(f"Generated Lightship.pdf: {len(ls_pdf)} bytes")

# 3. Application_Form_Booklet.pdf
app_pdf = generate_application_form_pdf(computed)
with open("Application_Form_Booklet.pdf", "wb") as f:
    f.write(app_pdf)
print(f"Generated Application_Form_Booklet.pdf: {len(app_pdf)} bytes")

# 4. lightship_preview.png (Page 1 = Complete Calculation Tables Page)
ls_doc = fitz.open(stream=ls_pdf, filetype="pdf")
pix = ls_doc[1].get_pixmap(dpi=200)
pix.save("lightship_preview.png")
print(f"Generated lightship_preview.png: {pix.width}x{pix.height} px, {os.path.getsize('lightship_preview.png')} bytes")
```

---

### Phase 3: Deliverables Forensic Audit Script
Worker will run an audit script (e.g., `audit_pdf_deliverables.py`) verifying:
1. `Detail_Calculation_Booklet.pdf`:
   - Page count: `len(doc) == 10`
   - File size > 200,000 bytes
   - Text overlaps: `0`
   - Bounding rects within `[0, 0, 595.28, 841.89]`
2. `Lightship.pdf`:
   - Page count: `len(doc) == 2`
   - File size > 150,000 bytes
   - Text overlaps: `0`
   - Clean element names: NO `(Rule` or `mm` in element names
3. `Application_Form_Booklet.pdf`:
   - Page count: `len(doc) == 25`
   - File size > 250,000 bytes
   - Text overlaps: `0`
   - Dual corner seals present on all pages
4. `lightship_preview.png`:
   - File size > 100,000 bytes
   - Dimensions: 1654 x 2339 pixels

---

### Phase 4: Live HTTP API Endpoint Verification
Ensure server is running on port 8055 (`python run_server.py 8055`).
Execute automated verification against:
- `GET http://127.0.0.1:8055/api/v1/pdf/detail-calc` (200, 10 pages)
- `POST http://127.0.0.1:8055/api/v1/pdf/detail-calc` (200, 10 pages)
- `GET http://127.0.0.1:8055/api/v1/pdf/lightship` (200, 2 pages)
- `POST http://127.0.0.1:8055/api/v1/pdf/lightship` (200, 2 pages)
- `GET http://127.0.0.1:8055/api/v1/pdf/application-form` (200, 25 pages)
- `POST http://127.0.0.1:8055/api/v1/pdf/application-form` (200, 25 pages)
- CORS preflight options check on all routes
- All 16 unit tests: `python -m unittest discover -s tests -p "test_*.py"`

---

## 5. Verification Method

To independently verify the strategy and findings:

### 1. Verify Unit Tests
Execute:
```powershell
python -m unittest discover -s tests -p "test_*.py"
```
**Expected**: `Ran 16 tests in ... OK`.

### 2. Verify Deliverable Generator Execution
Execute the standalone generation snippet to verify that all 3 PDF generators produce the exact target page counts without error:
```powershell
python -c "from app.repositories.state_repository import StateRepository; from app.services.state_service import StateService; from app.services.calculation_service import CalculationService; from app.services.pdf.detail_calc_pdf_service import generate_detail_calculation_booklet_pdf; from app.services.pdf.lightship_pdf_service import generate_lightship_booklet_pdf; from app.services.pdf.app_form_pdf_service import generate_application_form_pdf; import fitz; s = CalculationService.compute_all_calculations(StateService(StateRepository()).get_saved_state()); print('Detail Calc:', len(fitz.open(stream=generate_detail_calculation_booklet_pdf(s), filetype='pdf'))); print('Lightship:', len(fitz.open(stream=generate_lightship_booklet_pdf(s), filetype='pdf'))); print('App Form:', len(fitz.open(stream=generate_application_form_pdf(s), filetype='pdf')))"
```
**Expected Output**:
```
Detail Calc: 10
Lightship: 2
App Form: 25
```

### 3. Verify Absence of Text Overlaps via PyMuPDF
Execute the bounding box intersection check across all pages:
```powershell
python -c "import fitz; from app.repositories.state_repository import StateRepository; from app.services.state_service import StateService; from app.services.calculation_service import CalculationService; from app.services.pdf.app_form_pdf_service import generate_application_form_pdf; s = CalculationService.compute_all_calculations(StateService(StateRepository()).get_saved_state()); doc = fitz.open(stream=generate_application_form_pdf(s), filetype='pdf'); overlaps = [1 for p in doc for i, w1 in enumerate(p.get_text('words')) for w2 in p.get_text('words')[i+1:i+15] if w1[4] != w2[4] and not (fitz.Rect(w1[:4]) & fitz.Rect(w2[:4])).is_empty and (fitz.Rect(w1[:4]) & fitz.Rect(w2[:4])).get_area() > 0.40 * min(fitz.Rect(w1[:4]).get_area(), fitz.Rect(w2[:4]).get_area())]; print('Overlaps in 25 pages:', len(overlaps))"
```
**Expected Output**: `Overlaps in 25 pages: 0`.

### 4. Invalidation Conditions
This strategy is invalidated if:
- Any PDF generator produces a different page count (e.g. Detail Calc != 10, Lightship != 2, App Form != 25).
- ReportLab font registration fails on Arial and crashes rather than falling back to Helvetica.
- Route aliasing breaks existing `/api/pdf/*` calls from the single page application frontend.

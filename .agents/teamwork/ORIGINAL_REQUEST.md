# Original User Request

## Parameters
[skip-interview]
How this run was launched; not part of the task.

## Initial Request — 2026-10-30T08:40:43Z

Proceed directly to execution. All requirements have been fully aligned in the prior grill-me session:
1. Multi-Column Tables (Table 16, Table 15, Table 22/23, Table 30) must interpolate all physical columns (Web Thk, Face Area, Face Width).
2. Derive equivalent Section Modulus (Z_req) so main row compares cm³ to cm³.
3. Multi-column active highlights in TableViewData / renderDerivationTable (active_col_indices: [1, 2, 3]).
4. Unified multi-part comparison grid in Detail View (Base, Factor, Req, Prov, Margin, Pass/Fail for each part).
5. Main dashboard row shows equivalent Z, with tooltip showing breakdown. Overall status is strictly COMPLIANT only if ALL parts pass.
6. Update Auto-Comply optimizer to meet all component minimums.
7. Run all tests and verify deliverables on port 8055.

## Alignment Specification — 2026-10-30T08:39:40Z

Specification from user alignment:
Implement the Generalized Multi-Column Statutory Evaluation Framework:
1. Root Cause:
   In Table 16 (Center Keelson) and Table 15 (Side Keelson), the interpolator previously extracted only one column (Web Plate Thickness in mm, e.g. 13.29 mm) and placed it into the Section Modulus column ('Req SM [cm³]'), comparing it against Provided SM = 1274.33 cm³, producing an invalid margin of +1261.04.

2. Architecture & Requirements:
   A. Generalized Multi-Criterion Evaluator (Backend & Frontend):
      - In `table_14_16_keelson.py` and for all multi-column tables (Table 15 Side Keelson, Table 16 Center Keelson, Table 22/23 Pillars, Table 30 Coamings):
        * Interpolate all prescribed physical columns (e.g. for Table 16: Web Plate Thickness tw >= Req mm, Face Plate Sectional Area Af >= Req cm², Face Plate Width bf >= Req mm).
        * Derive the statutory required Section Modulus (Z_req) from structural catalog / rule equivalent geometry (e.g. baseline 1057.77 cm³ * 1.40 = 1480.88 cm³ for Center Keelson, baseline 400 cm³ * 1.40 = 560 cm³ for Side Keelson) so the main table compares cm³ to cm³.
        * Store all component evaluations in `derivation['components']` or `m['components']`:
          [{'name': 'Web Plate Thickness', 'param': 'web_thk', 'base': 9.49, 'rreq': 13.29, 'unit': 'mm', 'prov': 12.0, 'margin': -1.29, 'status': 'NON-COMPLIANT'},
           {'name': 'Face Plate Sectional Area', 'param': 'face_area', 'base': 50.8, 'rreq': 71.12, 'unit': 'cm²', 'prov': 10.0, 'margin': -61.12, 'status': 'NON-COMPLIANT'},
           {'name': 'Face Plate Width', 'param': 'face_width', 'base': 319.0, 'rreq': 319.0, 'unit': 'mm', 'prov': 100.0, 'margin': -219.0, 'status': 'NON-COMPLIANT'},
           {'name': 'Girder Section Modulus', 'param': 'sm', 'base': 1057.77, 'rreq': 1480.88, 'unit': 'cm³', 'prov': 1274.33, 'margin': -206.55, 'status': 'NON-COMPLIANT'}]
      - Strict Compliance: Overall member status is COMPLIANT only if ALL sub-components pass. If any sub-component fails, status is NON-COMPLIANT.

   B. Multi-Column Table View Visualizer:
      - In `TableViewData` and `renderDerivationTable`, support multiple active columns (`active_col_indices: [1, 2, 3]` and bounding cells for each active column) so all active columns in Table 16 and Table 15 are highlighted simultaneously.

   C. Unified Multi-Part Comparison Grid in Detail View:
      - In `CalcBrainView.js` and Detail View, display the structured comparison grid showing Base -> Factor -> Required -> Provided -> Margin -> Status (Pass/Fail) for each statutory component.

   D. Dashboard Row & Multi-Part Status Tooltip:
      - Main dashboard row displays equivalent Section Modulus (Req SM vs Prov SM).
      - Status column has tooltip/hover showing the green/red breakdown of each component.

   E. Auto-Comply Optimizer:
      - Update `app/services/auto_comply/optimizer.py` and `calc.js` so profile selection satisfies both Section Modulus and individual component minimums (e.g. tw >= tw_req, bf >= bf_req, Af >= Af_req).

   F. Verify and Test:
      - Run all test suites, verify live UI on port 8055, and confirm all PDF deliverables compile properly.

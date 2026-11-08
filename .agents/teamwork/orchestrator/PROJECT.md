# Project: Bangladesh Scantling Statutory Compliance Web App
# Scope: Generalized Multi-Column Statutory Evaluation Framework & Auto-Comply Optimizer

## Architecture
- **Framework**: FastAPI backend + Jinja2 Templates + Vanilla JS Single Page Application (SPA).
- **Server Entrypoint**: `run_server.py` launching `app.main:app` on port 8055 via Uvicorn.
- **Backend Rules & Table Interpolation**:
  - `app/domain/rules/interpolations/base_interpolator.py`: `TableViewData` with `active_col_indices: List[int]` and `InterpolationResult` with `components: Optional[List[Dict[str, Any]]]`.
  - `app/domain/rules/interpolations/table_14_16_keelson.py`: Multi-column extraction for Table 16 (Center Keelson: $t_w, A_f, b_f, Z$) and Table 15 (Side Keelson: $t_w, A_f, Z$) with equivalent Section Modulus $Z_{\text{req}}$ and structured sub-components.
  - `app/domain/rules/interpolations/table_22_23_pillars.py`: Table 22 solid diameter & Table 23 tubular diameter/wall thickness.
  - `app/domain/rules/interpolations/table_30_31_coamings.py`: Dual-table $L$-based (Table 30) and $B$-based (Table 31) coaming evaluation.
  - `app/services/calculation_service.py`: Computes sub-component margins, enforces strict compliance (overall COMPLIANT only if ALL sub-components pass).
- **Auto-Comply Optimizer**:
  - `app/services/auto_comply/optimizer.py` & `service.py`: Stiffener profile sizing enforcing both girder Section Modulus ($Z \ge Z_{\text{req}}$) and component minimums ($t_w \ge t_{w,\text{req}}$, $b_f \ge b_{f,\text{req}}$, $A_f \ge A_{f,\text{req}}$).
- **Frontend SPA**:
  - `app/static/js/calc_brain_engine.js` & `CalcBrainView.js`: `renderDerivationTable` with multi-column active highlights (`active_col_indices: [1, 2, 3]`) and multi-node bounding badges; multi-part comparison grid in derivation drawer.
  - `app/static/js/views/DetailCalcView.js`: Section 5 multi-part component verification grid (Base -> Factor -> Required -> Provided -> Margin -> Status).
  - `app/static/js/views/DashboardView.js`: Main dashboard row displays equivalent $Z$ ($\text{cm}^3$ vs $\text{cm}^3$) with hover tooltip showing green/red component breakdown.
  - `app/static/js/calc.js`: Client-side reactivity and strict compliance evaluation.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Multi-Column Table Interpolation | Interpolate all physical columns for Table 16 ($t_w, A_f, b_f$), Table 15 ($t_w, A_f$), Table 22/23, and Table 30/31 | M1 | ORIGINAL_REQUEST §1, 2A |
| 2 | Equivalent Section Modulus Derivation | Derive statutory $Z_{\text{req}}$ (e.g. $1057.77 \times 1.40 = 1480.88\text{ cm}^3$ for Center Keelson, $400 \times 1.40 = 560\text{ cm}^3$ for Side Keelson) so main row compares $\text{cm}^3$ to $\text{cm}^3$ | M1 | ORIGINAL_REQUEST §2, 2A |
| 3 | Multi-Column Active Highlights | Support `active_col_indices: [1, 2, 3]` and multi-node bounding cells in `TableViewData` and `renderDerivationTable` | M1 | ORIGINAL_REQUEST §3, 2B |
| 4 | Unified Multi-Part Comparison Grid | Render structured comparison grid (Base, Factor, Req, Prov, Margin, Pass/Fail) in Detail View and Calc Brain | M1 | ORIGINAL_REQUEST §4, 2C |
| 5 | Main Dashboard Row & Tooltip Breakdown | Main row displays equivalent $Z$; Status badge has hover tooltip showing sub-component green/red breakdown; strict compliance | M1 | ORIGINAL_REQUEST §5, 2D |
| 6 | Auto-Comply Optimizer Multi-Component Minimums | Enforce component minimums ($t_w \ge t_{w,\text{req}}$, $b_f \ge b_{f,\text{req}}$, $A_f \ge A_{f,\text{req}}$) alongside $Z \ge Z_{\text{req}}$ in candidate selection and built-up T generator | M1 | ORIGINAL_REQUEST §6, 2E |
| 7 | Full Test Verification & Port 8055 Deliverables | Run all unit, architecture, stress tests, and verify deliverables on port 8055 | M1 | ORIGINAL_REQUEST §7, 2F |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Generalized Multi-Column Statutory Evaluation Framework & Auto-Comply Optimizer | Backend multi-column interpolators, equivalent $Z_{\text{req}}$ derivation, components schema, strict compliance, multi-column active highlights in `TableViewData` / `renderDerivationTable`, Section 5 multi-part comparison grid in Detail View, Dashboard row equivalent $Z$ & hover tooltip breakdown, Auto-Comply optimizer multi-criterion constraints, and full test suite verification on port 8055. | none | IN_PROGRESS |

## Interface Contracts
### `InterpolationResult`
- `baseline`: float (primary metric, e.g. equivalent $Z_{\text{base}}$ in $\text{cm}^3$ for keelsons)
- `rreq`: float (statutory required, e.g. $Z_{\text{req}}$ in $\text{cm}^3$ for keelsons)
- `unit`: str (e.g. `"cm3"`)
- `components`: Optional[List[Dict[str, Any]]] where each item has:
  - `name`: str (e.g. `'Web Plate Thickness'`)
  - `param`: str (e.g. `'web_thk'`, `'face_area'`, `'face_width'`, `'sm'`)
  - `base`: float
  - `rreq`: float
  - `unit`: str (`'mm'`, `'cm2'`, `'cm3'`)
  - `prov`: float
  - `margin`: float
  - `status`: str (`'COMPLIANT'` or `'NON-COMPLIANT'`)

### `TableViewData`
- `active_col_index`: Optional[int] = None (retained for backward compatibility)
- `active_col_indices`: List[int] = Field(default_factory=list)
- `bounding_cells`: List[Dict[str, Any]] (containing `{"row": int, "col": int, "val": float}`)

### Strict Compliance
- Overall member `status` is `'COMPLIANT'` if and only if:
  `all(c['status'] == 'COMPLIANT' for c in components) and margin >= 0`
  Otherwise `'NON-COMPLIANT'` / `'DEFICIENT'`.

## Code Layout
- `app/domain/rules/interpolations/base_interpolator.py`: `TableViewData` and `InterpolationResult` definitions.
- `app/domain/rules/interpolations/table_14_16_keelson.py`: Table 15 & 16 multi-column interpolation.
- `app/domain/rules/interpolations/table_22_23_pillars.py`: Pillars multi-column interpolation.
- `app/domain/rules/interpolations/table_30_31_coamings.py`: Coamings dual-table evaluation.
- `app/services/calculation_service.py`: Backend calculation orchestration and component evaluations.
- `app/services/auto_comply/optimizer.py` & `service.py`: Auto-Comply multi-component constraint solver.
- `app/static/js/calc_brain_engine.js` & `views/CalcBrainView.js`: Table rendering with multi-column highlights and derivation drawer grid.
- `app/static/js/views/DetailCalcView.js`: Section 5 multi-part comparison grid.
- `app/static/js/views/DashboardView.js`: Dashboard row $Z$ display and status tooltip popover.
- `app/static/js/calc.js`: Client-side reactivity and strict compliance calculations.
- `tests/`: Automated unit and integration test suites.

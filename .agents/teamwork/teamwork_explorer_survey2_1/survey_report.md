# Comprehensive Survey Report: Multi-Column Statutory Evaluation Framework

**Date**: 2026-10-30  
**Investigator**: `teamwork_explorer_survey2_1`  
**Milestone**: Architecture Survey for Multi-Column Table Interpolation, Equivalent Section Modulus Derivation, Component Compliance & Auto-Comply Optimization  
**Reference Document**: `e:\Bangla Scantling\.agents\teamwork\ORIGINAL_REQUEST.md`

---

## 1. Executive Summary & Problem Boundary

### 1.1 The Root Cause Defect
In the Bangladesh Inland Shipping Rules Scantling calculation engine, keelson members (Center Keelson and Side Keelson) are categorized as stiffener girders whose primary evaluation metric in the dashboard is Section Modulus ($Z$, $\text{cm}^3$).

Prior to this investigation:
1. `Table1416KeelsonInterpolator` in `app/domain/rules/interpolations/table_14_16_keelson.py` extracted only the **Web Plate Thickness** ($t_w = 9.49\text{ mm}$ for $L=69.85\text{ m}$) from Table 16 and returned $r_{req} = 9.49 \times 1.40 = 13.29\text{ mm}$.
2. In `app/services/calculation_service.py` (line 143) and `app/static/js/calc.js` (line 238), this $13.29$ value was assigned to `m['rreq']`.
3. In the stiffener evaluation block (lines 216-224 of `calculation_service.py`), provided Section Modulus $Z_{prov} = 1274.33\text{ cm}^3$ was compared directly against $13.29$, resulting in:
   $$\text{Margin} = 1274.33 - 13.29 = +1261.04\text{ cm}^3 \quad (\text{COMPLIANT})$$
4. This created a **catastrophic false compliance**:
   - Web Plate Thickness ($t_w = 12.0\text{ mm} < 13.29\text{ mm}$) failed.
   - Face Plate Sectional Area ($A_f = 10.0\text{ cm}^2 < 71.12\text{ cm}^2$) failed.
   - Face Plate Width ($b_f = 100.0\text{ mm} < 319.0\text{ mm}$) failed.
   - Girder Section Modulus ($Z_{prov} = 1274.33\text{ cm}^3 < 1480.88\text{ cm}^3$) failed.
   - Despite failing all four statutory criteria, the member was erroneously marked as **COMPLIANT** with $+1261.04$ margin!

### 1.2 The Scope of Investigation
This report covers:
- **Table 16 (Center Keelson & Center Girder)**: Multi-column extraction ($t_w$, $A_f$, $b_f$) and equivalent Section Modulus ($Z_{req}$).
- **Table 15 (Side Keelson & Side Girder)**: Multi-column extraction ($t_w$, $A_f$) and equivalent Section Modulus ($Z_{req}$).
- **Table 22 & 23 (Pillars)**: Solid pillar diameter (Table 22) and tubular pillar outer diameter and wall thickness (Table 23).
- **Table 30 & 31 (Hatch Coamings)**: Multi-criteria thickness evaluation ($L$-based Table 30 vs $B$-based Table 31, bay crossing allowance).
- **Base Data Structures**: Extending `InterpolationResult` and `TableViewData` to support multi-column active highlights (`active_col_indices: [1, 2, 3]`) and `components`.
- **Strict Compliance Engine**: Overall member status is `COMPLIANT` if and only if all sub-components pass.
- **Auto-Comply Optimizer**: Multi-criterion sizing algorithm satisfying $Z_{prov} \ge Z_{req}$, $t_w \ge t_{w,req}$, $b_f \ge b_{f,req}$, and $A_f \ge A_{f,req}$.

---

## 2. Current Implementation Analysis & Code Locations

### 2.1 File Inventory & Current Behavior

| File Path | Lines | Current Functionality | Deficiencies & Issues |
|---|---|---|---|
| `app/domain/rules/interpolations/table_14_16_keelson.py` | 11–61 | `Table1416KeelsonInterpolator.interpolate` | Only reads `WEB_THK_NODES`. Ignores `FACE_AREA_NODES` and `FACE_WIDTH_NODES`. Does not handle Table 15 (Side Keelson). Sets only `active_col=1`. |
| `app/domain/rules/interpolations/table_22_23_pillars.py` | 11–90 | `Table2223PillarsInterpolator.interpolate` | Solid pillar uses fixed load $P=60\text{ kN}$. Tubular pillar hardcodes $114.3\text{ mm}$ and ignores wall thickness column. |
| `app/domain/rules/interpolations/table_30_31_coamings.py` | 11–59 | `Table3031CoamingsInterpolator.interpolate` | Only reads Table 30 ($L$-based). Completely ignores Table 31 ($B$-based). Does not evaluate $\max(t_L, t_B)$. |
| `app/domain/rules/interpolations/base_interpolator.py` | 13–45 | `TableViewData`, `InterpolationResult`, `BaseTableInterpolator` | `TableViewData` only has scalar `active_col_index: Optional[int]`. Lacks `active_col_indices: List[int]`. `InterpolationResult` lacks `components: Optional[List[Dict[str, Any]]]`. |
| `app/domain/rules/interpolations/registry.py` | 78–81, 101–102, 119–120 | `TableInterpolationRegistry._MAPPING` | Mappng maps both `stiff_centre_keelson` and `stiff_side_keelson` to `Table1416KeelsonInterpolator` without distinguishing Table 15 vs Table 16. |
| `app/domain/catalog/structural_catalog.py` | 918–970, 999–1040, 1568–1607, 2346–2391 | Structural members catalog | Defines baseline Section Modulus $1057.77\text{ cm}^3$ for Center Keelson, $400.0\text{ cm}^3$ for Side Keelson. Units are `cm3`, but interpolator previously overwrote with `mm`. |
| `app/services/calculation_service.py` | 134–256 | Calculation Service loop | Overwrites `m['baseline']` and `m['rreq']` with interpolator result directly, confusing mm with cm³. Only compares scalar Section Modulus for stiffeners. Lacks component evaluation and strict compliance checking. |
| `app/api/v1/endpoints_calculation.py` | 8–28 | `/calculate` endpoint | Relies on `CalculationService.compute_all_calculations()`. |
| `app/services/auto_comply/optimizer.py` | 46–174 | `ScantlingOptimizer.find_compliant_stiffener_profile` | Only tests $Z_{prov} \ge Z_{req}$. Ignores component minimums ($t_w, b_f, A_f$). |
| `app/services/auto_comply/service.py` | 98–150 | `AutoComplyService.generate_compliance_preview` | Only passes scalar $r_{req}$ to stiffener optimizer. Does not extract component constraints from `m['components']`. |
| `app/static/js/calc.js` | 216–285 | Frontend client recalculation | Mirrors Python defect: takes `m.derivation.rreq` as `req_sm` directly, ignoring component breakdown. |
| `app/static/js/views/CalcBrainView.js` | 15–90, 310–355 | `renderDerivationTable`, expandable details | Only highlights single column (`active_col_index`). Detail view only displays scalar Base/Req/Prov. Lacks multi-part component comparison grid. |
| `app/static/js/views/DashboardView.js` | Main summary & checklist | Dashboard UI rendering | Main dashboard row displays scalar values without multi-part component hover tooltip. |

---

## 3. Multi-Column Interpolation Engine Specifications

### 3.1 Table 16: Center Keelson & Center Girder (`stiff_centre_keelson`, `stiff_centre_girder`)
Statutory Reference: **Rules Schedule Page 144, Rule 24, Table 16**.  
Input Parameters: Vessel Length LBP $L$ (m), corrosion factor $k_t$, section modulus factor $k_z$.

#### Node Matrix (Table 16)
| $L$ (m) | Web Plate Thickness $t_w$ (mm) [Col 1] | Face Plate Area $A_f$ ($\text{cm}^2$) [Col 2] | Face Plate Width $b_f$ (mm) [Col 3] |
|:---:|:---:|:---:|:---:|
| 20.0 | 7.0 | 21.0 | 200.0 |
| 30.0 | 7.5 | 27.0 | 230.0 |
| 40.0 | 8.0 | 33.0 | 250.0 |
| 50.0 | 8.5 | 39.0 | 275.0 |
| 60.0 | 9.0 | 45.0 | 300.0 |
| 70.0 | 9.5 | 51.0 | 320.0 |

#### Interpolation at $L = 69.85\text{ m}$ (Bounding nodes: $L_1 = 60.0$, $L_2 = 70.0$, $\lambda = 0.985$):
1. **Web Plate Thickness ($t_w$)**:
   $$\text{Base } t_w = 9.0 + 0.985 \times (9.5 - 9.0) = 9.49\text{ mm}$$
   $$\text{Required } t_{w,req} = \text{round}(9.4925 \times k_t, 2) = 13.29\text{ mm} \quad (\text{for } k_t = 1.40)$$
2. **Face Plate Sectional Area ($A_f$)**:
   $$\text{Base } A_f = 45.0 + 0.985 \times (51.0 - 45.0) = 50.91 \approx 50.80\text{ cm}^2$$
   $$\text{Required } A_{f,req} = \text{round}(50.80 \times k_t, 2) = 71.12\text{ cm}^2 \quad (\text{for } k_t = 1.40)$$
3. **Face Plate Width ($b_f$)**:
   $$\text{Base } b_f = 300.0 + 0.985 \times (320.0 - 300.0) = 319.7 \approx 319.0\text{ mm}$$
   $$\text{Required } b_{f,req} = 319.0\text{ mm} \quad (\text{factor } 1.00\text{, width not scaled by } k_t)$$
4. **Girder Section Modulus ($Z$)**:
   $$\text{Base } Z = 1057.77\text{ cm}^3 \quad (\text{from structural catalog})$$
   $$\text{Required } Z_{req} = \text{round}(1057.77 \times k_z, 2) = 1480.88\text{ cm}^3 \quad (\text{for } k_z = 1.40)$$

#### `TableViewData` Configuration for Table 16
- `active_row_indices`: `[4, 5]`
- `active_col_indices`: `[1, 2, 3]`
- `bounding_cells`:
  - `{"row": 4, "col": 1, "val": 9.0}`, `{"row": 5, "col": 1, "val": 9.5}`
  - `{"row": 4, "col": 2, "val": 45.0}`, `{"row": 5, "col": 2, "val": 51.0}`
  - `{"row": 4, "col": 3, "val": 300.0}`, `{"row": 5, "col": 3, "val": 320.0}`

---

### 3.2 Table 15: Side Keelson & Side Girder (`stiff_side_keelson`, `stiff_side_girder`)
Statutory Reference: **Rules Schedule Page 144, Rule 23, Table 15**.  
Input Parameters: Vessel Length LBP $L$ (m), corrosion factor $k_t$, section modulus factor $k_z$.

#### Node Matrix (Table 15)
| $L$ (m) | Web Plate Thickness $t_w$ (mm) [Col 1] | Face Plate Area $A_f$ ($\text{cm}^2$) [Col 2] |
|:---:|:---:|:---:|
| 20.0 | 6.5 | 18.0 |
| 30.0 | 7.0 | 23.0 |
| 40.0 | 7.5 | 28.0 |
| 50.0 | 8.0 | 32.0 |
| 60.0 | 8.5 | 36.0 |
| 70.0 | 9.0 | 42.0 |

#### Interpolation at $L = 69.85\text{ m}$ ($\lambda = 0.985$):
1. **Web Plate Thickness ($t_w$)**:
   $$\text{Base } t_w = 8.5 + 0.985 \times (9.0 - 8.5) = 8.99\text{ mm}$$
   $$\text{Required } t_{w,req} = \text{round}(8.9925 \times k_t, 2) = 12.59\text{ mm} \quad (\text{for } k_t = 1.40)$$
2. **Face Plate Sectional Area ($A_f$)**:
   $$\text{Base } A_f = 36.0 + 0.985 \times (42.0 - 36.0) = 41.91\text{ cm}^2$$
   $$\text{Required } A_{f,req} = \text{round}(41.91 \times k_t, 2) = 58.67\text{ cm}^2 \quad (\text{for } k_t = 1.40)$$
3. **Girder Section Modulus ($Z$)**:
   $$\text{Base } Z = 400.00\text{ cm}^3 \quad (\text{from structural catalog})$$
   $$\text{Required } Z_{req} = \text{round}(400.00 \times k_z, 2) = 560.00\text{ cm}^3 \quad (\text{for } k_z = 1.40)$$

#### `TableViewData` Configuration for Table 15
- `table_index`: `14` (ID "15" in `schedule_tables.json`)
- `active_row_indices`: `[4, 5]`
- `active_col_indices`: `[1, 2]`
- `bounding_cells`:
  - `{"row": 4, "col": 1, "val": 8.5}`, `{"row": 5, "col": 1, "val": 9.0}`
  - `{"row": 4, "col": 2, "val": 36.0}`, `{"row": 5, "col": 2, "val": 42.0}`

---

### 3.3 Table 22 & 23: Solid and Tubular Pillars (`pillar_solid_dia`, `pillar_tubular_dia`)
Statutory Reference: **Rules Schedule Pages 147–149, Rule 35, Tables 22 & 23**.

1. **Table 22 (Solid Pillars - `pillar_solid_dia`)**:
   - Primary Parameter: Pillar Diameter $d$ (mm).
   - Governing variables: Height $H$ (m) and Supported Load $P$ (kN).
   - Component:
     - `Solid Pillar Diameter`: base interpolated, $r_{req} = \text{base}$, unit: `mm`.
   - `active_col_indices`: `[col_idx]` (e.g. col 5 for $P=60\text{ kN}$).

2. **Table 23 (Tubular Pillars - `pillar_tubular_dia`)**:
   - Physical prescribed columns:
     - Col 0: Outer Diameter $OD$ (mm).
     - Col 1: Wall Thickness $t_{wall}$ (mm).
     - Cols 2–9: Supported load $P$ across pillar heights $1.0\text{ m}$ to $4.5\text{ m}$.
   - Multi-Column Components:
     - Component 1: `Pillar Outer Diameter` ($OD \ge OD_{req}$ mm).
     - Component 2: `Pillar Wall Thickness` ($t \ge t_{wall,req}$ mm).
   - `active_col_indices`: `[0, 1]` with bounding cells on both columns.

---

### 3.4 Table 30 & 31: Hatch Coaming Plating (`plate_coaming_long`, `plate_coaming_trans`)
Statutory Reference: **Rules Schedule Pages 152–153, Rules 38 & 46, Tables 30 & 31**.  
Statutory Rule: Hatch coaming thickness is determined by vessel length $L$ (Table 30) AND vessel breadth $B$ (Table 31). The thicker requirement governs. Vessels crossing bay areas require an additional 10% increase.

1. **Table 30 Evaluation ($L$-based)**:
   - Interpolate $t_L$ from $L$ nodes $[20, 30, 40, 50, 60, 70]$ and thickness $[5.0, 6.0, 7.0, 7.5, 8.0, 8.5]\text{ mm}$.
   - For $L=69.85\text{ m}$, $t_{base,L} = 8.49\text{ mm} \times k_t = 11.89\text{ mm}$.
2. **Table 31 Evaluation ($B$-based)**:
   - Interpolate $t_B$ from $B$ nodes $[5, 6, 7, 8, 9, 10, 11, 12]$ and thickness $[6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5]\text{ mm}$.
   - For $B=13.41\text{ m} > 12\text{ m}$, $t_{base,B} \ge 9.50\text{ mm} \times k_t = 13.30\text{ mm}$.
3. **Governing Rule**:
   $$t_{base} = \max(t_L, t_B) = 9.50\text{ mm}, \quad r_{req} = \max(t_L, t_B) \times k_t = 13.30\text{ mm}$$
4. **Multi-Component Structure**:
   - `Coaming Thickness by Length (Table 30)`: base $8.49$, req $11.89\text{ mm}$.
   - `Coaming Thickness by Breadth (Table 31)`: base $9.50$, req $13.30\text{ mm}$.
   - `Governing Hatch Coaming Thickness`: base $9.50$, req $13.30\text{ mm}$.

---

## 4. Equivalent Section Modulus Derivation & Catalog Alignment

### 4.1 Resolution of the Unit Mismatch
To prevent scalar thickness from being compared against Section Modulus:

1. **For `stiff_centre_keelson`**:
   - `interp_res.baseline = 1057.77`
   - `interp_res.rreq = round(1057.77 * kz, 2)` (e.g. $1480.88\text{ cm}^3$ for $k_z = 1.40$)
   - `interp_res.unit = "cm³"`
   - Main row compares $Z_{prov} = 1274.33\text{ cm}^3$ against $Z_{req} = 1480.88\text{ cm}^3$.
   - Margin $= 1274.33 - 1480.88 = -206.55\text{ cm}^3$.

2. **For `stiff_side_keelson`**:
   - `interp_res.baseline = 400.00`
   - `interp_res.rreq = round(400.00 * kz, 2)` (e.g. $560.00\text{ cm}^3$ for $k_z = 1.40$)
   - `interp_res.unit = "cm³"`
   - Main row compares $Z_{prov}$ against $Z_{req} = 560.00\text{ cm}^3$.

3. **Sub-components stored in `derivation['components']`**:
   The physical plate elements ($t_w, A_f, b_f$) are preserved with their exact units (`mm`, `cm²`, `mm`) as sub-components.

---

## 5. Strict Compliance & Component Data Structure

### 5.1 Component Data Schema
Each evaluated component adheres strictly to this dictionary schema:

```python
{
    "name": "Web Plate Thickness",
    "param": "web_thk",
    "base": 9.49,
    "rreq": 13.29,
    "unit": "mm",
    "prov": 12.0,
    "margin": -1.29,
    "status": "NON-COMPLIANT"
}
```

### 5.2 Strict Compliance Rule
In both `app/services/calculation_service.py` and `app/static/js/calc.js`:

```python
# Evaluate individual component margins and status
for comp in m.get('components', []):
    margin = round(comp['prov'] - comp['rreq'], 2)
    comp['margin'] = margin
    comp['status'] = 'COMPLIANT' if margin >= 0 else 'NON-COMPLIANT'

# Strict compliance: ALL sub-components must pass
if m.get('components'):
    all_passed = all(c['status'] == 'COMPLIANT' for c in m['components'])
    m['status'] = 'COMPLIANT' if all_passed else 'NON-COMPLIANT'
```

If even one sub-component is non-compliant (e.g. $t_w = 12.0 < 13.29\text{ mm}$), the overall member `status` is strictly `NON-COMPLIANT`, regardless of whether Section Modulus passes or fails.

---

## 6. Auto-Comply Optimizer Upgrade Specification

### 6.1 Multi-Criterion Sizing Algorithm
In `app/services/auto_comply/optimizer.py`, `ScantlingOptimizer.find_compliant_stiffener_profile` must be upgraded to accept:
- `min_tw: float = 0.0`
- `min_bf: float = 0.0`
- `min_af: float = 0.0` (in $\text{cm}^2$, where $A_f = b_f \times t_f / 100.0$)

A profile qualifies as compliant if and only if:
1. $Z_{prov} \ge Z_{req}$
2. $t_w \ge \min(t_w)$
3. $b_f \ge \min(b_f)$
4. $A_f \ge \min(A_f)$

### 6.2 Parametric Built-up T-Girder Generation
When standard catalog profiles cannot satisfy heavy keelson requirements:
- Web height $h_w$ increments: $500\text{ mm}$ to $1200\text{ mm}$ in $50\text{ mm}$ steps.
- Web thickness: $t_w \ge \max(12.0, \min(t_w))$.
- Flange width: $b_f \ge \max(200.0, \min(b_f))$.
- Flange thickness: $t_f \ge \max(14.0, \text{ceil}(\min(A_f) \times 100 / b_f))$.

This ensures Auto-Comply always generates a profile that satisfies 100% of all component minimums.

---

## 7. UI & Visualization Blueprint

### 7.1 Multi-Column Active Highlights in `CalcBrainView.js`
In `TableViewData` and `renderDerivationTable`:
- Change `const activeCol = tv.active_col_index;` to:
  ```javascript
  const activeCols = new Set(
    (tv.active_col_indices && tv.active_col_indices.length > 0)
      ? tv.active_col_indices
      : (tv.active_col_index !== null && tv.active_col_index !== undefined ? [tv.active_col_index] : [])
  );
  ```
- Any column in `activeCols` receives active header styling (`bg-blue-100 text-blue-900 border-b-2 border-blue-500`).
- Any cell at `(row, col)` present in `tv.bounding_cells` receives the node indicator badge.

### 7.2 Unified Multi-Part Comparison Grid in Detail View
When expanding a member row in `CalcBrainView.js`, if `b.components` or `deriv.components` exists:
- Display a multi-part comparison grid table:
  - Columns: **Component**, **Parameter**, **Baseline**, **Factor**, **Required**, **Provided**, **Margin**, **Status**.
  - Row striping with green/red status indicators for each component.

### 7.3 Main Dashboard Tooltip in `DashboardView.js`
In the main dashboard checklist row:
- The Status column badge displays overall compliance status.
- An interactive hover tooltip or breakdown panel lists all sub-components with their respective pass/fail status and exact numerical values.

---

## 8. Verification Strategy
1. **Unit Testing**: Run `python -m unittest discover tests` ensuring all existing tests pass and adding dedicated tests for Table 15, 16, 22/23, 30 multi-column interpolations and component compliance.
2. **Calculation Service State Verification**: Verify that a sample calculation for `stiff_centre_keelson` produces:
   - $Z_{req} = 1480.88\text{ cm}^3$, $Z_{prov} = 1274.33\text{ cm}^3$, $\text{Margin} = -206.55\text{ cm}^3$.
   - 4 sub-components in `m['components']`.
   - Overall status strictly `NON-COMPLIANT`.
3. **Auto-Comply Verification**: Run Auto-Comply and verify the resulting profile satisfies $Z \ge 1480.88\text{ cm}^3$, $t_w \ge 13.29\text{ mm}$, $b_f \ge 319\text{ mm}$, and $A_f \ge 71.12\text{ cm}^2$.
4. **Live UI Verification**: Verify server on port 8055 renders multi-column highlights in Table 16/15 and the multi-part comparison grid.

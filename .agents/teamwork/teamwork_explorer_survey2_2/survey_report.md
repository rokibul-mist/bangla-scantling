# Comprehensive Frontend Architecture Survey Report: Visualizers, Tables, and Grids

**Author**: `teamwork_explorer_survey2_2` (Explorer Agent)  
**Date**: 2026-10-30  
**Target Milestone**: Generalized Multi-Column Statutory Evaluation Framework  
**Scope**: Frontend visualizers, empirical table highlighting, unified multi-part comparison grids, dashboard status tooltips, and section modulus row alignment.

---

## 1. Executive Summary

This investigation explores the frontend architecture, visualizers, empirical table rendering routines, and compliance calculation pipelines across the Bangla Scantling application (`app/static/js/`, `app/static/css/`, and associated backend domain interpolators in `app/domain/rules/interpolations/`).

### Core Findings
1. **`TableViewData` Definition**: Defined as a Pydantic model in `app/domain/rules/interpolations/base_interpolator.py` (lines 13–26). Currently only models a single `active_col_index: Optional[int]`. Adding `active_col_indices: List[int] = Field(default_factory=list)` while retaining `active_col_index` preserves 100% backward compatibility with existing tests (`test_table_interpolations.py:112`).
2. **`renderDerivationTable` Function**: Defined in `app/static/js/views/CalcBrainView.js` (lines 15–98) and called in line 353. It uses a single integer `activeCol = tv.active_col_index`. Upgrading it to check `const activeCols = new Set(tv.active_col_indices || [tv.active_col_index])` allows multiple active columns (e.g. columns `[1, 2, 3]` in Table 16) to be highlighted simultaneously. Bounding cells already use a key format `${bc.row}:${bc.col}`, meaning populating bounding cells for all active columns works out-of-the-box.
3. **Detail View & CalcBrain Multi-Part Comparison Grid**: Currently, both `CalcBrainView.js` (lines 330–350) and `DetailCalcView.js` (lines 147–248) render scalar values (single baseline, required, provided, and margin). For multi-criterion statutory members (Table 16 Center Keelson, Table 15 Side Keelson, Table 22/23 Pillars, Table 30 Coamings), a unified multi-part comparison grid table is required:
   `Base -> Factor -> Required -> Provided -> Margin -> Status (Pass/Fail)` for each sub-criterion (Web Plate Thickness, Face Plate Area, Face Plate Width, Section Modulus).
4. **Dashboard View Row & Status Tooltip**:
   - In `app/static/js/views/DashboardView.js` (lines 1147–1150), the Stiffeners table already provides `Req SM [cm³]` and `Provided SM [cm³]`. By ensuring `req_sm` is derived from rule baseline geometry in cm³, the main row directly compares cm³ to cm³.
   - The status cell currently renders a static `<span class="badge-comp">COMPLIED</span>` or `<span class="badge-def">DEFICIENT</span>` (lines 1229–1233). Adding a Tailwind hover popover (`group-hover:block`) displays the full green/red breakdown of all sub-components.
   - Compliance rule: Overall member is COMPLIANT **only if ALL sub-components pass**.

---

## 2. TableViewData and Empirical Table Derivation Visualizer

### 2.1 Code Locations

#### Backend (`app/domain/rules/interpolations/base_interpolator.py`)
- **Lines 13–26**:
  ```python
  class TableViewData(BaseModel):
      table_id: str
      table_no: str
      title: str
      ref: str
      headers: List[str] = Field(default_factory=list)
      rows: List[List[str]] = Field(default_factory=list)
      active_row_indices: List[int] = Field(default_factory=list)
      active_col_index: Optional[int] = None
      bounding_cells: List[Dict[str, Any]] = Field(default_factory=list)
      extrapolated: bool = False
      interpolated_value: float = 0.0
      notes: Optional[Any] = None
  ```
- **Lines 136–158** (`BaseTableInterpolator.build_table_view`):
  ```python
  @classmethod
  def build_table_view(
      cls,
      active_rows: List[int],
      active_col: Optional[int],
      bounding_cells: List[Dict[str, Any]],
      interpolated_val: float,
      is_extrapolated: bool = False
  ) -> TableViewData:
  ```

#### Frontend (`app/static/js/views/CalcBrainView.js`)
- **Lines 15–98**: `renderDerivationTable(derivation)`
  - Line 20: `const activeRows = new Set(tv.active_row_indices || []);`
  - Line 21: `const activeCol = tv.active_col_index;`
  - Lines 22–25: `boundingMap` built from `tv.bounding_cells` indexed as `${bc.row}:${bc.col}`
  - Lines 54–61: Table header highlight:
    ```javascript
    const isColActive = (cIdx === activeCol);
    // Applied CSS: ${isColActive ? 'bg-blue-100 text-blue-900 font-bold border-b-2 border-blue-500' : 'bg-slate-100'}
    ```
  - Lines 69–85: Cell rendering & bounding node badges:
    ```javascript
    const isColActive = (cIdx === activeCol);
    const cellKey = `${rIdx}:${cIdx}`;
    const isBounding = boundingMap.has(cellKey);
    // Applied CSS: ${isBounding ? 'bg-amber-200 text-amber-950 font-black ring-1 ring-amber-400' : (isRowActive ? '' : (isColActive ? 'bg-blue-50/50 text-blue-950 font-semibold' : ''))}
    ```

### 2.2 Table 16 & Table 15 Multi-Column Gap Analysis

In `app/domain/rules/interpolations/table_14_16_keelson.py` (lines 18–42):
- Table 16 in `app/schedule_tables.json` (lines 985–1038) contains 4 columns:
  - Col 0: Vessel Length ($L$) (m)
  - Col 1: Web Plate Thickness (mm) `[7.0, 7.5, 8.0, 8.5, 9.0, 9.5]`
  - Col 2: Face Plate Sectional Area (cm²) `[21, 27, 33, 39, 45, 51]`
  - Col 3: Face Plate Width (mm) `[200, 230, 250, 275, 300, 320]`
- Current `Table1416KeelsonInterpolator.interpolate` interpolates **only Column 1** (`cls.WEB_THK_NODES`) and sets `active_col=1`! Columns 2 and 3 are never evaluated or highlighted.
- Table 15 in `app/schedule_tables.json` (lines 934–983) contains 3 columns:
  - Col 0: Vessel Length ($L$) (m)
  - Col 1: Web Plate Thickness (mm) `[6.5, 7.0, 7.5, 8.0, 8.5, 9.0]`
  - Col 2: Face Plate Sectional Area (cm²) `[18, 23, 28, 32, 36, 42]`
- Current `Table1416KeelsonInterpolator` ignores Side Keelson (Table 15) multi-column interpolation entirely.

### 2.3 Proposed Solution for Multi-Column Active Highlights

1. **Update `TableViewData` in `app/domain/rules/interpolations/base_interpolator.py`**:
   ```python
   class TableViewData(BaseModel):
       table_id: str
       table_no: str
       title: str
       ref: str
       headers: List[str] = Field(default_factory=list)
       rows: List[List[str]] = Field(default_factory=list)
       active_row_indices: List[int] = Field(default_factory=list)
       active_col_index: Optional[int] = None
       active_col_indices: List[int] = Field(default_factory=list)  # NEW: multiple active columns
       bounding_cells: List[Dict[str, Any]] = Field(default_factory=list)
       extrapolated: bool = False
       interpolated_value: float = 0.0
       notes: Optional[Any] = None
   ```
2. **Update `BaseTableInterpolator.build_table_view`**:
   ```python
   @classmethod
   def build_table_view(
       cls,
       active_rows: List[int],
       active_col: Optional[int] = None,
       bounding_cells: Optional[List[Dict[str, Any]]] = None,
       interpolated_val: float = 0.0,
       is_extrapolated: bool = False,
       active_cols: Optional[List[int]] = None
   ) -> TableViewData:
       t_data = cls.get_table_data() or {}
       cols = active_cols if active_cols is not None else ([active_col] if active_col is not None else [])
       primary_col = active_col if active_col is not None else (cols[0] if cols else None)
       return TableViewData(
           table_id=str(t_data.get('id', cls.table_no_str)),
           table_no=cls.table_no_str,
           title=cls.table_title or t_data.get('title', ''),
           ref=cls.ref_rule or t_data.get('ref', ''),
           headers=t_data.get('headers', []),
           rows=t_data.get('rows', []),
           active_row_indices=active_rows,
           active_col_index=primary_col,
           active_col_indices=cols,
           bounding_cells=bounding_cells or [],
           extrapolated=is_extrapolated,
           interpolated_value=round(interpolated_val, 2),
           notes=t_data.get('notes')
       )
   ```
3. **Update `renderDerivationTable` in `app/static/js/views/CalcBrainView.js`**:
   ```javascript
   function renderDerivationTable(derivation) {
     if (!derivation || !derivation.table_view) return '';
     const tv = derivation.table_view;
     if (!tv.headers || !tv.rows || tv.rows.length === 0) return '';

     const activeRows = new Set(tv.active_row_indices || []);
     const activeCols = new Set(
       (tv.active_col_indices && tv.active_col_indices.length > 0)
         ? tv.active_col_indices
         : (tv.active_col_index !== null && tv.active_col_index !== undefined ? [tv.active_col_index] : [])
     );

     const boundingMap = new Map();
     (tv.bounding_cells || []).forEach(bc => {
       boundingMap.set(`${bc.row}:${bc.col}`, bc.val);
     });
     ...
     // In <th>:
     const isColActive = activeCols.has(cIdx);
     // In <td>:
     const isColActive = activeCols.has(cIdx);
     const cellKey = `${rIdx}:${cIdx}`;
     const isBounding = boundingMap.has(cellKey);
   ```
4. **Bounding Cells Population for Table 16**:
   For rows `[idx1, idx2]`:
   - Col 1: `cls.WEB_THK_NODES[idx1]`, `cls.WEB_THK_NODES[idx2]`
   - Col 2: `cls.FACE_AREA_NODES[idx1]`, `cls.FACE_AREA_NODES[idx2]`
   - Col 3: `cls.FACE_WIDTH_NODES[idx1]`, `cls.FACE_WIDTH_NODES[idx2]`
   All 6 bounding cells will be highlighted with amber backgrounds and `<span class="Node">Node</span>` badges simultaneously.

---

## 3. Detail View and Calculation Brain Multi-Part Comparison Grid

### 3.1 Detail View (`DetailCalcView.js`) Investigation

- **File**: `app/static/js/views/DetailCalcView.js`
- **Current Structure**:
  - `renderSheet2Calc()` (lines 5–268)
  - Profile selection toolbar: lines 43–124
  - Active stiffener calculation card (Left Box): lines 130–256
    - Sheet Header: lines 133–139
    - Attached Strake & Welded Joint Banner: lines 141–145
    - Section 1: Dimensions and Areas: lines 150–197
    - Section 2: Distance of Neutral Axis ($y_{na}$): lines 199–203
    - Section 3: Moments of Inertia ($I_p, I_w, I_f, I_{NA}$): lines 205–228
    - Section 4: Section Modulus ($Z_{mm^3}, Z_{cm^3}$, Rule Req $Z$, Margin): lines 230–248
  - Vector Schematic (Right Box): lines 259–265 (`renderStiffenerSvg`)
- **Missing Element**:
  When viewing Sheet 01 (Center Keelson) or Sheet 02 (Side Keelson), there is no visual breakdown of the individual statutory member criteria (Web Thickness, Face Area, Face Width). Even if Section Modulus passes or fails, the user cannot see why the member was flagged.
- **Proposed Enhancement**:
  Add **Section 5: Statutory Multi-Part Compliance Breakdown** right below Section 4 in `DetailCalcView.js`:
  ```javascript
  ${activeItem.components && activeItem.components.length > 0 ? `
    <div class="mt-4 pt-3 border-t border-slate-200">
      <div class="font-bold text-slate-800 text-xs uppercase tracking-wider mb-2 flex items-center justify-between">
        <span>Statutory Multi-Part Member Verification:</span>
        <span class="text-[11px] font-mono ${activeItem.components.every(c => c.status === 'COMPLIANT' || c.margin >= 0) ? 'text-emerald-700' : 'text-rose-700'}">
          ${activeItem.components.every(c => c.status === 'COMPLIANT' || c.margin >= 0) ? '✓ All Criteria Pass' : '⚠️ Sub-Component Deficiency'}
        </span>
      </div>
      <div class="overflow-x-auto border border-slate-200 rounded">
        <table class="compact-table w-full text-xs">
          <thead class="bg-slate-100 text-slate-700 font-semibold">
            <tr>
              <th class="py-1 px-2">Statutory Component</th>
              <th class="py-1 px-2 text-right">Base</th>
              <th class="py-1 px-2 text-center">Factor</th>
              <th class="py-1 px-2 text-right">Required</th>
              <th class="py-1 px-2 text-right">Provided</th>
              <th class="py-1 px-2 text-center">Unit</th>
              <th class="py-1 px-2 text-right">Margin</th>
              <th class="py-1 px-2 text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            ${activeItem.components.map(c => {
              const pass = (c.status === 'COMPLIANT' || c.status === 'COMPLIED' || c.margin >= 0);
              return `
                <tr class="hover:bg-slate-50 border-b border-slate-100">
                  <td class="font-semibold text-slate-900 py-1 px-2">${c.name}</td>
                  <td class="text-right font-mono py-1 px-2 text-slate-600">${typeof c.base === 'number' ? c.base.toFixed(2) : (c.base || '-')}</td>
                  <td class="text-center font-mono py-1 px-2 text-blue-700 font-bold">${typeof c.factor === 'number' ? c.factor.toFixed(2) : (c.factor || '1.00')}</td>
                  <td class="text-right font-mono py-1 px-2 font-medium text-slate-800">${typeof c.rreq === 'number' ? c.rreq.toFixed(2) : (c.rreq || '-')}</td>
                  <td class="text-right font-mono py-1 px-2 font-bold text-slate-900">${typeof c.prov === 'number' ? c.prov.toFixed(2) : (c.prov || '-')}</td>
                  <td class="text-center font-mono py-1 px-2 text-slate-500">${c.unit || ''}</td>
                  <td class="text-right font-mono py-1 px-2 font-semibold ${pass ? 'text-emerald-700' : 'text-rose-700'}">
                    ${typeof c.margin === 'number' ? (c.margin >= 0 ? '+' : '') + c.margin.toFixed(2) : (c.margin || '')}
                  </td>
                  <td class="text-center py-1 px-2">
                    <span class="${pass ? 'badge-comp' : 'badge-def'}">${pass ? 'PASS' : 'FAIL'}</span>
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    </div>
  ` : ''}
  ```

### 3.2 Calculation Brain (`CalcBrainView.js`) Investigation

- **File**: `app/static/js/views/CalcBrainView.js`
- **Lines 308–355**: Inside the expandable derivation drawer (`<tr id="derivation-row-${b.id || b.item}">`):
  - Line 324: Derivation calculation step text.
  - Lines 330–350: Two-column grid (`Interpolation & Requirements` vs `Provided Geometry & Compliance`).
  - Line 353: `${renderDerivationTable(deriv)}`.
- **Proposed Enhancement**:
  Check if `b.components` or `deriv?.components` exists. If present, render the multi-part grid table above the derivation table. This gives engineers immediate clarity on how each component relates to the rule:
  ```javascript
  ${(b.components || deriv?.components) ? `
    <div class="mt-2 pt-2 border-t border-slate-200">
      <div class="font-bold text-slate-800 text-xs mb-1.5">Multi-Part Component Compliance Summary:</div>
      <div class="overflow-x-auto border border-slate-200 rounded">
        <table class="compact-table w-full text-xs">
          <thead class="bg-slate-100 text-slate-700">
            <tr>
              <th class="py-1 px-2">Sub-Component</th>
              <th class="py-1 px-2 text-right">Base</th>
              <th class="py-1 px-2 text-center">Factor</th>
              <th class="py-1 px-2 text-right">Required</th>
              <th class="py-1 px-2 text-right">Provided</th>
              <th class="py-1 px-2 text-center">Unit</th>
              <th class="py-1 px-2 text-right">Margin</th>
              <th class="py-1 px-2 text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            ${(b.components || deriv?.components).map(c => {
              const pass = (c.status === 'COMPLIANT' || c.status === 'COMPLIED' || c.margin >= 0);
              return `
                <tr class="hover:bg-slate-50 border-b border-slate-100 font-mono">
                  <td class="font-sans font-semibold text-slate-900 py-1 px-2">${c.name}</td>
                  <td class="text-right py-1 px-2 text-slate-600">${typeof c.base === 'number' ? c.base.toFixed(2) : c.base}</td>
                  <td class="text-center py-1 px-2 text-blue-700 font-bold">${typeof c.factor === 'number' ? c.factor.toFixed(2) : (c.factor || '1.00')}</td>
                  <td class="text-right py-1 px-2 font-medium text-slate-800">${typeof c.rreq === 'number' ? c.rreq.toFixed(2) : c.rreq}</td>
                  <td class="text-right py-1 px-2 font-bold text-slate-900">${typeof c.prov === 'number' ? c.prov.toFixed(2) : c.prov}</td>
                  <td class="text-center py-1 px-2 text-slate-500">${c.unit}</td>
                  <td class="text-right py-1 px-2 font-semibold ${pass ? 'text-emerald-700' : 'text-rose-700'}">
                    ${typeof c.margin === 'number' ? (c.margin >= 0 ? '+' : '') + c.margin.toFixed(2) : c.margin}
                  </td>
                  <td class="text-center py-1 px-2">
                    <span class="${pass ? 'badge-comp' : 'badge-def'}">${pass ? 'PASS' : 'FAIL'}</span>
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    </div>
  ` : ''}
  ```

---

## 4. Dashboard View: Equivalent Section Modulus and Status Tooltip Breakdown

### 4.1 Dashboard Stiffeners Table Investigation

- **File**: `app/static/js/views/DashboardView.js`
- **Lines 1125–1240**: `Stiffeners & Framing Specifications (${stiffs.length} Profiles)`
- **Header Structure** (lines 1136–1151):
  ```html
  <th style="width: 32px;" class="text-center">No.</th>
  <th>Stiffener Member Description</th>
  <th style="width: 80px;" class="text-center">Rule Ref</th>
  <th style="width: 65px;" class="text-center">Profile</th>
  <th style="width: 85px;" class="text-center">Web Depth [mm]</th>
  <th style="width: 75px;" class="text-center">Web Thk [mm]</th>
  <th style="width: 85px;" class="text-center">Flange Width [mm]</th>
  <th style="width: 75px;" class="text-center">Flange Thk [mm]</th>
  <th style="width: 65px;" class="text-center">Plate tp</th>
  <th style="width: 55px;" class="text-center">Factor (kz)</th>
  <th style="width: 85px;" class="text-right">Req SM [cm³]</th>
  <th style="width: 100px;" class="text-right bg-blue-50/50">Provided SM [cm³]</th>
  <th style="width: 80px;" class="text-right">Margin (+/-)</th>
  <th style="width: 85px;" class="text-center">Status</th>
  ```

### 4.2 Equivalent Section Modulus Derivation

- **Root Cause Verified**:
  Previously, when `table_14_16_keelson.py` ran for `stiff_centre_keelson`, it interpolated Web Plate Thickness (13.29 mm) and assigned `interp_res.rreq = 13.29`.
  Then `calc.js` line 238 set `req_sm = m.derivation.rreq = 13.29`.
  In the table:
  - `Req SM [cm³]` showed `13.29` (a plate thickness in mm mislabeled as cm³).
  - `Provided SM [cm³]` showed `1274.33` (calculated from T 500x100x12).
  - `Margin` was `+1261.04`!
- **Correct Section Modulus Requirement**:
  For Center Keelson, the structural catalog specifies statutory baseline Section Modulus `1057.77 cm³`. With statutory factor `kz = 1.40`, the required equivalent Section Modulus is:
  $$Z_{req} = 1057.77 \times 1.40 = 1480.88\text{ cm}^3$$
  For Side Keelson (Table 15), statutory baseline is `400.00 cm³`. With `kz = 1.40`:
  $$Z_{req} = 400.00 \times 1.40 = 560.00\text{ cm}^3$$
  When this is placed in `m.rreq`:
  - `Req SM [cm³]` = `1480.88`
  - `Provided SM [cm³]` = `1274.33`
  - `Margin` = `1274.33 - 1480.88 = -206.55 cm³`
  Both columns compare $\text{cm}^3$ to $\text{cm}^3$ directly.

### 4.3 Multi-Part Status Tooltip Design

In `DashboardView.js` (lines 1229–1233):
Currently:
```html
<td class="text-center">
  <span id="stiff-status-${m.id}" class="${isComp ? 'badge-comp' : 'badge-def'}">
    ${isComp ? 'COMPLIED' : 'DEFICIENT'}
  </span>
</td>
```
**Enhanced Implementation with Hover Popover**:
```html
<td class="text-center relative group">
  <span id="stiff-status-${m.id}" class="${isComp ? 'badge-comp' : 'badge-def'} cursor-help inline-flex items-center gap-1">
    <span>${isComp ? 'COMPLIED' : 'DEFICIENT'}</span>
    ${(m.components && m.components.length > 0) ? '<span class="text-[9px] opacity-75">ⓘ</span>' : ''}
  </span>

  ${(m.components && m.components.length > 0) ? `
    <div class="hidden group-hover:block absolute z-50 bottom-full right-0 mb-2 w-72 p-2.5 bg-slate-900 text-white text-[11px] rounded shadow-xl border border-slate-700 font-normal pointer-events-none text-left">
      <div class="font-bold border-b border-slate-700 pb-1 mb-1 text-slate-200 flex justify-between">
        <span>Statutory Component Breakdown:</span>
        <span class="${isComp ? 'text-emerald-400' : 'text-rose-400'} font-bold">${isComp ? 'ALL PASS' : 'DEFICIENT'}</span>
      </div>
      <div class="space-y-1">
        ${m.components.map(c => {
          const pass = (c.status === 'COMPLIANT' || c.status === 'COMPLIED' || c.margin >= 0);
          return `
            <div class="flex items-center justify-between font-mono text-[10.5px]">
              <span class="truncate max-w-[130px] text-slate-300" title="${c.name}">${c.name}:</span>
              <span class="text-slate-400">${c.prov} / ${c.rreq} ${c.unit}</span>
              <span class="${pass ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-bold'}">
                ${pass ? '✓ PASS' : '✗ FAIL'}
              </span>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  ` : ''}
</td>
```

### 4.4 Dynamic Updates in `updateLiveDashboardDisplays()`

In `DashboardView.js` (lines 1739–1775):
When dimensions are modified interactively, `updateLiveDashboardDisplays()` must update both `stiff-status-${m.id}` class/text and re-evaluate `isComp` considering all sub-components:
```javascript
const allComponentsPass = !m.components || m.components.every(c => c.status === 'COMPLIANT' || c.margin >= 0);
const isComp = (m.margin >= 0) && allComponentsPass;
```
If `face_area` is $10.0\text{ cm}^2 < 71.12\text{ cm}^2$, `allComponentsPass` is `false`, and the badge becomes `DEFICIENT` with `badge-def` (red) styling.

---

## 5. Reactive Synchronization in `calc.js`

In `app/static/js/calc.js` (`recalculateAll`, lines 216–285):
When evaluating stiffeners:
```javascript
// Stiffener calculation with attached plate
const s_res = calcStiffenerSection(spacing, tp, hw, tw, bf, tf);
const prov_sm = s_res.z_cm3;

m.factor = kz;
let req_sm;
// Multi-component checks:
if (m.id === 'stiff_centre_keelson' || m.id === 'stiff_side_keelson') {
  const base_sm = (m.id === 'stiff_centre_keelson') ? 1057.77 : 400.00;
  req_sm = +(base_sm * kz).toFixed(2);
  m.rreq = req_sm;
  m.dact = +prov_sm.toFixed(2);

  // Derive / update sub-components
  const comps = (m.derivation && m.derivation.components) ? m.derivation.components : (m.components || []);
  comps.forEach(c => {
    if (c.param === 'web_thk') {
      c.prov = tw;
      c.margin = +(tw - c.rreq).toFixed(2);
      c.status = c.margin >= 0 ? 'COMPLIANT' : 'NON-COMPLIANT';
    } else if (c.param === 'face_area') {
      const act_af = +((bf * tf) / 100.0).toFixed(2);
      c.prov = act_af;
      c.margin = +(act_af - c.rreq).toFixed(2);
      c.status = c.margin >= 0 ? 'COMPLIANT' : 'NON-COMPLIANT';
    } else if (c.param === 'face_width') {
      c.prov = bf;
      c.margin = +(bf - c.rreq).toFixed(2);
      c.status = c.margin >= 0 ? 'COMPLIANT' : 'NON-COMPLIANT';
    } else if (c.param === 'sm') {
      c.prov = +prov_sm.toFixed(2);
      c.margin = +(prov_sm - c.rreq).toFixed(2);
      c.status = c.margin >= 0 ? 'COMPLIANT' : 'NON-COMPLIANT';
    }
  });

  m.components = comps;
  if (m.derivation) m.derivation.components = comps;

  const margin = +(prov_sm - req_sm).toFixed(2);
  const allPass = comps.every(c => c.status === 'COMPLIANT' || c.margin >= 0);
  m.margin = margin;
  m.status = (margin >= 0 && allPass) ? 'COMPLIANT' : 'NON-COMPLIANT';
  if (m.status === 'COMPLIANT') compliantCount++;
}
```

---

## 6. Auto-Comply Optimizer Interlock

In `app/services/auto_comply/optimizer.py` (lines 46–125):
- `find_compliant_stiffener_profile` must accept individual component minimum constraints:
  - `min_tw: float = 0.0`
  - `min_bf: float = 0.0`
  - `min_af: float = 0.0`
- A profile is considered compliant **only if**:
  1. $Z_{prov} \ge Z_{req}$
  2. $t_w \ge \text{min\_tw}$
  3. $b_f \ge \text{min\_bf}$
  4. $(b_f \times t_f) / 100.0 \ge \text{min\_af}$
- In `app/services/auto_comply/service.py` (lines 128–137):
  Extract component minimums from `m.get('components')` or `m.get('derivation', {}).get('components')` and pass them to `find_compliant_stiffener_profile`.

---

## 7. Exact File Paths, Line Numbers, and CSS Classes Summary

| Area / Feature | Exact File Path | Line Range | Key Functions / Classes | CSS Styles Applied |
|---|---|---|---|---|
| **Pydantic Model** | `app/domain/rules/interpolations/base_interpolator.py` | 13–26 | `class TableViewData` | N/A (Backend schema) |
| **Table View Builder** | `app/domain/rules/interpolations/base_interpolator.py` | 136–158 | `build_table_view` | N/A (Backend builder) |
| **Keelson Interpolator** | `app/domain/rules/interpolations/table_14_16_keelson.py` | 11–61 | `Table1416KeelsonInterpolator.interpolate` | N/A (Backend math) |
| **Derivation Table Visualizer** | `app/static/js/views/CalcBrainView.js` | 15–98 | `renderDerivationTable(derivation)` | `bg-blue-100`, `text-blue-900`, `border-b-2`, `border-blue-500`, `bg-amber-200`, `text-amber-950`, `ring-1`, `ring-amber-400` |
| **CalcBrain Derivation Drawer** | `app/static/js/views/CalcBrainView.js` | 308–355 | `renderCalcBrain()` drawer loop | `compact-table`, `badge-comp`, `badge-def` |
| **Detail Calc Booklet** | `app/static/js/views/DetailCalcView.js` | 5–268 | `renderSheet2Calc()` | `profile-toolbar`, `compact-table`, `badge-comp`, `badge-def` |
| **Stiffener Cross-Section SVG** | `app/static/js/calc.js` | 630–725 | `renderStiffenerSvg()` | Inline SVG vector paths |
| **Client-Side Recalculator** | `app/static/js/calc.js` | 49–355 | `recalculateAll(state)` | N/A (State manager) |
| **Dashboard Stiffeners Table** | `app/static/js/views/DashboardView.js` | 1125–1240 | `renderDashboard()` stiffener loop | `compact-table`, `bg-blue-50/50`, `text-blue-700`, `badge-comp`, `badge-def` |
| **Dashboard Live Updates** | `app/static/js/views/DashboardView.js` | 1601–1838 | `updateLiveDashboardDisplays()` | DOM elements by ID (`stiff-req-*`, `stiff-prov-*`, `stiff-status-*`) |
| **Optimizer Engine** | `app/services/auto_comply/optimizer.py` | 46–140 | `find_compliant_stiffener_profile()` | N/A (Python solver) |
| **Auto-Comply Service** | `app/services/auto_comply/service.py` | 98–160 | `AutoComplyService.generate_preview` | N/A (Python orchestration) |
| **UI Components CSS** | `app/static/css/components.css` | 1–124 | Badges, inputs, titles, tabs | `.badge-comp`, `.badge-def`, `.compact-input`, `.compact-title` |
| **Tables CSS** | `app/static/css/tables.css` | 1–27 | Table layouts | `.compact-table` |

---

## 8. Verification & Next Steps

1. **Independent Verification Method**:
   - Run Python test suite: `pytest tests/test_table_interpolations.py`
   - Run full unit tests: `python -m unittest discover tests`
   - Test server on port 8055: `python app/main.py`
   - Open browser at `http://localhost:8055/` and verify:
     1. Table 16 derivation drawer in Calculation Brain highlights Columns 1, 2, and 3 with 6 bounding node badges.
     2. Detail View (Sheet 01 Center Keelson) displays the multi-part comparison grid.
     3. Dashboard row for Center Keelson displays `Req SM [cm³] = 1480.88` vs `Provided SM [cm³] = 1274.33`, with status badge showing `DEFICIENT` and hovering reveals the full green/red breakdown of all sub-components.
2. **Implementer Handover**:
   All observations, line references, and code designs above are validated against the live repository code and ready for implementation.

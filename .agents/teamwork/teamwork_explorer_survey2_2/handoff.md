# Handoff Report: Frontend Visualizers, Tables, and Grids Survey

**Agent**: `teamwork_explorer_survey2_2`  
**Working Directory**: `e:\Bangla Scantling\.agents\teamwork\teamwork_explorer_survey2_2`  
**Handoff Type**: Hard (Investigation complete)  

---

## 1. Observation

1. **`TableViewData` Definition**:
   - In `app/domain/rules/interpolations/base_interpolator.py` (lines 13–26):
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
     `active_col_index` is currently a single `Optional[int]`.
2. **`renderDerivationTable` Definition**:
   - In `app/static/js/views/CalcBrainView.js` (lines 15–98):
     Line 21: `const activeCol = tv.active_col_index;`
     Line 55: `const isColActive = (cIdx === activeCol);` (in `<th>`)
     Line 70: `const isColActive = (cIdx === activeCol);` (in `<td>`)
     Line 22–25: `boundingMap.set(`${bc.row}:${bc.col}`, bc.val)`
     Line 72: `const isBounding = boundingMap.has(cellKey);`
   - Line 353: `${renderDerivationTable(deriv)}` is invoked in `renderCalcBrain()`.
3. **Table 16 / Table 15 Physical Column Interpolation**:
   - In `app/domain/rules/interpolations/table_14_16_keelson.py` (lines 18–42):
     Col 1 (`WEB_THK_NODES`) is interpolated, while Col 2 (`FACE_AREA_NODES`) and Col 3 (`FACE_WIDTH_NODES`) are declared on lines 20–21 but never evaluated.
     Line 38 sets `active_col=1`.
     Lines 31–34 only populate `bounding_cells` for `col: 1`.
4. **Detail Calc View (`DetailCalcView.js`) & `CalcBrainView.js`**:
   - In `DetailCalcView.js` (lines 130–256): Renders Sections 1 to 4 (`Dimensions & Areas`, `Neutral Axis`, `Moments of Inertia`, `Section Modulus`). No sub-component breakdown table exists.
   - In `CalcBrainView.js` (lines 330–350): Renders two general text boxes (`Interpolation & Requirements` and `Provided Geometry & Compliance`).
5. **Dashboard View (`DashboardView.js`)**:
   - Lines 1136–1151: Stiffeners table header has columns `Req SM [cm³]` and `Provided SM [cm³]`.
   - Lines 1224–1225:
     `Req SM [cm³]` renders `reqSm.toFixed(2)`
     `Provided SM [cm³]` renders `provSm.toFixed(2)`
   - Lines 1229–1233: Status column renders `<span id="stiff-status-${m.id}" class="${isComp ? 'badge-comp' : 'badge-def'}">${isComp ? 'COMPLIED' : 'DEFICIENT'}</span>` with no tooltip.
6. **Optimizer (`app/services/auto_comply/optimizer.py`)**:
   - Lines 68–73 in `find_compliant_stiffener_profile`: Checks `cur_res['z_cm3'] >= rreq_z`, but does not enforce minimums for `tw`, `bf`, or `af`.

---

## 2. Logic Chain

1. **Step 1 (Observation 1 & 2 -> Multi-Column Highlight Support)**:
   Because `renderDerivationTable` checks `isColActive = (cIdx === activeCol)` against a single integer, any multi-column table (like Table 16 with columns 1, 2, 3) only highlights column 1.
   By adding `active_col_indices: List[int] = Field(default_factory=list)` to `TableViewData` and updating `renderDerivationTable` to check `const activeCols = new Set(tv.active_col_indices || [tv.active_col_index])`, any number of columns can be highlighted simultaneously.
2. **Step 2 (Observation 2 & 3 -> Multi-Column Bounding Nodes)**:
   Because `renderDerivationTable` looks up bounding nodes using `boundingMap.has(`${rIdx}:${cIdx}`)`, expanding `bounding_cells` in `table_14_16_keelson.py` to include bounding cells for col 1, col 2, and col 3 immediately highlights all 6 bounding nodes across the table with no further changes needed to cell-matching logic.
3. **Step 3 (Observation 3, 4, 5 -> Unit and Dimension Alignment)**:
   In Table 16 and Table 15, Keelsons have two distinct statutory aspects:
   - Profile component minimums ($t_w \ge \text{req mm}$, $A_f \ge \text{req cm}^2$, $b_f \ge \text{req mm}$)
   - Girder bending strength ($Z \ge Z_{req}\text{ cm}^3$, derived from rule baseline geometry, e.g. $1057.77 \times 1.40 = 1480.88\text{ cm}^3$).
   Setting `m.rreq = 1480.88` aligns the units so the main dashboard row compares $\text{cm}^3$ to $\text{cm}^3$, eliminating the invalid $+1261.04$ margin artifact.
4. **Step 4 (Observation 4 & 5 -> Multi-Part Comparison Grid & Hover Breakdown)**:
   By storing the sub-component evaluations in `m.components`:
   - Detail View (`DetailCalcView.js`) can render Section 5 with the full multi-part grid table: `Base -> Factor -> Required -> Provided -> Margin -> Status (Pass/Fail)`.
   - Dashboard View (`DashboardView.js`) can wrap the status badge in a `relative group` popover to display the full green/red breakdown of all sub-components.
   - Strict compliance logic requires: overall status is `COMPLIANT` **only if ALL sub-components pass**.
5. **Step 5 (Observation 6 -> Optimizer Convergence)**:
   By passing `min_tw`, `min_bf`, and `min_af` into `ScantlingOptimizer.find_compliant_stiffener_profile`, the Auto-Comply solver ensures that the selected profile satisfies both the girder Section Modulus and individual statutory component thresholds.

---

## 3. Caveats

1. **Backwards Compatibility**: In `tests/test_table_interpolations.py:112`, `self.assertIsNotNone(tv.active_col_index)` explicitly checks that `active_col_index` is not None. Therefore, `TableViewData` MUST retain `active_col_index` alongside `active_col_indices`, populating `active_col_index = active_col_indices[0]` if `active_col_index` is omitted.
2. **Table 22/23 (Pillars)**: Pillars use column 5 for solid diameter and column 0 for tubular diameter. When multi-column evaluation is added, pillar tabular views must preserve single-column selection depending on whether tubular or solid pillar is being evaluated.
3. **Responsive DOM Updates**: When users edit dimensions live in the dashboard, `updateLiveDashboardDisplays` updates elements by ID (`stiff-req-*`, `stiff-prov-*`, `stiff-status-*`). Any tooltip container must be updated in tandem or maintained via classes so hover popovers remain accurate without requiring a full page re-render.

---

## 4. Conclusion

The frontend visualizer, derivation table highlighter, Detail View calculation card, Dashboard Stiffeners table, and client-side reactive recalculation engine are cleanly modularized and fully accessible in `app/static/js/`.

Implementing the Multi-Column Statutory Evaluation Framework requires:
1. `base_interpolator.py`: Add `active_col_indices` to `TableViewData` and `build_table_view`.
2. `CalcBrainView.js`: Update `renderDerivationTable` to use `activeCols = new Set(...)`, and add the multi-part comparison grid table in the derivation drawer.
3. `DetailCalcView.js`: Add Section 5: "Statutory Multi-Part Member Verification" displaying the Base -> Factor -> Required -> Provided -> Margin -> Status grid.
4. `calc.js`: In `recalculateAll`, derive equivalent Section Modulus in $\text{cm}^3$, evaluate all sub-components (`web_thk`, `face_area`, `face_width`, `sm`), and enforce strict compliance.
5. `DashboardView.js`: Add the status hover tooltip popover displaying the green/red sub-component breakdown, and update `updateLiveDashboardDisplays` accordingly.
6. `optimizer.py`: Incorporate component minimum constraints (`min_tw`, `min_bf`, `min_af`) into profile search.

The complete survey report with detailed line references and code diff blueprints is stored at:
`e:\Bangla Scantling\.agents\teamwork\teamwork_explorer_survey2_2\survey_report.md`.

---

## 5. Verification Method

1. **Unit Tests Verification**:
   ```powershell
   python -m unittest tests/test_table_interpolations.py
   python -m unittest discover tests
   ```
2. **Visual Inspection on Port 8055**:
   Run the dev server:
   ```powershell
   python app/main.py
   ```
   Navigate to `http://localhost:8055/`:
   - **Calculation Brain Tab**: Open Table 16 (Center Keelson) derivation. Confirm columns 1, 2, and 3 are highlighted in blue and all 6 bounding cells have amber badges.
   - **Detail Calculations Tab**: Select Sheet 01 (Center Keelson). Confirm Section 5 displays the multi-part comparison grid table.
   - **Dashboard Tab**: Check Center Keelson row. Confirm `Req SM [cm³]` displays `1480.88`, `Provided SM [cm³]` displays `1274.33`, `Margin` displays `-206.55`, status displays `DEFICIENT`, and hovering reveals the sub-component breakdown with red badges for deficient components.

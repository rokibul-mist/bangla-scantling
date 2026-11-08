# Handoff Report — Multi-Column Statutory Evaluation Framework Survey

**Date**: 2026-10-30  
**Agent**: `teamwork_explorer_survey2_1`  
**Handoff Type**: Hard (Task Complete)  
**Parent Agent**: `efb88a04-9314-4709-9685-7b01ddae6b2f`

---

## 1. Observation

1. **`app/domain/rules/interpolations/table_14_16_keelson.py` (lines 11–61)**:
   - Implements `Table1416KeelsonInterpolator`.
   - Defines:
     ```python
     L_NODES = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
     WEB_THK_NODES = [7.0, 7.5, 8.0, 8.5, 9.0, 9.5]
     FACE_AREA_NODES = [21.0, 27.0, 33.0, 40.0, 47.0, 55.0]
     FACE_WIDTH_NODES = [200.0, 230.0, 250.0, 270.0, 290.0, 300.0]
     ```
   - In `interpolate()` (line 28), it calls:
     ```python
     t_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, cls.L_NODES, cls.WEB_THK_NODES)
     rreq = round(t_base * kt, 2)
     ```
   - Only interpolates `WEB_THK_NODES`. `FACE_AREA_NODES` and `FACE_WIDTH_NODES` are completely unread.
   - Returns `InterpolationResult` with `baseline=round(t_base, 2)`, `rreq=rreq`, `unit="mm"`.
   - Completely omits Table 15 (Side Keelson) nodes and logic.

2. **`app/domain/rules/interpolations/registry.py` (lines 78–81)**:
   - Registers both Center Keelson and Side Keelson to `Table1416KeelsonInterpolator`:
     ```python
     "stiff_centre_keelson": Table1416KeelsonInterpolator,
     "stiff_centre_girder": Table1416KeelsonInterpolator,
     "stiff_side_keelson": Table1416KeelsonInterpolator,
     "stiff_side_girder": Table1416KeelsonInterpolator,
     ```
   - No conditional branching exists in `Table1416KeelsonInterpolator` for `member_id`.

3. **`app/services/calculation_service.py` (lines 139–225)**:
   - In lines 140–144:
     ```python
     interp_res = TableInterpolationRegistry.interpolate_member(m_id, calc_inputs)
     if interp_res:
         m['baseline'] = interp_res.baseline
         m['rreq'] = interp_res.rreq
         m['derivation'] = interp_res.to_dict()
     ```
   - In line 209–224:
     ```python
     s_res = calc_stiffener_section(spacing, tp, hw, tw, bf, tf)
     prov_sm = s_res['z_cm3'] # e.g. 1274.33 cm3
     req_sm = interp_res.rreq # e.g. 13.29 mm!
     m['rreq'] = req_sm
     m['dact'] = round(prov_sm, 2)
     margin = round(prov_sm - req_sm, 2) # 1274.33 - 13.29 = +1261.04
     is_comp = margin >= 0 # Evaluates to TRUE
     m['status'] = 'COMPLIANT' if is_comp else 'NON-COMPLIANT'
     ```
   - This directly creates the unit mismatch defect where $13.29\text{ mm}$ is subtracted from $1274.33\text{ cm}^3$.

4. **`app/domain/catalog/structural_catalog.py` (lines 918–970)**:
   - `stiff_centre_keelson` defines:
     ```python
     "baseline": 1057.77,
     "unit": "cm3",
     "table_ref": "Table 16",
     ```
   - `stiff_side_keelson` defines:
     ```python
     "baseline": 400.0,
     "unit": "cm3",
     "table_ref": "Table 15",
     ```

5. **`app/domain/rules/interpolations/base_interpolator.py` (lines 13–45)**:
   - `TableViewData` only defines scalar `active_col_index: Optional[int] = None`. It lacks `active_col_indices: List[int]`.
   - `InterpolationResult` lacks a `components` field.

6. **`app/domain/rules/interpolations/table_22_23_pillars.py` (lines 23–89)**:
   - For solid pillars (`pillar_solid_dia`), interpolates diameter for fixed load $P=60\text{ kN}$.
   - For tubular pillars (`pillar_tubular_dia`), hardcodes diameter $114.3\text{ mm}$ and ignores wall thickness column.

7. **`app/domain/rules/interpolations/table_30_31_coamings.py` (lines 22–58)**:
   - Only reads Table 30 ($L$-based). Table 31 ($B$-based) is never evaluated.

8. **`app/services/auto_comply/optimizer.py` (lines 46–140)**:
   - `find_compliant_stiffener_profile` only checks `z_prov >= rreq_z`. It does not accept or verify `min_tw`, `min_bf`, or `min_af`.

9. **Existing Test Suite**:
   - Running `python -m unittest discover tests` executed 21 tests and completed with `OK`.

---

## 2. Logic Chain

1. **Premise 1 (From Observation 1 & 3)**: `Table1416KeelsonInterpolator` returns web plate thickness $13.29\text{ mm}$ in `rreq`. When `calculation_service.py` receives this, it assigns it to `req_sm` and compares it directly against provided Section Modulus $1274.33\text{ cm}^3$.
2. **Premise 2 (From Observation 4)**: The structural catalog defines the authoritative equivalent Section Modulus baseline for `stiff_centre_keelson` as $1057.77\text{ cm}^3$ and `stiff_side_keelson` as $400.0\text{ cm}^3$.
3. **Inference 1**: To ensure the main table compares $\text{cm}^3$ to $\text{cm}^3$, the interpolator for keelsons must return equivalent Section Modulus ($Z_{base} = 1057.77\text{ cm}^3, Z_{req} = 1057.77 \times k_z = 1480.88\text{ cm}^3$) as the primary metric, while extracting all physical prescribed table dimensions into a structured `components` list.
4. **Premise 3 (From Observation 1, 6, 7)**: Tables 15, 16, 22/23, and 30/31 each contain multiple physical dimensions (web thickness, face area, face width; outer diameter, wall thickness; $L$-thickness vs $B$-thickness).
5. **Inference 2**: Multi-column evaluation requires:
   - Dynamic interpolation of all prescribed columns.
   - Populating `derivation['components']` with individual base, required, provided, margin, and status values.
   - Updating `TableViewData` to support `active_col_indices: [1, 2, 3]` and multi-column bounding nodes.
   - Enforcing strict compliance: `COMPLIANT` if and only if all sub-components pass.
6. **Premise 4 (From Observation 8)**: The Auto-Comply optimizer currently only evaluates Section Modulus.
7. **Inference 3**: To achieve true compliance without regression, Auto-Comply must constrain candidate selection and parametric T-girder generation by $t_w \ge \min(t_w)$, $b_f \ge \min(b_f)$, and $A_f \ge \min(A_f)$.

---

## 3. Caveats

- **Load Parameter in Table 22 (Pillars)**: Supported load $P$ is currently fixed to standard $P=60\text{ kN}$ in absence of user cargo deck load input. This default is safe and compliant with statutory guidelines.
- **Hatch Coaming Breadth Upper Node**: Vessel breadth $B=13.41\text{ m}$ exceeds Table 31's maximum tabulated node of $12.0\text{ m}$. Linear extrapolation yields $t_{base} \ge 9.50\text{ mm}$ (or $10.0\text{ mm}$ with 1D extrapolation).

---

## 4. Conclusion

The architecture of the multi-column framework is completely analyzed, verified, and mapped:
1. `base_interpolator.py`: Add `active_col_indices: List[int]` to `TableViewData` and `components: Optional[List[Dict[str, Any]]]` to `InterpolationResult`.
2. `table_14_16_keelson.py`: Implement multi-column extraction for Table 16 ($t_w, A_f, b_f, Z$) and Table 15 ($t_w, A_f, Z$), returning equivalent Section Modulus in $\text{cm}^3$ for the main row and all sub-components in `components`.
3. `table_22_23_pillars.py` and `table_30_31_coamings.py`: Multi-column extraction for outer diameter/wall thickness and $L$-thickness/$B$-thickness.
4. `calculation_service.py` & `calc.js`: Evaluate each sub-component, compute provided geometry, and enforce strict compliance.
5. `optimizer.py` & `service.py`: Add multi-component minimum constraints to stiffener profile selection.
6. `CalcBrainView.js` & `DashboardView.js`: Multi-column table active highlights (`active_col_indices`), detail view multi-part comparison grid, and dashboard status breakdown tooltip.

---

## 5. Verification Method

1. **Unit Tests**:
   - Command: `python -m unittest discover tests`
   - Expected: All tests pass with 0 failures and 0 errors.
2. **Component Integrity Test**:
   - Inspect calculation output for `stiff_centre_keelson` with provided profile `T 500x100x12/10`:
     - $Z_{req} = 1480.88\text{ cm}^3$, $Z_{prov} = 1274.33\text{ cm}^3$ ($\text{Margin} = -206.55\text{ cm}^3$).
     - Component $t_w$: $12.0\text{ mm} < 13.29\text{ mm}$ (`NON-COMPLIANT`).
     - Component $A_f$: $10.0\text{ cm}^2 < 71.12\text{ cm}^2$ (`NON-COMPLIANT`).
     - Component $b_f$: $100.0\text{ mm} < 319.0\text{ mm}$ (`NON-COMPLIANT`).
     - Overall status strictly `NON-COMPLIANT`.
3. **Survey Deliverables**:
   - Inspect `survey_report.md` at `e:\Bangla Scantling\.agents\teamwork\teamwork_explorer_survey2_1\survey_report.md`.

"""
Hull Strength Service
Orchestrates midship section assembly, longitudinal bending moments,
Table 66 & 67 stress verification, and report synthesis.
"""

from typing import Dict, Any, List, Optional
from app.domain.models.strength import (
    MidshipElement,
    MidshipSectionProperties,
    BendingMoments,
    Table66StressResult,
    LocalMemberStrengthItem,
    HullStrengthReport
)
from app.domain.calc.strength_calc import StrengthCalculator


class StrengthService:
    """
    Comprehensive hull strength and structural mechanics service.
    """

    @classmethod
    def assemble_midship_elements(cls, state: Dict[str, Any]) -> Tuple[List[MidshipElement], float]:
        """
        Auto-assemble continuous longitudinal midship cross-sectional elements from
        the active Dashboard inputs and Stiffeners catalog.
        """
        inp = state.get('dashboard_inputs', {}) or {}
        cb_dict = {r['id']: r for r in state.get('calculation_brain', []) if isinstance(r, dict)}
        s2_dict = {s['member_id']: s for s in state.get('sheet2_results', []) if isinstance(s, dict)}

        # Vessel particulars
        b_m = float(inp.get('breadth', 13.41) or 13.41)
        d_m = float(inp.get('depth', 5.18) or 5.18)
        b_mm = b_m * 1000.0
        d_mm = d_m * 1000.0

        # Thicknesses from dashboard or calculation brain
        t_keel = float(inp.get('t_keel') or cb_dict.get('plate_keel', {}).get('dact') or 13.0)
        t_bottom = float(inp.get('t_bottom') or cb_dict.get('plate_bottom', {}).get('dact') or 12.0)
        t_bilge = float(inp.get('t_bilge') or cb_dict.get('plate_bilge', {}).get('dact') or 14.0)
        t_side = float(inp.get('t_side') or cb_dict.get('plate_side', {}).get('dact') or 12.0)
        t_deck = float(inp.get('t_deck_all') or cb_dict.get('plate_main_deck', {}).get('dact') or 12.0)
        t_coaming = float(cb_dict.get('plate_coaming_long', {}).get('dact') or 13.0)
        t_inner_bottom = float(inp.get('t_inner_bottom') or cb_dict.get('plate_inner_bottom', {}).get('dact') or 12.0)

        hull_type = str(inp.get('hull_type', 'Single Hull')).lower()
        has_double_bottom = ('double bottom' in hull_type) or ('double hull' in hull_type)

        elements: List[MidshipElement] = []

        # 1. Flat Keel Plate (Centerline lower flange)
        b_keel_mm = float(cb_dict.get('plate_keel_width', {}).get('dact') or 1100.0)
        elements.append(MidshipElement(
            id="midship_keel",
            name="Keel Plate",
            category="bottom",
            width_mm=b_keel_mm,
            thk_mm=t_keel,
            quantity=1,
            lever_y_mm=round(t_keel / 2.0, 2),
            is_vertical=False,
            notes="Centerline flat keel continuous strake"
        ))

        # 2. Bottom Shell Plating (Port & Starboard)
        # Net breadth subtracting keel and 2 bilge curves (bilge radius ~ 800 mm)
        bilge_radius_mm = 800.0
        b_bottom_net = max(b_mm - b_keel_mm - (2.0 * bilge_radius_mm), 2000.0)
        elements.append(MidshipElement(
            id="midship_bottom_shell",
            name="Bottom Shell Plating (Port & Stbd)",
            category="bottom",
            width_mm=round(b_bottom_net, 1),
            thk_mm=t_bottom,
            quantity=1,
            lever_y_mm=round(t_bottom / 2.0, 2),
            is_vertical=False,
            notes="Bottom shell continuous strakes"
        ))

        # 3. Bilge Plating (Port & Starboard)
        # Girth of 90-degree bilge arc ~ pi/2 * R ~ 1.57 * 800 ~ 1256 mm
        bilge_girth_mm = round((3.14159 / 2.0) * bilge_radius_mm, 1)
        bilge_cg_y_mm = round(bilge_radius_mm * (1.0 - 2.0 / 3.14159), 2)  # ~ 290 mm
        elements.append(MidshipElement(
            id="midship_bilge",
            name="Bilge Plating (Port & Stbd Strake)",
            category="bottom",
            width_mm=bilge_girth_mm,
            thk_mm=t_bilge,
            quantity=2,
            lever_y_mm=bilge_cg_y_mm,
            is_vertical=False,
            notes="Port & starboard curved bilge strakes"
        ))

        # 4. Side Shell Plating (Port & Starboard vertical webs)
        # Vertical height from top of bilge to lower edge of sheer strake (sheer strake ~ 1000 mm)
        h_sheer_mm = 1000.0
        h_side_web = max(d_mm - bilge_radius_mm - h_sheer_mm, 1000.0)
        side_cg_y_mm = round(bilge_radius_mm + (h_side_web / 2.0), 2)
        elements.append(MidshipElement(
            id="midship_side_shell",
            name="Side Shell Plating (Port & Stbd)",
            category="side",
            width_mm=round(h_side_web, 1),
            thk_mm=t_side,
            quantity=2,
            lever_y_mm=side_cg_y_mm,
            is_vertical=True,
            notes="Vertical side shell continuous plating"
        ))

        # 5. Sheer Strake (Port & Starboard top side web)
        sheer_cg_y_mm = round(d_mm - (h_sheer_mm / 2.0), 2)
        elements.append(MidshipElement(
            id="midship_sheer_strake",
            name="Sheer Strake (Port & Stbd)",
            category="side",
            width_mm=h_sheer_mm,
            thk_mm=t_side,
            quantity=2,
            lever_y_mm=sheer_cg_y_mm,
            is_vertical=True,
            notes="Upper vertical side shell sheer strake"
        ))

        # 6. Strength Deck Plating Abreast of Hatches (Port & Starboard)
        # Width outside hatchway: typical hatch width ~ 55% of breadth
        b_hatch_mm = round(b_mm * 0.55, 1)
        b_deck_abreast = max(b_mm - b_hatch_mm, 2000.0)
        elements.append(MidshipElement(
            id="midship_deck_plating",
            name="Strength Deck Plating (Abreast of Hatches)",
            category="deck",
            width_mm=round(b_deck_abreast, 1),
            thk_mm=t_deck,
            quantity=1,
            lever_y_mm=d_mm - (t_deck / 2.0),
            is_vertical=False,
            notes="Continuous strength deck outside cargo openings"
        ))

        # 7. Continuous Hatch Side Coamings (Port & Starboard)
        # Hatch coaming height ~ 600 mm above deck
        h_coam_mm = 600.0
        coam_cg_y_mm = round(d_mm + (h_coam_mm / 2.0), 2)
        elements.append(MidshipElement(
            id="midship_hatch_coaming",
            name="Continuous Hatch Side Coamings",
            category="deck",
            width_mm=h_coam_mm,
            thk_mm=t_coaming,
            quantity=2,
            lever_y_mm=coam_cg_y_mm,
            is_vertical=True,
            notes="Continuous longitudinal hatch side coamings"
        ))

        # 8. Center Keelson / Girder (T-Profile)
        ck_item = s2_dict.get('stiff_centre_keelson', {})
        ck_hw = float(ck_item.get('web_height', 400.0) or 400.0)
        ck_tw = float(ck_item.get('web_thk', 12.0) or 12.0)
        ck_bf = float(ck_item.get('flange_width', 250.0) or 250.0)
        ck_tf = float(ck_item.get('flange_thk', 12.0) or 12.0)

        # Center keelson web
        elements.append(MidshipElement(
            id="midship_ck_web",
            name="Center Keelson Web Plate",
            category="bottom",
            width_mm=ck_hw,
            thk_mm=ck_tw,
            quantity=1,
            lever_y_mm=round(t_keel + (ck_hw / 2.0), 2),
            is_vertical=True,
            notes="Center keelson continuous web"
        ))
        # Center keelson face plate / flange
        elements.append(MidshipElement(
            id="midship_ck_flange",
            name="Center Keelson Face Plate",
            category="bottom",
            width_mm=ck_bf,
            thk_mm=ck_tf,
            quantity=1,
            lever_y_mm=round(t_keel + ck_hw + (ck_tf / 2.0), 2),
            is_vertical=False,
            notes="Center keelson continuous face flange"
        ))

        # 9. Side Keelsons / Side Girders (Port & Starboard T-Profiles)
        sk_item = s2_dict.get('stiff_side_keelson', {})
        sk_hw = float(sk_item.get('web_height', 400.0) or 400.0)
        sk_tw = float(sk_item.get('web_thk', 11.0) or 11.0)
        sk_bf = float(sk_item.get('flange_width', 100.0) or 100.0)
        sk_tf = float(sk_item.get('flange_thk', 11.0) or 11.0)

        # Side keelsons web (2 pieces)
        elements.append(MidshipElement(
            id="midship_sk_web",
            name="Side Keelsons Web Plates (P & S)",
            category="bottom",
            width_mm=sk_hw,
            thk_mm=sk_tw,
            quantity=2,
            lever_y_mm=round(t_bottom + (sk_hw / 2.0), 2),
            is_vertical=True,
            notes="Port & starboard side keelsons continuous web"
        ))
        # Side keelsons flange (2 pieces)
        elements.append(MidshipElement(
            id="midship_sk_flange",
            name="Side Keelsons Face Plates (P & S)",
            category="bottom",
            width_mm=sk_bf,
            thk_mm=sk_tf,
            quantity=2,
            lever_y_mm=round(t_bottom + sk_hw + (sk_tf / 2.0), 2),
            is_vertical=False,
            notes="Port & starboard side keelsons continuous flange"
        ))

        # 10. Main Deck Center & Side Longitudinal Girders (Under deck)
        dg_item = s2_dict.get('stiff_deck_girder', {})
        dg_hw = float(dg_item.get('web_height', 300.0) or 300.0)
        dg_tw = float(dg_item.get('web_thk', 11.0) or 11.0)
        dg_bf = float(dg_item.get('flange_width', 175.0) or 175.0)
        dg_tf = float(dg_item.get('flange_thk', 11.0) or 11.0)

        # Deck girders web (2 longitudinals abreast of hatches)
        elements.append(MidshipElement(
            id="midship_dg_web",
            name="Continuous Deck Girders Web (P & S)",
            category="deck",
            width_mm=dg_hw,
            thk_mm=dg_tw,
            quantity=2,
            lever_y_mm=round(d_mm - t_deck - (dg_hw / 2.0), 2),
            is_vertical=True,
            notes="Under-deck continuous longitudinal girders web"
        ))
        # Deck girders flange (2 pieces)
        elements.append(MidshipElement(
            id="midship_dg_flange",
            name="Continuous Deck Girders Flange (P & S)",
            category="deck",
            width_mm=dg_bf,
            thk_mm=dg_tf,
            quantity=2,
            lever_y_mm=round(d_mm - t_deck - dg_hw - (dg_tf / 2.0), 2),
            is_vertical=False,
            notes="Under-deck continuous longitudinal girders flange"
        ))

        # 11. Inner Bottom / Tank Top Plating (If Double Bottom / Tanker)
        if has_double_bottom:
            h_db_mm = 850.0  # standard double bottom height
            elements.append(MidshipElement(
                id="midship_inner_bottom",
                name="Double Bottom Tank Top Plating",
                category="inner_bottom",
                width_mm=round(b_mm * 0.85, 1),
                thk_mm=t_inner_bottom,
                quantity=1,
                lever_y_mm=h_db_mm,
                is_vertical=False,
                notes="Continuous inner bottom plating"
            ))

        return elements, d_m

    @classmethod
    def calculate_hull_strength(cls, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the complete statutory hull strength calculation suite:
        1. Design Bending Moments per Rule 209
        2. Required Midship Section Modulus
        3. Midship Cross-Section Numerical Integration (A, y_NA, I_NA, Z_deck, Z_bottom)
        4. Schedule Table 66 Global Stress Evaluation
        5. Schedule Table 67 Local Member Stress Evaluation
        """
        if state is None:
            from app.repositories.state_repository import StateRepository
            repo = StateRepository()
            state = repo.get_saved_state() or repo.get_state()

        inp = state.get('dashboard_inputs', {}) or {}
        vessel_name = str(inp.get('vessel_name', 'M.V. CROWN MARINERS-65'))
        vessel_type = str(inp.get('vessel_type', 'Steel Body Cargo Vessel'))
        route_name = str(inp.get('route', inp.get('proposed_route', 'Inland & bay crossing')))
        
        lbp = float(inp.get('lbp', 69.85) or 69.85)
        breadth = float(inp.get('breadth', 13.41) or 13.41)
        depth = float(inp.get('depth', 5.18) or 5.18)
        draft = float(inp.get('draft', 4.00) or 4.00)
        cb = float(inp.get('cb', 0.75) or 0.75)

        # Route multipliers
        factor_kt = float(state.get('factors', {}).get('kt', 1.40) or 1.40)
        factor_kz = float(state.get('factors', {}).get('kz', 1.40) or 1.40)

        # 1. Design Bending Moments
        moments = StrengthCalculator.calculate_design_bending_moments(
            lbp=lbp,
            breadth=breadth,
            depth=depth,
            draft=draft,
            cb=cb,
            kt=factor_kt
        )

        # 2. Required Midship Section Modulus
        z_req_cm3 = StrengthCalculator.calculate_statutory_required_modulus(
            m_design_knm=moments.m_design_knm,
            lbp=lbp,
            breadth=breadth,
            cb=cb,
            kt=factor_kt
        )

        # 3. Assemble and Integrate Midship Cross-Section
        elements, depth_m = cls.assemble_midship_elements(state)

        # Handle selective element inclusion/exclusion
        excluded_ids = state.get('midship_excluded_element_ids')
        selected_ids = state.get('midship_selected_element_ids')
        if excluded_ids is not None:
            excl_set = set(excluded_ids)
            for el in elements:
                el.is_included = (el.id not in excl_set)
        elif selected_ids is not None:
            sel_set = set(selected_ids)
            for el in elements:
                el.is_included = (el.id in sel_set)

        props = StrengthCalculator.integrate_midship_cross_section(
            elements=elements,
            depth_m=depth_m,
            required_sm_cm3=z_req_cm3
        )

        # Side shell thickness for shear stress calculation
        t_side = float(inp.get('t_side') or 12.0)

        # 4. Schedule Table 66 Stresses
        table_66 = StrengthCalculator.evaluate_table_66_stresses(
            m_design_knm=moments.m_design_knm,
            q_design_kn=moments.shear_force_design_kn,
            props=props,
            depth_m=depth_m,
            side_shell_thk_mm=t_side
        )

        # 5. Schedule Table 67 Local Member Stresses
        table_67 = StrengthCalculator.evaluate_table_67_local_members(state)

        # 6. Classic Assumed Neutral Axis Integration (Rule 209 / ISO 1976 Standard)
        assumed_na_mm = float(state.get('assumed_na_mm', 0) or 0)
        if assumed_na_mm <= 0:
            assumed_na_mm = round((depth * 1000.0) * 0.55, 1)

        assumed_axis_results = StrengthCalculator.calculate_assumed_axis_integration(
            elements=elements,
            depth_m=depth_m,
            length_m=lbp,
            assumed_na_mm=assumed_na_mm
        )

        # Overall Status
        all_local_pass = all(m.status == "COMPLIANT" for m in table_67)
        is_compliant = (props.modulus_margin_cm3 >= 0.0 and table_66.is_overall_compliant and all_local_pass)
        overall_status = "COMPLIANT" if is_compliant else "NON-COMPLIANT"

        summary_text = (
            f"Vessel '{vessel_name}' complies with Bangladesh Inland Steel Ships Construction Rules 2001 (Rules 209 & 223). "
            f"Provided Midship Section Modulus ({props.modulus_actual_cm3:,.2f} cm³) exceeds statutory requirement "
            f"({props.modulus_rule_required_cm3:,.2f} cm³) by +{props.modulus_margin_pct:.1f}%. "
            f"Maximum Hull Girder Bending Stress is {table_66.max_bending_stress_n_mm2:.2f} N/mm² (Limit: 130.0 N/mm² per Table 66)."
            if is_compliant else
            f"Hull longitudinal strength requirements deficient under governing design bending moment {moments.m_design_knm:,.2f} kN·m."
        )

        # Detailed Practical Working & Mathematical Breakdown
        active_els = [el for el in elements if getattr(el, 'is_included', True)]
        sum_ay_m3 = sum((el.area_mm2 * 1e-6) * (el.lever_y_mm * 1e-3) for el in active_els)
        sum_a_m2 = sum((el.area_mm2 * 1e-6) for el in active_els)
        sum_i0_m4 = sum((el.own_inertia_mm4 * 1e-12) for el in active_els)
        sum_ad2_m4 = sum((el.area_mm2 * 1e-6) * (((el.lever_y_mm - props.neutral_axis_above_keel_mm) * 1e-3) ** 2) for el in active_els)

        z1_stress_cm3 = round((moments.m_design_knm * 1000.0) / 130.0, 2)
        z2_emp_cm3 = round(1.75 * factor_kt * (lbp ** 2) * breadth * (cb + 0.70), 2)
        a_shear_mm2 = round(2.0 * (depth * 1000.0) * t_side, 1)

        practical_working = {
            "step1_bending_moments": {
                "title": "Step 1: Longitudinal Design Bending Moments (Rule 209)",
                "description": "Statutory still water, wave-induced, and route-scaled design moments per Bangladesh Inland Shipping Rules 2001.",
                "cw_formula": "C_w = 0.08 × k_t × √L",
                "cw_substitution": f"0.08 × {factor_kt:.2f} × √({lbp:.2f}) = {moments.wave_coefficient_cw:.3f}",
                "msw_formula": "M_sw = 0.06 × C_b × L² × B × (d + 0.02 × L)",
                "msw_substitution": f"0.06 × {cb:.3f} × ({lbp:.2f})² × {breadth:.2f} × ({draft:.2f} + 0.02 × {lbp:.2f}) = {moments.m_sw_knm:,.2f} kN·m",
                "mw_hog_formula": "M_w,hog = 0.19 × C_w × L² × B × C_b",
                "mw_hog_substitution": f"0.19 × {moments.wave_coefficient_cw:.3f} × ({lbp:.2f})² × {breadth:.2f} × {cb:.3f} = {moments.m_wave_hog_knm:,.2f} kN·m",
                "mw_sag_formula": "M_w,sag = 0.11 × C_w × L² × B × (C_b + 0.70)",
                "mw_sag_substitution": f"0.11 × {moments.wave_coefficient_cw:.3f} × ({lbp:.2f})² × {breadth:.2f} × ({cb:.3f} + 0.70) = {moments.m_wave_sag_knm:,.2f} kN·m",
                "mt_hog_formula": "M_t,hog = M_sw + M_w,hog",
                "mt_hog_substitution": f"{moments.m_sw_knm:,.2f} + {moments.m_wave_hog_knm:,.2f} = {moments.m_total_hog_knm:,.2f} kN·m",
                "mt_sag_formula": "M_t,sag = M_sw + M_w,sag",
                "mt_sag_substitution": f"{moments.m_sw_knm:,.2f} + {moments.m_wave_sag_knm:,.2f} = {moments.m_total_sag_knm:,.2f} kN·m",
                "m_design": f"M_design = max(M_t,hog, M_t,sag) = {moments.m_design_knm:,.2f} kN·m ({moments.design_condition})",
                "qt_formula": "Q_t = 2.50 × M_design / L",
                "qt_substitution": f"(2.50 × {moments.m_design_knm:,.2f}) / {lbp:.2f} = {moments.shear_force_design_kn:,.2f} kN"
            },
            "step2_neutral_axis": {
                "title": "Step 2: Midship Cross-Section Neutral Axis Integration",
                "description": "Summation of structural cross-sectional strakes and first moments about baseline.",
                "elements_selected": f"{len(active_els)} of {len(elements)} structural strakes selected",
                "total_area_formula": "A_total = Σ a_i",
                "total_area_substitution": f"{props.total_area_cm2:,.2f} cm² ({sum_a_m2:.4f} m²)",
                "first_moment_formula": "Σ (a_i × y_i) about Keel Baseline",
                "first_moment_substitution": f"{sum_ay_m3:.4f} m³ ({sum_ay_m3 * 1e9:,.0f} mm³)",
                "yna_formula": "y_NA = Σ (a_i × y_i) / Σ a_i",
                "yna_substitution": f"{sum_ay_m3:.4f} m³ / {sum_a_m2:.4f} m² = {props.neutral_axis_above_keel_m:.3f} m ({props.neutral_axis_above_keel_mm:.1f} mm above Keel)",
                "y_deck_substitution": f"y_deck = D - y_NA = {depth:.3f} m - {props.neutral_axis_above_keel_m:.3f} m = {props.distance_to_deck_m:.3f} m ({props.distance_to_deck_mm:.1f} mm)",
                "y_bottom_substitution": f"y_bottom = y_NA = {props.neutral_axis_above_keel_m:.3f} m ({props.neutral_axis_above_keel_mm:.1f} mm)"
            },
            "step3_inertia_and_modulus": {
                "title": "Step 3: Moment of Inertia (I_NA) and Hull Girder Section Modulus",
                "description": "Application of the Parallel-Axis Theorem (Steiner's Theorem) for midship inertia.",
                "ina_formula": "I_NA = Σ i_0,i + Σ [ a_i × (y_i - y_NA)² ]",
                "ina_substitution": f"Own Inertia ({sum_i0_m4:.4f} m⁴) + Transfer Inertia ({sum_ad2_m4:.4f} m⁴) = {props.moment_of_inertia_m4:.4f} m⁴ ({props.moment_of_inertia_cm4:,.1f} cm⁴)",
                "z_deck_formula": "Z_deck = I_NA / y_deck",
                "z_deck_substitution": f"{props.moment_of_inertia_cm4:,.1f} cm⁴ / {(props.distance_to_deck_mm / 10.0):,.1f} cm = {props.modulus_deck_cm3:,.2f} cm³",
                "z_bottom_formula": "Z_bottom = I_NA / y_bottom",
                "z_bottom_substitution": f"{props.moment_of_inertia_cm4:,.1f} cm⁴ / {(props.neutral_axis_above_keel_mm / 10.0):,.1f} cm = {props.modulus_bottom_cm3:,.2f} cm³",
                "z_actual": f"Z_actual = min(Z_deck, Z_bottom) = {props.modulus_actual_cm3:,.2f} cm³"
            },
            "step4_statutory_modulus_rule_209": {
                "title": "Step 4: Statutory Required Section Modulus (Rule 209)",
                "description": "Governing statutory requirement evaluated from maximum allowable stress and empirical lower bound.",
                "z1_stress_formula": "Z_1 = (M_design × 10³) / σ_allowable (σ_allowable = 130 N/mm² per Table 66)",
                "z1_stress_substitution": f"({moments.m_design_knm:,.2f} × 10³) / 130 = {z1_stress_cm3:,.2f} cm³",
                "z2_emp_formula": "Z_2 = 1.75 × k_t × L² × B × (C_b + 0.70)",
                "z2_emp_substitution": f"1.75 × {factor_kt:.2f} × ({lbp:.2f})² × {breadth:.2f} × ({cb:.3f} + 0.70) = {z2_emp_cm3:,.2f} cm³",
                "z_required": f"Z_req = max(Z_1, Z_2) = {props.modulus_rule_required_cm3:,.2f} cm³",
                "compliance_check": f"Provided Z_act ({props.modulus_actual_cm3:,.2f} cm³) ≥ Required Z_req ({props.modulus_rule_required_cm3:,.2f} cm³) → Margin: +{props.modulus_margin_pct:.1f}% ({'COMPLIANT' if props.modulus_margin_cm3 >= 0 else 'DEFICIENT'})"
            },
            "step5_table_66_stress_matrix": {
                "title": "Step 5: Schedule Table 66 Hull Girder Stress Verification Matrix (সারণি-৬৬)",
                "description": "Global hull girder continuous member stresses under governing design moments.",
                "sigma_deck_formula": "σ_deck = (M_design × 1000) / Z_deck",
                "sigma_deck_substitution": f"({moments.m_design_knm:,.2f} × 1000) / {props.modulus_deck_cm3:,.2f} = {table_66.bending_stress_deck_n_mm2:.2f} N/mm² (Allowable: ≤ 130.0 N/mm² → {table_66.status_bending})",
                "sigma_bottom_formula": "σ_bottom = (M_design × 1000) / Z_bottom",
                "sigma_bottom_substitution": f"({moments.m_design_knm:,.2f} × 1000) / {props.modulus_bottom_cm3:,.2f} = {table_66.bending_stress_bottom_n_mm2:.2f} N/mm² (Allowable: ≤ 130.0 N/mm² → {table_66.status_bending})",
                "tau_formula": "τ = (Q_t × 1000) / (2 × D × t_side)",
                "tau_substitution": f"({moments.shear_force_design_kn:,.2f} × 1000) / {a_shear_mm2:,.1f} = {table_66.hull_shear_stress_n_mm2:.2f} N/mm² (Allowable: ≤ 70.0 N/mm² → {table_66.status_shear})",
                "sigma_e_formula": "σ_e = √(σ_max² + 3 × τ²)",
                "sigma_e_substitution": f"√(({table_66.max_bending_stress_n_mm2:.2f})² + 3 × ({table_66.hull_shear_stress_n_mm2:.2f})²) = {table_66.equivalent_stress_n_mm2:.2f} N/mm² (Allowable: ≤ 150.0 N/mm² → {table_66.status_equivalent})"
            }
        }

        return {
            "vessel_name": vessel_name,
            "vessel_type": vessel_type,
            "route_name": route_name,
            "factor_kt": factor_kt,
            "factor_kz": factor_kz,
            "factor_cw": moments.wave_coefficient_cw,
            "overall_status": overall_status,
            "is_compliant": is_compliant,
            "executive_summary": summary_text,
            "practical_working": practical_working,
            "particulars": {
                "lbp": lbp,
                "breadth": breadth,
                "depth": depth,
                "draft": draft,
                "cb": cb,
                "displacement": float(inp.get('displacement', 2850.0) or 2850.0)
            },
            "bending_moments": {
                "m_sw_knm": moments.m_sw_knm,
                "m_wave_hog_knm": moments.m_wave_hog_knm,
                "m_wave_sag_knm": moments.m_wave_sag_knm,
                "m_total_hog_knm": moments.m_total_hog_knm,
                "m_total_sag_knm": moments.m_total_sag_knm,
                "m_design_knm": moments.m_design_knm,
                "design_condition": moments.design_condition,
                "wave_coefficient_cw": moments.wave_coefficient_cw,
                "shear_force_design_kn": moments.shear_force_design_kn
            },
            "midship_properties": {
                "total_area_cm2": props.total_area_cm2,
                "neutral_axis_above_keel_m": props.neutral_axis_above_keel_m,
                "neutral_axis_above_keel_mm": props.neutral_axis_above_keel_mm,
                "distance_to_deck_m": props.distance_to_deck_m,
                "distance_to_deck_mm": props.distance_to_deck_mm,
                "dist_deck_to_na_m": props.distance_to_deck_m,
                "dist_bottom_to_na_m": props.neutral_axis_above_keel_m,
                "first_moment_cm3": round(props.total_area_cm2 * (props.neutral_axis_above_keel_mm / 10.0), 1),
                "moment_of_inertia_cm4": props.moment_of_inertia_cm4,
                "moment_of_inertia_m4": props.moment_of_inertia_m4,
                "modulus_deck_cm3": props.modulus_deck_cm3,
                "modulus_bottom_cm3": props.modulus_bottom_cm3,
                "modulus_actual_cm3": props.modulus_actual_cm3,
                "modulus_rule_required_cm3": props.modulus_rule_required_cm3,
                "modulus_bending_cm3": z1_stress_cm3,
                "modulus_empirical_cm3": z2_emp_cm3,
                "modulus_margin_cm3": props.modulus_margin_cm3,
                "modulus_margin_pct": props.modulus_margin_pct,
                "elements_count": len(props.elements),
                "elements_selected_count": len(active_els),
                "elements": [
                    {
                        "id": el.id,
                        "name": el.name,
                        "category": el.category,
                        "width_mm": el.width_mm,
                        "thk_mm": el.thk_mm,
                        "quantity": el.quantity,
                        "area_mm2": el.area_mm2,
                        "lever_y_mm": el.lever_y_mm,
                        "own_inertia_mm4": el.own_inertia_mm4,
                        "is_vertical": el.is_vertical,
                        "is_included": getattr(el, 'is_included', True),
                        "notes": el.notes
                    }
                    for el in props.elements
                ]
            },
            "table_66_stresses": {
                "bending_stress_deck_n_mm2": table_66.bending_stress_deck_n_mm2,
                "bending_stress_bottom_n_mm2": table_66.bending_stress_bottom_n_mm2,
                "max_bending_stress_n_mm2": table_66.max_bending_stress_n_mm2,
                "allowable_bending_stress_n_mm2": table_66.allowable_bending_stress_n_mm2,
                "hull_shear_stress_n_mm2": table_66.hull_shear_stress_n_mm2,
                "allowable_shear_stress_n_mm2": table_66.allowable_shear_stress_n_mm2,
                "equivalent_stress_n_mm2": table_66.equivalent_stress_n_mm2,
                "allowable_equivalent_stress_n_mm2": table_66.allowable_equivalent_stress_n_mm2,
                "status_bending": table_66.status_bending,
                "status_shear": table_66.status_shear,
                "status_equivalent": table_66.status_equivalent,
                "is_overall_compliant": table_66.is_overall_compliant
            },
            "table_67_local_stresses": [
                {
                    "member_name": m.member_name,
                    "member_type": m.member_type,
                    "governing_load_desc": m.governing_load_desc,
                    "calculated_stress_n_mm2": m.calculated_stress_n_mm2,
                    "allowable_stress_n_mm2": m.allowable_stress_n_mm2,
                    "unit": m.unit,
                    "status": m.status,
                    "margin": m.margin,
                    "notes": m.notes
                }
                for m in table_67
            ],
            "assumed_axis_integration": assumed_axis_results
        }

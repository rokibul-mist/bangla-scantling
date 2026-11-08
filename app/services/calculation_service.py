import math
from typing import Dict, Any, List

from app.domain.rules.factors import evaluate_statutory_factors
from app.domain.rules.limits import evaluate_frame_spacing_limit, evaluate_collision_bulkhead_limit
from app.domain.catalog.structural_catalog import get_active_members
from app.domain.calc.section_modulus import calc_stiffener_section
from app.services.lightship_service import LightshipService
from app.services.compliance_service import ComplianceService
from app.domain.rules.interpolations.registry import TableInterpolationRegistry

def _to_float(val: Any, default: float = 0.0) -> float:
    try:
        if val is None or val == "":
            return default
        return float(val)
    except (ValueError, TypeError):
        return default

def _evaluate_components(
    components: List[Dict[str, Any]],
    hw: float,
    tw: float,
    bf: float,
    tf: float,
    prov_sm: float
) -> tuple[List[Dict[str, Any]], bool]:
    eval_list = []
    all_pass = True
    prov_face_area = round((bf * tf) / 100.0, 2)  # mm * mm -> cm2

    for comp in components:
        c_copy = dict(comp)
        param = c_copy.get('param')
        rreq = float(c_copy.get('rreq', 0.0))

        if param == 'web_thk':
            prov = tw
        elif param in ['face_area', 'flange_area']:
            prov = prov_face_area
        elif param in ['face_width', 'flange_width']:
            prov = bf
        elif param == 'web_depth':
            prov = hw
        elif param == 'sm':
            prov = round(prov_sm, 2)
        else:
            prov = round(prov_sm, 2)

        c_margin = round(prov - rreq, 2)
        c_status = 'COMPLIANT' if c_margin >= 0 else 'NON-COMPLIANT'
        if c_status != 'COMPLIANT':
            all_pass = False

        c_copy['prov'] = prov
        c_copy['margin'] = c_margin
        c_copy['status'] = c_status
        eval_list.append(c_copy)

    return eval_list, all_pass

class CalculationService:
    @staticmethod
    def compute_all_calculations(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes the full state with dashboard_inputs, stiffener_custom_dims, provided values
        and computes:
        - Dynamic calculation brain compliance audit (based on active hull type and vessel type)
        - Dynamic Sheet-2 detailed calculations with attached plate thickness from welded plate
        - Lightship Weight breakdown
        - Scantling Checklist updates
        """
        inputs = state.get('dashboard_inputs', {}) or {}
        custom_dims = state.get('stiffener_custom_dims', {}) or {}

        # Factor Multiplier according to statutory rules
        kt, kz, rule_desc = evaluate_statutory_factors(inputs)
        is_bay = kt > 1.0 or 'bay' in str(inputs.get('proposed_route', inputs.get('route', ''))).lower()

        # Hull Construction Type: 'Double Bottom', 'Double Hull', 'Single Hull'
        hull_type = str(inputs.get('hull_type', 'Double Bottom'))
        if hull_type == 'Single Bottom':
            hull_type = 'Single Hull'
        is_single_hull = 'single' in hull_type.lower()
        is_double_hull = 'double hull' in hull_type.lower()
        vessel_type = str(inputs.get('vessel_type', 'Steel Body Cargo Vessel'))

        # Store effective factors & hull type
        inputs['effective_kt'] = kt
        inputs['effective_kz'] = kz
        inputs['factor_rule_desc'] = rule_desc
        inputs['hull_type'] = hull_type

        lbp = _to_float(inputs.get('lbp'), 69.85)
        loa = _to_float(inputs.get('loa'), 76.21)
        breadth = _to_float(inputs.get('breadth'), 13.41)
        depth = _to_float(inputs.get('depth'), 5.18)
        draft = _to_float(inputs.get('draft'), 4.0)
        spacing = _to_float(inputs.get('frame_spacing'), 550.0)
        cb = _to_float(inputs.get('cb', inputs.get('Cb', 0.82)), 0.82)

        # Active plate thicknesses from inputs or statutory baselines
        plate_thk_map = {
            't_keel': _to_float(inputs.get('t_keel', inputs.get('plate_keel')), 13.0),
            'w_keel': _to_float(inputs.get('w_keel'), 1100.0),
            't_bottom': _to_float(inputs.get('t_bottom', inputs.get('plate_bottom')), 12.0),
            't_bilge': _to_float(inputs.get('t_bilge', inputs.get('plate_bilge')), 14.0),
            't_side': _to_float(inputs.get('t_side', inputs.get('plate_side')), 12.0),
            't_sheer': _to_float(inputs.get('t_sheer', inputs.get('t_side')), 12.0),
            't_deck_all': _to_float(inputs.get('t_deck_all', inputs.get('plate_deck')), 12.0),
            't_deck_hatch': _to_float(inputs.get('t_deck_hatch', inputs.get('plate_deck_hatch')), 12.0),
            't_inner_bottom': 0.0 if is_single_hull else _to_float(inputs.get('t_inner_bottom', inputs.get('plate_inner_bottom')), 14.0),
            't_margin': 0.0 if is_single_hull else _to_float(inputs.get('t_margin'), 14.0),
            't_inner_side': _to_float(inputs.get('t_inner_side'), 12.0),
            't_hopper': _to_float(inputs.get('t_hopper'), 12.0),
            't_bhd': _to_float(inputs.get('t_bhd', inputs.get('plate_bhd')), 10.0),
            't_bhd_collision': _to_float(inputs.get('t_bhd_collision'), 11.0),
            't_coaming': _to_float(inputs.get('t_coaming'), 12.0),
            't_hatch_long': _to_float(inputs.get('t_hatch_long'), 13.0),
            't_hatch_trans': _to_float(inputs.get('t_hatch_trans'), 12.0),
            't_hatch_cover': _to_float(inputs.get('t_hatch_cover'), 8.0),
            't_stem': _to_float(inputs.get('t_stem'), 14.0),
            't_transom': _to_float(inputs.get('t_transom'), 12.0),
            't_bulwark': _to_float(inputs.get('t_bulwark'), 6.0),
            't_poop_deck': _to_float(inputs.get('t_poop_deck'), 7.0),
            't_forecastle_deck': _to_float(inputs.get('t_forecastle_deck'), 7.0),
            't_nav_deck': _to_float(inputs.get('t_nav_deck'), 6.0),
            't_second_deck': _to_float(inputs.get('t_second_deck'), 6.5),
            't_passenger_deck': _to_float(inputs.get('t_passenger_deck'), 6.0),
            't_wet_deck': _to_float(inputs.get('t_wet_deck'), 8.0),
            't_tunnel_side': _to_float(inputs.get('t_tunnel_side'), 8.5),
            't_chine': _to_float(inputs.get('t_chine'), 14.0),
            't_rake': _to_float(inputs.get('t_rake'), 12.0),
            't_long_bhd': _to_float(inputs.get('t_long_bhd'), 10.0),
            't_tank_bhd': _to_float(inputs.get('t_tank_bhd'), 10.0),
            't_cofferdam': _to_float(inputs.get('t_cofferdam'), 9.0),
            't_wash_bhd': _to_float(inputs.get('t_wash_bhd'), 9.0),
            't_pump_room_bhd': _to_float(inputs.get('t_pump_room_bhd'), 9.0),
            't_deck_strip': _to_float(inputs.get('t_deck_strip'), 12.0),
            't_floor_web': _to_float(inputs.get('t_floor_web'), 10.0),
            't_chain_locker': _to_float(inputs.get('t_chain_locker'), 8.0),
            't_rudder': _to_float(inputs.get('t_rudder', inputs.get('rudder_blade_thk')), 10.0),
            't_tank_boundary': _to_float(inputs.get('t_tank_boundary'), 11.0),
        }

        # Fetch active structural members dynamically for this hull type & vessel type
        active_members = get_active_members(hull_type, vessel_type)
        custom_brain_dact = state.get('custom_brain_dact', {}) or {}

        # Calculation context inputs for statutory table interpolators
        calc_inputs = {
            'lbp': lbp,
            'length': lbp,
            'L': lbp,
            'breadth': breadth,
            'B': breadth,
            'depth': depth,
            'D': depth,
            'draft': draft,
            'd': draft,
            'cb': cb,
            'Cb': cb,
            'frame_spacing': spacing,
            'spacing': spacing,
            'effective_kt': kt,
            'effective_kz': kz,
            'kt': kt,
            'kz': kz,
            'is_single_hull': is_single_hull,
            **inputs
        }

        sheet2_results = []
        sheet_counter = 1

        for m in active_members:
            m_id = m['id']
            m_type = m['type']
            raw_base = float(m.get('baseline', 0) or 0)

            # Dynamic statutory rule empirical table interpolation
            interp_res = TableInterpolationRegistry.interpolate_member(m_id, calc_inputs)
            if interp_res:
                m['baseline'] = interp_res.baseline
                m['rreq'] = interp_res.rreq
                m['derivation'] = interp_res.to_dict()
                if interp_res.table_no:
                    m['table_ref'] = interp_res.table_no
            else:
                factor_for_m = kz if m_type == 'stiffener' else (kt if m_type == 'plate' else 1.0)
                calc_rreq = round(raw_base * factor_for_m, 2)
                m['baseline'] = raw_base
                m['factor'] = factor_for_m
                m['rreq'] = calc_rreq
                m['derivation'] = {
                    'baseline': raw_base,
                    'rreq': calc_rreq,
                    'unit': m.get('unit', 'mm'),
                    'table_no': m.get('table_ref', 'Statutory Rule'),
                    'table_title': m.get('name', ''),
                    'formula_desc': 'Statutory Baseline Multiplier',
                    'derivation_text': (
                        f"Rule evaluation for {m.get('name')}: Baseline = {raw_base} {m.get('unit', 'mm')} × factor({factor_for_m:.2f}) = {calc_rreq} {m.get('unit', 'mm')}."
                        if factor_for_m != 1.0
                        else f"Rule evaluation for {m.get('name')}: Baseline = {raw_base} {m.get('unit', 'mm')}."
                    ),
                    'table_view': None
                }

            if m_type == 'plate':
                # Plating Member
                b_key = m.get('bound_plate_key', '')
                if custom_brain_dact.get(m_id) is not None:
                    prov_val = _to_float(custom_brain_dact.get(m_id), raw_base)
                elif b_key and inputs.get(b_key) is not None:
                    prov_val = _to_float(inputs.get(b_key), raw_base)
                elif inputs.get(m_id) is not None:
                    prov_val = _to_float(inputs.get(m_id), raw_base)
                elif b_key in plate_thk_map:
                    prov_val = plate_thk_map[b_key]
                else:
                    prov_val = _to_float(inputs.get(b_key, raw_base), raw_base)

                eff_factor = kt
                if interp_res and interp_res.inputs_used and 'factor' in interp_res.inputs_used:
                    eff_factor = float(interp_res.inputs_used['factor'])
                elif 'width' in m_id or m_id in ['plate_keel_width', 'w_keel', 'plate_bulwark', 'plate_chain_locker_wall']:
                    eff_factor = 1.00

                m['factor'] = eff_factor
                req_val = interp_res.rreq if interp_res else round(raw_base * eff_factor, 2)
                m['rreq'] = req_val
                if 'derivation' in m and m['derivation']:
                    m['derivation']['rreq'] = req_val
                    m['derivation']['factor'] = eff_factor
                    m['derivation']['baseline'] = m['baseline']
                m['dact'] = prov_val

                margin = round(prov_val - req_val, 2)
                is_comp = margin >= 0
                m['margin'] = margin
                m['status'] = 'COMPLIANT' if is_comp else 'NON-COMPLIANT'

            elif m_type == 'stiffener':
                # Stiffener Member with attached plating
                w_key = m.get('welded_plate_key', 't_side')
                tp = plate_thk_map.get(w_key, 12.0)

                # Profile dimensions: user custom dimensions or default catalog
                c_dim = custom_dims.get(m_id, {})
                d_prof = m.get('default_profile') or {}

                ptype = c_dim.get('profile_type') or d_prof.get('profile_type', 'L')
                hw = _to_float(c_dim.get('web_depth') or d_prof.get('web_depth', 150), 150.0)
                tw = _to_float(c_dim.get('web_thk') or d_prof.get('web_thk', 10), 10.0)
                bf = 0.0 if ptype == 'FB' else _to_float(c_dim.get('flange_width') or d_prof.get('flange_width', 100), 100.0)
                tf = 0.0 if ptype == 'FB' else _to_float(c_dim.get('flange_thk') or d_prof.get('flange_thk', 10), 10.0)

                # Section modulus calculation with attached plate thickness tp
                s_res = calc_stiffener_section(spacing, tp, hw, tw, bf, tf, profile_type=ptype)
                prov_sm = s_res['z_cm3']

                # Required calculation
                m['factor'] = kz
                req_sm = interp_res.rreq if interp_res else round(raw_base * kz, 2)
                m['rreq'] = req_sm
                if 'derivation' in m and m['derivation']:
                    m['derivation']['rreq'] = req_sm
                    m['derivation']['factor'] = kz
                    m['derivation']['baseline'] = m['baseline']
                m['dact'] = round(prov_sm, 2)

                margin = round(prov_sm - req_sm, 2)
                is_comp = margin >= 0

                # Multi-criterion components evaluation if table prescribes multiple physical parts
                raw_comps = (interp_res.components if interp_res and interp_res.components else (m.get('derivation', {}).get('components') or []))
                if raw_comps:
                    comp_evals, all_pass = _evaluate_components(raw_comps, hw, tw, bf, tf, prov_sm)
                    m['components'] = comp_evals
                    if 'derivation' in m and m['derivation']:
                        m['derivation']['components'] = comp_evals
                    is_comp = is_comp and all_pass

                m['margin'] = margin
                m['status'] = 'COMPLIANT' if is_comp else 'NON-COMPLIANT'

                m['welded_plate_thickness'] = tp
                m['profile_type'] = ptype
                m['web_depth'] = hw
                m['web_thk'] = tw
                m['flange_width'] = bf
                m['flange_thk'] = tf

                # Add to Sheet-2 detailed calculations booklet
                sheet2_results.append({
                    'id': sheet_counter,
                    'member_id': m_id,
                    'name': m['name'],
                    'type': 'section_modulus',
                    'table_ref': m.get('table_ref', ''),
                    'welded_on_plate': m.get('welded_on_plate', ''),
                    'welded_plate_key': w_key,
                    'plate_width': spacing,
                    'plate_thk': tp,
                    'web_height': hw,
                    'web_thk': tw,
                    'flange_width': bf,
                    'flange_thk': tf,
                    'rreq': req_sm,
                    'margin': margin,
                    'status': 'COMPLIANT' if is_comp else 'NON-COMPLIANT',
                    'derivation': m.get('derivation'),
                    **s_res,
                    'profile_type': ptype
                })
                sheet_counter += 1

            else:
                # Dimension / Limit / Equipment / Piping
                eff_f = 1.00
                if interp_res and interp_res.inputs_used and 'factor' in interp_res.inputs_used:
                    eff_f = interp_res.inputs_used['factor']
                m['factor'] = eff_f
                req_val = interp_res.rreq if interp_res else raw_base
                m['rreq'] = req_val
                if 'derivation' in m and m['derivation']:
                    m['derivation']['factor'] = eff_f
                    m['derivation']['baseline'] = m['baseline']

                # Actual value
                if inputs.get(m_id) is not None:
                    dact = _to_float(inputs.get(m_id), req_val)
                elif custom_brain_dact.get(m_id) is not None:
                    dact = _to_float(custom_brain_dact.get(m_id), req_val)
                else:
                    dact = _to_float(m.get('dact', req_val), req_val)
                m['dact'] = dact

                if m_id == 'frame_spacing_limit':
                    req_limit, is_comp, margin = evaluate_frame_spacing_limit(lbp, spacing)
                    m['rreq'] = req_limit
                    m['dact'] = spacing
                    m['margin'] = margin
                elif m_id == 'bhd_collision_pos':
                    actual_pos = _to_float(inputs.get('actual_collision_bhd_pos', 4.8), 4.8)
                    min_pos, max_pos, is_comp, margin = evaluate_collision_bulkhead_limit(lbp, actual_pos)
                    m['rreq'] = min_pos
                    m['dact'] = actual_pos
                    m['margin'] = margin
                else:
                    is_comp = dact >= req_val
                    m['margin'] = round(dact - req_val, 2)

                raw_comps = (interp_res.components if interp_res and interp_res.components else (m.get('derivation', {}).get('components') or []))
                if raw_comps:
                    comp_evals = []
                    all_c_pass = True
                    for c in raw_comps:
                        c_copy = dict(c)
                        c_req = float(c_copy.get('rreq', req_val))
                        c_prov = float(c_copy.get('prov', dact) if c_copy.get('prov') is not None else dact)
                        c_margin = round(c_prov - c_req, 2)
                        c_pass = c_margin >= 0
                        if not c_pass:
                            all_c_pass = False
                        c_copy['prov'] = c_prov
                        c_copy['margin'] = c_margin
                        c_copy['status'] = 'COMPLIANT' if c_pass else 'NON-COMPLIANT'
                        comp_evals.append(c_copy)
                    m['components'] = comp_evals
                    if 'derivation' in m and m['derivation']:
                        m['derivation']['components'] = comp_evals

                m['status'] = 'COMPLIANT' if is_comp else 'NON-COMPLIANT'

        # Dynamically update Stiffener Profiles (Table 4) derived Section Modulus
        prof_plate_map = {
            1: 't_side', 2: 't_bottom', 3: 't_side', 4: 't_deck_all',
            5: 't_deck_all', 6: 't_deck_all', 7: 't_bhd', 8: 't_bhd',
            9: 't_side', 10: 't_deck_hatch'
        }
        stiff_profiles = state.get('stiffener_profiles', [])
        for p in stiff_profiles:
            p_id = p.get('id', 1)
            w_key = prof_plate_map.get(p_id, 't_side')
            tp = plate_thk_map.get(w_key, 12.0)
            ptype = p.get('profile_type', 'L')
            hw = float(p.get('web_depth', 150))
            tw = float(p.get('web_thk', 10))
            bf = float(p.get('flange_width', 100))
            tf = float(p.get('flange_thk', 10))
            s_res = calc_stiffener_section(spacing, tp, hw, tw, bf, tf, profile_type=ptype)
            p['derived_sm'] = round(s_res['z_cm3'], 2)
            p['yna'] = round(s_res['yna'], 2)
            p['tp'] = tp

        # Update Scantling Checklist
        chk = state.get('scantling_checklist', [])
        for row in chk:
            r_no = row.get('no')
            if r_no == 1: row['provided'] = plate_thk_map.get('t_keel', 13.0)
            elif r_no == 2: row['provided'] = plate_thk_map.get('t_bottom', 12.0)
            elif r_no == 3: row['provided'] = plate_thk_map.get('t_bilge', 14.0)
            elif r_no == 4: row['provided'] = plate_thk_map.get('t_side', 12.0)
            elif r_no == 5: row['provided'] = plate_thk_map.get('t_deck_hatch', 12.0)
            elif r_no == 6: row['provided'] = plate_thk_map.get('t_deck_all', 12.0)
            elif r_no == 15: row['provided'] = plate_thk_map.get('t_bhd', 10.0)
            elif r_no == 17: row['provided'] = plate_thk_map.get('t_hatch_long', 13.0)
            elif r_no == 18: row['provided'] = plate_thk_map.get('t_hatch_trans', 12.0)
            elif r_no == 19: row['provided'] = plate_thk_map.get('t_hatch_cover', 8.0)
            elif r_no == 21: row['provided'] = plate_thk_map.get('t_inner_bottom', 14.0)

            b_val = float(row.get('baseline', 0) or 0)
            if r_no in [1, 2, 3, 4, 5, 6, 15, 17, 18, 19, 21]:
                row['factor'] = kt
                row['required'] = round(b_val * kt, 2)
            else:
                row['factor'] = kz
                row['required'] = round(b_val * kz, 2)

            rreq = float(row.get('required', 0))
            dact = float(row.get('provided', 0))
            row['margin'] = round(dact - rreq, 2)
            row['margin_pct'] = round((dact - rreq) / rreq, 4) if rreq > 0 else 0.0
            row['status'] = 'COMPLIED' if dact >= rreq else 'DEFICIENT'

        # Lightship weight synthesis calculation via dedicated service
        ls_data = LightshipService.calculate_lightship(state, plate_thk_map, is_single_hull)

        # Compliance summary statistics via dedicated service
        summary_stats = ComplianceService.evaluate_summary_stats(active_members, is_bay)

        return {
            'dashboard_inputs': inputs,
            'stiffener_custom_dims': custom_dims,
            'stiffener_profiles': state.get('stiffener_profiles', []),
            'scantling_checklist': state.get('scantling_checklist', []),
            'propulsion_items': state.get('propulsion_items', []),
            'rudder_items': state.get('rudder_items', []),
            'piping_items': state.get('piping_items', []),
            'anchoring_items': state.get('anchoring_items', []),
            'outfitting_items': state.get('outfitting_items', []),
            'sheet2_results': sheet2_results,
            'lightship_plates': ls_data['plates'],
            'lightship_angles': ls_data['angles'],
            'lightship_summary': ls_data['summary'],
            'calculation_brain': active_members,
            'summary_stats': summary_stats,
            'designer_seal_png': state.get('designer_seal_png') if 'designer_seal_png' in state and state.get('designer_seal_png') is not None else '/static/designer_seal_default.png',
            'checker_seal_png': state.get('checker_seal_png') if 'checker_seal_png' in state and state.get('checker_seal_png') is not None else '/static/checker_seal_default.png',
            'application_form_pages': state.get('application_form_pages', []),
            'empirical_tables': state.get('empirical_tables', [])
        }

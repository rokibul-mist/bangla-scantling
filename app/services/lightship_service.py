"""
Naval Architecture Lightship Weight Estimation Service.
Computes net steel plating, structural stiffeners, and statutory 56% outfitting allowances
based on realistic shipyard bills of materials, statutory scantlings, and ship dimensions.
"""

from typing import Dict, Any, List
from app.domain.calc.weight_calc import calc_plate_weight, calc_angle_weight, calc_lightship_allowances


def clean_element_name(raw_name: str) -> str:
    """Removes dimensions, rule citations, or trailing notes for statutory Clean Element Names."""
    if not raw_name:
        return ""
    name = raw_name.strip()
    if '(' in name and not name.startswith('Superstructure') and not name.startswith('Second') and not name.startswith('BHD') and not name.startswith('Deck Beam'):
        name = name.split('(')[0].strip()
    for suffix in [" Plating Thickness", " Thickness"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)] + " Plating" if "Plating" not in name else name[:-len(suffix)]
    return name.strip()


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Safely converts val to float, returning default if None, empty string, or invalid."""
    if val is None or val == "":
        return default
    try:
        f = float(val)
        import math
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (ValueError, TypeError):
        return default


def _safe_int(val: Any, default: int = 0) -> int:
    """Safely converts val to int, returning default if None, empty string, or invalid."""
    if val is None or val == "":
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


class LightshipService:
    """
    Computes realistic naval architecture lightship displacement and weight breakdown.
    Net Steel is derived from realistic structural plate assemblies and profile groups.
    """

    # Master baseline structural plate assemblies (19 standard shipbuilding assemblies)
    # L0, B0: reference dimensions for LOA=76.21m, B=13.41m, D=5.18m
    MASTER_BOM_PLATES = [
        {"sn": 1, "id": "plate_keel", "name": "Keel Plate", "bound_key": "t_keel", "l0": 76210, "b0": 600, "t_def": 13.0, "qty_def": 1, "scale_l": "loa", "scale_b": "fixed"},
        {"sn": 2, "id": "plate_bottom", "name": "Bottom Shell Plating", "bound_key": "t_bottom", "l0": 76210, "b0": 4605, "t_def": 12.0, "qty_def": 2, "scale_l": "loa", "scale_b": "bm"},
        {"sn": 3, "id": "plate_bilge", "name": "Bilge Plating", "bound_key": "t_bilge", "l0": 76210, "b0": 3000, "t_def": 14.0, "qty_def": 2, "scale_l": "loa", "scale_b": "fixed"},
        {"sn": 4, "id": "plate_side", "name": "Side Shell Plating", "bound_key": "t_side", "l0": 76210, "b0": 3680, "t_def": 12.0, "qty_def": 2, "scale_l": "loa", "scale_b": "dm"},
        {"sn": 5, "id": "plate_sheer_strake", "name": "Sheer Strake Plating", "bound_key": "t_side", "l0": 76210, "b0": 900, "t_def": 12.0, "qty_def": 2, "scale_l": "loa", "scale_b": "fixed"},
        {"sn": 6, "id": "plate_bulwark", "name": "Bulwark Plating", "bound_key": "t_bulwark", "l0": 50600, "b0": 1000, "t_def": 10.0, "qty_def": 2, "scale_l": "loa", "scale_b": "fixed"},
        {"sn": 7, "id": "plate_deck_hatch", "name": "Hatchway Deck Plating", "bound_key": "t_deck_hatch", "l0": 47740, "b0": 2100, "t_def": 12.0, "qty_def": 2, "scale_l": "loa", "scale_b": "fixed"},
        {"sn": 8, "id": "plate_main_deck", "name": "Main Deck Plating", "bound_key": "t_deck_all", "l0": 17350, "b0": 11928, "t_def": 12.0, "qty_def": 1, "scale_l": "loa", "scale_b": "bm"},
        {"sn": 9, "id": "plate_main_deck_wall", "name": "Main Deck Wall (Superstructure)", "bound_key": "t_side", "l0": 15753, "b0": 2300, "t_def": 10.0, "qty_def": 1, "scale_l": "loa", "scale_b": "fixed"},
        {"sn": 10, "id": "plate_poop_wall", "name": "Poop Deck Wall", "bound_key": "t_side", "l0": 8803, "b0": 2100, "t_def": 8.0, "qty_def": 1, "scale_l": "loa", "scale_b": "fixed"},
        {"sn": 11, "id": "plate_poop_deck", "name": "Poop Deck Plating", "bound_key": "t_poop_deck", "l0": 15499, "b0": 9781, "t_def": 7.0, "qty_def": 1, "scale_l": "loa", "scale_b": "bm"},
        {"sn": 12, "id": "plate_bridge_wall", "name": "Bridge Deck Wall", "bound_key": "t_side", "l0": 3100, "b0": 2000, "t_def": 8.0, "qty_def": 1, "scale_l": "fixed", "scale_b": "fixed"},
        {"sn": 13, "id": "plate_bridge_deck", "name": "Bridge Deck Plating", "bound_key": "t_nav_deck", "l0": 7840, "b0": 8803, "t_def": 6.0, "qty_def": 1, "scale_l": "fixed", "scale_b": "bm"},
        {"sn": 14, "id": "plate_bhd", "name": "Transverse Watertight Bulkheads", "bound_key": "t_bhd", "l0": 6705, "b0": 5180, "t_def": 10.0, "qty_def": 5, "scale_l": "bm", "scale_b": "dm"},
        {"sn": 15, "id": "plate_hatch_covers", "name": "Cargo Hatch Covers Plating", "bound_key": "t_deck_hatch", "l0": 14630, "b0": 8993, "t_def": 10.0, "qty_def": 3, "scale_l": "loa", "scale_b": "bm"},
        {"sn": 16, "id": "plate_forecastle_deck", "name": "Forecastle Deck Plating", "bound_key": "t_forecastle_deck", "l0": 10111, "b0": 8516, "t_def": 12.0, "qty_def": 1, "scale_l": "loa", "scale_b": "bm"},
        {"sn": 17, "id": "plate_inner_bottom", "name": "Double Bottom Tank Top Plate", "bound_key": "t_inner_bottom", "l0": 76210, "b0": 13410, "t_def": 12.0, "qty_def": 0, "scale_l": "loa", "scale_b": "bm"},  # 0 if single hull, 1 if double bottom
        {"sn": 18, "id": "plate_stem_transom", "name": "Stem, Stern & Rudder Assembly", "bound_key": "t_stem", "l0": 8000, "b0": 3500, "t_def": 14.0, "qty_def": 2, "scale_l": "fixed", "scale_b": "fixed"},
        {"sn": 19, "id": "plate_partitions", "name": "Superstructure Partition Bulkheads", "bound_key": "t_side", "l0": 11928, "b0": 2300, "t_def": 6.0, "qty_def": 2, "scale_l": "bm", "scale_b": "fixed"}
    ]

    # Master baseline structural stiffener assemblies (21 standard shipbuilding assemblies)
    MASTER_BOM_ANGLES = [
        {"sn": 1, "id": "stiff_centre_keelson", "name": "Center Keelson", "weld_plate": "Keel Plate", "hw": 500, "bf": 400, "tw": 12.0, "len0": 76210, "qty_def": 1, "scale_len": "loa"},
        {"sn": 2, "id": "stiff_side_keelson", "name": "Side Keelson", "weld_plate": "Bottom Shell Plating", "hw": 500, "bf": 150, "tw": 11.0, "len0": 76210, "qty_def": 8, "scale_len": "loa"},
        {"sn": 3, "id": "stiff_side_stringer", "name": "Side Stringer", "weld_plate": "Side Shell Plating", "hw": 324, "bf": 90, "tw": 11.0, "len0": 76210, "qty_def": 6, "scale_len": "loa"},
        {"sn": 4, "id": "stiff_deck_girder", "name": "Deck Girder", "weld_plate": "Main Deck Plating", "hw": 300, "bf": 90, "tw": 11.0, "len0": 76210, "qty_def": 7, "scale_len": "loa"},
        {"sn": 5, "id": "stiff_floor_single", "name": "Floor", "weld_plate": "Bottom Shell Plating", "hw": 500, "bf": 150, "tw": 14.0, "len0": 6705, "qty_def": 126, "scale_len": "bm_half"},
        {"sn": 6, "id": "stiff_web_frame", "name": "Web Frame", "weld_plate": "Side Shell Plating", "hw": 324, "bf": 90, "tw": 11.0, "len0": 4380, "qty_def": 27, "scale_len": "dm"},
        {"sn": 7, "id": "stiff_main_frame", "name": "Main Frame", "weld_plate": "Side Shell Plating", "hw": 190, "bf": 90, "tw": 9.0, "len0": 4380, "qty_def": 100, "scale_len": "dm"},
        {"sn": 8, "id": "stiff_deck_beam", "name": "Deck Beam", "weld_plate": "Main Deck Plating", "hw": 140, "bf": 90, "tw": 9.0, "len0": 6705, "qty_def": 52, "scale_len": "bm_half"},
        {"sn": 9, "id": "stiff_deck_web_beam", "name": "Deck Web", "weld_plate": "Main Deck Plating", "hw": 300, "bf": 90, "tw": 11.0, "len0": 6705, "qty_def": 27, "scale_len": "bm_half"},
        {"sn": 10, "id": "stiff_deck_beam_main", "name": "Deck Beam (Main Deck)", "weld_plate": "Main Deck Plating", "hw": 75, "bf": 75, "tw": 6.0, "len0": 6705, "qty_def": 30, "scale_len": "bm_half"},
        {"sn": 11, "id": "stiff_deck_beam_poop", "name": "Deck Beam (Poop Deck)", "weld_plate": "Poop Deck Plating", "hw": 65, "bf": 65, "tw": 6.0, "len0": 3813, "qty_def": 18, "scale_len": "fixed"},
        {"sn": 12, "id": "stiff_deck_beam_bridge", "name": "Deck Beam (Bridge Deck)", "weld_plate": "Bridge Deck Plating", "hw": 50, "bf": 50, "tw": 5.0, "len0": 2897, "qty_def": 7, "scale_len": "fixed"},
        {"sn": 13, "id": "stiff_bhd_vertical", "name": "BHD Angle (Vertical)", "weld_plate": "Transverse Watertight Bulkheads", "hw": 120, "bf": 120, "tw": 10.0, "len0": 5180, "qty_def": 45, "scale_len": "dm"},
        {"sn": 14, "id": "stiff_bhd_horizontal", "name": "BHD Angle (Horizontal)", "weld_plate": "Transverse Watertight Bulkheads", "hw": 120, "bf": 120, "tw": 10.0, "len0": 13410, "qty_def": 25, "scale_len": "bm"},
        {"sn": 15, "id": "stiff_hatch_girder", "name": "Hatch Girder", "weld_plate": "Hatchway Deck Plating", "hw": 65, "bf": 65, "tw": 6.0, "len0": 4605, "qty_def": 15, "scale_len": "fixed"},
        {"sn": 16, "id": "stiff_super_girder_main", "name": "Superstructure Girder (Main Deck)", "weld_plate": "Main Deck Wall (Superstructure)", "hw": 75, "bf": 75, "tw": 6.0, "len0": 2300, "qty_def": 31, "scale_len": "fixed"},
        {"sn": 17, "id": "stiff_super_girder_poop", "name": "Superstructure Girder (Poop Deck)", "weld_plate": "Poop Deck Wall", "hw": 65, "bf": 65, "tw": 6.0, "len0": 2100, "qty_def": 17, "scale_len": "fixed"},
        {"sn": 18, "id": "stiff_super_girder_bridge", "name": "Superstructure Girder (Bridge Deck)", "weld_plate": "Bridge Deck Wall", "hw": 50, "bf": 50, "tw": 5.0, "len0": 2000, "qty_def": 6, "scale_len": "fixed"},
        {"sn": 19, "id": "stiff_super_long_main", "name": "Superstructure Long. Girder (Main Deck)", "weld_plate": "Main Deck Wall (Superstructure)", "hw": 200, "bf": 90, "tw": 7.0, "len0": 15753, "qty_def": 1, "scale_len": "fixed"},
        {"sn": 20, "id": "stiff_super_long_poop", "name": "Superstructure Long. Girder (Poop Deck)", "weld_plate": "Poop Deck Wall", "hw": 200, "bf": 90, "tw": 7.0, "len0": 8803, "qty_def": 1, "scale_len": "fixed"},
        {"sn": 21, "id": "stiff_super_long_bridge", "name": "Superstructure Long. Girder (Bridge Deck)", "weld_plate": "Bridge Deck Wall", "hw": 200, "bf": 90, "tw": 7.0, "len0": 3100, "qty_def": 1, "scale_len": "fixed"},
    ]

    @classmethod
    def calculate_lightship(
        cls,
        state: Dict[str, Any],
        plate_thk_map: Dict[str, float],
        is_single_hull: bool
    ) -> Dict[str, Any]:
        """
        Dynamically drives Lightship plates and stiffeners from the realistic master BOM.
        Synchronizes thicknesses and profile geometries with active calculation results
        while preserving realistic naval architectural dimensions and weights.
        """
        inputs = state.get('dashboard_inputs', {}) or {}
        loa_m = _safe_float(inputs.get('loa'), 76.21)
        if loa_m <= 0:
            loa_m = 76.21
        loa_mm = loa_m * 1000.0

        bm_m = _safe_float(inputs.get('breadth'), 13.41)
        if bm_m <= 0:
            bm_m = 13.41
        bm_mm = bm_m * 1000.0

        dm_m = _safe_float(inputs.get('depth'), 5.18)
        if dm_m <= 0:
            dm_m = 5.18
        dm_mm = dm_m * 1000.0

        # Ratios relative to standard 76.21m x 13.41m x 5.18m baseline
        scale_l_ratio = loa_mm / 76210.0 if loa_mm > 0 else 1.0
        scale_b_ratio = bm_mm / 13410.0 if bm_mm > 0 else 1.0
        scale_d_ratio = dm_mm / 5180.0 if dm_mm > 0 else 1.0

        # Fast lookup of active brain items
        brain_by_id = {}
        for m in state.get('calculation_brain', []):
            if m.get('id'):
                brain_by_id[m['id']] = m

        stiff_dims = state.get('stiffener_custom_dims', {}) or {}
        custom_brain_dact = state.get('custom_brain_dact', {}) or {}

        # Lookups of existing plates & angles if user previously edited them
        existing_plates_by_sn = {}
        for p in state.get('lightship_plates', []):
            if p.get('sn') is not None:
                existing_plates_by_sn[p['sn']] = p

        existing_angles_by_sn = {}
        for a in state.get('lightship_angles', []):
            if a.get('sn') is not None:
                existing_angles_by_sn[a['sn']] = a

        # 1. Synthesize Plates
        plates: List[Dict[str, Any]] = []
        total_plate_kg = 0.0

        for tmpl in cls.MASTER_BOM_PLATES:
            sn = tmpl["sn"]
            m_id = tmpl["id"]
            name = clean_element_name(tmpl["name"])
            saved = existing_plates_by_sn.get(sn, {})
            if saved and saved.get('id') and saved.get('id') != m_id and saved.get('name') != name:
                saved = {}

            # Thickness: link to active scantling / brain / dashboard
            bound_k = tmpl.get("bound_key", "")
            t_val = tmpl["t_def"]
            if custom_brain_dact.get(m_id) is not None and str(custom_brain_dact[m_id]).strip() != "":
                t_val = _safe_float(custom_brain_dact[m_id], tmpl["t_def"])
            elif inputs.get(bound_k) is not None and str(inputs[bound_k]).strip() != "":
                t_val = _safe_float(inputs[bound_k], tmpl["t_def"])
            elif m_id in brain_by_id and brain_by_id[m_id].get('dact') is not None and str(brain_by_id[m_id]['dact']).strip() != "":
                t_val = _safe_float(brain_by_id[m_id]['dact'], tmpl["t_def"])
            elif bound_k in plate_thk_map and str(plate_thk_map[bound_k]).strip() != "":
                t_val = _safe_float(plate_thk_map[bound_k], tmpl["t_def"])
            elif saved.get('t') is not None and str(saved.get('t')).strip() != "":
                t_val = _safe_float(saved['t'], tmpl["t_def"])

            if t_val <= 0:
                t_val = tmpl["t_def"]

            # Dimension Scaling
            default_l = tmpl["l0"]
            if tmpl["scale_l"] == "loa":
                default_l = round(tmpl["l0"] * scale_l_ratio, 1)
            elif tmpl["scale_l"] == "bm":
                default_l = round(bm_mm, 1)

            default_b = tmpl["b0"]
            if tmpl["scale_b"] == "bm":
                default_b = round(tmpl["b0"] * scale_b_ratio, 1)
            elif tmpl["scale_b"] == "dm":
                default_b = round(tmpl["b0"] * scale_d_ratio, 1)

            # Hull type dependency: Single hull vessels have no double bottom tank top plate
            default_qty = tmpl["qty_def"]
            if m_id == "plate_inner_bottom":
                default_qty = 0 if is_single_hull else 1

            # Sanitize any previous corrupted dimensions
            saved_l = _safe_float(saved.get('l'), default_l)
            if saved_l <= 0:
                saved_l = default_l
            saved_b = _safe_float(saved.get('b'), default_b)
            if saved_b <= 0:
                saved_b = default_b
            saved_qty = _safe_int(saved.get('qty'), default_qty)
            if saved_qty < 0:
                saved_qty = default_qty

            # Guard against corrupted 76m x 13m stem/partition entries
            if tmpl["scale_l"] == "fixed" and saved_l > 25000.0:
                saved_l = default_l
            if tmpl["scale_b"] == "fixed" and saved_b > 6000.0:
                saved_b = default_b
            if m_id == "plate_inner_bottom" and is_single_hull:
                saved_qty = 0

            p_data = {
                'sn': sn,
                'id': m_id,
                'name': name,
                'l': saved_l,
                'b': saved_b,
                't': t_val,
                'density': 7850,
                'qty': saved_qty
            }

            p_res = calc_plate_weight(
                l_dim=p_data['l'],
                b_dim=p_data['b'],
                t=p_data['t'],
                density=p_data['density'],
                qty=p_data['qty']
            )
            p_data['vol'] = p_res['vol']
            p_data['weight_kg'] = p_res['weight_kg']
            p_data['weight_tonne'] = p_res['weight_tonne']
            total_plate_kg += p_data['weight_kg']
            plates.append(p_data)

        # 2. Synthesize Angles & Stiffeners
        angles: List[Dict[str, Any]] = []
        total_angle_kg = 0.0

        for tmpl in cls.MASTER_BOM_ANGLES:
            sn = tmpl["sn"]
            s_id = tmpl["id"]
            name = clean_element_name(tmpl["name"])
            saved = existing_angles_by_sn.get(sn, {})
            if saved and ((saved.get('id') and saved.get('id') != s_id) or (not saved.get('id') and saved.get('name') != name)):
                saved = {}

            # Profile Dimensions: dynamically linked to stiffener custom dims or brain
            c_dim = stiff_dims.get(s_id, {})
            brain_m = brain_by_id.get(s_id, {})
            d_prof = brain_m.get('default_profile', {})

            hw = _safe_float(c_dim.get('web_depth') or brain_m.get('web_depth') or d_prof.get('web_depth') or saved.get('l_dim'), tmpl["hw"])
            tw = _safe_float(c_dim.get('web_thk') or brain_m.get('web_thk') or d_prof.get('web_thk') or saved.get('t'), tmpl["tw"])
            bf = _safe_float(c_dim.get('flange_width') or brain_m.get('flange_width') or d_prof.get('flange_width') or saved.get('b_dim'), tmpl["bf"])

            if hw <= 0:
                hw = tmpl["hw"]
            if tw <= 0:
                tw = tmpl["tw"]
            if bf < 0:
                bf = tmpl["bf"]

            # Span Length Scaling
            default_len = tmpl["len0"]
            if tmpl["scale_len"] == "loa":
                default_len = round(tmpl["len0"] * scale_l_ratio, 1)
            elif tmpl["scale_len"] == "bm":
                default_len = round(bm_mm, 1)
            elif tmpl["scale_len"] == "bm_half":
                default_len = round(bm_mm / 2.0, 1)
            elif tmpl["scale_len"] == "dm":
                default_len = round(dm_mm > 500.0 and dm_mm - 500.0 or dm_mm, 1)
            elif tmpl["scale_len"] == "quarter_l":
                default_len = round(loa_mm * 0.25, 1)
            elif tmpl["scale_len"] == "loa_hatch":
                default_len = round(loa_mm * 0.62, 1)

            default_qty = tmpl["qty_def"]

            saved_len = _safe_float(saved.get('length'), default_len)
            if saved_len <= 0:
                saved_len = default_len
            saved_qty = _safe_int(saved.get('qty'), default_qty)
            if saved_qty < 0:
                saved_qty = default_qty

            # Guard against corrupted 40-qty side stringer or hatch girder entries
            if s_id in ["stiff_side_stringer", "stiff_hatch_girder"] and saved_qty > 10:
                saved_qty = default_qty

            a_data = {
                'sn': sn,
                'id': s_id,
                'name': name,
                'welded_on_plate': tmpl["weld_plate"],
                'l_dim': hw,
                'b_dim': bf,
                't': tw,
                'length': saved_len,
                'density': 7850,
                'qty': saved_qty
            }

            a_res = calc_angle_weight(
                l_dim=a_data['l_dim'],
                b_dim=a_data['b_dim'],
                t=a_data['t'],
                length=a_data['length'],
                density=a_data['density'],
                qty=a_data['qty']
            )
            a_data['area'] = a_res['area']
            a_data['vol'] = a_res['vol']
            a_data['weight_kg'] = a_res['weight_kg']
            a_data['weight_tonne'] = a_res['weight_tonne']
            total_angle_kg += a_data['weight_kg']
            angles.append(a_data)

        # 3. Outfitting & Synthesis
        total_steel_t = (total_plate_kg + total_angle_kg) / 1000.0
        allowances = calc_lightship_allowances(total_steel_t)

        lightship_summary = {
            'total_plate_tonne': round(total_plate_kg / 1000.0, 3),
            'total_angle_tonne': round(total_angle_kg / 1000.0, 3),
            'total_steel_tonne': round(total_steel_t, 3),
            **allowances
        }

        return {
            'plates': plates,
            'angles': angles,
            'summary': lightship_summary
        }

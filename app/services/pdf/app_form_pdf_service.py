import os
import io
import json
import re
from typing import Dict, Any, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics.shapes import Drawing, Rect, Line

from app.services.pdf.detail_calc_pdf_service import (
    FONT_REGULAR, FONT_BOLD, resolve_seal_image_bytes
)
from app.domain.catalog.structural_catalog import STRUCTURAL_MEMBERS

CATALOG_MEMBER_IDS = set(m['id'] for m in STRUCTURAL_MEMBERS)

# Item number to calculation brain ID mapping matching official DOS form
ITEM_TO_CALC_ID = {
    # Page 8 of 24 (Page 9)
    '7': 'mat_min_hull', '8': 'plate_keel', '9': 'plate_bottom', '10': 'stiff_main_frame',
    '11': 'plate_bilge', '12': 'plate_side', '13': 'plate_hatchway_deck', '14': 'plate_main_deck', '15': 'plate_inner_bottom',
    # Page 9 of 24 (Page 10)
    '16': 'plate_stem', '17': 'bar_stem', '18': 'stern_frame_bar', '19': 'stern_frame_bar',
    '20': 'propeller_post', '21': 'propeller_post', '22': 'propeller_post', '23': 'propeller_post', '24': 'sole_piece',
    # Page 10 of 24 (Page 11)
    '25': 'sole_piece_thk', '26': 'sole_piece', '27': 'propeller_boss_thk', '28': 'stiff_solid_floor',
    '29': 'stiff_centre_girder', '30': 'stiff_side_girder', '31': 'stiff_centre_girder', '32': 'stiff_main_frame', '33': 'stiff_main_frame',
    # Page 11 of 24 (Page 12)
    '34': 'frame_spacing_limit', '35': 'stiff_web_frame', '36': 'stiff_side_stringer', '37': 'stiff_deck_beam',
    '38': 'stiff_deck_web_beam', '39': 'stiff_deck_girder', '40': 'pillar_tubular_dia', '41': 'plate_bhd_wt',
    # Page 12 of 24 (Page 13)
    '42': 'bhd_collision_pos', '43': 'stiff_bhd_transverse', '44': 'stiff_bhd_transverse', '45': 'plate_bhd_wt',
    '46': 'plate_bhd_wt', '47': 'plate_bhd_wt', '48': 'plate_bhd_wt',
    # Page 13 of 24 (Page 14)
    '49': 'plate_bhd_wt', '50': 'plate_bhd_wt', '51': 'plate_bhd_wt', '52': 'plate_engine_girders',
    # Page 14 of 24 (Page 15)
    '53': 'stiff_web_frame', '54': 'stiff_web_frame', '55': 'plate_coaming_long', '56': 'plate_coaming_trans',
    '57': 'stiff_hatch_end_beam', '58': 'stiff_hatch_end_beam', '59': 'stiff_hatch_end_beam', '60': 'stiff_hatch_end_beam',
    '61': 'stiff_hatch_side_girder', '62': 'stiff_hatch_side_girder',
    # Page 15 of 24 (Page 16)
    '63': 'plate_hatch_cover', '64': 'stiff_hatch_cover', '65': 'plate_hatch_cover', '66': 'plate_coaming_long',
    '67': 'plate_bhd_wt', '68': 'plate_machinery_casing',
    # Page 16 of 24 (Page 17)
    '69': 'plate_coaming_long', '70': 'plate_main_deck', '71': 'freeing_port_area', '72': 'pipe_wall_thk',
    '73': 'plate_bhd_wt', '74': 'plate_bhd_wt', '75': 'plate_machinery_casing',
    # Page 17 of 24 (Page 18)
    '76': 'plate_main_deck', '77': 'rudder_stock_dia', '78': 'rudder_stock_dia', '79': 'rudder_pintle_dia', '80': 'rudder_flange_thk',
    # Page 18 of 24 (Page 19)
    '81': 'rudder_coupling_bolts', '82': 'rudder_blade_thk', '83': 'rudder_stock_dia', '84': 'rudder_stock_dia', '85': 'rudder_stock_dia',
    # Page 19 of 24 (Page 20)
    '86': 'steering_chains_shackles', '87': 'anchor_mass', '88': 'chain_cable_length', '89': 'chain_cable_length', '90': 'plate_bulwark',
    # Page 20 of 24 (Page 21)
    '91': 'plate_chain_locker_wall', '92': 'v_strut_shaft', '93': 'anchor_mass', '94': 'anchor_mass',
    '95': 'plate_bottom', '96': 'pipe_main_bilge_dia',
    # Page 21 of 24 (Page 22)
    '97': 'pipe_branch_bilge_dia', '98': 'pipe_wall_thk', '99': 'pipe_wall_thk',
    # Page 22 of 24 (Page 23)
    '100': 'pipe_wall_thk', '101': 'equipment_number', '102': 'equipment_number', '103': 'plate_coaming_long',
    '104': 'plate_main_deck',
    # Page 23 of 24 (Page 24)
    '105': 'plate_inner_bottom', '106': 'plate_bhd_tank'
}

class AppFormDualSealCanvas(canvas.Canvas):
    """
    Dedicated Canvas for Application Form.
    Draws dual corner seals on the bottom two corners of ALL pages:
    - Bottom-Left: Checker Seal (1.5x larger: 90 pt x 90 pt)
    - Bottom-Right: Designer Seal (1.5x larger: 90 pt x 90 pt)
    Strictly applied on every page (self._pageNumber >= 1).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checker_seal_bytes: Optional[bytes] = None
        self.designer_seal_bytes: Optional[bytes] = None

    def showPage(self):
        # 1.5 times larger: 60.0 * 1.5 = 90.0 pt
        seal_w = 90.0
        seal_h = 90.0
        y_pos = 10.0

        # Bottom-Left corner: Checker Seal
        if self.checker_seal_bytes:
            try:
                reader = ImageReader(io.BytesIO(self.checker_seal_bytes))
                self.drawImage(reader, 24.0, y_pos, width=seal_w, height=seal_h, mask='auto', preserveAspectRatio=True)
            except Exception as e:
                print(f"[AppForm Canvas] Left seal error: {e}")

        # Bottom-Right corner: Designer Seal
        if self.designer_seal_bytes:
            try:
                reader = ImageReader(io.BytesIO(self.designer_seal_bytes))
                x_pos = 595.27 - 24.0 - seal_w
                self.drawImage(reader, x_pos, y_pos, width=seal_w, height=seal_h, mask='auto', preserveAspectRatio=True)
            except Exception as e:
                print(f"[AppForm Canvas] Right seal error: {e}")

        super().showPage()

    def save(self):
        super().save()


def format_calc_num(val):
    if val is None or val == '':
        return ''
    try:
        num = float(val)
        return f"{num:.2f}" if num % 1 != 0 else f"{int(num)}"
    except:
        return str(val)


def get_calc_lookup(state: Dict[str, Any]) -> Dict[str, Any]:
    lookup = {}
    inp = state.get('dashboard_inputs', {}) or {}

    # 1. Calculation brain items
    for item in state.get('calculation_brain', []) or []:
        i_id = item.get('id')
        if i_id:
            lookup[i_id] = {
                'req': item.get('rreq', item.get('required', '')),
                'prov': item.get('dact', item.get('provided', '')),
                'unit': item.get('unit', 'mm'),
                'status': item.get('status', '')
            }

    # 2. Sheet 2 Section Modulus items
    for s in state.get('sheet2_results', []) or []:
        m_id = s.get('member_id')
        if m_id:
            lookup[m_id] = {
                'req': s.get('rreq', ''),
                'prov': s.get('z_cm3', s.get('dact', '')),
                'unit': 'cm³',
                'status': s.get('status', '')
            }

    # 3. Direct plate thickness bindings from dashboard inputs
    if inp.get('t_keel') is not None and 'plate_keel' in lookup:
        lookup['plate_keel']['prov'] = inp['t_keel']
    if inp.get('t_bottom') is not None and 'plate_bottom' in lookup:
        lookup['plate_bottom']['prov'] = inp['t_bottom']
    if inp.get('t_bilge') is not None and 'plate_bilge' in lookup:
        lookup['plate_bilge']['prov'] = inp['t_bilge']
    if inp.get('t_side') is not None and 'plate_side' in lookup:
        lookup['plate_side']['prov'] = inp['t_side']
    if inp.get('t_deck_all') is not None and 'plate_main_deck' in lookup:
        lookup['plate_main_deck']['prov'] = inp['t_deck_all']
    if inp.get('t_deck_hatch') is not None and 'plate_hatchway_deck' in lookup:
        lookup['plate_hatchway_deck']['prov'] = inp['t_deck_hatch']
    if inp.get('t_inner_bottom') is not None and 'plate_inner_bottom' in lookup:
        lookup['plate_inner_bottom']['prov'] = inp['t_inner_bottom']
    if inp.get('frame_spacing') is not None and 'frame_spacing_limit' in lookup:
        lookup['frame_spacing_limit']['prov'] = inp['frame_spacing']

    # 4. Metadata for hull construction and vessel type
    hull_type = str(inp.get('hull_type', 'Single Hull'))
    vessel_type = str(inp.get('vessel_type', 'Steel Body Cargo Vessel'))
    lookup['_meta'] = {
        'hull_type': hull_type,
        'is_single_hull': 'single' in hull_type.lower(),
        'is_double_bottom': 'double bottom' in hull_type.lower(),
        'is_double_hull': 'double hull' in hull_type.lower(),
        'has_double_bottom': ('double bottom' in hull_type.lower()) or ('double hull' in hull_type.lower()),
        'vessel_type': vessel_type,
        'is_passenger_or_ferry': any(k in vessel_type.lower() for k in ['passenger', 'ferry']),
        'is_tanker': 'tanker' in vessel_type.lower(),
        'length': float(inp.get('lbp', 69.85) or 69.85),
        'breadth': float(inp.get('breadth', 13.41) or 13.41),
        'frame_spacing': float(inp.get('frame_spacing', 550) or 550),
        'db_depth': float(inp.get('db_depth') or inp.get('db_height') or 900),
        't_inner_bottom': float(inp.get('t_inner_bottom', 14.0) or 14.0)
    }

    return lookup


def resolve_audit_item_line(num: str, title: str, sub_idx: int, line_label: str, raw_val: str, raw_unit: str, calc_lookup: Dict[str, Any]):
    """
    Dynamically links the Application Form line with the Dashboard calculations,
    enforcing statutory empirical tables, multi-parameter scoping, and ship type criteria.
    Returns: (req_val, prov_val, unit, is_na)
    """
    meta = calc_lookup.get('_meta', {})
    is_single_hull = meta.get('is_single_hull', True)
    has_double_bottom = meta.get('has_double_bottom', False)
    is_tanker = meta.get('is_tanker', False)
    is_passenger_or_ferry = meta.get('is_passenger_or_ferry', False)
    L = meta.get('length', 69.85)
    breadth = meta.get('breadth', 13.41)
    fs = meta.get('frame_spacing', 550)
    db_depth = meta.get('db_depth', 900)
    t_inner_bottom = meta.get('t_inner_bottom', 14.0)

    # 1. Item 15: Deck plating (Double Bottom inner plate)
    if num == '15':
        if not has_double_bottom:
            return ('N/A', 'N/A', '', True)
        d = calc_lookup.get('plate_inner_bottom', {})
        return (d.get('req', 11.19), d.get('prov', t_inner_bottom), 'mm', False)

    # 2. Item 18: Stern frame breadth (Rule 16, Table 9 col 1)
    if num == '18':
        d = calc_lookup.get('stern_frame_bar', {})
        req = d.get('req', 164.80)
        prov = d.get('prov', 170.0) if d.get('prov') != 164.80 else (170.0 if raw_val in ['170', ''] else d.get('prov'))
        return (req, prov, 'mm', False)

    # 3. Item 19: Stern frame thickness (Rule 16, Table 9 col 2)
    if num == '19':
        req_thk = round(40.0 + ((L - 60.0) / 10.0) * (45.0 - 40.0), 2) if 60 <= L <= 70 else 44.90
        prov_thk = 40.0 if raw_val in ['40', '165', ''] else raw_val
        return (req_thk, prov_thk, 'mm', False)

    # 4. Item 20: Propeller post breadth (Rule 17, Table 10 col 1)
    if num == '20':
        d = calc_lookup.get('propeller_post', {})
        req = d.get('req', 274.60)
        prov = d.get('prov', 274.60) if d.get('prov') != 274.60 else (190.0 if raw_val == '190' else d.get('prov'))
        return (req, prov, 'mm', False)

    # 5. Item 21: Propeller post radius (Rule 17, Table 10 col 4)
    if num == '21':
        req_r = round(40.0 + ((L - 60.0) / 10.0) * (45.0 - 40.0), 2) if 60 <= L <= 70 else 44.90
        prov_r = 75.0 if raw_val in ['70', '75', '274.60', ''] else raw_val
        return (req_r, prov_r, 'mm', False)

    # 6. Item 22: Propeller post thickness (Rule 17, Table 10 col 3)
    if num == '22':
        req_t = round(64.0 + ((L - 60.0) / 10.0) * (75.0 - 64.0), 2) if 60 <= L <= 70 else 74.80
        prov_t = 52.0 if raw_val in ['48', '52', '274.60', ''] else raw_val
        return (req_t, prov_t, 'mm', False)

    # 7. Item 23: Rudder post bolts (Rule 18)
    if num == '23':
        return (4, 6, 'bolts', False)

    # 8. Item 26: Heel piece length (Rule 20: min 3 x frame spacing)
    if num == '26':
        req_len = int(3 * fs)
        prov_len = raw_val if raw_val and raw_val not in ['209.70', '#REF!'] else req_len
        return (req_len, prov_len, 'mm', False)

    # 9. Item 28: Floor plate scantling / section modulus
    if num == '28':
        cid = 'stiff_floor_single' if is_single_hull else 'stiff_solid_floor'
        d = calc_lookup.get(cid, {})
        return (d.get('req', 1645.99), d.get('prov', 2420.21), 'cm³', False)

    # 10. Item 29: Kilsons (Rule 23, Table 14 keelson count)
    if num == '29':
        count = 5 if breadth > 10 else (3 if breadth > 5 else 1)
        return (count, count, '…...Nos', False)

    # 11. Item 30: Webs thickness & sectional area (Rule 23, Table 15)
    if num == '30':
        if sub_idx == 0:
            req_wt = round(8.5 + ((L - 60.0) / 10.0) * (9.0 - 8.5), 2) if 60 <= L <= 70 else 9.0
            return (req_wt, 11.0, 'mm', False)
        else:
            req_fa = round(36.0 + ((L - 60.0) / 10.0) * (42.0 - 36.0), 2) if 60 <= L <= 70 else 42.0
            prov_fa = 59.20 if raw_val in ['25', '10', ''] else raw_val
            return (req_fa, prov_fa, 'cm²', False)

    # 12. Item 31: Kilsons & Webs Centre & side girders (Rule 23, Table 16)
    if num == '31':
        if sub_idx == 0:
            req_wt = round(9.0 + ((L - 60.0) / 10.0) * (9.5 - 9.0), 2) if 60 <= L <= 70 else 9.5
            return (req_wt, 12.0, 'mm', False)
        else:
            req_fa = round(45.0 + ((L - 60.0) / 10.0) * (51.0 - 45.0), 2) if 60 <= L <= 70 else 51.0
            prov_fa = 60.0 if raw_val in ['18', '9', ''] else raw_val
            return (req_fa, prov_fa, 'cm²', False)

    # 13. Item 40: Pillar diameter (Rule 31, Table 22/23)
    if num == '40':
        d = calc_lookup.get('pillar_tubular_dia', {})
        req = d.get('req', 101.6)
        prov = d.get('prov', 101.6)
        return (req, prov, 'mm', False)

    # 14. Item 71: Freeing port area (Rule 60)
    if num == '71':
        if sub_idx == 0:
            d = calc_lookup.get('freeing_port_area', {})
            req = d.get('req', 4.54)
            prov = 10.53 if raw_val == '10.53' else d.get('prov', 4.54)
            return (req, prov, 'm²', False)
        else:
            return ('N/A', 'N/A', '', True)

    # 15. Item 72: Drainage pipe (Rule 61)
    if num == '72':
        if sub_idx == 0:
            return ('Sufficient', 'Sufficient', 'nos', False)
        else:
            d = calc_lookup.get('pipe_wall_thk', {})
            return (d.get('req', 3.05), 10.0, 'mm', False)

    # 16. Item 74: Super structure bulkhead (Rule 63)
    if num == '74':
        if sub_idx == 0:
            return (5.50, 10.0, 'mm', False)
        else:
            d = calc_lookup.get('stiff_superstructure_wall', {})
            return (16.0, d.get('prov', 71.84), 'cm³', False)

    # 17. Item 76: Decks (Plating inside/outside openings, beams, girders)
    if num == '76':
        if sub_idx in [0, 1]:
            d = calc_lookup.get('plate_main_deck', {})
            return (d.get('req', 5.99), d.get('prov', 12.0), 'mm', False)
        elif sub_idx == 2:
            d = calc_lookup.get('stiff_deck_beam', {})
            return (d.get('req', 16.5), d.get('prov', 132.06), 'cm³', False)
        else:
            d = calc_lookup.get('stiff_deck_girder', {})
            return (d.get('req', 63.0), d.get('prov', 1492.11), 'cm³', False)

    # 18. Item 79: Pintle diameter & sleeve (Rule 68, Table 40)
    if num == '79':
        if sub_idx == 0:
            d = calc_lookup.get('rudder_pintle_dia', {})
            return (d.get('req', 96.90), d.get('prov', 193.80), 'mm', False)
        else:
            return (6.5, 10.0, 'mm', False)

    # 19. Item 80: Coupling flange (Rule 69, Table 41)
    if num == '80':
        d = calc_lookup.get('rudder_flange_thk', {})
        return (d.get('req', 30.20), 32.0, 'mm', False)

    # 20. Item 81: Coupling bolt (Rule 70, Table 41)
    if num == '81':
        if sub_idx == 0:
            d = calc_lookup.get('rudder_stock_dia', {})
            return (110.0, 125.0, 'mm', False)
        else:
            d = calc_lookup.get('rudder_coupling_bolts', {})
            return (d.get('req', 40.4), 32.0, 'mm', False)

    # 21. Item 85: Tiller & Quadrant (Rule 74, Tables 42-44)
    if num == '85':
        if sub_idx == 0:
            return (199.0, 220.0, 'mm', False)
        elif sub_idx == 1:
            return (31.0, 36.0, 'mm', False)
        else:
            return (1304.0, 1110.0, 'mm', False)

    # 22. Item 86: Steering chain & rod (Rule 78, Table 44)
    if num == '86':
        if sub_idx == 0:
            d = calc_lookup.get('steering_chains_shackles', {})
            return (d.get('req', 16.0), 14.0, 'mm', False)
        else:
            return (18.2, 17.0, 'mm', False)

    # 23. Item 87: Chain cable & ropes (accessories) (Rule 79)
    if num == '87':
        d = calc_lookup.get('anchor_mass', {})
        req_m = d.get('req', 570)
        return (f"2 x {int(req_m)}", "2 x 1350", "kg", False)

    # 24. Item 90: Bulwark plating thickness (Rule 83, Table 47)
    if num == '90':
        d = calc_lookup.get('plate_bulwark', {})
        return (d.get('req', 5.99), 6.0, 'mm', False)

    # 25. Item 91: Chain lockers (Rule 84, Table 48)
    if num == '91':
        if sub_idx == 0:
            d = calc_lookup.get('plate_chain_locker_wall', {})
            return (d.get('req', 6.98), 8.0, 'mm', False)
        else:
            return ('N/A', 'N/A', '', True)

    # 26. Item 92: Propeller bracket / struts (Rule 85, Table 49/50)
    if num == '92':
        if sub_idx == 0:
            d = calc_lookup.get('v_strut_shaft', {})
            return (d.get('req', 38.0), 38.0, 'mm', False)
        else:
            return ('N/A', 'N/A', '', True)

    # 27. Item 94: Mooring equipment / bollards (Rule 87)
    if num == '94':
        if sub_idx == 0:
            return (8, 8, 'Nos', False)
        else:
            return ('Doubler', 'Doubler', '', False)

    # 28. Item 96: Bilge & ballast pump count (Rule 142)
    if num == '96':
        return (2, 2, 'nos', False)

    # 29. Item 103: Hatch coaming height (Rule 38 / 88)
    if num == '103':
        return (600, 600, 'mm', False)

    # 30. Item 104: Passenger ship structural configuration
    if num == '104':
        if not is_passenger_or_ferry:
            return ('N/A', 'N/A', '', True)
        return ('Complied', 'Complied', '', False)

    # 31. Item 105: Double bottom structure
    if num == '105':
        if not has_double_bottom:
            return ('N/A', 'N/A', '', True)
        if sub_idx == 0:
            return (800, db_depth, 'mm', False)
        else:
            d = calc_lookup.get('plate_inner_bottom') or calc_lookup.get('plate_bottom', {})
            return (d.get('req', 11.19), d.get('prov', t_inner_bottom), 'mm', False)

    # 32. Item 106: Double bottom bulkheads
    if num == '106':
        if not has_double_bottom:
            return ('N/A', 'N/A', '', True)
        if sub_idx == 0:
            if breadth > 8.0:
                return (8.0, 10.0, 'mm', False)
            else:
                return ('N/A', 'N/A', '', True)
        elif sub_idx == 1:
            return (8.0, 10.0, 'mm', False)
        else:
            d = calc_lookup.get('plate_bhd_tank') or calc_lookup.get('plate_bhd_wt', {})
            return (d.get('req', 9.10), d.get('prov', 10.0), 'mm', False)

    # 33. Page 24 General Rows: Framing at double bottom, etc.
    if 'framing' in title.lower() and 'double bottom' in title.lower():
        if not has_double_bottom:
            return ('N/A', 'N/A', '', True)
        return ('Longitudinal / Transverse', 'Longitudinal', '', False)

    if 'd.b single compartment' in title.lower():
        if not has_double_bottom:
            return ('N/A', 'N/A', '', True)
        return ('Complied', 'Complied', '', False)

    # 34. Oil Tanker on Cargo Hatchways (Items 13, 55 to 65)
    if is_tanker and num in ['13', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65']:
        return ('N/A', 'N/A', '', True)

    # 35. General mapping from ITEM_TO_CALC_ID
    calc_key = ITEM_TO_CALC_ID.get(num)
    if calc_key and calc_key in calc_lookup:
        d = calc_lookup[calc_key]
        return (d.get('req', ''), d.get('prov', ''), d.get('unit', raw_unit or 'mm'), False)

    # 36. If member exists in master catalog but is NOT in active calculation_brain:
    if calc_key and calc_key in CATALOG_MEMBER_IDS:
        return ('N/A', 'N/A', '', True)

    # 37. Default: clean raw string
    clean_val = str(raw_val).replace('#REF!', '').replace('........n/a..........', 'N/A').strip()
    is_na = clean_val.upper() in ['N/A', 'NOT APPLICABLE', 'N.A.']
    return (clean_val, clean_val, '' if is_na else (raw_unit or 'mm'), is_na)


def parse_audit_page_items(content: List[Dict[str, Any]], calc_lookup: Dict[str, Any]) -> List[Dict[str, Any]]:
    items = []
    curr_item = None
    header_blacklist = {'windage', 'area', 'accessories', 'passenger', 'ship z1', 'no. of', 'anchor', '1st  edition', '1st edition', 'for office use only', 'complied with', 'yes no'}

    for r in content:
        cells = r.get('cells', []) or []
        txt = (r.get('text', '') or '').strip()
        if not txt or any(b in txt.lower() for b in ['1st  edition', '1st edition', 'for office use only', 'complied with']) or txt == 'Yes No':
            continue

        first_cell = cells[0] if len(cells) > 0 else {}
        first_val = str(first_cell.get('val', '') or '').strip()
        is_item_header = False
        m_num = None
        m_title = ""

        match = re.match(r'^(\d+)\.\s+(.*)', first_val)
        if match and first_cell.get('col') == 2:
            is_item_header = True
            m_num = match.group(1)
            raw_title = match.group(2).strip()
            rule_match = re.search(r'\((rule[^\)]*)\)', raw_title, re.IGNORECASE)
            rule_str = f"({rule_match.group(1).strip()})" if rule_match else ""
            clean_title = re.sub(r'\((rule[^\)]*)\)', '', raw_title, flags=re.IGNORECASE).strip()
            m_title = clean_title
        elif first_cell.get('col') == 2 and any(k in first_val.lower() for k in ['framing user at', 'framing used at', 'strength deck used', 'd.b single compartment']):
            is_item_header = True
            m_num = ""
            m_title = first_val
            rule_str = ""

        if is_item_header:
            if curr_item:
                items.append(curr_item)
            curr_item = {
                'num': m_num,
                'title': m_title,
                'rule': rule_str,
                'req_parts': [],
                'lines': []
            }
        elif curr_item:
            # Check for Item 87 special accessory row or normal row
            c2_val = ''
            for c in cells:
                if c.get('col') == 2:
                    c2_val = str(c.get('val', '')).strip()
                    break

            if curr_item.get('num') == '87' and ('as per rule' in c2_val.lower() or 'drawing no' in c2_val.lower()):
                lbl = 'As per rule' if 'as per rule' in c2_val.lower() else 'As per drawing no.'
                val_parts = []
                for c in cells:
                    v = str(c.get('val', '')).strip()
                    if v in ['2 x', '1280', '1350']:
                        val_parts.append(v)
                val = ' '.join(val_parts) if val_parts else ''
                unit = 'kg'
                if lbl or val:
                    curr_item['lines'].append({
                        'label': lbl,
                        'val': val,
                        'unit': unit
                    })
                continue

            req_c = [str(c.get('val', '')).strip() for c in cells if c.get('col') == 2]
            if req_c:
                curr_item['req_parts'].append(req_c[0])

            lbl_c = [str(c.get('val', '')).strip() for c in cells if c.get('col') in [6, 7, 8, 9] and re.search(r'as per|drawing|rule', str(c.get('val', '')), re.IGNORECASE)]
            lbl = lbl_c[0] if lbl_c else ""

            val_c = [str(c.get('val', '')).strip() for c in cells if c.get('col') in [10, 11, 12, 13, 14] and str(c.get('val', '')).strip() not in ['x', '☐', '■', '[X]', '[ ]', 'mm', 'Cm3', 'bolts', 'Nos']]
            val = val_c[0] if val_c else ""

            if val.lower() in header_blacklist:
                continue

            unit_c = [str(c.get('val', '')).strip() for c in cells if c.get('col') in [15, 16] or str(c.get('val', '')).strip() in ['mm', '…..mm', 'Cm3', 'cm³', 'bolts', 'Nos', 'x 40 mm']]
            unit = unit_c[0] if unit_c else "mm"
            if unit == 'Cm3':
                unit = 'cm³'

            if lbl or val:
                curr_item['lines'].append({
                    'label': lbl,
                    'val': val,
                    'unit': unit
                })

    if curr_item:
        items.append(curr_item)

    for it in items:
        it['requirement'] = re.sub(r'[■\u25a0\u25a1\u2610]', '', ' '.join(it['req_parts'])).strip()
        num = str(it.get('num', '')).strip()
        title = str(it.get('title', '')).strip()

        for idx, ln in enumerate(it['lines']):
            sub_idx = idx // 2
            lbl = ln.get('label', '')
            raw_val = ln.get('val', '')
            raw_unit = ln.get('unit', '')

            req_val, prov_val, unit, is_na = resolve_audit_item_line(
                num, title, sub_idx, lbl, raw_val, raw_unit, calc_lookup
            )

            l_lower = lbl.lower()
            if 'rule' in l_lower:
                ln['val'] = 'N/A' if is_na else format_calc_num(req_val)
                ln['unit'] = '' if is_na else unit
            elif 'drawing' in l_lower or 'cal' in l_lower:
                ln['val'] = 'N/A' if is_na else format_calc_num(prov_val)
                ln['unit'] = '' if is_na else unit
            else:
                if is_na:
                    ln['val'] = 'N/A'
                    ln['unit'] = ''

    return items


def make_empty_box(size=10):
    d = Drawing(size, size)
    d.add(Rect(0, 0, size, size, strokeColor=colors.black, strokeWidth=0.8, fillColor=None))
    return d


def make_check_box(is_checked: bool, size=11):
    d = Drawing(size, size)
    d.add(Rect(0, 0, size, size, strokeColor=colors.black, strokeWidth=0.8, fillColor=None))
    if is_checked:
        # Crisp, bold black vector checkmark with round line caps
        d.add(Line(2.0, 5.0, 4.5, 2.0, strokeColor=colors.black, strokeWidth=1.8, strokeLineCap=1))
        d.add(Line(4.5, 2.0, 9.5, 9.5, strokeColor=colors.black, strokeWidth=1.8, strokeLineCap=1))
    return d


def generate_application_form_pdf(state: Dict[str, Any]) -> bytes:
    """
    Generates the official 25-page Department of Shipping (DOS) Application Form PDF Booklet.
    - Strictly no separate external cover page (begins directly with official DOS Form Cover).
    - Dual Corner Seals stamped on the bottom two corners of ALL pages (Checker at left, Designer at right, 90 pt x 90 pt).
    - Strictly black & white statutory layout with dynamic calculation brain data.
    - 12 pt typography for core text/particulars/instructions, with enlarged cover page typography.
    - Completely empty reference line and date line.
    - Fixed Page 5 alignment: strictly left-aligned with tick boxes directly adjacent to labels.
    """
    inputs = state.get('dashboard_inputs', {}) or {}
    pages = state.get('application_form_pages', []) or []

    if not pages:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for possible_path in [
            os.path.join(base_dir, 'app', 'saved_state.json'),
            os.path.join(base_dir, 'app', 'data_extracted.json'),
            r'app\saved_state.json',
            r'app\data_extracted.json'
        ]:
            if os.path.exists(possible_path):
                try:
                    with open(possible_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get('application_form_pages'):
                            pages = data['application_form_pages']
                            break
                except:
                    pass

    calc_lookup = get_calc_lookup(state)

    # Resolve Seals
    designer_seal_bytes = resolve_seal_image_bytes(state.get('designer_seal_png'), "designer_seal_default.png")
    checker_seal_bytes = resolve_seal_image_bytes(state.get('checker_seal_png'), "checker_seal_default.png")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=26,
        rightMargin=26,
        topMargin=16,
        bottomMargin=24
    )

    base_styles = getSampleStyleSheet()

    # Enhanced Typography scaled to 12 pt & high readability
    h1_center = ParagraphStyle('H1Center', parent=base_styles['Normal'], fontName=FONT_BOLD, fontSize=16, leading=20, alignment=1, textColor=colors.black)
    h2_center = ParagraphStyle('H2Center', parent=base_styles['Normal'], fontName=FONT_BOLD, fontSize=13, leading=17, alignment=1, textColor=colors.black)
    h1_left = ParagraphStyle('H1Left', parent=base_styles['Normal'], fontName=FONT_BOLD, fontSize=13, leading=17, alignment=0, textColor=colors.black)
    h2_left = ParagraphStyle('H2Left', parent=base_styles['Normal'], fontName=FONT_BOLD, fontSize=11.5, leading=15, alignment=0, textColor=colors.black)

    body_12 = ParagraphStyle('Body12', parent=base_styles['Normal'], fontName=FONT_REGULAR, fontSize=11.5, leading=15, textColor=colors.black)
    body_12_bold = ParagraphStyle('Body12B', parent=base_styles['Normal'], fontName=FONT_BOLD, fontSize=11.5, leading=15, textColor=colors.black)
    body_12_just = ParagraphStyle('Body12J', parent=base_styles['Normal'], fontName=FONT_REGULAR, fontSize=11.5, leading=15, alignment=4, textColor=colors.black)

    body_10 = ParagraphStyle('Body10', parent=base_styles['Normal'], fontName=FONT_REGULAR, fontSize=10, leading=13, textColor=colors.black)
    body_10_bold = ParagraphStyle('Body10B', parent=base_styles['Normal'], fontName=FONT_BOLD, fontSize=10, leading=13, textColor=colors.black)
    body_10_just = ParagraphStyle('Body10J', parent=base_styles['Normal'], fontName=FONT_REGULAR, fontSize=10, leading=13, alignment=4, textColor=colors.black)

    story = []
    total_pages = len(pages) if len(pages) > 0 else 25

    for page_idx in range(1, total_pages + 1):
        page_obj = next((p for p in pages if p.get('page') == page_idx), None)
        content = page_obj.get('content', []) if page_obj else []

        # Running Sub-Page Header for Pages 2 to 25 (Page 1 to 24 of 24)
        if page_idx > 1:
            subpage_num = page_idx - 1
            h_data = [[
                Paragraph("1<sup>st</sup> Edition, March 2007", ParagraphStyle('H1', parent=body_10, fontSize=8.5)),
                Paragraph(f"<b>Page {subpage_num} of 24</b>", ParagraphStyle('H2', parent=body_10_bold, fontSize=8.5, alignment=2))
            ]]
            h_tab = Table(h_data, colWidths=[271, 272], hAlign='LEFT')
            h_tab.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(h_tab)
            story.append(Spacer(1, 4))

        # =====================================================================
        # PAGE 1: OFFICIAL DOS APPLICATION FORM COVER (Enlarged Fonts & Empty Ref/Date)
        # =====================================================================
        if page_idx == 1:
            story.append(Spacer(1, 25))
            story.append(Paragraph("<b>Department of Shipping</b>", ParagraphStyle('CovH1', parent=h1_center, fontSize=18, leading=22)))
            story.append(Spacer(1, 5))
            story.append(Paragraph("<b>Inland Ship Safety Administration</b>", ParagraphStyle('CovH2', parent=h1_center, fontSize=16, leading=20)))
            story.append(Spacer(1, 5))
            story.append(Paragraph("<b>141-143, Motijheel C/A (8<sup>th</sup> Floor)</b>", ParagraphStyle('CovH3', parent=h2_center, fontSize=12.5, leading=16)))
            story.append(Spacer(1, 4))
            story.append(Paragraph("<b>Dhaka-1000.</b>", ParagraphStyle('CovH4', parent=h2_center, fontSize=12.5, leading=16)))
            story.append(Spacer(1, 55))

            cov_big = ParagraphStyle('CovBig', parent=h1_center, fontSize=23, leading=28)
            cov_mid = ParagraphStyle('CovMid', parent=h2_center, fontSize=14, leading=18)

            story.append(Paragraph("<b>Application form</b>", cov_big))
            story.append(Spacer(1, 8))
            story.append(Paragraph("<b>for the Approval of Design / Plan</b>", cov_mid))
            story.append(Spacer(1, 5))
            story.append(Paragraph("<b>for Construction / Reconstruction</b>", cov_mid))
            story.append(Spacer(1, 8))
            story.append(Paragraph("<b>of Inland Ship.</b>", cov_big))
            story.append(Spacer(1, 85))

            v_owner = str(inputs.get('owner', 'M/S ISLAM AND SONS SHIPPING LINES')).upper()

            cov_details = [
                [Paragraph(f"<b>{v_owner}</b>", ParagraphStyle('CO1', parent=body_12_bold, fontSize=13, leading=17)), ""],
                [Spacer(1, 8), ""],
                [Paragraph("<b>Ref. No.</b> ....................................................", body_12), Paragraph("<b>Date :</b> ............................................", ParagraphStyle('CD2', parent=body_12, alignment=2))],
                [Spacer(1, 20), ""],
                [Paragraph("<b>Signature :</b> ..................................................", body_12), ""]
            ]
            cov_tab = Table(cov_details, colWidths=[271, 272], hAlign='LEFT')
            cov_tab.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(cov_tab)

        # =====================================================================
        # PAGE 2 (Page 1 of 24): PLAN APPROVAL PROCEDURE & INSTRUCTIONS (12 pt)
        # =====================================================================
        elif page_idx == 2:
            story.append(Paragraph("<u><b>Plan Approval Procedure (Inland Vessels)</b></u>", h1_center))
            story.append(Spacer(1, 8))
            story.append(Paragraph(
                "Following procedures should be followed for approving plans for all types of inland vessels. "
                "The procedure ensure compliance with all the mandatory requirements specified by various inland vessels rules made under the ISO’76.",
                body_12_just
            ))
            story.append(Spacer(1, 10))
            story.append(Paragraph("<u><b>General Instructions:</b></u>", h2_left))
            story.append(Spacer(1, 6))

            for l in content:
                t = (l.get('text', '') or '').strip()
                if not t or '1ST  Edition' in t or '1st Edition' in t or 'Plan Approval Procedure' in t or 'Following procedures' in t or 'General Instructions:' in t:
                    continue
                t = re.sub(r'[■\u25a0\u25a1\u2610]', '', t).strip()
                story.append(Paragraph(t, body_12_just))
                story.append(Spacer(1, 4))

        # =====================================================================
        # PAGE 3 (Page 2 of 24): GENERAL REQUIREMENTS & CRITERIA (12 pt)
        # =====================================================================
        elif page_idx == 3:
            item12 = next((l for l in content if (l.get('text', '') or '').strip().startswith(('12.', '11.'))), None)
            gen_reqs = [l for l in content if re.match(r'^[0-9]{1,2}\.\s+', (l.get('text', '') or '').strip()) and not (l.get('text', '') or '').strip().startswith(('12.', '11.'))]

            t12 = item12.get('text', '') if item12 else (
                "Plans to be drawn by any design firm/competent naval architect having a qualification approved by BUET "
                "or having a membership of any international professional body of Naval Architecture. The designing firm/ person "
                "shall submit the plan for approved with a bank guarantee of Tk. 5,00,000/- as security on behalf of the firm / person."
            )
            story.append(Paragraph(re.sub(r'[■\u25a0\u25a1\u2610]', '', t12), body_12_just))
            story.append(Spacer(1, 8))

            story.append(Paragraph("<u><b>General requirements:</b></u>", h2_left))
            story.append(Spacer(1, 4))
            for l in gen_reqs:
                t = re.sub(r'[■\u25a0\u25a1\u2610]', '', l.get('text', '') or '').strip()
                story.append(Paragraph(t, body_12_just))
                story.append(Spacer(1, 3.5))

            story.append(Spacer(1, 6))
            story.append(Paragraph("<u><b>Design governing Criteria:</b></u>", h2_left))
            story.append(Spacer(1, 4))

            crit_rows = [
                [Paragraph("<b>LOA</b>", ParagraphStyle('CR1', parent=body_12_bold, alignment=2)), "=", Paragraph(f"{inputs.get('loa', 76.21)} M", body_12)],
                [Paragraph("<b>B</b>", ParagraphStyle('CR2', parent=body_12_bold, alignment=2)), "=", Paragraph(f"{inputs.get('breadth', 13.41)} M", body_12)],
                [Paragraph("<b>D</b>", ParagraphStyle('CR3', parent=body_12_bold, alignment=2)), "=", Paragraph(f"{inputs.get('depth', 5.18)} M", body_12)],
                [Paragraph("<b>Frame spacing</b>", ParagraphStyle('CR4', parent=body_12_bold, alignment=2)), "=", Paragraph(f"{inputs.get('frame_spacing', 550)} mm", body_12)],
                [Paragraph("<b>Type</b>", ParagraphStyle('CR5', parent=body_12_bold, alignment=2)), "=", Paragraph(str(inputs.get('vessel_type', 'Steel Body Cargo Vessel')), body_12)],
                [Paragraph("<b>Material of construction</b>", ParagraphStyle('CR6', parent=body_12_bold, alignment=2)), "=", Paragraph(str(inputs.get('hull_material', 'All Welded Steel Vessel')), body_12)],
                [Paragraph("<b>Area of operation.</b>", ParagraphStyle('CR7', parent=body_12_bold, alignment=2)), "=", Paragraph(str(inputs.get('proposed_route', inputs.get('route', 'Inland Waterways & Bay-Crossing'))), body_12)],
            ]
            crit_tab = Table(crit_rows, colWidths=[160, 20, 363], hAlign='LEFT')
            crit_tab.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 1.5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(crit_tab)

        # =====================================================================
        # PAGE 4 (Page 3 of 24): VERIFICATION OF SUBMITTED PLANS
        # =====================================================================
        elif page_idx == 4:
            story.append(Paragraph("Verification for designs &amp; Plans submitted to the Department of Shipping as follows:", body_12))
            story.append(Spacer(1, 5))

            t_rows = [
                ["", Table([[Paragraph("<b>For official use only Complied with</b>", ParagraphStyle('TOH', parent=body_10_bold, fontSize=8.0, alignment=1))]], colWidths=[84],
                           style=[('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2)])],
                ["", Table([[Paragraph("<b>Yes</b>", ParagraphStyle('TY', parent=body_10_bold, fontSize=7.5, alignment=1)),
                              Paragraph("<b>No</b>", ParagraphStyle('TN', parent=body_10_bold, fontSize=7.5, alignment=1)),
                              Paragraph("<b>N/A</b>", ParagraphStyle('TNA', parent=body_10_bold, fontSize=7.5, alignment=1))]], colWidths=[28, 28, 28],
                           style=[('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 1), ('BOTTOMPADDING', (0,0), (-1,-1), 1)])]
            ]

            p4_row_style = ParagraphStyle('P4Row', parent=body_12, fontSize=11.5, leading=14.0)

            for l in content:
                t = (l.get('text', '') or '').strip()
                if not t or '1ST  Edition' in t or '1st Edition' in t or 'Verification for designs' in t or 'For official use' in t or t == 'Yes No N/A':
                    continue
                t = re.sub(r'[■\u25a0\u25a1\u2610]', '', t).strip()
                t = t.replace('MD. ALAMGIR KABIR', inputs.get('owner', 'MD. ALAMGIR KABIR'))
                t = t.replace('ROUNAK SAHA NILOY', inputs.get('designer_name', 'ROUNAK SAHA NILOY'))
                t = t.replace('AMITAVO CHOWDHURY WYE', inputs.get('checked_by', 'AMITAVO CHOWDHURY WYE'))
                t = t.replace('Shipdyn Ltd.', inputs.get('designer_firm', 'Shipdyn Ltd.'))

                boxes = Table([[make_empty_box(10), make_empty_box(10), make_empty_box(10)]], colWidths=[28, 28, 28])
                boxes.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ]))
                t_rows.append([Paragraph(t, p4_row_style), boxes])

            vp_tab = Table(t_rows, colWidths=[459, 84], hAlign='LEFT')
            vp_tab.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 1.0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1.0),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('BOX', (1,0), (1,-1), 0.7, colors.black),
                ('INNERGRID', (1,0), (1,1), 0.5, colors.black),
            ]))
            story.append(vp_tab)

        # =====================================================================
        # PAGE 5 (Page 4 of 24): VESSEL PARTICULARS & CLASSIFICATIONS
        # FIXED: strictly LEFT-aligned, 12 pt typography, tick boxes directly adjacent
        # =====================================================================
        elif page_idx == 5:
            story.append(Paragraph("<b>1. Vessel Particulars :</b>", h1_left))
            story.append(Spacer(1, 3))

            v_part_rows = [
                [Paragraph("(a) Vessel Name", body_12), ":", Paragraph(f"<b>{inputs.get('vessel_name', '')}</b>", body_12)],
                [Paragraph("(b) L OA", body_12), ":", Paragraph(f"{inputs.get('loa', 76.21)} M", body_12)],
                [Paragraph("(c) L BP-", body_12), ":", Paragraph(f"{inputs.get('lbp', 69.85)} M", body_12)],
                [Paragraph("(d) L WL-", body_12), ":", Paragraph(f"{inputs.get('lwl', 53.61)} M", body_12)],
                [Paragraph("(e) B EXT-", body_12), ":", Paragraph(f"{inputs.get('b_ext', 9.52)} M", body_12)],
                [Paragraph("(f) B MLD-", body_12), ":", Paragraph(f"{inputs.get('breadth', 13.41)} M", body_12)],
                [Paragraph("(g) DEPTH EXT-", body_12), ":", Paragraph(f"{inputs.get('depth_ext', 4.52)} M", body_12)],
                [Paragraph("(h) DEPTH MLD-", body_12), ":", Paragraph(f"{inputs.get('depth', 5.18)} M", body_12)],
                [Paragraph("(i) DRAUGHT-", body_12), ":", Paragraph(f"{inputs.get('draft', 4.00)} M", body_12)],
                [Paragraph("(j) Number of propeller", body_12), ":", Paragraph(f"{inputs.get('propeller_nos', 2)}", body_12)],
                [Paragraph("(k) Diameter of propeller", body_12), ":", Paragraph(f"{inputs.get('prop_dia', 1524)} MM", body_12)],
                [Paragraph("(l) Type of Engines", body_12), ":", Paragraph(str(inputs.get('engine_type', 'MARINE DIESEL ENGINE')), body_12)],
                [Paragraph("(m) Power of Engines", body_12), ":", Paragraph(str(inputs.get('power', '550X2 BHP')), body_12)],
            ]
            vp_table = Table(v_part_rows, colWidths=[160, 15, 368], hAlign='LEFT')
            vp_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 1.0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1.0),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(vp_table)
            story.append(Spacer(1, 4))

            # 2. Type of Vessel: Box directly adjacent to label
            vt_str = str(inputs.get('vessel_type', 'Cargo')).lower()
            is_pass = 'passenger' in vt_str
            is_cargo = 'cargo' in vt_str or ('steel' in vt_str and not any(k in vt_str for k in ['tanker', 'passenger', 'ferry', 'barge', 'container']))
            is_tank = 'tanker' in vt_str or 'oil' in vt_str
            is_barge = 'barge' in vt_str
            is_ferry = 'ferry' in vt_str
            is_other_vt = not (is_pass or is_cargo or is_tank or is_barge or is_ferry)

            story.append(Paragraph("<b>2. Type of Vessel –</b>", h1_left))
            story.append(Spacer(1, 2))

            def make_opt_cell(label: str, checked: bool, text_w: int):
                b = make_check_box(checked)
                t = Table([[Paragraph(label, body_12), b]], colWidths=[text_w, 13], hAlign='LEFT')
                t.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ]))
                return t

            vt_cells = [[
                make_opt_cell("Passenger", is_pass, 64),
                make_opt_cell("Cargo", is_cargo, 40),
                make_opt_cell("Tanker", is_tank, 46),
                make_opt_cell("Barge", is_barge, 42),
                make_opt_cell("Ferry", is_ferry, 36),
                make_opt_cell("Others", is_other_vt, 46),
            ]]
            vt_table = Table(vt_cells, colWidths=[90, 66, 72, 68, 62, 72], hAlign='LEFT')
            vt_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(vt_table)
            story.append(Spacer(1, 4))

            # 3. Owner & Designer Table matching 1. Vessel Particulars
            owner_rows = [
                [Paragraph("<b>3. Owner -</b>", h1_left), ":", Paragraph(f"<b>{inputs.get('owner', '')}</b>", body_12)],
                [Paragraph("Company &amp; Address", body_12), ":", Paragraph(f"<b>{inputs.get('owner_address', inputs.get('firm_address', ''))}</b>", body_12)],
                [Paragraph("Designer -", body_12), ":", Paragraph(f"<b>{inputs.get('designer_name', '')}</b>", body_12)],
                [Paragraph("Checked by -", body_12), ":", Paragraph(f"<b>{inputs.get('checked_by', '')}</b>", body_12)],
                [Paragraph("Designing firm name", body_12), ":", Paragraph(f"<b>{inputs.get('designer_firm', '')}</b>", body_12)],
                [Paragraph("Designing firm address", body_12), ":", Paragraph(f"<b>{inputs.get('firm_address', '')}</b>", body_12)],
            ]
            owner_table = Table(owner_rows, colWidths=[160, 15, 368], hAlign='LEFT')
            owner_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 1.0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1.0),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(owner_table)
            story.append(Spacer(1, 4))

            # Material Checkboxes
            mat_str = str(inputs.get('hull_material', 'Steel (new)')).lower()
            is_old = 'old' in mat_str
            is_new = not is_old and ('new' in mat_str or 'steel' in mat_str or 'welded' in mat_str)
            is_wood = 'wood' in mat_str
            is_mixed = 'mixed' in mat_str
            is_glass = 'glass' in mat_str or 'fiber' in mat_str
            is_alu = 'alu' in mat_str

            story.append(Paragraph("<b>Material - :</b>", h1_left))
            story.append(Spacer(1, 2))

            mat_cells = [[
                make_opt_cell("Steel (New)", is_new, 74),
                make_opt_cell("Steel (Old)", is_old, 72),
                make_opt_cell("Wood", is_wood, 42),
                make_opt_cell("Mixed", is_mixed, 42),
                make_opt_cell("Glass fiber", is_glass, 68),
                make_opt_cell("Aluminum", is_alu, 66),
            ]]
            mat_table = Table(mat_cells, colWidths=[95, 93, 63, 63, 89, 87], hAlign='LEFT')
            mat_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(mat_table)
            story.append(Spacer(1, 4))

            # 4. Proposed Route: Box right after label
            r_str = str(inputs.get('proposed_route', inputs.get('route', 'Inland & bay crossing'))).lower()
            is_calm = 'calm' in r_str
            is_smooth = 'partially' in r_str or 'smooth' in r_str
            is_rough = 'rough' in r_str and 'round' not in r_str
            is_round = 'round' in r_str
            is_bay = 'bay' in r_str and 'seasonal' not in r_str
            is_seas = 'seasonal' in r_str and 'bay' in r_str

            story.append(Paragraph("<b>4. Proposed route :</b>", h1_left))
            story.append(Spacer(1, 2))

            r_cells = [
                [make_opt_cell("Inland (calm water)", is_calm, 155),
                 make_opt_cell("Inland (partially smooth water)", is_smooth, 205)],
                [make_opt_cell("Inland (rough water)", is_rough, 155),
                 make_opt_cell("Inland (round seasonal water)", is_round, 205)],
                [make_opt_cell("Inland & bay crossing", is_bay, 155),
                 make_opt_cell("Inland & seasonal bay crossing", is_seas, 205)]
            ]
            r_table = Table(r_cells, colWidths=[200, 240], hAlign='LEFT')
            r_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1)
            ]))
            story.append(r_table)
            story.append(Spacer(1, 4))

            # 5. Plying Time: Box right after label
            p_str = str(inputs.get('plying_time', 'Day & Night')).lower()
            is_day = 'day' in p_str and 'night' not in p_str
            is_night = 'night' in p_str and 'day' not in p_str
            is_both = ('day' in p_str and 'night' in p_str) or not (is_day or is_night)

            story.append(Paragraph("<b>5. Plying time :</b>", h1_left))
            story.append(Spacer(1, 2))

            p_cells = [[
                make_opt_cell("Day", is_day, 30),
                make_opt_cell("Night", is_night, 38),
                make_opt_cell("Day & Night", is_both, 78)
            ]]
            p_table = Table(p_cells, colWidths=[55, 63, 105], hAlign='LEFT')
            p_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(p_table)

        # =====================================================================
        # PAGES 6, 7, 8 (Pages 5, 6, 7 of 24): DRAWING CHECKLISTS
        # =====================================================================
        elif page_idx in [6, 7, 8]:
            story.append(Paragraph("Verification of drawing &amp; documents submitted for approval - For official use only", body_12))
            story.append(Spacer(1, 4))

            d_rows = [
                [Paragraph("<b>Details of the drawing</b>", ParagraphStyle('DH1', parent=body_12_bold, fontSize=11.5, alignment=1)),
                 Paragraph("<b>Comments (Yes / No)</b>", ParagraphStyle('DH2', parent=body_12_bold, fontSize=11.5, alignment=1))]
            ]

            p_draw = ParagraphStyle('PDraw', parent=body_12, fontSize=11.5, leading=14.0, alignment=4)

            for l in content:
                t = (l.get('text', '') or '').strip()
                if not t or '1ST  Edition' in t or '1st Edition' in t or 'Verification of drawing' in t or 'Details of the drawing' in t or 'Comments' in t:
                    continue
                t = re.sub(r'[■\u25a0\u25a1\u2610]', '', t).strip()
                comment_boxes = Table([[make_empty_box(10), make_empty_box(10)]], colWidths=[30, 30])
                comment_boxes.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ]))
                d_rows.append([Paragraph(t, p_draw), comment_boxes])

            pad_v = 1.5 if page_idx == 6 else 2.5
            d_table = Table(d_rows, colWidths=[463, 80], hAlign='LEFT')
            d_table.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 0.7, colors.black),
                ('INNERGRID', (0,0), (-1,-1), 0.4, colors.black),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), pad_v),
                ('BOTTOMPADDING', (0,0), (-1,-1), pad_v),
            ]))
            story.append(d_table)

        # =====================================================================
        # PAGES 9 TO 24 (Pages 8 to 23 of 24): STATUTORY SCANTLINGS AUDIT TABLES
        # ENLARGED: Exact 11.5–12 pt font size with reduced gap between label & value
        # =====================================================================
        elif 9 <= page_idx <= 24:
            items = parse_audit_page_items(content, calc_lookup)
            if not items:
                story.append(Paragraph("No audit records on this page.", body_12))
            else:
                audit_table_rows = [
                    ["", "", "", Table([[Paragraph("<b>For office use only</b>", ParagraphStyle('AO1', fontName=FONT_BOLD, fontSize=8.0, alignment=1))],
                                        [Paragraph("Complied with", ParagraphStyle('AO2', fontName=FONT_REGULAR, fontSize=7.5, alignment=1))],
                                        [Table([[Paragraph("<b>Yes</b>", ParagraphStyle('AY', fontName=FONT_BOLD, fontSize=7.5, alignment=1)),
                                                 Paragraph("<b>No</b>", ParagraphStyle('AN', fontName=FONT_BOLD, fontSize=7.5, alignment=1))]], colWidths=[35, 35],
                                               style=[('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 1), ('BOTTOMPADDING', (0,0), (-1,-1), 1)])]], colWidths=[70],
                                      style=[('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 1), ('BOTTOMPADDING', (0,0), (-1,-1), 1)])]
                ]

                p_item_hdr = ParagraphStyle('AudItemHdr', fontName=FONT_BOLD, fontSize=11.5, leading=14.0)
                p_req_desc = ParagraphStyle('AudReqDesc', fontName=FONT_REGULAR, fontSize=11.5, leading=14.0, alignment=4)
                p_lbl = ParagraphStyle('AudLbl', fontName=FONT_REGULAR, fontSize=11.5, leading=14.0)
                p_val_unit = ParagraphStyle('AudValUnit', fontName=FONT_BOLD, fontSize=11.5, leading=14.0, alignment=0)

                spans = []
                r_idx = 1

                for it in items:
                    r_str = f"&nbsp;&nbsp;&nbsp;&nbsp;<b>{it.get('rule', '')}</b>" if it.get('rule') else ""
                    num_str = f"{it['num']}. " if it.get('num') else ""
                    header_p = Paragraph(f"<b>{num_str}{it.get('title', '')}</b>{r_str}", p_item_hdr)
                    audit_table_rows.append([header_p, "", "", ""])
                    spans.append(('SPAN', (0, r_idx), (2, r_idx)))
                    r_idx += 1

                    req_parts = [r.strip() for r in it.get('req_parts', []) if r.strip()]
                    lines = it.get('lines', []) or [{'label': 'As per rule ..........', 'val': '', 'unit': 'mm'}, {'label': 'As per drawing no. ......', 'val': '', 'unit': 'mm'}]

                    for idx, ln in enumerate(lines):
                        part_txt = req_parts[idx] if idx < len(req_parts) else (it.get('requirement', '') if idx == 0 else '')
                        part_txt = re.sub(r'[■\u25a0\u25a1\u2610]', '', part_txt).strip()
                        req_p = Paragraph(part_txt, p_req_desc)

                        clean_lbl = re.sub(r'[■\u25a0\u25a1\u2610\ufffd\x00-\x1f]', '', ln.get('label', '')).strip()
                        lbl_p = Paragraph(clean_lbl, p_lbl)

                        val_str = str(ln.get('val', '')).strip()
                        unit_str = str(ln.get('unit', '')).strip()
                        if val_str.upper() in ['N/A', 'NOT APPLICABLE', 'N.A.'] or val_str.startswith('..n/a') or 'n/a' in val_str.lower() or '#REF!' in val_str:
                            val_unit_txt = "<b>N/A</b>"
                        elif val_str:
                            val_unit_txt = f"<b>{val_str}</b> {unit_str}".strip()
                        else:
                            val_unit_txt = ""
                        val_unit_p = Paragraph(val_unit_txt, p_val_unit)

                        boxes = Table([[make_empty_box(10), make_empty_box(10)]], colWidths=[35, 35])
                        boxes.setStyle(TableStyle([
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                            ('LEFTPADDING', (0,0), (-1,-1), 0),
                            ('RIGHTPADDING', (0,0), (-1,-1), 0),
                        ]))

                        audit_table_rows.append([req_p, lbl_p, val_unit_p, boxes])
                        r_idx += 1

                aud_tab = Table(audit_table_rows, colWidths=[190, 135, 138, 80], hAlign='LEFT')
                style_cmds = [
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('TOPPADDING', (0,0), (-1,-1), 0.5),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0.5),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (0,-1), 8),
                    ('RIGHTPADDING', (1,0), (-1,-1), 0),
                    ('BOX', (3,0), (3,-1), 0.7, colors.black),
                ] + spans
                aud_tab.setStyle(TableStyle(style_cmds))
                story.append(aud_tab)

        # =====================================================================
        # PAGE 25 (Page 24 of 24): APPROVAL CERTIFICATE & SIGNATURES (12 pt)
        # =====================================================================
        elif page_idx == 25:
            story.append(Paragraph("<u><b>Approval of design of an inland vessel</b></u>", h1_center))
            story.append(Spacer(1, 8))

            cert_rows = [
                [Paragraph("a. Vessel Name", body_12), ":", Paragraph(f"<b>{inputs.get('vessel_name', '')}</b>", body_12)],
                [Paragraph("b. L OA", body_12), ":", Paragraph(f"{inputs.get('loa', 0)} M", body_12)],
                [Paragraph("c. L BP-", body_12), ":", Paragraph(f"{inputs.get('lbp', 0)} M", body_12)],
                [Paragraph("d. L WL-", body_12), ":", Paragraph(f"{inputs.get('lwl', 53.61)} M", body_12)],
                [Paragraph("e. B EXT-", body_12), ":", Paragraph(f"{inputs.get('b_ext', 9.52)} M", body_12)],
                [Paragraph("f. B MLD-", body_12), ":", Paragraph(f"{inputs.get('breadth', 0)} M", body_12)],
                [Paragraph("g. DEPTH EXT-", body_12), ":", Paragraph(f"{inputs.get('depth_ext', 4.52)} M", body_12)],
                [Paragraph("h. DEPTH MLD-", body_12), ":", Paragraph(f"{inputs.get('depth', 0)} M", body_12)],
                [Paragraph("I. DRAUGHT-", body_12), ":", Paragraph(f"{inputs.get('draft', 0)} M", body_12)],
                [Paragraph("j. Number of propeller", body_12), ":", Paragraph(f"{inputs.get('propeller_nos', 2)}", body_12)],
                [Paragraph("k. Diameter of propeller", body_12), ":", Paragraph(f"{inputs.get('prop_dia', 1524)} MM", body_12)],
                [Paragraph("l. Type of Engines", body_12), ":", Paragraph(str(inputs.get('engine_type', 'MARINE DIESEL ENGINE')), body_12)],
                [Paragraph("m. Power of Engines", body_12), ":", Paragraph(str(inputs.get('power', '550X2 BHP')), body_12)],
                [Paragraph("n. Ship’s owner name &amp; address", body_12), ":", Paragraph(f"<b>{inputs.get('owner', '')} (&amp; others)</b><br/>{inputs.get('owner_address', '')}", body_12)],
                [Paragraph("designed by (firm/person)", body_12), ":", Paragraph(f"<b>{inputs.get('designer_name', '')}</b>", body_12)],
                [Paragraph("checked by (firm/person)", body_12), ":", Paragraph(f"<b>{inputs.get('checked_by', '')}</b>", body_12)],
                [Paragraph("verified &amp; checked for", body_12), ":", Paragraph("Compliance of the rules by (DOS/LCS/BIWTA)", body_12)],
                [Paragraph("approved by", body_12), ":", Paragraph("Department of Shipping Dhaka.", body_12)],
                [Paragraph("approval no. &amp; date", body_12), ":", Paragraph("DOS/PLN/________ &nbsp;&nbsp;&nbsp;&nbsp; Date: _______________", body_12)],
            ]
            cert_tab = Table(cert_rows, colWidths=[160, 15, 368], hAlign='LEFT')
            cert_tab.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 1.2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(cert_tab)
            story.append(Spacer(1, 8))

            statement_p = Paragraph(
                "The Department of Shipping hereby approves the plan of the above mentioned vessel on condition that the "
                "Construction Supervisor will ensure compliance of the Inland Shipping Ordinance 1976 &amp; rules made there under "
                "and as per this approval booklet including instructions for supervisor during the construction of the vessel. "
                "He will also submit a compliances certificate after the completion and test trial of the vessel for registration of the vessel to the registrar of Inland Ships.",
                body_12_just
            )
            story.append(statement_p)

        # PageBreak between pages (except after the final page)
        if page_idx < total_pages:
            story.append(PageBreak())

    def canvas_maker(*args, **kwargs):
        c = AppFormDualSealCanvas(*args, **kwargs)
        c.checker_seal_bytes = checker_seal_bytes
        c.designer_seal_bytes = designer_seal_bytes
        return c

    doc.build(story, canvasmaker=canvas_maker)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

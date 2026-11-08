"""
Application Form Item Mapping for Structural Stiffener Members
Maps each structural stiffener member ID to its corresponding Item Number,
Statutory Rule, Title, and Page Number on the official Department of Shipping (DOS)
25-page statutory submission application form.
"""

from typing import Dict, Any

STIFFENER_APP_FORM_MAP: Dict[str, Dict[str, Any]] = {
    # 1. Single Bottom Girders / Keelsons
    'stiff_centre_keelson': {
        'item_no': '31',
        'rule': 'Rule 23',
        'title': 'Kilsons & Webs (Centre girder)',
        'page': 11,
        'table_ref': 'Table 16'
    },
    'stiff_side_keelson': {
        'item_no': '31',
        'rule': 'Rule 23',
        'title': 'Kilsons & Webs (Side girder)',
        'page': 11,
        'table_ref': 'Table 15'
    },
    'stiff_floor_single': {
        'item_no': '28',
        'rule': 'Rule 22',
        'title': 'Bottom construction (Floor plate)',
        'page': 11,
        'table_ref': 'Table 13'
    },
    'stiff_bottom_transverse_barge': {
        'item_no': '28',
        'rule': 'Rule 22',
        'title': 'Bottom construction (Floor plate)',
        'page': 11,
        'table_ref': 'Table 13'
    },

    # 2. Double Bottom Structures
    'stiff_centre_girder': {
        'item_no': '31',
        'rule': 'Rule 23',
        'title': 'Double bottom centre girder',
        'page': 11,
        'table_ref': 'Table 16'
    },
    'stiff_side_girder': {
        'item_no': '31',
        'rule': 'Rule 23',
        'title': 'Double bottom side girder',
        'page': 11,
        'table_ref': 'Table 15'
    },
    'stiff_solid_floor': {
        'item_no': '105',
        'rule': 'Rule 22',
        'title': 'Double bottom solid floor',
        'page': 24,
        'table_ref': 'Table 13'
    },
    'stiff_open_bracket_floor': {
        'item_no': '105',
        'rule': 'Rule 22',
        'title': 'Double bottom bracket floor',
        'page': 24,
        'table_ref': 'Table 13'
    },
    'stiff_floor_girder_vertical': {
        'item_no': '105',
        'rule': 'Rule 22',
        'title': 'Double bottom vertical stiffener',
        'page': 24,
        'table_ref': 'Table 52'
    },
    'stiff_bottom_longitudinal': {
        'item_no': '105',
        'rule': 'Rule 25',
        'title': 'Double bottom longitudinals',
        'page': 24,
        'table_ref': 'Table 66'
    },
    'stiff_inner_bottom_longitudinal': {
        'item_no': '105',
        'rule': 'Rule 25',
        'title': 'Inner bottom longitudinals',
        'page': 24,
        'table_ref': 'Table 66'
    },
    'stiff_hopper_longitudinal': {
        'item_no': '105',
        'rule': 'Rule 25',
        'title': 'Hopper tank longitudinals',
        'page': 24,
        'table_ref': 'Table 66'
    },

    # 3. Side Framing & Stringers
    'stiff_main_frame': {
        'item_no': '33',
        'rule': 'Rule 25',
        'title': 'Side frame (Section modulus)',
        'page': 11,
        'table_ref': 'Table 17'
    },
    'stiff_side_longitudinal': {
        'item_no': '33',
        'rule': 'Rule 25',
        'title': 'Side shell longitudinal frame',
        'page': 11,
        'table_ref': 'Table 66'
    },
    'stiff_side_longitudinal_barge': {
        'item_no': '33',
        'rule': 'Rule 25',
        'title': 'Side shell longitudinal frame',
        'page': 11,
        'table_ref': 'Table 66'
    },
    'stiff_inner_side_longitudinal': {
        'item_no': '33',
        'rule': 'Rule 25',
        'title': 'Inner side longitudinal frame',
        'page': 11,
        'table_ref': 'Table 66'
    },
    'stiff_web_frame': {
        'item_no': '35',
        'rule': 'Rule 26',
        'title': 'Web frame (Transverse framing)',
        'page': 12,
        'table_ref': 'Table 19'
    },
    'stiff_side_stringer': {
        'item_no': '36',
        'rule': 'Rule 27',
        'title': 'Side stringer (between web framing)',
        'page': 12,
        'table_ref': 'Table 19'
    },
    'stiff_side_transverse': {
        'item_no': '35',
        'rule': 'Rule 26',
        'title': 'Side transverse in wing tank',
        'page': 12,
        'table_ref': 'Table 19'
    },
    'stiff_horizontal_stringer': {
        'item_no': '36',
        'rule': 'Rule 27',
        'title': 'Horizontal stringer in wing tank',
        'page': 12,
        'table_ref': 'Table 19'
    },

    # 4. Deck Members
    'stiff_deck_beam': {
        'item_no': '37',
        'rule': 'Rule 28',
        'title': 'Deck beam (Section modulus)',
        'page': 12,
        'table_ref': 'Table 20'
    },
    'stiff_deck_longitudinal': {
        'item_no': '37',
        'rule': 'Rule 28',
        'title': 'Strength deck longitudinal beam',
        'page': 12,
        'table_ref': 'Table 36'
    },
    'stiff_deck_web_beam': {
        'item_no': '38',
        'rule': 'Rule 29',
        'title': 'Deck web beam (Section modulus)',
        'page': 12,
        'table_ref': 'Table 29'
    },
    'stiff_deck_girder': {
        'item_no': '39',
        'rule': 'Rule 30',
        'title': 'Deck girder (Section modulus)',
        'page': 12,
        'table_ref': 'Table 21'
    },
    'stiff_deck_transverse': {
        'item_no': '38',
        'rule': 'Rule 29',
        'title': 'Deck transverse web beam',
        'page': 12,
        'table_ref': 'Table 21'
    },
    'stiff_cross_deck_beam': {
        'item_no': '37',
        'rule': 'Rule 28',
        'title': 'Cross deck beam',
        'page': 12,
        'table_ref': 'Table 20'
    },
    'stiff_catamaran_cross_beam': {
        'item_no': '37',
        'rule': 'Rule 28',
        'title': 'Cross beam joining hulls',
        'page': 12,
        'table_ref': 'Table 20'
    },
    'stiff_catamaran_cross_girder': {
        'item_no': '39',
        'rule': 'Rule 30',
        'title': 'Cross deck girder',
        'page': 12,
        'table_ref': 'Table 21'
    },
    'stiff_catamaran_wet_deck': {
        'item_no': '76',
        'rule': 'Rule 65',
        'title': 'Wet deck stiffener',
        'page': 18,
        'table_ref': 'Table 36'
    },

    # 5. Superstructure Members
    'stiff_roof_beam': {
        'item_no': '74',
        'rule': 'Rule 63',
        'title': 'Superstructure roof beam',
        'page': 17,
        'table_ref': 'Table 36'
    },
    'stiff_roof_girder_side': {
        'item_no': '74',
        'rule': 'Rule 63',
        'title': 'Superstructure side roof girder',
        'page': 17,
        'table_ref': 'Table 37'
    },
    'stiff_roof_girder_centre': {
        'item_no': '74',
        'rule': 'Rule 63',
        'title': 'Superstructure centre roof girder',
        'page': 17,
        'table_ref': 'Table 37'
    },
    'stiff_superstructure_wall': {
        'item_no': '74',
        'rule': 'Rule 63',
        'title': 'Superstructure wall stiffener',
        'page': 17,
        'table_ref': 'Table 35'
    },
    'stiff_superstructure_frame': {
        'item_no': '74',
        'rule': 'Rule 63',
        'title': 'Superstructure main frame',
        'page': 17,
        'table_ref': 'Table 35'
    },

    # 6. Bulkhead & Hatch Members
    'stiff_bhd_transverse': {
        'item_no': '44',
        'rule': 'Rule 34',
        'title': 'Watertight bulkhead stiffeners',
        'page': 13,
        'table_ref': 'Table 26'
    },
    'stiff_tank_bhd_stringer': {
        'item_no': '48',
        'rule': 'Rule 37',
        'title': 'Tank bulkhead horizontal stringer',
        'page': 13,
        'table_ref': 'Table 28'
    },
    'stiff_tank_bhd_web': {
        'item_no': '48',
        'rule': 'Rule 37',
        'title': 'Tank bulkhead vertical web',
        'page': 13,
        'table_ref': 'Table 28'
    },
    'stiff_hatch_end_beam': {
        'item_no': '60',
        'rule': 'Rule 50',
        'title': 'Hatchway transverse beam',
        'page': 15,
        'table_ref': 'Table 33'
    },
    'stiff_hatch_side_girder': {
        'item_no': '62',
        'rule': 'Rule 51',
        'title': 'Hatchway side girder beam',
        'page': 15,
        'table_ref': 'Table 21'
    },
    'stiff_portable_hatch_beam': {
        'item_no': '60',
        'rule': 'Rule 50',
        'title': 'Portable removable hatch beam',
        'page': 15,
        'table_ref': 'Table 32'
    },
    'stiff_hatch_cover': {
        'item_no': '64',
        'rule': 'Rule 52',
        'title': 'Steel hatch cover stiffeners',
        'page': 16,
        'table_ref': 'Table 34'
    }
}


def get_stiffener_app_form_info(member_id: str, name: str = '', table_ref: str = '') -> Dict[str, Any]:
    """
    Returns the Application Form mapping information for a stiffener member:
    {
        'item_no': '31',
        'rule': 'Rule 23',
        'title': 'Kilsons & Webs (Centre girder)',
        'page': 11,
        'table_ref': 'Table 16'
    }
    """
    if member_id and member_id in STIFFENER_APP_FORM_MAP:
        info = dict(STIFFENER_APP_FORM_MAP[member_id])
        if table_ref:
            info['table_ref'] = table_ref
        return info

    # Fallback heuristics based on member name
    name_l = (name or '').lower()
    if 'keelson' in name_l or 'girder' in name_l:
        return {'item_no': '31', 'rule': 'Rule 23', 'title': name or 'Kilsons & Girders', 'page': 11, 'table_ref': table_ref or 'Table 16'}
    if 'floor' in name_l:
        return {'item_no': '28', 'rule': 'Rule 22', 'title': name or 'Bottom Floor Plate', 'page': 11, 'table_ref': table_ref or 'Table 13'}
    if 'frame' in name_l and 'web' not in name_l and 'super' not in name_l:
        return {'item_no': '33', 'rule': 'Rule 25', 'title': name or 'Side Frame', 'page': 11, 'table_ref': table_ref or 'Table 17'}
    if 'web frame' in name_l:
        return {'item_no': '35', 'rule': 'Rule 26', 'title': name or 'Web Frame', 'page': 12, 'table_ref': table_ref or 'Table 19'}
    if 'stringer' in name_l:
        return {'item_no': '36', 'rule': 'Rule 27', 'title': name or 'Side Stringer', 'page': 12, 'table_ref': table_ref or 'Table 19'}
    if 'deck beam' in name_l or 'beam' in name_l and 'hatch' not in name_l and 'roof' not in name_l:
        return {'item_no': '37', 'rule': 'Rule 28', 'title': name or 'Deck Beam', 'page': 12, 'table_ref': table_ref or 'Table 20'}
    if 'deck girder' in name_l:
        return {'item_no': '39', 'rule': 'Rule 30', 'title': name or 'Deck Girder', 'page': 12, 'table_ref': table_ref or 'Table 21'}
    if 'roof' in name_l or 'superstructure' in name_l:
        return {'item_no': '74', 'rule': 'Rule 63', 'title': name or 'Superstructure Stiffener', 'page': 17, 'table_ref': table_ref or 'Table 35'}
    if 'bulkhead' in name_l or 'bhd' in name_l:
        return {'item_no': '44', 'rule': 'Rule 34', 'title': name or 'Bulkhead Stiffener', 'page': 13, 'table_ref': table_ref or 'Table 26'}
    if 'hatch' in name_l and 'cover' in name_l:
        return {'item_no': '64', 'rule': 'Rule 52', 'title': name or 'Steel Hatch Cover', 'page': 16, 'table_ref': table_ref or 'Table 34'}
    if 'hatch' in name_l:
        return {'item_no': '60', 'rule': 'Rule 50', 'title': name or 'Hatchway Beam', 'page': 15, 'table_ref': table_ref or 'Table 32'}

    return {'item_no': '—', 'rule': 'Statutory Rule', 'title': name or 'Structural Member', 'page': '—', 'table_ref': table_ref or 'Statutory Table'}

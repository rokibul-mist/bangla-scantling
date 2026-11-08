"""
Vessel Structural Members Catalog & Hull Type Rules Engine
Based on statutory Bangladesh Inland Shipping Rules 2001 / SRO 308 / ISO 1976
and Resource/vessel_structural_members_3d_list_v5.md.
"""

# Master Structural Members Catalog
# Every member defines its category, type (plate vs stiffener), governing table,
# applicable hull types, applicable vessel types, welded-on plate mapping,
# and default profile geometry.

STRUCTURAL_MEMBERS = [
    {
        "id": "mat_min_hull",
        "name": "Minimum Hull Plate Material",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Rule 8(1)",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 4.0,
        "unit": "mm",
        "notes": "Mild steel structural plate requirement",
        "desc": "Minimum Hull Plate Material",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_keel",
        "name": "Keel Plating Thickness",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 1",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 7.99,
        "bound_plate_key": "t_keel",
        "unit": "mm",
        "notes": "Rule 9, Table 1 - Heavy keel strake",
        "desc": "Keel Plating Thickness",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_keel_width",
        "name": "Keel Plating Width",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 1",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 1093.0,
        "bound_plate_key": "w_keel",
        "unit": "mm",
        "notes": "Rule 9, Table 1 - Minimum keel width",
        "desc": "Keel Plating Width",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_bottom",
        "name": "Bottom Shell Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 2",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 7.89,
        "bound_plate_key": "t_bottom",
        "unit": "mm",
        "notes": "Rule 10, Table 2 - Flat of bottom shell",
        "desc": "Bottom Shell Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_bilge",
        "name": "Bilge Plating Thickness",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 3",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Ferry",
            "Oil Tanker",
            "Catamaran",
            "Container",
            "Passenger"
        ],
        "baseline": 9.49,
        "bound_plate_key": "t_bilge",
        "unit": "mm",
        "notes": "Rule 11, Table 3 - Curved bilge strake",
        "desc": "Bilge Plating Thickness",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_chine",
        "name": "Chine Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 3",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Barge"
        ],
        "baseline": 9.49,
        "bound_plate_key": "t_chine",
        "unit": "mm",
        "notes": "Table 3 - Corner chine strake on hard-chine barge hulls",
        "desc": "Chine Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_rake",
        "name": "Rake Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 2",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Barge"
        ],
        "baseline": 7.89,
        "bound_plate_key": "t_rake",
        "unit": "mm",
        "notes": "Table 2 - Sloped rake plating at forward and aft barge swim ends",
        "desc": "Rake Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_side",
        "name": "Side Shell Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 4",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 7.49,
        "bound_plate_key": "t_side",
        "unit": "mm",
        "notes": "Rule 12, Table 4 - Side shell plating",
        "desc": "Side Shell Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_sheer_strake",
        "name": "Sheer Strake Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 4, Table 6",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 7.49,
        "bound_plate_key": "t_sheer",
        "unit": "mm",
        "notes": "Rule 12/14, Table 4 & 6 - Upper deck edge strake",
        "desc": "Sheer Strake Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_main_deck",
        "name": "Main Strength Deck Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 6",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 5.99,
        "bound_plate_key": "t_deck_all",
        "unit": "mm",
        "notes": "Rule 14, Table 6 - Weather deck plating",
        "desc": "Main Strength Deck Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_poop_deck",
        "name": "Poop Deck Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 6",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Passenger",
            "Ferry",
            "Oil Tanker"
        ],
        "baseline": 5.5,
        "bound_plate_key": "t_poop_deck",
        "unit": "mm",
        "notes": "Table 6 - Aft accommodation poop deck plating",
        "desc": "Poop Deck Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_forecastle_deck",
        "name": "Forecastle Deck Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 6",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Container",
            "Oil Tanker"
        ],
        "baseline": 5.5,
        "bound_plate_key": "t_forecastle_deck",
        "unit": "mm",
        "notes": "Table 6 - Forward forecastle weather deck plating",
        "desc": "Forecastle Deck Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_upper_passenger_deck",
        "name": "Upper Passenger Deck Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 6",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Passenger",
            "Ferry"
        ],
        "baseline": 5.0,
        "bound_plate_key": "t_passenger_deck",
        "unit": "mm",
        "notes": "Table 6 - Upper passenger deck superstructure plating",
        "desc": "Upper Passenger Deck Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_second_deck",
        "name": "Second / Tween Deck Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 6",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Passenger",
            "Steel Body Cargo Vessel"
        ],
        "baseline": 5.5,
        "bound_plate_key": "t_second_deck",
        "unit": "mm",
        "notes": "Table 6 - Intermediate lower / tween deck plating",
        "desc": "Second / Tween Deck Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_nav_deck",
        "name": "Navigation Bridge Deck Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 6",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Ferry",
            "Oil Tanker",
            "Catamaran",
            "Container",
            "Passenger"
        ],
        "baseline": 5.0,
        "bound_plate_key": "t_nav_deck",
        "unit": "mm",
        "notes": "Table 6 - Wheelhouse & navigation deck crown plating",
        "desc": "Navigation Bridge Deck Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_wet_deck",
        "name": "Wet Deck Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 6",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Catamaran"
        ],
        "baseline": 6.5,
        "bound_plate_key": "t_wet_deck",
        "unit": "mm",
        "notes": "Table 6 - Cross-structure bottom wet deck slamming plate",
        "desc": "Wet Deck Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_deck_strip",
        "name": "Deck Strip Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 6",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Container"
        ],
        "baseline": 6.5,
        "bound_plate_key": "t_deck_strip",
        "unit": "mm",
        "notes": "Table 6 - Transverse strength deck plating between container hatch bays",
        "desc": "Deck Strip Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_hatchway_deck",
        "name": "Strength Deck at Hatchways",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 5",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Container",
            "Barge"
        ],
        "baseline": 6.5,
        "bound_plate_key": "t_deck_hatch",
        "unit": "mm",
        "notes": "Rule 13, Table 5 - Deck alongside cargo hatchways",
        "desc": "Strength Deck at Hatchways",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_inner_bottom",
        "name": "Inner Bottom Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 1",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 7.99,
        "bound_plate_key": "t_inner_bottom",
        "unit": "mm",
        "notes": "Rule 9, Table 1 - Tank top plating",
        "desc": "Inner Bottom Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_margin",
        "name": "Margin Plate",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 1",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 7.99,
        "bound_plate_key": "t_margin",
        "unit": "mm",
        "notes": "Rule 9, Table 1 - Outboard inclined bilge margin strake",
        "desc": "Margin Plate",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_solid_floor_web",
        "name": "Solid Floor Web Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 13, Table 15",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 8.5,
        "bound_plate_key": "t_floor_web",
        "unit": "mm",
        "notes": "Table 13 & 15 - Full depth floor web plate in double bottom",
        "desc": "Solid Floor Web Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_inner_side",
        "name": "Inner Side Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 27, Table 4",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 7.0,
        "bound_plate_key": "t_inner_side",
        "unit": "mm",
        "notes": "Rule 44, Table 27 - Double hull longitudinal side boundary",
        "desc": "Inner Side Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_tunnel_side",
        "name": "Inner Hull Tunnel Side Shell",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 4",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Catamaran"
        ],
        "baseline": 7.49,
        "bound_plate_key": "t_tunnel_side",
        "unit": "mm",
        "notes": "Table 4 - Inboard hull side shell facing tunnel",
        "desc": "Inner Hull Tunnel Side Shell",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_hopper",
        "name": "Hopper Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 27",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Oil Tanker",
            "Container",
            "Barge"
        ],
        "baseline": 7.0,
        "bound_plate_key": "t_hopper",
        "unit": "mm",
        "notes": "Rule 44, Table 27 - Sloped hopper tank plate",
        "desc": "Hopper Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_stem",
        "name": "Plate Stem Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 7",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Ferry",
            "Oil Tanker",
            "Catamaran",
            "Container",
            "Passenger"
        ],
        "baseline": 8.0,
        "bound_plate_key": "t_stem",
        "unit": "mm",
        "notes": "Rule 15, Table 7 - Curved plate stem at forward end",
        "desc": "Plate Stem Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "plate_transom",
        "name": "Transom Stern Plating",
        "category": "GROUP 1: HULL SHELL & DECK PLATING",
        "type": "plate",
        "table_ref": "Table 4",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 7.0,
        "bound_plate_key": "t_transom",
        "unit": "mm",
        "notes": "Rule 12, Table 4 - Vertical flat stern transom plate",
        "desc": "Transom Stern Plating",
        "group": "GROUP 1: HULL SHELL & DECK PLATING"
    },
    {
        "id": "bar_stem",
        "name": "Bar Stem Breadth & Thickness",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 8",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Ferry",
            "Oil Tanker",
            "Catamaran",
            "Container",
            "Passenger"
        ],
        "baseline": 115.0,
        "unit": "mm",
        "notes": "Rule 16, Table 8 - Solid rectangular bar stem bar breadth",
        "desc": "Bar Stem Breadth & Thickness",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "stern_frame_bar",
        "name": "Stern Frame Bar Breadth",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 9",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Ferry",
            "Oil Tanker",
            "Catamaran",
            "Container",
            "Passenger"
        ],
        "baseline": 115.0,
        "unit": "mm",
        "notes": "Rule 17, Table 9 - Solid rectangular stern bar breadth",
        "desc": "Stern Frame Bar Breadth",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "propeller_post",
        "name": "Propeller Post Dimensions",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 10",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 130.0,
        "unit": "mm",
        "notes": "Rule 18, Table 10 - Screw aperture propeller post",
        "desc": "Propeller Post Dimensions",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "sole_piece",
        "name": "Sole Piece Breadth",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 11",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 150.0,
        "unit": "mm",
        "notes": "Rule 19, Table 11 - Sole piece below propeller aperture",
        "desc": "Sole Piece Breadth",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "sole_piece_thk",
        "name": "Sole Piece Thickness",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 11",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 100.0,
        "unit": "mm",
        "notes": "Rule 19, Table 11 - Vertical thickness of bottom sole piece",
        "desc": "Sole Piece Thickness",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "propeller_boss_thk",
        "name": "Propeller Boss Wall Thickness",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 12",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 40.0,
        "unit": "mm",
        "notes": "Rule 20, Table 12 - Shaft boss casing surrounding stern tube",
        "desc": "Propeller Boss Wall Thickness",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "v_strut_shaft",
        "name": "V-Strut Propeller Shaft Bracket",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 49",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Catamaran",
            "Ferry",
            "Passenger",
            "all"
        ],
        "baseline": 45.0,
        "unit": "mm",
        "notes": "Table 49 - Two-arm V-bracket section for twin-screw shaft support",
        "desc": "V-Strut Propeller Shaft Bracket",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "i_strut_shaft",
        "name": "I-Strut Propeller Shaft Bracket",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 50",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Catamaran",
            "Ferry",
            "Passenger",
            "all"
        ],
        "baseline": 50.0,
        "unit": "mm",
        "notes": "Table 50 - Single-arm I-strut bracket for shaft support",
        "desc": "I-Strut Propeller Shaft Bracket",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "rudder_stock_dia",
        "name": "Rudder Stock Diameter - Supported",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 38",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 110.0,
        "unit": "mm",
        "notes": "Rule 62, Table 38 - Rudder head diameter with bottom pintle support",
        "desc": "Rudder Stock Diameter - Supported",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "rudder_stock_spade_dia",
        "name": "Rudder Stock Diameter - Spade",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 39",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Catamaran",
            "Ferry",
            "Passenger",
            "all"
        ],
        "baseline": 125.0,
        "unit": "mm",
        "notes": "Table 39 - Unsupported cantilever spade rudder stock diameter",
        "desc": "Rudder Stock Diameter - Spade",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "rudder_pintle_dia",
        "name": "Rudder Pintle Diameter",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 40",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 60.0,
        "unit": "mm",
        "notes": "Rule 64, Table 40 - Lower and middle rudder bearing pintles",
        "desc": "Rudder Pintle Diameter",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "rudder_flange_thk",
        "name": "Rudder Coupling Flange Thickness",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 41, Table 42",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 28.0,
        "unit": "mm",
        "notes": "Rule 65, Table 41 & 42 - Horizontal rudder palm coupling flange",
        "desc": "Rudder Coupling Flange Thickness",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "rudder_coupling_bolts",
        "name": "Rudder Coupling Bolts Diameter",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 41, Table 42",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 25.0,
        "unit": "mm",
        "notes": "Table 41 & 42 - High tensile fitted coupling bolts diameter",
        "desc": "Rudder Coupling Bolts Diameter",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "rudder_blade_thk",
        "name": "Rudder Blade Plating Thickness",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "plate",
        "table_ref": "Table 4",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 8.0,
        "bound_plate_key": "t_rudder",
        "unit": "mm",
        "notes": "Rule 66, Table 4 - Double plate streamlined rudder side shell",
        "desc": "Rudder Blade Plating Thickness",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "steering_tiller_quadrant",
        "name": "Steering Tiller / Quadrant Hub",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 43",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 110.0,
        "unit": "mm",
        "notes": "Table 43 - Steering tiller arm and quadrant hub dimensions",
        "desc": "Steering Tiller / Quadrant Hub",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "steering_chains_shackles",
        "name": "Steering Chains & Shackles",
        "category": "GROUP 2: STEMS, STERN FRAMES & RUDDER",
        "type": "dimension",
        "table_ref": "Table 44",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 16.0,
        "unit": "mm",
        "notes": "Table 44 - Steering rod, short link chain and shackle pin size",
        "desc": "Steering Chains & Shackles",
        "group": "GROUP 2: STEMS, STERN FRAMES & RUDDER"
    },
    {
        "id": "stiff_centre_keelson",
        "name": "Centre Keelson",
        "category": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS",
        "type": "stiffener",
        "table_ref": "Table 16",
        "applicable_hull_types": [
            "Single Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 1057.77,
        "unit": "cm3",
        "welded_on_plate": "Bottom Shell Plating",
        "welded_plate_key": "t_bottom",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 500,
            "web_thk": 12.0,
            "flange_width": 100,
            "flange_thk": 10.0
        },
        "notes": "Rule 24, Table 16 - Centerline deep keelson girder",
        "desc": "Centre Keelson",
        "group": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS"
    },
    {
        "id": "stiff_side_keelson",
        "name": "Side Keelson",
        "category": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS",
        "type": "stiffener",
        "table_ref": "Table 15",
        "applicable_hull_types": [
            "Single Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 400.0,
        "unit": "cm3",
        "welded_on_plate": "Bottom Shell Plating",
        "welded_plate_key": "t_bottom",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 350,
            "web_thk": 10.0,
            "flange_width": 100,
            "flange_thk": 10.0
        },
        "notes": "Rule 23, Table 15 - Off-centre bottom side keelson",
        "desc": "Side Keelson",
        "group": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS"
    },
    {
        "id": "stiff_floor_single",
        "name": "Bottom Transverse Floor Plate",
        "category": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS",
        "type": "stiffener",
        "table_ref": "Table 13",
        "applicable_hull_types": [
            "Single Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 222.18,
        "unit": "cm3",
        "welded_on_plate": "Bottom Shell Plating",
        "welded_plate_key": "t_bottom",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 400,
            "web_thk": 9.0,
            "flange_width": 75,
            "flange_thk": 9.0
        },
        "notes": "Rule 21, Table 13 - Single bottom transverse plate floor",
        "desc": "Bottom Transverse Floor Plate",
        "group": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS"
    },
    {
        "id": "stiff_centre_girder",
        "name": "Centre Girder",
        "category": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS",
        "type": "stiffener",
        "table_ref": "Table 16",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 1057.77,
        "unit": "cm3",
        "welded_on_plate": "Bottom Shell Plating",
        "welded_plate_key": "t_bottom",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 850,
            "web_thk": 12.0,
            "flange_width": 150,
            "flange_thk": 14.0
        },
        "notes": "Rule 24, Table 16 - Double bottom centerline watertight girder",
        "desc": "Centre Girder",
        "group": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS"
    },
    {
        "id": "stiff_side_girder",
        "name": "Side Girder",
        "category": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS",
        "type": "stiffener",
        "table_ref": "Table 15",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 400.0,
        "unit": "cm3",
        "welded_on_plate": "Bottom Shell Plating",
        "welded_plate_key": "t_bottom",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 850,
            "web_thk": 10.0,
            "flange_width": 120,
            "flange_thk": 12.0
        },
        "notes": "Rule 23, Table 15 - Double bottom off-centre intercostal girder",
        "desc": "Side Girder",
        "group": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS"
    },
    {
        "id": "stiff_solid_floor",
        "name": "Solid Floor",
        "category": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS",
        "type": "stiffener",
        "table_ref": "Table 13",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 222.18,
        "unit": "cm3",
        "welded_on_plate": "Bottom Shell Plating",
        "welded_plate_key": "t_bottom",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 850,
            "web_thk": 9.5,
            "flange_width": 90,
            "flange_thk": 10.0
        },
        "notes": "Rule 21, Table 13 - Double bottom transverse solid plate floor",
        "desc": "Solid Floor",
        "group": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS"
    },
    {
        "id": "stiff_open_bracket_floor",
        "name": "Open Bracket Floor",
        "category": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS",
        "type": "stiffener",
        "table_ref": "Table 13, Table 52",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 180.0,
        "unit": "cm3",
        "welded_on_plate": "Bottom Shell Plating",
        "welded_plate_key": "t_bottom",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 150,
            "web_thk": 10.0,
            "flange_width": 90,
            "flange_thk": 10.0
        },
        "notes": "Table 13 & 52 - Intermediate open frame bracket floor",
        "desc": "Open Bracket Floor",
        "group": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS"
    },
    {
        "id": "stiff_floor_girder_vertical",
        "name": "Floor & Girder Vertical Stiffener",
        "category": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS",
        "type": "stiffener",
        "table_ref": "Table 52",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 45.0,
        "unit": "cm3",
        "welded_on_plate": "Solid Floor Web Plating",
        "welded_plate_key": "t_floor_web",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 100,
            "web_thk": 8.0,
            "flange_width": 65,
            "flange_thk": 8.0
        },
        "notes": "Table 52 - Vertical stiffeners on floor and girder web plates",
        "desc": "Floor & Girder Vertical Stiffener",
        "group": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS"
    },
    {
        "id": "stiff_bottom_transverse_barge",
        "name": "Bottom Transverse Web Frame",
        "category": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS",
        "type": "stiffener",
        "table_ref": "Table 13, Table 67",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Barge"
        ],
        "baseline": 350.0,
        "unit": "cm3",
        "welded_on_plate": "Bottom Shell Plating",
        "welded_plate_key": "t_bottom",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 300,
            "web_thk": 10.0,
            "flange_width": 100,
            "flange_thk": 12.0
        },
        "notes": "Table 13 - Deep transverse web ring floor on barge bottom",
        "desc": "Bottom Transverse Web Frame",
        "group": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS"
    },
    {
        "id": "stiff_bottom_longitudinal",
        "name": "Bottom Longitudinal",
        "category": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS",
        "type": "stiffener",
        "table_ref": "Table 66, Table 52",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 145.0,
        "unit": "cm3",
        "welded_on_plate": "Bottom Shell Plating",
        "welded_plate_key": "t_bottom",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 150,
            "web_thk": 10.0,
            "flange_width": 90,
            "flange_thk": 10.0
        },
        "notes": "Table 66 & 52 - Longitudinal stiffeners on outer bottom shell",
        "desc": "Bottom Longitudinal",
        "group": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS"
    },
    {
        "id": "stiff_inner_bottom_longitudinal",
        "name": "Inner Bottom Longitudinal",
        "category": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS",
        "type": "stiffener",
        "table_ref": "Table 66, Table 52",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 125.0,
        "unit": "cm3",
        "welded_on_plate": "Inner Bottom Plating",
        "welded_plate_key": "t_inner_bottom",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 125,
            "web_thk": 9.0,
            "flange_width": 75,
            "flange_thk": 9.0
        },
        "notes": "Table 66 & 52 - Longitudinal stiffeners supporting tank top",
        "desc": "Inner Bottom Longitudinal",
        "group": "GROUP 3: BOTTOM CONSTRUCTION, FLOORS & KEELSONS"
    },
    {
        "id": "stiff_main_frame",
        "name": "Main Side Transverse Frame",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "stiffener",
        "table_ref": "Table 17",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 177.2,
        "unit": "cm3",
        "welded_on_plate": "Side Shell Plating",
        "welded_plate_key": "t_side",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 150,
            "web_thk": 10.0,
            "flange_width": 100,
            "flange_thk": 10.0
        },
        "notes": "Rule 25, Table 17 - Side shell transverse main frame",
        "desc": "Main Side Transverse Frame",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "stiff_web_frame",
        "name": "Side Web Frame",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "stiffener",
        "table_ref": "Table 19",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 550.0,
        "unit": "cm3",
        "welded_on_plate": "Side Shell Plating",
        "welded_plate_key": "t_side",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 350,
            "web_thk": 11.0,
            "flange_width": 120,
            "flange_thk": 12.0
        },
        "notes": "Rule 27, Table 19 - Heavy transverse web frame",
        "desc": "Side Web Frame",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "stiff_side_stringer",
        "name": "Side Stringer",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "stiffener",
        "table_ref": "Table 19",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 350.0,
        "unit": "cm3",
        "welded_on_plate": "Side Shell Plating",
        "welded_plate_key": "t_side",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 250,
            "web_thk": 10.0,
            "flange_width": 100,
            "flange_thk": 10.0
        },
        "notes": "Rule 27, Table 19 - Side shell longitudinal horizontal girder",
        "desc": "Side Stringer",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "stiff_side_transverse",
        "name": "Side Transverse in Wing Tank",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "stiffener",
        "table_ref": "Table 19",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 650.0,
        "unit": "cm3",
        "welded_on_plate": "Side Shell Plating",
        "welded_plate_key": "t_side",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 400,
            "web_thk": 11.0,
            "flange_width": 120,
            "flange_thk": 12.0
        },
        "notes": "Rule 27, Table 19 - Vertical web transverse in double-hull wing tank",
        "desc": "Side Transverse in Wing Tank",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "stiff_horizontal_stringer",
        "name": "Horizontal Stringer in Wing Tank",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "stiffener",
        "table_ref": "Table 19",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 450.0,
        "unit": "cm3",
        "welded_on_plate": "Side Shell Plating",
        "welded_plate_key": "t_side",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 300,
            "web_thk": 10.0,
            "flange_width": 100,
            "flange_thk": 10.0
        },
        "notes": "Table 19 - Horizontal longitudinal girder in wing tank",
        "desc": "Horizontal Stringer in Wing Tank",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "stiff_side_longitudinal",
        "name": "Shell Side Longitudinal",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "stiffener",
        "table_ref": "Table 66, Table 52",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 130.0,
        "unit": "cm3",
        "welded_on_plate": "Side Shell Plating",
        "welded_plate_key": "t_side",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 150,
            "web_thk": 10.0,
            "flange_width": 90,
            "flange_thk": 10.0
        },
        "notes": "Table 66 & 52 - Longitudinal stiffeners on outer side shell",
        "desc": "Shell Side Longitudinal",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "stiff_side_longitudinal_barge",
        "name": "Side Longitudinals",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "stiffener",
        "table_ref": "Table 66, Table 52",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom"
        ],
        "applicable_vessel_types": [
            "Barge"
        ],
        "baseline": 130.0,
        "unit": "cm3",
        "welded_on_plate": "Side Shell Plating",
        "welded_plate_key": "t_side",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 150,
            "web_thk": 10.0,
            "flange_width": 90,
            "flange_thk": 10.0
        },
        "notes": "Table 66 & 52 - Longitudinal stiffeners on side shell of barge",
        "desc": "Side Longitudinals",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "stiff_inner_side_longitudinal",
        "name": "Inner Side Longitudinal",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "stiffener",
        "table_ref": "Table 66, Table 52",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 120.0,
        "unit": "cm3",
        "welded_on_plate": "Inner Side Plating",
        "welded_plate_key": "t_inner_side",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 125,
            "web_thk": 9.0,
            "flange_width": 75,
            "flange_thk": 9.0
        },
        "notes": "Table 66 & 52 - Longitudinal stiffeners on inner skin",
        "desc": "Inner Side Longitudinal",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "stiff_hopper_longitudinal",
        "name": "Hopper Longitudinal",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "stiffener",
        "table_ref": "Table 66, Table 52",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Oil Tanker",
            "Container",
            "Barge"
        ],
        "baseline": 125.0,
        "unit": "cm3",
        "welded_on_plate": "Hopper Plating",
        "welded_plate_key": "t_hopper",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 125,
            "web_thk": 9.0,
            "flange_width": 75,
            "flange_thk": 9.0
        },
        "notes": "Table 66 & 52 - Stiffeners on inclined hopper plate",
        "desc": "Hopper Longitudinal",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "bracket_bilge",
        "name": "Bilge Bracket",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "dimension",
        "table_ref": "Table 52",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 450.0,
        "unit": "mm",
        "notes": "Rule 72, Table 52 - Bilge corner bracket connecting floor and main frame",
        "desc": "Bilge Bracket",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "bracket_deck",
        "name": "Deck Beam End Bracket to Frame",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "dimension",
        "table_ref": "Table 52",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 350.0,
        "unit": "mm",
        "notes": "Rule 72, Table 52 - Beam knee bracket at deck-to-shell connection",
        "desc": "Deck Beam End Bracket to Frame",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "bracket_tank_boundary",
        "name": "Tank Boundary Bracket",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "dimension",
        "table_ref": "Table 52",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 350.0,
        "unit": "mm",
        "notes": "Table 52 - Gusset bracket at tank boundary corners",
        "desc": "Tank Boundary Bracket",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "bracket_hopper",
        "name": "Hopper Corner Knuckle Bracket",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "dimension",
        "table_ref": "Table 52",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 400.0,
        "unit": "mm",
        "notes": "Table 52 - Triangular stiffening bracket at hopper knuckle",
        "desc": "Hopper Corner Knuckle Bracket",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "bracket_knuckle",
        "name": "Knuckle Bracket",
        "category": "GROUP 4: FRAMING SYSTEMS & STRINGERS",
        "type": "dimension",
        "table_ref": "Table 52",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 350.0,
        "unit": "mm",
        "notes": "Table 52 - Stiffening bracket where shell plate changes angle",
        "desc": "Knuckle Bracket",
        "group": "GROUP 4: FRAMING SYSTEMS & STRINGERS"
    },
    {
        "id": "pillar_solid_dia",
        "name": "Solid Round Deck Pillar",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "dimension",
        "table_ref": "Table 22",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 85.0,
        "unit": "mm",
        "notes": "Rule 35, Table 22 - Solid round steel deck supporting pillar",
        "desc": "Solid Round Deck Pillar",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "pillar_tubular_dia",
        "name": "Tubular Steel Deck Pillar",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "dimension",
        "table_ref": "Table 23",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 114.0,
        "unit": "mm",
        "notes": "Table 23 - Hollow circular tubular deck supporting pillar",
        "desc": "Tubular Steel Deck Pillar",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_deck_beam",
        "name": "Transverse Strength Deck Beam",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 20",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 103.0,
        "unit": "cm3",
        "welded_on_plate": "Main Strength Deck Plating",
        "welded_plate_key": "t_deck_all",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 125,
            "web_thk": 9.0,
            "flange_width": 75,
            "flange_thk": 9.0
        },
        "notes": "Rule 28, Table 20 - Transverse weather deck beam",
        "desc": "Transverse Strength Deck Beam",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_deck_longitudinal",
        "name": "Strength Deck Longitudinal Beams",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 36",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 95.0,
        "unit": "cm3",
        "welded_on_plate": "Main Strength Deck Plating",
        "welded_plate_key": "t_deck_all",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 125,
            "web_thk": 9.0,
            "flange_width": 75,
            "flange_thk": 9.0
        },
        "notes": "Rule 48, Table 36 - Longitudinal weather deck stiffeners",
        "desc": "Strength Deck Longitudinal Beams",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_deck_web_beam",
        "name": "Strength Deck Transverse Web Beams",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 29",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 350.0,
        "unit": "cm3",
        "welded_on_plate": "Main Strength Deck Plating",
        "welded_plate_key": "t_deck_all",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 250,
            "web_thk": 10.0,
            "flange_width": 100,
            "flange_thk": 10.0
        },
        "notes": "Rule 45, Table 29 - Deep transverse deck beam",
        "desc": "Strength Deck Transverse Web Beams",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_deck_girder",
        "name": "Main Deck Center Longitudinal Girder",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 21",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 850.0,
        "unit": "cm3",
        "welded_on_plate": "Main Strength Deck Plating",
        "welded_plate_key": "t_deck_all",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 450,
            "web_thk": 11.0,
            "flange_width": 150,
            "flange_thk": 14.0
        },
        "notes": "Rule 33, Table 21 - Continuous deck centerline girder",
        "desc": "Main Deck Center Longitudinal Girder",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_deck_transverse",
        "name": "Deck Transverse Web Beam",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 21, Table 37, Table 67",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Oil Tanker",
            "Barge"
        ],
        "baseline": 500.0,
        "unit": "cm3",
        "welded_on_plate": "Main Strength Deck Plating",
        "welded_plate_key": "t_deck_all",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 350,
            "web_thk": 10.0,
            "flange_width": 120,
            "flange_thk": 12.0
        },
        "notes": "Table 21 & 37 - Heavy transverse deck girder spanning between wing tanks",
        "desc": "Deck Transverse Web Beam",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_cross_deck_beam",
        "name": "Cross Deck Beam",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 20, Table 36",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Container"
        ],
        "baseline": 180.0,
        "unit": "cm3",
        "welded_on_plate": "Deck Strip Plating",
        "welded_plate_key": "t_deck_strip",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 200,
            "web_thk": 9.0,
            "flange_width": 90,
            "flange_thk": 10.0
        },
        "notes": "Table 20 & 36 - Transverse deck stiffener supporting strip plate",
        "desc": "Cross Deck Beam",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_catamaran_cross_beam",
        "name": "Cross Beam Joining Hulls",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 20, Table 21",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Catamaran"
        ],
        "baseline": 750.0,
        "unit": "cm3",
        "welded_on_plate": "Wet Deck Plating",
        "welded_plate_key": "t_wet_deck",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 450,
            "web_thk": 12.0,
            "flange_width": 150,
            "flange_thk": 14.0
        },
        "notes": "Table 20 & 21 - Primary transverse bridging beam connecting twin demi-hulls",
        "desc": "Cross Beam Joining Hulls",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_catamaran_cross_girder",
        "name": "Cross Deck Girder",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 21, Table 37",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Catamaran"
        ],
        "baseline": 850.0,
        "unit": "cm3",
        "welded_on_plate": "Main Strength Deck Plating",
        "welded_plate_key": "t_deck_all",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 500,
            "web_thk": 12.0,
            "flange_width": 150,
            "flange_thk": 15.0
        },
        "notes": "Table 21 & 37 - Longitudinal deck girder over bridging cross-structure",
        "desc": "Cross Deck Girder",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_catamaran_wet_deck",
        "name": "Wet Deck Stiffener",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 36",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Catamaran"
        ],
        "baseline": 115.0,
        "unit": "cm3",
        "welded_on_plate": "Wet Deck Plating",
        "welded_plate_key": "t_wet_deck",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 125,
            "web_thk": 9.0,
            "flange_width": 75,
            "flange_thk": 9.0
        },
        "notes": "Table 36 - Stiffener on wet deck bottom plate resisting wave impact",
        "desc": "Wet Deck Stiffener",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "bracket_catamaran_haunch",
        "name": "Catamaran Haunch Bracket",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "dimension",
        "table_ref": "Table 52",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Catamaran"
        ],
        "baseline": 500.0,
        "unit": "mm",
        "notes": "Table 52 - Deep radius haunch bracket at cross beam to inner hull junction",
        "desc": "Catamaran Haunch Bracket",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "bracket_container_cell_guide",
        "name": "Cell Guide Support Bracket",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "dimension",
        "table_ref": "Table 52",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Container"
        ],
        "baseline": 350.0,
        "unit": "mm",
        "notes": "Table 52 - Vertical angle guide support bracket securing container stacks",
        "desc": "Cell Guide Support Bracket",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_roof_beam",
        "name": "Superstructure Roof Beam",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 36",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Passenger",
            "Ferry",
            "Steel Body Cargo Vessel"
        ],
        "baseline": 55.0,
        "unit": "cm3",
        "welded_on_plate": "Navigation Bridge Deck Plating",
        "welded_plate_key": "t_nav_deck",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 90,
            "web_thk": 7.0,
            "flange_width": 60,
            "flange_thk": 7.0
        },
        "notes": "Table 36 - Lightweight roof beam supporting cabin/wheelhouse roof",
        "desc": "Superstructure Roof Beam",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_roof_girder_side",
        "name": "Side Roof Girder",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 37",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Passenger",
            "Ferry",
            "Steel Body Cargo Vessel"
        ],
        "baseline": 120.0,
        "unit": "cm3",
        "welded_on_plate": "Navigation Bridge Deck Plating",
        "welded_plate_key": "t_nav_deck",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 150,
            "web_thk": 8.0,
            "flange_width": 75,
            "flange_thk": 8.0
        },
        "notes": "Table 37 - Longitudinal roof side girder supporting roof beams",
        "desc": "Side Roof Girder",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_roof_girder_centre",
        "name": "Centre Roof Girder",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 37",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Passenger",
            "Ferry",
            "Steel Body Cargo Vessel"
        ],
        "baseline": 150.0,
        "unit": "cm3",
        "welded_on_plate": "Navigation Bridge Deck Plating",
        "welded_plate_key": "t_nav_deck",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 175,
            "web_thk": 8.0,
            "flange_width": 75,
            "flange_thk": 8.0
        },
        "notes": "Table 37 - Centerline roof girder supporting wheelhouse / saloon crown",
        "desc": "Centre Roof Girder",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_superstructure_wall",
        "name": "Superstructure Wall Stiffener",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 35",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 65.0,
        "unit": "cm3",
        "welded_on_plate": "Side Shell Plating",
        "welded_plate_key": "t_side",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 100,
            "web_thk": 7.0,
            "flange_width": 65,
            "flange_thk": 7.0
        },
        "notes": "Rule 47, Table 35 - Vertical stiffeners on superstructure front and sides",
        "desc": "Superstructure Wall Stiffener",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "stiff_superstructure_frame",
        "name": "Superstructure Main Frame",
        "category": "GROUP 5: DECKS, GIRDERS & PILLARS",
        "type": "stiffener",
        "table_ref": "Table 35",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 85.0,
        "unit": "cm3",
        "welded_on_plate": "Side Shell Plating",
        "welded_plate_key": "t_side",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 125,
            "web_thk": 8.0,
            "flange_width": 75,
            "flange_thk": 8.0
        },
        "notes": "Table 35 - Transverse frame in passenger saloon and cabin tiers",
        "desc": "Superstructure Main Frame",
        "group": "GROUP 5: DECKS, GIRDERS & PILLARS"
    },
    {
        "id": "bhd_collision_pos",
        "name": "Collision Bulkhead Position",
        "category": "GROUP 6: WATERTIGHT BULKHEADS & TANKS",
        "type": "dimension",
        "table_ref": "Table 24",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 4.19,
        "unit": "m",
        "notes": "Rule 38, Table 24 - 0.05L to 0.08L from forward perpendicular",
        "desc": "Collision Bulkhead Position",
        "group": "GROUP 6: WATERTIGHT BULKHEADS & TANKS"
    },
    {
        "id": "plate_bhd_wt",
        "name": "Transverse Watertight Bulkhead Plating",
        "category": "GROUP 6: WATERTIGHT BULKHEADS & TANKS",
        "type": "plate",
        "table_ref": "Table 26",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 6.5,
        "bound_plate_key": "t_bhd",
        "unit": "mm",
        "notes": "Rule 40, Table 26 - Transverse watertight subdivision bulkhead",
        "desc": "Transverse Watertight Bulkhead Plating",
        "group": "GROUP 6: WATERTIGHT BULKHEADS & TANKS"
    },
    {
        "id": "plate_bhd_collision",
        "name": "Collision & Aft Peak Bulkhead Plating",
        "category": "GROUP 6: WATERTIGHT BULKHEADS & TANKS",
        "type": "plate",
        "table_ref": "Table 25",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 7.5,
        "bound_plate_key": "t_bhd_collision",
        "unit": "mm",
        "notes": "Rule 39, Table 25 - Heavy collision bulkhead plating",
        "desc": "Collision & Aft Peak Bulkhead Plating",
        "group": "GROUP 6: WATERTIGHT BULKHEADS & TANKS"
    },
    {
        "id": "plate_bhd_tank",
        "name": "Deep Tank Bulkhead Plating",
        "category": "GROUP 6: WATERTIGHT BULKHEADS & TANKS",
        "type": "plate",
        "table_ref": "Table 27",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Oil Tanker",
            "all"
        ],
        "baseline": 7.5,
        "bound_plate_key": "t_tank_bhd",
        "unit": "mm",
        "notes": "Rule 44, Table 27 - Boundary plating for liquid cargo & fuel deep tanks",
        "desc": "Deep Tank Bulkhead Plating",
        "group": "GROUP 6: WATERTIGHT BULKHEADS & TANKS"
    },
    {
        "id": "plate_long_bhd",
        "name": "Longitudinal Bulkhead Plating",
        "category": "GROUP 6: WATERTIGHT BULKHEADS & TANKS",
        "type": "plate",
        "table_ref": "Table 27",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Oil Tanker"
        ],
        "baseline": 7.5,
        "bound_plate_key": "t_long_bhd",
        "unit": "mm",
        "notes": "Table 27 - Centreline liquid tight longitudinal bulkhead in tankers",
        "desc": "Longitudinal Bulkhead Plating",
        "group": "GROUP 6: WATERTIGHT BULKHEADS & TANKS"
    },
    {
        "id": "plate_tank_boundary",
        "name": "Tank Boundary Plating",
        "category": "GROUP 6: WATERTIGHT BULKHEADS & TANKS",
        "type": "plate",
        "table_ref": "Table 27",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 7.0,
        "bound_plate_key": "t_tank_boundary",
        "unit": "mm",
        "notes": "Table 27 - Watertight boundary plating enclosing fuel/water double bottom tanks",
        "desc": "Tank Boundary Plating",
        "group": "GROUP 6: WATERTIGHT BULKHEADS & TANKS"
    },
    {
        "id": "plate_cofferdam",
        "name": "Cofferdam Bulkhead Plating",
        "category": "GROUP 6: WATERTIGHT BULKHEADS & TANKS",
        "type": "plate",
        "table_ref": "Table 26",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Oil Tanker"
        ],
        "baseline": 6.5,
        "bound_plate_key": "t_cofferdam",
        "unit": "mm",
        "notes": "Table 26 - Dry void isolating bulkhead separating cargo tanks from machinery",
        "desc": "Cofferdam Bulkhead Plating",
        "group": "GROUP 6: WATERTIGHT BULKHEADS & TANKS"
    },
    {
        "id": "plate_pump_room_bhd",
        "name": "Pump Room Bulkhead Plating",
        "category": "GROUP 6: WATERTIGHT BULKHEADS & TANKS",
        "type": "plate",
        "table_ref": "Table 26",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Oil Tanker"
        ],
        "baseline": 6.5,
        "bound_plate_key": "t_pump_room_bhd",
        "unit": "mm",
        "notes": "Table 26 - Gastight and watertight boundary enclosing cargo pump room",
        "desc": "Pump Room Bulkhead Plating",
        "group": "GROUP 6: WATERTIGHT BULKHEADS & TANKS"
    },
    {
        "id": "plate_wash_bhd",
        "name": "Wash Bulkhead Plating",
        "category": "GROUP 6: WATERTIGHT BULKHEADS & TANKS",
        "type": "plate",
        "table_ref": "Table 27",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Oil Tanker"
        ],
        "baseline": 6.5,
        "bound_plate_key": "t_wash_bhd",
        "unit": "mm",
        "notes": "Table 27 - Perforated anti-sloshing wash bulkhead plating in cargo tanks",
        "desc": "Wash Bulkhead Plating",
        "group": "GROUP 6: WATERTIGHT BULKHEADS & TANKS"
    },
    {
        "id": "plate_chain_locker_wall",
        "name": "Bow Chain Locker Wall Plating",
        "category": "GROUP 6: WATERTIGHT BULKHEADS & TANKS",
        "type": "plate",
        "table_ref": "Table 48",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 6.0,
        "bound_plate_key": "t_chain_locker",
        "unit": "mm",
        "notes": "Table 48 - Heavy wear plate enclosing forward anchor chain locker",
        "desc": "Bow Chain Locker Wall Plating",
        "group": "GROUP 6: WATERTIGHT BULKHEADS & TANKS"
    },
    {
        "id": "stiff_bhd_transverse",
        "name": "Watertight Bulkhead Vertical Stiffeners",
        "category": "GROUP 6: WATERTIGHT BULKHEADS & TANKS",
        "type": "stiffener",
        "table_ref": "Table 26, Table 25",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 115.0,
        "unit": "cm3",
        "welded_on_plate": "Transverse Watertight Bulkhead Plating",
        "welded_plate_key": "t_bhd",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 125,
            "web_thk": 9.0,
            "flange_width": 75,
            "flange_thk": 9.0
        },
        "notes": "Rule 40, Table 26 - Vertical stiffeners on watertight bulkheads",
        "desc": "Watertight Bulkhead Vertical Stiffeners",
        "group": "GROUP 6: WATERTIGHT BULKHEADS & TANKS"
    },
    {
        "id": "stiff_tank_bhd_stringer",
        "name": "Tank Bulkhead Horizontal Stringer",
        "category": "GROUP 6: WATERTIGHT BULKHEADS & TANKS",
        "type": "stiffener",
        "table_ref": "Table 28, Table 53",
        "applicable_hull_types": [
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Oil Tanker",
            "all"
        ],
        "baseline": 250.0,
        "unit": "cm3",
        "welded_on_plate": "Deep Tank Bulkhead Plating",
        "welded_plate_key": "t_tank_bhd",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 250,
            "web_thk": 10.0,
            "flange_width": 90,
            "flange_thk": 10.0
        },
        "notes": "Table 28 & 53 - Horizontal girder on cargo tank bulkheads",
        "desc": "Tank Bulkhead Horizontal Stringer",
        "group": "GROUP 6: WATERTIGHT BULKHEADS & TANKS"
    },
    {
        "id": "stiff_tank_bhd_web",
        "name": "Tank Bulkhead Vertical Web",
        "category": "GROUP 6: WATERTIGHT BULKHEADS & TANKS",
        "type": "stiffener",
        "table_ref": "Table 28, Table 53",
        "applicable_hull_types": [
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Oil Tanker"
        ],
        "baseline": 350.0,
        "unit": "cm3",
        "welded_on_plate": "Deep Tank Bulkhead Plating",
        "welded_plate_key": "t_tank_bhd",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 300,
            "web_thk": 10.0,
            "flange_width": 100,
            "flange_thk": 10.0
        },
        "notes": "Table 28 & 53 - Deep vertical web stiffener on tank transverse bulkhead",
        "desc": "Tank Bulkhead Vertical Web",
        "group": "GROUP 6: WATERTIGHT BULKHEADS & TANKS"
    },
    {
        "id": "plate_coaming_long",
        "name": "Longitudinal Hatch Coaming Plating",
        "category": "GROUP 7: HATCHWAYS, COAMINGS & COVERS",
        "type": "plate",
        "table_ref": "Table 30, Table 31",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Container",
            "Barge"
        ],
        "baseline": 9.0,
        "bound_plate_key": "t_coaming",
        "unit": "mm",
        "notes": "Rule 46, Table 30 & 31 - Side continuous hatch coaming plating",
        "desc": "Longitudinal Hatch Coaming Plating",
        "group": "GROUP 7: HATCHWAYS, COAMINGS & COVERS"
    },
    {
        "id": "plate_coaming_trans",
        "name": "Transverse Hatch Coaming Plating",
        "category": "GROUP 7: HATCHWAYS, COAMINGS & COVERS",
        "type": "plate",
        "table_ref": "Table 30, Table 31",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Container",
            "Barge"
        ],
        "baseline": 9.0,
        "bound_plate_key": "t_coaming",
        "unit": "mm",
        "notes": "Rule 46, Table 30 & 31 - Forward & aft hatch end coaming plating",
        "desc": "Transverse Hatch Coaming Plating",
        "group": "GROUP 7: HATCHWAYS, COAMINGS & COVERS"
    },
    {
        "id": "stiff_coaming_stay",
        "name": "Hatch Coaming Stay Bracket",
        "category": "GROUP 7: HATCHWAYS, COAMINGS & COVERS",
        "type": "dimension",
        "table_ref": "Table 52",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Container",
            "Steel Body Cargo Vessel",
            "Barge"
        ],
        "baseline": 300.0,
        "unit": "mm",
        "notes": "Table 52 - Outboard triangular stay supporting vertical coaming plate",
        "desc": "Hatch Coaming Stay Bracket",
        "group": "GROUP 7: HATCHWAYS, COAMINGS & COVERS"
    },
    {
        "id": "stiff_hatch_end_beam",
        "name": "Cargo Hatchway Transverse Beams",
        "category": "GROUP 7: HATCHWAYS, COAMINGS & COVERS",
        "type": "stiffener",
        "table_ref": "Table 33(a), Table 33(b)",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Container",
            "Barge"
        ],
        "baseline": 650.0,
        "unit": "cm3",
        "welded_on_plate": "Strength Deck at Hatchways",
        "welded_plate_key": "t_deck_hatch",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 350,
            "web_thk": 11.0,
            "flange_width": 120,
            "flange_thk": 12.0
        },
        "notes": "Rule 46, Table 33(a/b) - Heavy transverse beam at hatch ends",
        "desc": "Cargo Hatchway Transverse Beams",
        "group": "GROUP 7: HATCHWAYS, COAMINGS & COVERS"
    },
    {
        "id": "stiff_hatch_side_girder",
        "name": "Cargo Hatchway Side Longitudinal Beams",
        "category": "GROUP 7: HATCHWAYS, COAMINGS & COVERS",
        "type": "stiffener",
        "table_ref": "Table 21, Table 37",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Container",
            "Barge"
        ],
        "baseline": 850.0,
        "unit": "cm3",
        "welded_on_plate": "Strength Deck at Hatchways",
        "welded_plate_key": "t_deck_hatch",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 400,
            "web_thk": 12.0,
            "flange_width": 140,
            "flange_thk": 14.0
        },
        "notes": "Rule 46, Table 21 & 37 - Heavy longitudinal girder under hatch coaming",
        "desc": "Cargo Hatchway Side Longitudinal Beams",
        "group": "GROUP 7: HATCHWAYS, COAMINGS & COVERS"
    },
    {
        "id": "stiff_portable_hatch_beam",
        "name": "Portable Removable Hatch Beam",
        "category": "GROUP 7: HATCHWAYS, COAMINGS & COVERS",
        "type": "stiffener",
        "table_ref": "Table 32",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Barge"
        ],
        "baseline": 420.0,
        "unit": "cm3",
        "welded_on_plate": "Main Strength Deck Plating",
        "welded_plate_key": "t_deck_all",
        "default_profile": {
            "profile_type": "T",
            "web_depth": 300,
            "web_thk": 10.0,
            "flange_width": 100,
            "flange_thk": 12.0
        },
        "notes": "Table 32 - Removable web beams seated in coaming sockets",
        "desc": "Portable Removable Hatch Beam",
        "group": "GROUP 7: HATCHWAYS, COAMINGS & COVERS"
    },
    {
        "id": "stiff_hatch_cover",
        "name": "Steel Hatch Cover Stiffeners",
        "category": "GROUP 7: HATCHWAYS, COAMINGS & COVERS",
        "type": "stiffener",
        "table_ref": "Table 34",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "Steel Body Cargo Vessel",
            "Container",
            "Barge"
        ],
        "baseline": 75.0,
        "unit": "cm3",
        "welded_on_plate": "Main Strength Deck Plating",
        "welded_plate_key": "t_deck_all",
        "default_profile": {
            "profile_type": "L",
            "web_depth": 100,
            "web_thk": 8.0,
            "flange_width": 65,
            "flange_thk": 8.0
        },
        "notes": "Rule 46, Table 34 - Stiffeners on pontoon / folding steel hatch covers",
        "desc": "Steel Hatch Cover Stiffeners",
        "group": "GROUP 7: HATCHWAYS, COAMINGS & COVERS"
    },
    {
        "id": "plate_machinery_casing",
        "name": "Machinery Casing Plating",
        "category": "GROUP 8: MACHINERY CASINGS & SEATINGS",
        "type": "plate",
        "table_ref": "Rule 56",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 5.0,
        "unit": "mm",
        "notes": "Rule 56 - Engine casing boundary plate above weather deck",
        "desc": "Machinery Casing Plating",
        "group": "GROUP 8: MACHINERY CASINGS & SEATINGS"
    },
    {
        "id": "plate_engine_bedplate",
        "name": "Engine Foundation Top Plate",
        "category": "GROUP 8: MACHINERY CASINGS & SEATINGS",
        "type": "plate",
        "table_ref": "Rule 56",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 19.0,
        "unit": "mm",
        "notes": "Rule 56 - Main engine sole plate thickness",
        "desc": "Engine Foundation Top Plate",
        "group": "GROUP 8: MACHINERY CASINGS & SEATINGS"
    },
    {
        "id": "plate_engine_girders",
        "name": "Engine Foundation Longitudinal Girders",
        "category": "GROUP 8: MACHINERY CASINGS & SEATINGS",
        "type": "plate",
        "table_ref": "Rule 56",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 12.0,
        "unit": "mm",
        "notes": "Rule 56 - Heavy foundation girder web thickness",
        "desc": "Engine Foundation Longitudinal Girders",
        "group": "GROUP 8: MACHINERY CASINGS & SEATINGS"
    },
    {
        "id": "bulwark_height",
        "name": "Bulwark Minimum Height",
        "category": "GROUP 9: BULWARKS & FREEING PORTS",
        "type": "dimension",
        "table_ref": "Rule 59",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 1000.0,
        "unit": "mm",
        "notes": "Rule 59/83 - Minimum 1000 mm safety height",
        "desc": "Bulwark Minimum Height",
        "group": "GROUP 9: BULWARKS & FREEING PORTS"
    },
    {
        "id": "plate_bulwark",
        "name": "Bulwark Plating Thickness",
        "category": "GROUP 9: BULWARKS & FREEING PORTS",
        "type": "plate",
        "table_ref": "Table 47",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 5.99,
        "bound_plate_key": "t_bulwark",
        "unit": "mm",
        "notes": "Rule 59, Table 47 - Weather deck bulwark plating",
        "desc": "Bulwark Plating Thickness",
        "group": "GROUP 9: BULWARKS & FREEING PORTS"
    },
    {
        "id": "freeing_port_area",
        "name": "Freeing Port Total Area per Side",
        "category": "GROUP 9: BULWARKS & FREEING PORTS",
        "type": "dimension",
        "table_ref": "Rule 60",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 4.54,
        "unit": "m2",
        "notes": "Rule 60 - Rapid deck water clearance drainage area",
        "desc": "Freeing Port Total Area per Side",
        "group": "GROUP 9: BULWARKS & FREEING PORTS"
    },
    {
        "id": "equipment_number",
        "name": "Equipment Number Z Calculation",
        "category": "GROUP 10: EQUIPMENT NUMBER, ANCHORS & CABLES",
        "type": "dimension",
        "table_ref": "Rule 79",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 420.0,
        "unit": "Z",
        "notes": "Rule 79: \u0394^(2/3) + 2*B*h + A/10",
        "desc": "Equipment Number Z Calculation",
        "group": "GROUP 10: EQUIPMENT NUMBER, ANCHORS & CABLES"
    },
    {
        "id": "anchor_mass",
        "name": "Bower Anchor Mass",
        "category": "GROUP 10: EQUIPMENT NUMBER, ANCHORS & CABLES",
        "type": "equipment",
        "table_ref": "Table 45",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 660.0,
        "unit": "kg",
        "notes": "Rule 80, Table 45 - Mass of bower anchor",
        "desc": "Bower Anchor Mass",
        "group": "GROUP 10: EQUIPMENT NUMBER, ANCHORS & CABLES"
    },
    {
        "id": "chain_cable_length",
        "name": "Stud Link Chain Cable Total Length",
        "category": "GROUP 10: EQUIPMENT NUMBER, ANCHORS & CABLES",
        "type": "equipment",
        "table_ref": "Table 46",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 275.0,
        "unit": "m",
        "notes": "Rule 81, Table 46 - Total length of anchor chain",
        "desc": "Stud Link Chain Cable Total Length",
        "group": "GROUP 10: EQUIPMENT NUMBER, ANCHORS & CABLES"
    },
    {
        "id": "shaft_intermediate_dia",
        "name": "Intermediate Shaft Diameter",
        "category": "GROUP 11: MACHINERY SHAFTING & BEARINGS",
        "type": "dimension",
        "table_ref": "Table 54",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 85.0,
        "unit": "mm",
        "notes": "Rule 87, Table 54 - Rule intermediate line shaft diameter",
        "desc": "Intermediate Shaft Diameter",
        "group": "GROUP 11: MACHINERY SHAFTING & BEARINGS"
    },
    {
        "id": "shaft_thrust_dia",
        "name": "Thrust Shaft Diameter",
        "category": "GROUP 11: MACHINERY SHAFTING & BEARINGS",
        "type": "dimension",
        "table_ref": "Table 55",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 95.0,
        "unit": "mm",
        "notes": "Rule 88, Table 55 - Rule thrust collar shaft diameter",
        "desc": "Thrust Shaft Diameter",
        "group": "GROUP 11: MACHINERY SHAFTING & BEARINGS"
    },
    {
        "id": "shaft_propeller_dia",
        "name": "Propeller Shaft Diameter",
        "category": "GROUP 11: MACHINERY SHAFTING & BEARINGS",
        "type": "dimension",
        "table_ref": "Table 56",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 105.0,
        "unit": "mm",
        "notes": "Rule 89, Table 56 - Heavy tailshaft diameter",
        "desc": "Propeller Shaft Diameter",
        "group": "GROUP 11: MACHINERY SHAFTING & BEARINGS"
    },
    {
        "id": "pipe_main_bilge_dia",
        "name": "Main Bilge Suction Pipe Diameter",
        "category": "GROUP 12: PIPING & PUMPING SYSTEMS",
        "type": "dimension",
        "table_ref": "Table 61",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 65.0,
        "unit": "mm",
        "notes": "Rule 96/142, Table 61 - Machinery space bilge main",
        "desc": "Main Bilge Suction Pipe Diameter",
        "group": "GROUP 12: PIPING & PUMPING SYSTEMS"
    },
    {
        "id": "pipe_branch_bilge_dia",
        "name": "Branch Bilge Suction Pipe Diameter",
        "category": "GROUP 12: PIPING & PUMPING SYSTEMS",
        "type": "dimension",
        "table_ref": "Table 61",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 50.0,
        "unit": "mm",
        "notes": "Rule 96/142, Table 61 - Hold suction branch pipes",
        "desc": "Branch Bilge Suction Pipe Diameter",
        "group": "GROUP 12: PIPING & PUMPING SYSTEMS"
    },
    {
        "id": "pipe_wall_thk",
        "name": "Bilge & Ballast Pipe Wall Thickness",
        "category": "GROUP 12: PIPING & PUMPING SYSTEMS",
        "type": "dimension",
        "table_ref": "Table 62",
        "applicable_hull_types": [
            "Single Hull",
            "Double Bottom",
            "Double Hull"
        ],
        "applicable_vessel_types": [
            "all"
        ],
        "baseline": 4.5,
        "unit": "mm",
        "notes": "Rule 97, Table 62 - Steel suction pipe wall",
        "desc": "Bilge & Ballast Pipe Wall Thickness",
        "group": "GROUP 12: PIPING & PUMPING SYSTEMS"
    }
]


def get_active_members(hull_type: str = "Double Bottom", vessel_type: str = "Steel Body Cargo Vessel"):
    """
    Returns the list of active structural members based on hull_type and vessel_type.
    """
    h_clean = "Double Bottom"
    if "single" in (hull_type or "").lower():
        h_clean = "Single Hull"
    elif "double hull" in (hull_type or "").lower():
        h_clean = "Double Hull"

    v_clean = vessel_type or "Steel Body Cargo Vessel"

    active = []
    item_counter = 1
    for m in STRUCTURAL_MEMBERS:
        # Check hull type
        h_app = m.get("applicable_hull_types", ["all"])
        if "all" not in h_app and h_clean not in h_app:
            continue

        # Check vessel type
        v_app = m.get("applicable_vessel_types", ["all"])
        if "all" not in v_app and v_clean not in v_app:
            continue

        item_copy = dict(m)
        item_copy["item"] = item_counter
        item_copy["desc"] = m.get("desc") or m.get("name")
        item_copy["group"] = m.get("group") or m.get("category")
        item_counter += 1
        active.append(item_copy)

    return active

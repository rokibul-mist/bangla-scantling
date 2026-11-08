import sys
import copy
sys.path.insert(0, '.')

from app.services.vessel_service import VesselService
from app.repositories.state_repository import StateRepository

state_repo = StateRepository()
vessel_service = VesselService()

master_state = state_repo.get_state()

# 1. Flagship Cargo Vessel
vessel_service.save_vessel_from_state(
    master_state,
    vessel_id="vsl_crown_mariners_67",
    custom_meta={
        "vessel_name": "M.V. CROWN MARINERS - 67",
        "owner": "Crown Navigation Ltd.",
        "yard_ref": "YD-2026/089",
        "notes": "Flagship 69.85m Steel Cargo Vessel fully evaluated per Bangladesh Inland Shipping Rules 2001 & SRO 308/2001."
    }
)

# 2. Oil Tanker Model
tanker_state = copy.deepcopy(master_state)
tanker_state['dashboard_inputs'].update({
    'vessel_name': 'M.V. KARNAPHULI OIL - 12',
    'vessel_type': 'Oil Tanker',
    'hull_type': 'Double Bottom',
    'route': 'Inland route',
    'lbp': 72.50,
    'breadth': 12.80,
    'depth': 5.20,
    'draft': 3.90,
    'cb': 0.78,
    'frame_spacing': 550.0,
    'speed': 10.5,
    't_keel': 14.0,
    't_bottom': 12.5,
    't_bilge': 13.5,
    't_side': 12.0,
    't_inner_bottom': 12.0
})
vessel_service.save_vessel_from_state(
    tanker_state,
    vessel_id="vsl_karnaphuli_oil_12",
    custom_meta={
        "vessel_name": "M.V. KARNAPHULI OIL - 12",
        "owner": "Karnaphuli Petroleum Lines Ltd.",
        "yard_ref": "KPL-TK-2025/04",
        "notes": "Double Bottom Oil Tanker designed for inland carriage of Class B & C petroleum products."
    }
)

# 3. Passenger Ferry Model
ferry_state = copy.deepcopy(master_state)
ferry_state['dashboard_inputs'].update({
    'vessel_name': 'M.V. MEGHNA EXPRESS - 05',
    'vessel_type': 'Ferry',
    'hull_type': 'Single Hull',
    'route': 'Inland route',
    'lbp': 52.00,
    'breadth': 9.80,
    'depth': 3.80,
    'draft': 2.40,
    'cb': 0.70,
    'frame_spacing': 500.0,
    'speed': 12.0,
    't_keel': 11.0,
    't_bottom': 9.5,
    't_bilge': 10.0,
    't_side': 9.0,
    't_deck_all': 8.0
})
vessel_service.save_vessel_from_state(
    ferry_state,
    vessel_id="vsl_meghna_express_05",
    custom_meta={
        "vessel_name": "M.V. MEGHNA EXPRESS - 05",
        "owner": "Meghna Inland Waterways Co.",
        "yard_ref": "MIW-F-2026/01",
        "notes": "High capacity coastal-inland passenger & vehicle ferry operating Dhaka - Barishal route."
    }
)

print("Default vessels seeded successfully.")
for v in vessel_service.list_vessels():
    print(f"- {v['vessel_name']} ({v['vessel_type']}): Lightship={v.get('results_summary', {}).get('lightship_tonnes')} T")

import sys
import json
sys.path.insert(0, '.')

from app.domain.catalog.structural_catalog import get_active_members
from app.domain.rules.interpolations.registry import TableInterpolationRegistry

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

inputs = state.get('dashboard_inputs', {})
hull_type = inputs.get('hull_type', 'Single Hull')
vessel_type = inputs.get('vessel_type', 'Steel Body Cargo Vessel')

active_members = get_active_members(hull_type, vessel_type)
stern_m = next((m for m in active_members if m['id'] == 'stern_frame_bar'), None)
print("stern_m in active_members:", stern_m is not None)
if stern_m:
    print("stern_m baseline before:", stern_m.get('baseline'))
    res = TableInterpolationRegistry.interpolate_member('stern_frame_bar', inputs)
    print("res:", res.rreq if res else None)

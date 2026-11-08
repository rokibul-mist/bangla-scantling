import sys
sys.path.insert(0, '.')
from app.domain.catalog.structural_catalog import STRUCTURAL_MEMBERS

for m in STRUCTURAL_MEMBERS:
    if m.get('type') == 'stiffener':
        d_prof = m.get('default_profile') or {}
        print(f"{m['id']}: name={m['name']}, ptype={d_prof.get('profile_type')}, hw={d_prof.get('web_depth')}, tw={d_prof.get('web_thk')}, bf={d_prof.get('flange_width')}, tf={d_prof.get('flange_thk')}")

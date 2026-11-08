import sys
import json
sys.path.insert(0, '.')

from app.services.calculation_service import CalculationService

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

print("Computing calculations...")
updated_state = CalculationService.compute_all_calculations(state)

with open('app/saved_state.json', 'w', encoding='utf-8') as f:
    json.dump(updated_state, f, indent=2)

print("Successfully recomputed state and saved app/saved_state.json")
s2 = updated_state.get('sheet2_results', [])
for item in s2[:5]:
    print(f"Sheet {item.get('id')}: {item.get('member_id')} ({item.get('name')}) -> ptype={item.get('profile_type')}, hw={item.get('web_height')}, bf={item.get('flange_width')}")

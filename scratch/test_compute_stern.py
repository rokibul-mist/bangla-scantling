import sys
import json
sys.path.insert(0, '.')

from app.services.calculation_service import CalculationService

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

new_state = CalculationService.compute_all_calculations(state)
for m in new_state['calculation_brain']:
    if m['id'] == 'stern_frame_bar':
        print("AFTER COMPUTE: rreq =", m['rreq'], "baseline =", m['baseline'], "derivation =", m.get('derivation'))

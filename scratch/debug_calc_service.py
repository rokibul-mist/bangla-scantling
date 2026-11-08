import sys
import json
sys.path.insert(0, '.')

from app.services.calculation_service import CalculationService

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

# Let's inspect what happens during compute_all_calculations
inputs = state.get('dashboard_inputs', {})
print("dashboard_inputs lbp:", inputs.get('lbp'), "L:", inputs.get('L'))

from app.domain.rules.interpolations.registry import TableInterpolationRegistry
res = TableInterpolationRegistry.interpolate_member('stern_frame_bar', inputs)
print("direct interp res:", res.rreq if res else None)

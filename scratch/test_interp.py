import sys
sys.path.insert(0, '.')
from app.domain.rules.interpolations.registry import TableInterpolationRegistry

print("Registered stern_frame_bar:", TableInterpolationRegistry.REGISTRY.get('stern_frame_bar'))

calc_inputs = {
    'lbp': 69.85, 'length': 69.85, 'L': 69.85,
    'breadth': 13.41, 'B': 13.41,
    'depth': 5.18, 'D': 5.18,
    'draft': 4.0, 'd': 4.0,
    'cb': 0.75, 'Cb': 0.75,
    'frame_spacing': 550.0, 'spacing': 550.0,
    'effective_kt': 1.0, 'effective_kz': 1.0,
    'kt': 1.0, 'kz': 1.0,
    'is_single_hull': True,
}
res = TableInterpolationRegistry.interpolate_member('stern_frame_bar', calc_inputs)
print("Result:", res)

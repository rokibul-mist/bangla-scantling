import json

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

c_dims = state.get('stiffener_custom_dims', {})
print("stiff_centre_keelson:", c_dims.get('stiff_centre_keelson'))
print("stiff_side_keelson:", c_dims.get('stiff_side_keelson'))
print("stiff_floor_single:", c_dims.get('stiff_floor_single'))

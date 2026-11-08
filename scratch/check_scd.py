import json

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

scd = state.get('stiffener_custom_dims', {})
print("stiffener_custom_dims keys count:", len(scd))
for k, v in scd.items():
    print(f"{k}: {v}")

import json

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

for m in state.get('calculation_brain', []):
    if m['id'] in ['plate_main_deck', 'plate_bulwark']:
        print(m['id'], "baseline:", m.get('baseline'), "rreq:", m.get('rreq'), "factor:", m.get('factor'))

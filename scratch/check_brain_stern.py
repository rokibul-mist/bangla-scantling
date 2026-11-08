import json

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

for item in state.get('calculation_brain', []):
    if 'stern' in item.get('id', '').lower():
        print("calculation_brain stern item:", item.get('id'), "rreq:", item.get('rreq'), "dact:", item.get('dact'), "baseline:", item.get('baseline'))

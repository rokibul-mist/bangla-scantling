import json
with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)
for m in state.get('calculation_brain', []):
    if m['id'] == 'stern_frame_bar':
        print("ON DISK: rreq =", m['rreq'])

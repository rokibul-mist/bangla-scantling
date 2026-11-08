import json

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

for m in state.get('scantling_members', []):
    if m.get('id') == 'stern_frame_bar':
        print("scantling_members stern_frame_bar:", m)

for c in state.get('scantling_checklist', []):
    if 'stern' in c.get('item', '').lower():
        print("checklist stern:", c)

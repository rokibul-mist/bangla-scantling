import json

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

for k, v in state.items():
    if isinstance(v, dict):
        if 'stern_frame_bar' in v:
            print(f"In dict {k}: stern_frame_bar = {v['stern_frame_bar']}")
    elif isinstance(v, list):
        for idx, item in enumerate(v):
            if isinstance(item, dict) and item.get('id') == 'stern_frame_bar':
                print(f"In list {k}[{idx}]: item = {item}")

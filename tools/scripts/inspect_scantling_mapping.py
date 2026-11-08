import json

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

scantlings = state.get('scantlings', [])
print(f"Total scantlings in state: {len(scantlings)}")
for s in scantlings:
    print(f"[{s.get('id')}] {s.get('name')} | req: {s.get('required')} | prov: {s.get('provided')} | type: {s.get('type')}")

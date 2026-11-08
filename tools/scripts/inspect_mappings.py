import json, re

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

cb = state.get('calculation_brain', [])
s2 = state.get('sheet2_results', [])

print("Calculation Brain items:")
for item in cb:
    print(f"  [{item.get('id')}] {item.get('name')}: Req={item.get('rreq')}, Prov={item.get('dact')} {item.get('unit')}")

print("\nSheet 2 items:")
for item in s2:
    print(f"  [{item.get('member_id')}] {item.get('name')}: Req={item.get('rreq')}, Prov Z={item.get('z_cm3'):.2f} cm3")

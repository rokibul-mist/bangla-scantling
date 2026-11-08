import json

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

s2 = state.get('sheet2_results', [])
print(f"Total sheet2 results: {len(s2)}")
for item in s2[:10]:
    print(f"Sheet {item.get('id')}: {item.get('member_id')} ({item.get('name')}) -> profile_type={item.get('profile_type')}, flange_width={item.get('flange_width')}")

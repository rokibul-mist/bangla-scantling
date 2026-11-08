import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

# 1. Print all sheet2_results members
s2 = state.get('sheet2_results', [])
print(f"Total sheet2 members: {len(s2)}")
for s in s2:
    print(f"Sheet {s.get('id', 0):2d}: id='{s.get('member_id')}', name='{s.get('name')}', rule_ref='{s.get('table_ref')}'")

# 2. Extract all numbered items from application form pages
pages = state.get('application_form_pages', [])
print(f"\n--- Application Form Numbered Items ---")
import re
for p_idx, page in enumerate(pages):
    for row in page.get('content', []):
        text = row.get('text', '').strip()
        m = re.match(r'^(\d+)\.\s+(.*)', text)
        if m:
            print(f"Page {p_idx+1:2d} | Item {m.group(1):>3s}: {m.group(2)[:80]}")

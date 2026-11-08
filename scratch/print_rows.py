import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

for page in state.get('application_form_pages', []):
    for row in page.get('content', []):
        r_num = row.get('row')
        if 344 <= r_num <= 348:
            print(f"row {r_num}: {row.get('text')}")
            for c in row.get('cells', []):
                print(f"   col {c.get('col')}: {c.get('val')}")

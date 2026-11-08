import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

pages = state.get('application_form_pages', [])
for p_idx, page in enumerate(pages):
    for row in page.get('content', []):
        text = row.get('text', '')
        for term in ['keelson', 'frame', 'floor', 'beam', 'girder', 'stringer']:
            if term in text.lower():
                print(f"Page {p_idx+1}: row {row.get('row')}: {text}")

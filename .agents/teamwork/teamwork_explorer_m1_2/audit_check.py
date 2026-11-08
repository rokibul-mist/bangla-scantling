import sys, os
sys.path.insert(0, os.path.abspath('.'))
import json
from app.services.pdf.app_form_pdf_service import parse_audit_page_items, get_calc_lookup

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

lookup = get_calc_lookup(state)
pages = state.get('application_form_pages', [])
total_items = 0
for i, page in enumerate(pages):
    content = page.get('content', [])
    if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict) and 'cells' in content[0]:
        items = parse_audit_page_items(content, lookup)
        total_items += len(items)
        if len(items) > 0:
            nums = [it.get('num') for it in items]
            print(f"Page {i+1} has {len(items)} items: {nums}")

print(f"Total audit items across booklet: {total_items}")

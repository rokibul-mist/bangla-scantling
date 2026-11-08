import sys
import json
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

from app.services.pdf.app_form_pdf_service import parse_audit_page_items, get_calc_lookup

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

lookup = get_calc_lookup(state)
pages = state.get('application_form_pages', [])
for p_idx, p in enumerate(pages):
    items = parse_audit_page_items(p.get('content', []), lookup)
    for it in items:
        if it.get('num') == '18':
            print(f"Page {p_idx}: title={it.get('title')}, lines={it.get('lines')}")

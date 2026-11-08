import sys
sys.path.insert(0, '.')
import json
from app.services.pdf.app_form_pdf_service import parse_audit_page_items, get_calc_lookup

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

lookup = get_calc_lookup(state)
p9 = state.get('application_form_pages', [])[9]
for r in p9.get('content', []):
    print(r.get('row'), r.get('text'))

import sys
sys.path.insert(0, '.')
import json
from app.services.pdf.app_form_pdf_service import get_calc_lookup

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

lookup = get_calc_lookup(state)
print("stern_frame_bar:", lookup.get('stern_frame_bar'))
print("bar_stem:", lookup.get('bar_stem'))
print("plate_stem:", lookup.get('plate_stem'))

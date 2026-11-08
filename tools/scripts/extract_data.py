import openpyxl
import json
import os

def clean_val(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return v
    s = str(v).strip()
    return s

wb = openpyxl.load_workbook('Master Form-Final--UserFriendly.xlsx', data_only=True)

# 1. Dashboard Inputs
ws_db = wb['Dashboard']
dashboard_inputs = {
    'vessel_name': clean_val(ws_db['C3'].value),
    'vessel_type': clean_val(ws_db['F3'].value),
    'route': clean_val(ws_db['L3'].value),
    'loa': clean_val(ws_db['C4'].value),
    'lbp': clean_val(ws_db['F4'].value),
    'breadth': clean_val(ws_db['C5'].value),
    'depth': clean_val(ws_db['F5'].value),
    'draft': clean_val(ws_db['C6'].value),
    'displacement': clean_val(ws_db['F6'].value),
    'block_coeff': clean_val(ws_db['C7'].value),
    'frame_spacing': clean_val(ws_db['F7'].value),
    'power': clean_val(ws_db['C8'].value),
    'prop_dia': clean_val(ws_db['F8'].value),
    'owner': clean_val(ws_db['C9'].value),
    'designer_name': clean_val(ws_db['F9'].value),
    'owner_reg': clean_val(ws_db['C10'].value),
    'designer_firm': clean_val(ws_db['F10'].value),
    'route_factor_input': clean_val(ws_db['I5'].value) or 1.4,
    'modulus_factor_input': clean_val(ws_db['I6'].value) or 1.4,
    # Col N & O
    'lwl': clean_val(ws_db['O3'].value) or 53.61,
    'b_ext': clean_val(ws_db['O4'].value) or 9.52,
    'depth_ext': clean_val(ws_db['O5'].value) or 4.52,
    'propeller_nos': clean_val(ws_db['O6'].value) or 2,
    'engine_type': clean_val(ws_db['O7'].value) or "MARINE DIESEL ENGINE",
    'checked_by': clean_val(ws_db['O8'].value) or "AMITAVO CHOWDHURY WYE",
    'firm_address': clean_val(ws_db['O9'].value) or "128, Malek Mansion, Motijheel C/A, Dhaka-1000",
    'hull_material': clean_val(ws_db['O10'].value) or "Steel (old)",
    'plying_time': clean_val(ws_db['O11'].value) or "Day & Night",
    'owner_so': clean_val(ws_db['O12'].value) or "S/O ABDUS SOBAN KHALASHI",
    'owner_address': clean_val(ws_db['O13'].value) or "Satbhita, Narisha, Dohar, Dhaka",
    'double_bottom_inner_plate': 14.0 # Resolved from backup
}

# 2. Stiffener Profile Dimensions (Inputs in rows 40-49)
stiffener_profiles = []
for r in range(40, 50):
    stiffener_profiles.append({
        'id': clean_val(ws_db.cell(r, 2).value),
        'name': clean_val(ws_db.cell(r, 3).value),
        'web_depth': clean_val(ws_db.cell(r, 5).value),
        'web_thk': clean_val(ws_db.cell(r, 6).value),
        'flange_width': clean_val(ws_db.cell(r, 7).value),
        'flange_thk': clean_val(ws_db.cell(r, 8).value),
        'derived_sm': clean_val(ws_db.cell(r, 9).value),
        'unit': 'cm3',
        'ref': clean_val(ws_db.cell(r, 12).value)
    })

# 3. Provided Values and Scantling Checklist (Rows 15-34)
scantling_checklist = []
for r in range(15, 35):
    scantling_checklist.append({
        'no': clean_val(ws_db.cell(r, 2).value),
        'description': clean_val(ws_db.cell(r, 3).value),
        'rule': clean_val(ws_db.cell(r, 4).value),
        'baseline': clean_val(ws_db.cell(r, 5).value),
        'factor': clean_val(ws_db.cell(r, 6).value),
        'required': clean_val(ws_db.cell(r, 7).value),
        'provided': clean_val(ws_db.cell(r, 8).value),
        'unit': clean_val(ws_db.cell(r, 9).value),
        'margin': clean_val(ws_db.cell(r, 10).value),
        'margin_pct': clean_val(ws_db.cell(r, 11).value),
        'status': clean_val(ws_db.cell(r, 12).value)
    })

# 4. Propulsion (Rows 54-55)
propulsion_items = []
for r in range(54, 56):
    propulsion_items.append({
        'no': clean_val(ws_db.cell(r, 2).value),
        'item': clean_val(ws_db.cell(r, 3).value),
        'rule': clean_val(ws_db.cell(r, 4).value),
        'baseline': clean_val(ws_db.cell(r, 5).value),
        'factor': clean_val(ws_db.cell(r, 6).value),
        'required': clean_val(ws_db.cell(r, 7).value),
        'provided': clean_val(ws_db.cell(r, 8).value),
        'unit': clean_val(ws_db.cell(r, 9).value),
        'margin': clean_val(ws_db.cell(r, 10).value),
        'margin_pct': clean_val(ws_db.cell(r, 11).value),
        'status': clean_val(ws_db.cell(r, 12).value)
    })

# 5. Rudder & Steering (Rows 60-74)
rudder_items = []
for r in range(60, 75):
    rudder_items.append({
        'no': clean_val(ws_db.cell(r, 2).value),
        'item': clean_val(ws_db.cell(r, 3).value),
        'rule': clean_val(ws_db.cell(r, 4).value),
        'baseline': clean_val(ws_db.cell(r, 5).value),
        'factor': clean_val(ws_db.cell(r, 6).value),
        'required': clean_val(ws_db.cell(r, 7).value),
        'provided': clean_val(ws_db.cell(r, 8).value),
        'unit': clean_val(ws_db.cell(r, 9).value),
        'margin': clean_val(ws_db.cell(r, 10).value),
        'margin_pct': clean_val(ws_db.cell(r, 11).value),
        'status': clean_val(ws_db.cell(r, 12).value)
    })

# 6. Piping (Rows 80-85)
piping_items = []
for r in range(80, 86):
    piping_items.append({
        'no': clean_val(ws_db.cell(r, 2).value),
        'item': clean_val(ws_db.cell(r, 3).value),
        'rule': clean_val(ws_db.cell(r, 4).value),
        'baseline': clean_val(ws_db.cell(r, 5).value),
        'factor': clean_val(ws_db.cell(r, 6).value),
        'required': clean_val(ws_db.cell(r, 7).value),
        'provided': clean_val(ws_db.cell(r, 8).value),
        'unit': clean_val(ws_db.cell(r, 9).value),
        'margin': clean_val(ws_db.cell(r, 10).value),
        'margin_pct': clean_val(ws_db.cell(r, 11).value),
        'status': clean_val(ws_db.cell(r, 12).value)
    })

# 7. Anchoring & Mooring (Rows 91-98)
anchoring_items = []
for r in range(91, 99):
    anchoring_items.append({
        'no': clean_val(ws_db.cell(r, 2).value),
        'item': clean_val(ws_db.cell(r, 3).value),
        'rule': clean_val(ws_db.cell(r, 4).value),
        'baseline': clean_val(ws_db.cell(r, 5).value),
        'factor': clean_val(ws_db.cell(r, 6).value),
        'required': clean_val(ws_db.cell(r, 7).value),
        'provided': clean_val(ws_db.cell(r, 8).value),
        'unit': clean_val(ws_db.cell(r, 9).value),
        'margin': clean_val(ws_db.cell(r, 10).value),
        'margin_pct': clean_val(ws_db.cell(r, 11).value),
        'status': clean_val(ws_db.cell(r, 12).value)
    })

# 8. Outfitting & Openings (Rows 104-110)
outfitting_items = []
for r in range(104, 111):
    outfitting_items.append({
        'no': clean_val(ws_db.cell(r, 2).value),
        'item': clean_val(ws_db.cell(r, 3).value),
        'rule': clean_val(ws_db.cell(r, 4).value),
        'baseline': clean_val(ws_db.cell(r, 5).value),
        'factor': clean_val(ws_db.cell(r, 6).value),
        'required': clean_val(ws_db.cell(r, 7).value),
        'provided': clean_val(ws_db.cell(r, 8).value),
        'unit': clean_val(ws_db.cell(r, 9).value),
        'margin': clean_val(ws_db.cell(r, 10).value),
        'margin_pct': clean_val(ws_db.cell(r, 11).value),
        'status': clean_val(ws_db.cell(r, 12).value)
    })

# 9. Calculation Brain (76 items across 12 groups)
ws_cb = wb['Calculation Brain']
calculation_brain = []
current_group = "GROUP 1: HULL SHELL & DECK PLATING"
for r in range(6, 94):
    b_val = ws_cb.cell(r, 2).value
    if b_val and str(b_val).startswith('GROUP'):
        current_group = str(b_val).strip()
        continue
    item_no = clean_val(ws_cb.cell(r, 2).value)
    desc = clean_val(ws_cb.cell(r, 3).value)
    if item_no is not None and desc is not None:
        calculation_brain.append({
            'group': current_group,
            'item': item_no,
            'desc': desc,
            'rule': clean_val(ws_cb.cell(r, 4).value),
            'formula': clean_val(ws_cb.cell(r, 5).value),
            'inputs': clean_val(ws_cb.cell(r, 6).value),
            'baseline': clean_val(ws_cb.cell(r, 7).value),
            'factor': clean_val(ws_cb.cell(r, 8).value),
            'rreq': clean_val(ws_cb.cell(r, 9).value),
            'dact': clean_val(ws_cb.cell(r, 10).value),
            'unit': clean_val(ws_cb.cell(r, 11).value),
            'margin': clean_val(ws_cb.cell(r, 12).value),
            'status': clean_val(ws_cb.cell(r, 13).value),
            'notes': clean_val(ws_cb.cell(r, 14).value)
        })

# 10. Sheet-2 Calculations (20 calculation blocks)
ws_s2 = wb['Sheet-2-Calculation Sheet']
sheet2_blocks = [
    {'id': 1, 'name': 'Side Transverse Frames', 'type': 'section_modulus', 'row_start': 2, 'row_end': 16,
     'plate_width': 550, 'plate_thk': 12, 'web_height': 150, 'web_thk': 10, 'flange_width': 100, 'flange_thk': 10},
    {'id': 2, 'name': 'Bottom Construction & Floor Plate', 'type': 'section_modulus', 'row_start': 17, 'row_end': 31,
     'plate_width': 550, 'plate_thk': 12, 'web_height': 500, 'web_thk': 12, 'flange_width': 300, 'flange_thk': 12},
    {'id': 3, 'name': 'Transverse Frame Spacing Rule', 'type': 'rule_limit', 'row_start': 32, 'row_end': 38,
     'rule_formula': '450 + 2*Lbp', 'lbp': 69.85, 'standard_spacing': 500, 'actual_spacing': 550, 'limit': 589.7},
    {'id': 4, 'name': 'Side Shell Longitudinal Stringers', 'type': 'section_modulus', 'row_start': 39, 'row_end': 53,
     'plate_width': 550, 'plate_thk': 12, 'web_height': 250, 'web_thk': 12, 'flange_width': 100, 'flange_thk': 12},
    {'id': 5, 'name': 'Strength Deck Longitudinal Beams', 'type': 'section_modulus', 'row_start': 54, 'row_end': 68,
     'plate_width': 550, 'plate_thk': 12, 'web_height': 130, 'web_thk': 10, 'flange_width': 90, 'flange_thk': 10},
    {'id': 6, 'name': 'Strength Deck Transverse Web Beams', 'type': 'section_modulus', 'row_start': 69, 'row_end': 83,
     'plate_width': 550, 'plate_thk': 12, 'web_height': 200, 'web_thk': 11, 'flange_width': 100, 'flange_thk': 11},
    {'id': 7, 'name': 'Main Deck Center Longitudinal Girder', 'type': 'section_modulus', 'row_start': 84, 'row_end': 98,
     'plate_width': 550, 'plate_thk': 12, 'web_height': 350, 'web_thk': 12, 'flange_width': 150, 'flange_thk': 12},
    {'id': 8, 'name': 'Collision Bulkhead Statutory Location', 'type': 'range_check', 'row_start': 99, 'row_end': 105,
     'rule': 'Rule 33', 'min_factor': 0.05, 'max_factor': 0.08, 'lbp': 69.85, 'actual_pos': 4.8, 'min_limit': 3.49, 'max_limit': 5.59},
    {'id': 9, 'name': 'Aft Peak Watertight Bulkhead Stiffeners', 'type': 'section_modulus', 'row_start': 106, 'row_end': 120,
     'plate_width': 550, 'plate_thk': 10, 'web_height': 100, 'web_thk': 9, 'flange_width': 90, 'flange_thk': 9},
    {'id': 10, 'name': 'Cargo Hold & Other Bulkhead Stiffeners', 'type': 'section_modulus', 'row_start': 121, 'row_end': 135,
     'plate_width': 550, 'plate_thk': 10, 'web_height': 100, 'web_thk': 9, 'flange_width': 90, 'flange_thk': 9},
    {'id': 11, 'name': 'Engine Room Center Keelson Area', 'type': 'area_derivation', 'row_start': 136, 'row_end': 142,
     'rule': 'Rule 44', 'web_height': 510, 'web_thk': 18, 'flange_width': 175, 'flange_thk': 12, 'area_mm2': 9180, 'area_cm2': 91.8},
    {'id': 12, 'name': 'Engine Room Heavy Web Frames', 'type': 'section_modulus', 'row_start': 143, 'row_end': 157,
     'plate_width': 550, 'plate_thk': 12, 'web_height': 450, 'web_thk': 12, 'flange_width': 200, 'flange_thk': 12},
    {'id': 13, 'name': 'Cargo Hatch Coaming & Auxiliaries', 'type': 'section_modulus', 'row_start': 158, 'row_end': 172,
     'plate_width': 550, 'plate_thk': 25, 'web_height': 80, 'web_thk': 8, 'flange_width': 60, 'flange_thk': 8},
    {'id': 14, 'name': 'Cargo Hatchway Transverse Beams', 'type': 'section_modulus', 'row_start': 173, 'row_end': 187,
     'plate_width': 550, 'plate_thk': 25, 'web_height': 80, 'web_thk': 8, 'flange_width': 60, 'flange_thk': 8},
    {'id': 15, 'name': 'Cargo Hatchway Side Long. Beams', 'type': 'section_modulus', 'row_start': 188, 'row_end': 202,
     'plate_width': 550, 'plate_thk': 25, 'web_height': 80, 'web_thk': 8, 'flange_width': 60, 'flange_thk': 8},
    {'id': 16, 'name': 'Steel Weather-tight Hatch Covers', 'type': 'section_modulus', 'row_start': 203, 'row_end': 217,
     'plate_width': 550, 'plate_thk': 25, 'web_height': 80, 'web_thk': 8, 'flange_width': 60, 'flange_thk': 8},
    {'id': 17, 'name': 'Superstructure & Deckhouse Stiffeners', 'type': 'section_modulus', 'row_start': 218, 'row_end': 232,
     'plate_width': 550, 'plate_thk': 5, 'web_height': 50, 'web_thk': 6, 'flange_width': 50, 'flange_thk': 6},
    {'id': 18, 'name': 'Engine Casing Structural Stiffeners', 'type': 'section_modulus', 'row_start': 233, 'row_end': 247,
     'plate_width': 550, 'plate_thk': 5, 'web_height': 50, 'web_thk': 6, 'flange_width': 50, 'flange_thk': 6},
    {'id': 19, 'name': 'Poop & Accommodation Deck Beams', 'type': 'section_modulus', 'row_start': 248, 'row_end': 262,
     'plate_width': 550, 'plate_thk': 5, 'web_height': 75, 'web_thk': 6, 'flange_width': 75, 'flange_thk': 6},
    {'id': 20, 'name': 'Poop Deck Longitudinal Girders', 'type': 'section_modulus', 'row_start': 263, 'row_end': 277,
     'plate_width': 550, 'plate_thk': 5, 'web_height': 200, 'web_thk': 7, 'flange_width': 90, 'flange_thk': 7}
]

# 11. Lightship Calculation
ws_ls = wb['Lightship Calculation']
lightship_plates = []
for r in range(16, 35):
    sn = clean_val(ws_ls.cell(r, 1).value)
    name = clean_val(ws_ls.cell(r, 2).value)
    if sn and name:
        l = clean_val(ws_ls.cell(r, 3).value) or 0
        b = clean_val(ws_ls.cell(r, 4).value) or 0
        t = clean_val(ws_ls.cell(r, 5).value)
        if name == 'Tank Top Plate' and (t is None or str(t).startswith('#')):
            t = 14.0 # Resolved from backup
        t = float(t or 0)
        vol = (l/1000.0) * (b/1000.0) * (t/1000.0)
        density = clean_val(ws_ls.cell(r, 7).value) or 7850
        qty = clean_val(ws_ls.cell(r, 8).value) or 1
        weight_kg = vol * density * qty
        weight_t = weight_kg / 1000.0
        lightship_plates.append({
            'sn': sn, 'name': name, 'l': l, 'b': b, 't': t,
            'vol': round(vol, 6), 'density': density, 'qty': qty,
            'weight_kg': round(weight_kg, 2), 'weight_tonne': round(weight_t, 3)
        })

lightship_angles = []
for r in range(39, 60):
    sn = clean_val(ws_ls.cell(r, 1).value)
    name = clean_val(ws_ls.cell(r, 2).value)
    if sn and name:
        l_dim = clean_val(ws_ls.cell(r, 3).value) or 0
        b_dim = clean_val(ws_ls.cell(r, 4).value) or 0
        t = clean_val(ws_ls.cell(r, 5).value) or 0
        area = clean_val(ws_ls.cell(r, 6).value) or 0
        length = clean_val(ws_ls.cell(r, 7).value) or 0
        vol = (area / 1e6) * (length / 1000.0)
        density = clean_val(ws_ls.cell(r, 9).value) or 7850
        qty = clean_val(ws_ls.cell(r, 10).value) or 1
        weight_kg = vol * density * qty
        weight_t = weight_kg / 1000.0
        lightship_angles.append({
            'sn': sn, 'name': name, 'l_dim': l_dim, 'b_dim': b_dim, 't': t,
            'area': area, 'length': length, 'vol': round(vol, 6),
            'density': density, 'qty': qty, 'weight_kg': round(weight_kg, 2),
            'weight_tonne': round(weight_t, 3)
        })

# 12. Empirical Tables (67 tables)
ws_et = wb['Empirical Rules Tables']
tables = []
current_table = None

for r in range(1, ws_et.max_row+1):
    b_val = ws_et.cell(r, 2).value
    if b_val and ('সারণি-' in str(b_val) or 'Table' in str(b_val)):
        if current_table:
            tables.append(current_table)
        current_table = {
            'id': len(tables) + 1,
            'title': str(b_val).strip(),
            'ref': '',
            'headers': [],
            'rows': [],
            'notes': []
        }
        continue
    if current_table:
        if b_val and 'বিধিবদ্ধ' in str(b_val):
            current_table['ref'] = str(b_val).strip()
            continue
        if b_val and ('•' in str(b_val) or 'শর্ত' in str(b_val) or 'Note' in str(b_val)):
            current_table['notes'].append(str(b_val).strip())
            continue
        row_vals = [ws_et.cell(r, c).value for c in range(2, 9)]
        if any(v is not None for v in row_vals):
            vals_clean = [str(v).strip() if v is not None else '' for v in row_vals]
            while vals_clean and vals_clean[-1] == '':
                vals_clean.pop()
            if not current_table['headers']:
                current_table['headers'] = vals_clean
            else:
                current_table['rows'].append(vals_clean)

if current_table:
    tables.append(current_table)

# 13. Application Form Structure & Content (Pages 1 to 24)
ws_af = wb['Application Form']
af_pages = []
current_page_num = 1
current_page_lines = []

for r in range(1, 1083):
    line_cells = []
    for c in range(1, 30):
        v = ws_af.cell(r, c).value
        if v is not None:
            line_cells.append({'col': c, 'val': str(v).strip()})
    
    # Check if page boundary
    line_text = ' '.join(c['val'] for c in line_cells)
    if 'Page ' in line_text and 'of 24' in line_text:
        if current_page_lines:
            af_pages.append({
                'page': current_page_num,
                'content': current_page_lines
            })
            current_page_num += 1
            current_page_lines = []
    if line_cells:
        current_page_lines.append({'row': r, 'cells': line_cells, 'text': line_text})

if current_page_lines:
    af_pages.append({
        'page': current_page_num,
        'content': current_page_lines
    })

data = {
    'dashboard_inputs': dashboard_inputs,
    'stiffener_profiles': stiffener_profiles,
    'scantling_checklist': scantling_checklist,
    'propulsion_items': propulsion_items,
    'rudder_items': rudder_items,
    'piping_items': piping_items,
    'anchoring_items': anchoring_items,
    'outfitting_items': outfitting_items,
    'calculation_brain': calculation_brain,
    'sheet2_blocks': sheet2_blocks,
    'lightship_plates': lightship_plates,
    'lightship_angles': lightship_angles,
    'empirical_tables': tables,
    'application_form_pages': af_pages
}

with open('app/data_extracted.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('SUCCESS: Extracted all excel data to app/data_extracted.json!')
print(f"Tables: {len(tables)}, Brain items: {len(calculation_brain)}, App form pages: {len(af_pages)}")

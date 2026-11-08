with open('app/services/calculation_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. calc_stiffener_section call at line 260
target1 = "s_res = calc_stiffener_section(spacing, tp, hw, tw, bf, tf)"
replace1 = "s_res = calc_stiffener_section(spacing, tp, hw, tw, bf, tf, profile_type=ptype)"
assert target1 in content, "target1 not found"
content = content.replace(target1, replace1, 1)

# 2. sheet2_results profile_type overwrite fix
target2 = """                # Add to Sheet-2 detailed calculations booklet
                sheet2_results.append({
                    'id': sheet_counter,
                    'member_id': m_id,
                    'name': m['name'],
                    'type': 'section_modulus',
                    'table_ref': m.get('table_ref', ''),
                    'welded_on_plate': m.get('welded_on_plate', ''),
                    'welded_plate_key': w_key,
                    'plate_width': spacing,
                    'plate_thk': tp,
                    'profile_type': ptype,
                    'web_height': hw,
                    'web_thk': tw,
                    'flange_width': bf,
                    'flange_thk': tf,
                    'rreq': req_sm,
                    'margin': margin,
                    'status': 'COMPLIANT' if is_comp else 'NON-COMPLIANT',
                    'derivation': m.get('derivation'),
                    **s_res
                })"""

replace2 = """                # Add to Sheet-2 detailed calculations booklet
                sheet2_results.append({
                    'id': sheet_counter,
                    'member_id': m_id,
                    'name': m['name'],
                    'type': 'section_modulus',
                    'table_ref': m.get('table_ref', ''),
                    'welded_on_plate': m.get('welded_on_plate', ''),
                    'welded_plate_key': w_key,
                    'plate_width': spacing,
                    'plate_thk': tp,
                    'web_height': hw,
                    'web_thk': tw,
                    'flange_width': bf,
                    'flange_thk': tf,
                    'rreq': req_sm,
                    'margin': margin,
                    'status': 'COMPLIANT' if is_comp else 'NON-COMPLIANT',
                    'derivation': m.get('derivation'),
                    **s_res,
                    'profile_type': ptype
                })"""
# normalize newlines for replacement
target2_norm = target2.replace('\r\n', '\n')
content_norm = content.replace('\r\n', '\n')
assert target2_norm in content_norm, "target2 not found"
content_norm = content_norm.replace(target2_norm, replace2.replace('\r\n', '\n'), 1)

# 3. profile_type in stiff_profiles at line 392
target3 = """            hw = float(p.get('web_depth', 150))
            tw = float(p.get('web_thk', 10))
            bf = float(p.get('flange_width', 100))
            tf = float(p.get('flange_thk', 10))
            s_res = calc_stiffener_section(spacing, tp, hw, tw, bf, tf)"""

replace3 = """            ptype = p.get('profile_type', 'L')
            hw = float(p.get('web_depth', 150))
            tw = float(p.get('web_thk', 10))
            bf = float(p.get('flange_width', 100))
            tf = float(p.get('flange_thk', 10))
            s_res = calc_stiffener_section(spacing, tp, hw, tw, bf, tf, profile_type=ptype)"""
target3_norm = target3.replace('\r\n', '\n')
assert target3_norm in content_norm, "target3 not found"
content_norm = content_norm.replace(target3_norm, replace3.replace('\r\n', '\n'), 1)

with open('app/services/calculation_service.py', 'w', encoding='utf-8') as f:
    f.write(content_norm)

print("Successfully updated app/services/calculation_service.py")

with open('app/services/pdf/app_form_pdf_service.py', 'r', encoding='utf-8') as f:
    code = f.read().replace('\r\n', '\n')

old_line = "            d = calc_lookup.get('plate_superstructure_wall') or calc_lookup.get('plate_bhd_wt', {})"
new_line = "            d = calc_lookup.get('plate_superstructure_wall', {})"
assert old_line in code, "old_line not found"
code = code.replace(old_line, new_line)

with open('app/services/pdf/app_form_pdf_service.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated app_form_pdf_service.py")

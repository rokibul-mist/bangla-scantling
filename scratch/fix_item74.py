with open('app/services/pdf/app_form_pdf_service.py', 'r', encoding='utf-8') as f:
    code = f.read().replace('\r\n', '\n')

old_part = """    # 16. Item 74: Super structure bulkhead (Rule 63)
    if num == '74':
        if sub_idx == 0:
            d = calc_lookup.get('plate_superstructure_wall', {})
            return (d.get('req', 5.50), 10.0, 'mm', False)
        else:
            d = calc_lookup.get('stiff_superstructure_wall', {})
            return (d.get('req', 16.0), d.get('prov', 71.84), 'cm³', False)"""

new_part = """    # 16. Item 74: Super structure bulkhead (Rule 63)
    if num == '74':
        if sub_idx == 0:
            return (5.50, 10.0, 'mm', False)
        else:
            d = calc_lookup.get('stiff_superstructure_wall', {})
            return (16.0, d.get('prov', 71.84), 'cm³', False)"""

assert old_part in code, "old_part not found"
code = code.replace(old_part, new_part)

with open('app/services/pdf/app_form_pdf_service.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated Item 74 in app_form_pdf_service.py")

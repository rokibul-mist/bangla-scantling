import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pymupdf

from app.repositories.state_repository import StateRepository
from app.services.calculation_service import CalculationService
from app.services.pdf.lightship_pdf_service import generate_lightship_booklet_pdf
from app.services.pdf.strength_pdf_service import generate_hull_strength_booklet_pdf
from app.services.pdf.app_form_pdf_service import generate_application_form_pdf
from app.services.pdf.detail_calc_pdf_service import generate_detail_calculation_booklet_pdf

def build_all():
    state_repo = StateRepository()
    state = state_repo.get_state()
    computed = CalculationService.compute_all_calculations(state)
    
    os.makedirs('deliverables', exist_ok=True)
    
    # 1. Generate Lightship.xlsx with openpyxl live formulas
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Lightship'
    ws.views.sheetView[0].showGridLines = True

    FONT_FAMILY = 'Segoe UI'
    HEADER_FONT = Font(name=FONT_FAMILY, size=9, bold=True, color='1A202C')
    SECTION_BANNER_FONT = Font(name=FONT_FAMILY, size=11, bold=True, color='0F172A')
    DATA_FONT = Font(name=FONT_FAMILY, size=9, bold=False, color='262626')
    BOLD_DATA_FONT = Font(name=FONT_FAMILY, size=9, bold=True, color='111827')
    META_HEADER_FONT = Font(name=FONT_FAMILY, size=11, bold=True, color='1E3A8A')

    FILL_HEADER = PatternFill(start_color='F2F4F7', end_color='F2F4F7', fill_type='solid')
    FILL_ZEBRA = PatternFill(start_color='F9FAFB', end_color='F9FAFB', fill_type='solid')
    FILL_WHITE = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
    FILL_SUBTOTAL = PatternFill(start_color='E5E7EB', end_color='E5E7EB', fill_type='solid')
    FILL_TOTAL = PatternFill(start_color='D1D5DB', end_color='D1D5DB', fill_type='solid')

    BORDER_DARK = Side(border_style='thin', color='262626')
    BORDER_LIGHT = Side(border_style='thin', color='D1D5DB')
    BORDER_DOUBLE = Side(border_style='double', color='262626')

    BORDER_DATA_ZEBRA = Border(left=BORDER_LIGHT, right=BORDER_LIGHT, top=BORDER_LIGHT, bottom=BORDER_LIGHT)
    BORDER_TOTAL = Border(top=BORDER_DARK, bottom=BORDER_DOUBLE)

    part = computed.get('dashboard_inputs', {})
    ws['B2'] = 'Name Of the Vessel'
    ws['C2'] = part.get('vessel_name', 'M.V. CROWN MARINERS - 67')
    ws['B2'].font = META_HEADER_FONT
    ws['C2'].font = META_HEADER_FONT

    p_list = [
        ('LOA (Length Overall)', float(part.get('loa', 76.21) or 76.21), 'm'),
        ('LWL (Waterline Length)', float(part.get('lwl', 72.50) or 72.50), 'm'),
        ('LBP (Length Bet. Perpendiculars)', float(part.get('lbp', 69.85) or 69.85), 'm'),
        ('B (Breadth Moulded)', float(part.get('breadth', 13.41) or 13.41), 'm'),
        ('D (Depth Moulded)', float(part.get('depth', 5.18) or 5.18), 'm'),
        ('d (Loaded Draft)', float(part.get('draft', 4.0) or 4.0), 'm'),
        ('Displacement (Delta)', float(part.get('displacement', 3200) or 3200), 't'),
        ('Block Coefficient (Cb)', float(part.get('cb', 0.75) or 0.75), '-'),
        ('Frame Spacing (s)', float(part.get('frame_spacing', 550) or 550), 'mm'),
    ]

    ws['B6'] = 'VESSEL PRINCIPAL PARTICULARS'
    ws['B6'].font = SECTION_BANNER_FONT
    for idx, (label, val, unit) in enumerate(p_list, start=7):
        ws[f'B{idx}'] = label
        ws[f'C{idx}'] = val
        ws[f'D{idx}'] = unit
        ws[f'B{idx}'].font = DATA_FONT
        ws[f'C{idx}'].font = BOLD_DATA_FONT
        ws[f'D{idx}'].font = DATA_FONT

    start_plate_hdr = 17
    ws[f'B{start_plate_hdr-1}'] = 'HULL PLATING STRUCTURAL MEMBERS'
    ws[f'B{start_plate_hdr-1}'].font = SECTION_BANNER_FONT

    headers_plate_1 = ['S/N', 'ELEMENT', 'L', 'B', 't', 'Volume', 'Steel Density', 'Quantity', 'Weight', 'Weight']
    headers_plate_2 = ['', '(Plate)', '(mm)', '(mm)', '(mm)', '(m3)', 'kg/m3', '(Pcs)', '(KG)', '(Tonne)']

    for c_idx, (h1, h2) in enumerate(zip(headers_plate_1, headers_plate_2), start=1):
        c_letter = get_column_letter(c_idx)
        c1 = ws[f'{c_letter}{start_plate_hdr}']
        c2 = ws[f'{c_letter}{start_plate_hdr+1}']
        c1.value, c2.value = h1, h2
        c1.font, c2.font = HEADER_FONT, HEADER_FONT
        c1.fill, c2.fill = FILL_HEADER, FILL_HEADER
        c1.alignment = Alignment(horizontal='center', vertical='center')
        c2.alignment = Alignment(horizontal='center', vertical='center')
        c1.border = Border(left=BORDER_LIGHT, right=BORDER_LIGHT, top=BORDER_DARK)
        c2.border = Border(left=BORDER_LIGHT, right=BORDER_LIGHT, bottom=BORDER_DARK)

    start_plate_row = 19
    plates = computed.get('lightship_plates', [])
    for i, p in enumerate(plates, start=1):
        r = start_plate_row + i - 1
        ws[f'A{r}'] = i
        ws[f'B{r}'] = p.get('name', f'Plate {i}')
        ws[f'C{r}'] = p.get('l', 0)
        ws[f'D{r}'] = p.get('b', 0)
        ws[f'E{r}'] = p.get('t', 0)
        ws[f'F{r}'] = f'=(C{r}*D{r}*E{r})/1000000000'
        ws[f'G{r}'] = 7850
        ws[f'H{r}'] = p.get('qty', 1)
        ws[f'I{r}'] = f'=(F{r}*G{r}*H{r})'
        ws[f'J{r}'] = f'=I{r}/1000'
        row_fill = FILL_WHITE if i % 2 == 1 else FILL_ZEBRA
        for col_l in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
            c = ws[f'{col_l}{r}']
            c.font = DATA_FONT
            c.fill = row_fill
            c.border = BORDER_DATA_ZEBRA

    end_plate_row = start_plate_row + len(plates) - 1
    total_plate_row = 38
    ws[f'H{total_plate_row}'] = 'Total Plate Weight'
    ws[f'H{total_plate_row}'].font = BOLD_DATA_FONT
    ws[f'J{total_plate_row}'] = f'=SUM(J{start_plate_row}:J{end_plate_row})'
    ws[f'J{total_plate_row}'].font = BOLD_DATA_FONT
    ws[f'J{total_plate_row}'].fill = FILL_SUBTOTAL
    ws[f'J{total_plate_row}'].border = BORDER_TOTAL

    start_angle_hdr = 41
    ws[f'B{start_angle_hdr-1}'] = 'STIFFENER PROFILES & GEOMETRY CATALOG'
    ws[f'B{start_angle_hdr-1}'].font = SECTION_BANNER_FONT

    headers_angle_1 = ['S/N', 'ELEMENT', 'L', 'B', 't', 'Area', 'Length', 'Volume', 'Steel Density', 'Quantity', 'Weight', 'Weight']
    headers_angle_2 = ['', '(Angle / Profile)', '(mm)', '(mm)', '(mm)', '(mm2)', '(mm)', '(m3)', '(kg/m3)', '(Pcs)', '(KG)', '(Tonne)']

    for c_idx, (h1, h2) in enumerate(zip(headers_angle_1, headers_angle_2), start=1):
        c_letter = get_column_letter(c_idx)
        c1 = ws[f'{c_letter}{start_angle_hdr}']
        c2 = ws[f'{c_letter}{start_angle_hdr+1}']
        c1.value, c2.value = h1, h2
        c1.font, c2.font = HEADER_FONT, HEADER_FONT
        c1.fill, c2.fill = FILL_HEADER, FILL_HEADER
        c1.border = Border(left=BORDER_LIGHT, right=BORDER_LIGHT, top=BORDER_DARK)
        c2.border = Border(left=BORDER_LIGHT, right=BORDER_LIGHT, bottom=BORDER_DARK)

    start_angle_row = 43
    angles = computed.get('lightship_angles', [])
    for i, s in enumerate(angles, start=1):
        r = start_angle_row + i - 1
        ws[f'A{r}'] = i
        ws[f'B{r}'] = s.get('name', f'Stiffener {i}')
        ws[f'C{r}'] = s.get('hw', 0)
        ws[f'D{r}'] = s.get('bf', 0)
        ws[f'E{r}'] = s.get('tw', 0)
        ws[f'F{r}'] = f'=(C{r}*E{r})+(D{r}*E{r})'
        ws[f'G{r}'] = s.get('length', 0)
        ws[f'H{r}'] = f'=(G{r}*F{r})/1000000000'
        ws[f'I{r}'] = 7850
        ws[f'J{r}'] = s.get('qty', 1)
        ws[f'K{r}'] = f'=(H{r}*I{r}*J{r})'
        ws[f'L{r}'] = f'=K{r}/1000'
        row_fill = FILL_WHITE if i % 2 == 1 else FILL_ZEBRA
        for col_l in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
            c = ws[f'{col_l}{r}']
            c.font = DATA_FONT
            c.fill = row_fill
            c.border = BORDER_DATA_ZEBRA

    end_angle_row = start_angle_row + len(angles) - 1
    total_angle_row = 64
    ws[f'J{total_angle_row}'] = 'Total Angle Weight'
    ws[f'J{total_angle_row}'].font = BOLD_DATA_FONT
    ws[f'L{total_angle_row}'] = f'=SUM(L{start_angle_row}:L{end_angle_row})'
    ws[f'L{total_angle_row}'].font = BOLD_DATA_FONT
    ws[f'L{total_angle_row}'].fill = FILL_SUBTOTAL
    ws[f'L{total_angle_row}'].border = BORDER_TOTAL

    r_sum_start = 67
    ws[f'B{r_sum_start-1}'] = 'LIGHTSHIP WEIGHT SUMMARY & OUTFITTING ALLOWANCES'
    ws[f'B{r_sum_start-1}'].font = SECTION_BANNER_FONT

    default_allowances = [
        ('Total Light ship (plate & angle)', f'=J{total_plate_row}+L{total_angle_row}', True, FILL_SUBTOTAL),
        ('Allowance (20%)', f'=I{r_sum_start}*20%', False, None),
        ('Outfit & deck equipment (15%)', f'=I{r_sum_start}*15%', False, None),
        ('Piping, valves & fittings (10%)', f'=I{r_sum_start}*10%', False, None),
        ('Electrical & instrumentation (5%)', f'=I{r_sum_start}*3%', False, None),
        ('Accommodation fittings & furniture (1%)', f'=I{r_sum_start}*1%', False, None),
        ('Miscellaneous (7%)', f'=I{r_sum_start}*7%', False, None),
        ('Total Light ship', f'=SUM(I{r_sum_start}:I{r_sum_start+6})', True, FILL_TOTAL),
    ]

    for offset, (label, formula, is_bold, fill_color) in enumerate(default_allowances):
        curr_r = r_sum_start + offset
        ws[f'E{curr_r}'] = label
        ws[f'I{curr_r}'] = formula
        ws[f'J{curr_r}'] = 'tonne'
        ws[f'E{curr_r}'].font = BOLD_DATA_FONT if is_bold else DATA_FONT
        ws[f'I{curr_r}'].font = BOLD_DATA_FONT if is_bold else DATA_FONT

    wb.save('Lightship.xlsx')
    wb.save('deliverables/Lightship.xlsx')
    print('[+] Generated Lightship.xlsx in root and deliverables/')

    # 2. Lightship PDF
    ls_pdf = generate_lightship_booklet_pdf(computed)
    with open('Lightship.pdf', 'wb') as f:
        f.write(ls_pdf)
    with open('deliverables/Lightship.pdf', 'wb') as f:
        f.write(ls_pdf)
    print(f'[+] Generated Lightship.pdf ({len(ls_pdf):,} bytes)')

    # 3. Lightship Preview PNG
    doc = pymupdf.open('Lightship.pdf')
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=200)
    pix.save('lightship_preview.png')
    pix.save('deliverables/lightship_preview.png')
    doc.close()
    print(f'[+] Generated lightship_preview.png ({os.path.getsize("lightship_preview.png"):,} bytes)')

    # 4. Hull Strength PDF
    str_pdf = generate_hull_strength_booklet_pdf(computed)
    with open('Hull_Strength_Booklet.pdf', 'wb') as f:
        f.write(str_pdf)
    with open('deliverables/Hull_Strength_Booklet.pdf', 'wb') as f:
        f.write(str_pdf)
    print(f'[+] Generated Hull_Strength_Booklet.pdf ({len(str_pdf):,} bytes)')

    # 5. Application Form PDF
    app_pdf = generate_application_form_pdf(computed)
    with open('Application_Form_Booklet.pdf', 'wb') as f:
        f.write(app_pdf)
    with open('deliverables/Application_Form_Booklet.pdf', 'wb') as f:
        f.write(app_pdf)
    print(f'[+] Generated Application_Form_Booklet.pdf ({len(app_pdf):,} bytes)')

    # 6. Detail Calc PDF
    det_pdf = generate_detail_calculation_booklet_pdf(computed)
    with open('Detail_Calculation_Booklet.pdf', 'wb') as f:
        f.write(det_pdf)
    with open('deliverables/Detail_Calculation_Booklet.pdf', 'wb') as f:
        f.write(det_pdf)
    print(f'[+] Generated Detail_Calculation_Booklet.pdf ({len(det_pdf):,} bytes)')

if __name__ == '__main__':
    build_all()

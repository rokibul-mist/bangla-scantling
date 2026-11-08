import json, re, io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
import fitz

def parse_audit_page(content):
    items = []
    curr = None
    for r in content:
        cells = r.get('cells', [])
        txt = (r.get('text') or '').strip()
        if not txt or '1ST  Edition' in txt or 'For office use only' in txt or 'Complied with' in txt or txt == 'Yes No':
            continue
        first_cell = cells[0] if cells else {}
        first_val = str(first_cell.get('val', '')).strip()
        m_item = re.match(r'^(\d+)\.\s+(.*)', first_val)
        is_item_header = bool(m_item and first_cell.get('col') == 2)
        if is_item_header:
            if curr: items.append(curr)
            raw_title = m_item.group(2).strip()
            m_rule = re.search(r'\((rule[^\)]*)\)', raw_title, re.IGNORECASE)
            rule_str = f"({m_rule.group(1).strip()})" if m_rule else ""
            clean_title = re.sub(r'\((rule[^\)]*)\)', '', raw_title, flags=re.IGNORECASE).strip()
            curr = {'num': m_item.group(1), 'title': clean_title, 'rule': rule_str, 'req_parts': [], 'lines': []}
        elif curr:
            req_c = [str(c.get('val', '')).strip() for c in cells if c.get('col') == 2]
            if req_c:
                curr['req_parts'].append(req_c[0])
            lbl_c = [str(c.get('val', '')).strip() for c in cells if c.get('col') in [6, 7, 8, 9] and re.search(r'as per|drawing|rule', str(c.get('val', '')), re.I)]
            lbl = lbl_c[0] if lbl_c else ''
            val_c = [str(c.get('val', '')).strip() for c in cells if c.get('col') in [10, 11, 12, 13, 14] and str(c.get('val', '')).strip() not in ['x', '☐', '■', '[X]', '[ ]', 'mm', 'Cm3', 'bolts', 'Nos']]
            val = val_c[0] if val_c else ''
            unit_c = [str(c.get('val', '')).strip() for c in cells if c.get('col') in [15, 16] or str(c.get('val', '')).strip() in ['mm', '…..mm', 'Cm3', 'bolts', 'Nos', 'x 40 mm']]
            unit = unit_c[0].strip() if unit_c else 'mm'
            if lbl or val:
                curr['lines'].append({'label': lbl, 'val': val, 'unit': unit})
    if curr: items.append(curr)
    for it in items:
        it['requirement'] = ' '.join(it['req_parts']).strip()
    return items

def build_pdf_audit_table_noborder(items, row_gap=6):
    col_widths = [150, 165, 55, 45, 54, 54] # total 523 pt

    style_req = ParagraphStyle('AudReq', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.black)
    style_lbl = ParagraphStyle('AudLbl', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.black)
    style_val = ParagraphStyle('AudVal', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, alignment=2, textColor=colors.black)
    style_unt = ParagraphStyle('AudUnt', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.black)
    style_box = ParagraphStyle('AudBox', fontName='Helvetica', fontSize=9.5, leading=9.5, alignment=1, textColor=colors.black)
    style_item_hdr = ParagraphStyle('AudItemHdr', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.black)
    
    style_off_top = ParagraphStyle('AudOffT', fontName='Helvetica-Bold', fontSize=7.5, leading=9, alignment=1, textColor=colors.black)
    style_off_sub = ParagraphStyle('AudOffS', fontName='Helvetica-Bold', fontSize=7.5, leading=9, alignment=1, textColor=colors.black)
    style_off_col = ParagraphStyle('AudOffC', fontName='Helvetica-Bold', fontSize=7.5, leading=9, alignment=1, textColor=colors.black)

    data = []
    t_styles = [
        # Top-right office use box headers
        ('SPAN', (4, 0), (5, 0)),
        ('SPAN', (4, 1), (5, 1)),
        ('LINEABOVE', (4, 0), (5, 0), 0.75, colors.black),
        ('LINEBELOW', (4, 0), (5, 0), 0.5, colors.black),
        ('LINEBELOW', (4, 1), (5, 1), 0.5, colors.black),
        ('LINEBELOW', (4, 2), (5, 2), 0.5, colors.black),
        ('LINEBEFORE', (4, 0), (4, -1), 0.75, colors.black),
        ('LINEAFTER', (5, 0), (5, -1), 0.75, colors.black),
        ('LINEBEFORE', (5, 2), (5, -1), 0.5, colors.black), # line between Yes and No
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]

    # Row 0
    data.append(['', '', '', '', Paragraph("<u>For office use only</u>", style_off_top), ''])
    # Row 1
    data.append(['', '', '', '', Paragraph("Complied with", style_off_sub), ''])
    # Row 2
    data.append(['', '', '', '', Paragraph("Yes", style_off_col), Paragraph("No", style_off_col)])

    curr_row = 3
    for idx, it in enumerate(items):
        lines = it.get('lines', [])
        if not lines:
            lines = [
                {'label': 'As per rule ..........', 'val': '-', 'unit': 'mm'},
                {'label': 'As per drawing no. ......', 'val': '-', 'unit': 'mm'}
            ]

        # Item title row
        rule_text = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>{it['rule']}</b>" if it['rule'] else ""
        item_title_p = Paragraph(f"<b>{it['num']}. {it['title']}</b>{rule_text}", style_item_hdr)
        data.append([item_title_p, '', '', '', '', ''])

        item_row_idx = curr_row
        t_styles.append(('SPAN', (0, item_row_idx), (3, item_row_idx)))
        curr_row += 1

        sub_start_idx = curr_row
        req_p = Paragraph(it.get('requirement') or '', style_req)

        for l_idx, ln in enumerate(lines):
            r_req = req_p if l_idx == 0 else ''
            r_lbl = Paragraph(ln.get('label') or 'As per rule ..........', style_lbl)
            r_val = Paragraph(str(ln.get('val') or ''), style_val)
            r_unt = Paragraph(str(ln.get('unit') or 'mm'), style_unt)
            r_yes = Paragraph("&#x25A2;", style_box)
            r_no  = Paragraph("&#x25A2;", style_box)

            data.append([r_req, r_lbl, r_val, r_unt, r_yes, r_no])
            curr_row += 1

        sub_end_idx = curr_row - 1

        if len(lines) > 1:
            t_styles.append(('SPAN', (0, sub_start_idx), (0, sub_end_idx)))

        t_styles.append(('VALIGN', (0, sub_start_idx), (0, sub_end_idx), 'TOP'))
        t_styles.append(('VALIGN', (4, sub_start_idx), (5, sub_end_idx), 'MIDDLE'))
        t_styles.append(('ALIGN', (4, sub_start_idx), (5, sub_end_idx), 'CENTER'))

        # Add gap after each component (except after last item)
        if idx < len(items) - 1 and row_gap > 0:
            data.append(['', '', '', '', '', ''])
            # style padding for gap row
            t_styles.append(('BOTTOMPADDING', (0, curr_row), (-1, curr_row), row_gap))
            t_styles.append(('TOPPADDING', (0, curr_row), (-1, curr_row), 0))
            curr_row += 1

    # Close bottom of right box
    t_styles.append(('LINEBELOW', (4, curr_row - 1), (5, curr_row - 1), 0.75, colors.black))

    t = Table(data, colWidths=col_widths, repeatRows=0)
    t.setStyle(TableStyle(t_styles))
    return t

with open('app/data_extracted.json', encoding='utf-8') as f:
    d = json.load(f)

# Test Page 10
p10 = next(p for p in d.get('application_form_pages', []) if p['page'] == 10)
items10 = parse_audit_page(p10.get('content', []))

buf = io.BytesIO()
doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=28, bottomMargin=55)
story = []

# Header
hdr = Table([
    [Paragraph("1<sup>ST</sup> Edition, March 2007", ParagraphStyle('HdrL', fontName='Helvetica', fontSize=8, leading=10)),
     '',
     Paragraph("Page 9 of 24", ParagraphStyle('HdrR', fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=2))]
], colWidths=[200, 123, 200])
hdr.setStyle(TableStyle([
    ('TOPPADDING', (0,0), (-1,-1), 0),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
]))
story.append(hdr)

story.append(build_pdf_audit_table_noborder(items10, row_gap=5))
doc.build(story)

buf.seek(0)
doc_fitz = fitz.open(stream=buf.read(), filetype='pdf')
print(f"Generated PDF with {len(doc_fitz)} page(s)")
p = doc_fitz[0]
pix = p.get_pixmap(dpi=150)
pix.save(r"C:\Users\MUNNA\.gemini\antigravity\brain\7e18d46f-a07c-4bde-9cf7-ac324cac7605\test_noborder_p10.png")
print("Saved test_noborder_p10.png")

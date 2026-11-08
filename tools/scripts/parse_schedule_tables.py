import os
import re
import json

def parse_schedule_tables():
    md_path = 'rules_markdown/01_scantling_tables_schedule.md'
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split by lines
    lines = text.split('\n')
    
    current_part = {
        'id': 1,
        'name_bn': 'অংশ ১ : হাল প্লেটিং, স্টেম ও স্টার্ন পোস্ট (সারণি ১ হতে ১২)',
        'name_en': 'Part I: Hull Plating, Stem & Stern Frame (Tables 1 - 12)',
        'pages': 'পৃষ্ঠা ১৩৯ – ১৪৩'
    }

    tables = []
    current_table = None
    collecting_table_md = False
    table_lines = []
    collecting_notes = False
    notes_lines = []

    part_pattern = re.compile(r'^##\s+(অংশ\s+(\d+|[০-৯]+)\s*:[^\n]+)')
    table_pattern = re.compile(r'^###\s+(সারণি-([০-৯\d]+(?:\s*\([কখ]\))?)\s*:\s*([^\n]+))')
    sub_pattern = re.compile(r'^\*\((.*?\s*\|\s*(পৃষ্ঠা[^\)]*))\)\*')

    def finalize_table(t, t_lines, n_lines):
        if not t:
            return
        
        # Parse table markdown lines
        headers = []
        rows = []
        header_parsed = False
        
        for l in t_lines:
            l_str = l.strip()
            if not l_str.startswith('|') or not l_str.endswith('|'):
                continue
            cells = [c.strip() for c in l_str[1:-1].split('|')]
            if all(re.match(r'^:?-+:?$', c) for c in cells):
                header_parsed = True
                continue
            if not header_parsed:
                headers = cells
            else:
                rows.append(cells)
                
        t['headers'] = headers
        t['rows'] = rows
        t['notes'] = [n.strip() for n in n_lines if n.strip()]
        tables.append(t)

    for i, line in enumerate(lines):
        line_str = line.strip()
        
        # Check part header
        m_part = part_pattern.match(line_str)
        if m_part:
            # Look ahead for subtitle
            sub_en = ''
            pages_str = ''
            if i + 1 < len(lines):
                next_l = lines[i+1].strip()
                m_sub = sub_pattern.match(next_l)
                if m_sub:
                    sub_en = m_sub.group(1).split('|')[0].strip()
                    pages_str = m_sub.group(2).strip()
            
            p_bn = m_part.group(1).strip()
            # Determine part number
            p_num = len([p for p in tables if p.get('part_id')]) // 10 + 1
            if 'অংশ ১' in p_bn: p_num = 1
            elif 'অংশ ২' in p_bn: p_num = 2
            elif 'অংশ ৩' in p_bn: p_num = 3
            elif 'অংশ ৪' in p_bn: p_num = 4
            elif 'অংশ ৫' in p_bn: p_num = 5
            elif 'অংশ ৬' in p_bn: p_num = 6
            elif 'অংশ ৭' in p_bn: p_num = 7

            current_part = {
                'id': p_num,
                'name_bn': p_bn,
                'name_en': sub_en or f'Part {p_num}',
                'pages': pages_str
            }
            continue

        # Check table header
        m_tab = table_pattern.match(line_str)
        if m_tab:
            # Finalize previous table
            if current_table:
                finalize_table(current_table, table_lines, notes_lines)
                table_lines = []
                notes_lines = []

            tab_num_raw = m_tab.group(2).strip()
            tab_title_bn = m_tab.group(3).strip()

            # English title and page from next line
            tab_title_en = ''
            page_ref = ''
            if i + 1 < len(lines):
                next_l = lines[i+1].strip()
                if next_l.startswith('*(') and next_l.endswith(')*'):
                    inner = next_l[2:-2]
                    parts_inner = inner.split('|')
                    tab_title_en = parts_inner[0].strip()
                    if len(parts_inner) > 1:
                        page_ref = parts_inner[1].strip()

            # Normalize Bengali numerals in ID
            bn_digits = {'০':'0', '১':'1', '২':'2', '৩':'3', '৪':'4', '৫':'5', '৬':'6', '৭':'7', '৮':'8', '৯':'9'}
            tab_id_en = ''
            for ch in tab_num_raw:
                if ch in bn_digits:
                    tab_id_en += bn_digits[ch]
                elif ch in ['ক', 'খ', '(', ')']:
                    if ch == 'ক': tab_id_en += 'a'
                    elif ch == 'খ': tab_id_en += 'b'
                elif ch.isdigit():
                    tab_id_en += ch

            current_table = {
                'id': tab_id_en or tab_num_raw,
                'table_no_bn': tab_num_raw,
                'title_bn': tab_title_bn,
                'title_en': tab_title_en,
                'title': f"সারণি {tab_num_raw} : {tab_title_bn}" + (f" ({tab_title_en})" if tab_title_en else ""),
                'ref': f"বিধিমালা তফসিল • {page_ref}" if page_ref else "বিধিমালা তফসিল",
                'page': page_ref,
                'part_id': current_part['id'],
                'part_name_bn': current_part['name_bn'],
                'part_name_en': current_part['name_en'],
            }
            collecting_table_md = False
            collecting_notes = False
            continue

        if current_table:
            if line_str.startswith('|') and line_str.endswith('|'):
                table_lines.append(line_str)
            elif line_str.startswith('>') or line_str.startswith('*মানসমূহ') or line_str.startswith('✍️'):
                notes_lines.append(line_str.lstrip('>').strip())
            elif line_str.startswith('---'):
                # End of table
                pass

    if current_table:
        finalize_table(current_table, table_lines, notes_lines)

    print(f"Parsed {len(tables)} tables successfully!")
    
    # Save to app/data_extracted_schedule_tables.json
    out_path = 'app/schedule_tables.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(tables, f, ensure_ascii=False, indent=2)
    print(f"Saved to {out_path}")

    # Also update app/data_extracted.json and scantling_data.json
    try:
        data_path = 'app/data_extracted.json'
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            d['empirical_tables'] = tables
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print(f"Updated {data_path} with {len(tables)} tables")
    except Exception as e:
        print(f"Error updating data_extracted.json: {e}")

if __name__ == '__main__':
    parse_schedule_tables()

import sys
sys.stdout.reconfigure(encoding='utf-8')
import openpyxl

path = r"C:\Users\MUNNA\.gemini\antigravity\brain\7e18d46f-a07c-4bde-9cf7-ac324cac7605\.user_uploaded\media_1792995524389_0824a1c7.xlsx"
wb = openpyxl.load_workbook(path, data_only=True)
print("Sheet names:", wb.sheetnames)

for name in wb.sheetnames:
    if 'sheet' in name.lower() or '2' in name:
        ws = wb[name]
        print(f"\n--- {name} ---")
        for r in range(1, 35):
            row_vals = [str(ws.cell(r, c).value or '') for c in range(1, 12)]
            if any(row_vals):
                print(f"Row {r:2d}: {' | '.join(row_vals)}")

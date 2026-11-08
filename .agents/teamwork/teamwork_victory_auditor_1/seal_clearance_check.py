import pymupdf

doc = pymupdf.open("Lightship.pdf")
p2 = doc[1]
# Find drawings and text bounding boxes on page 2
blocks = p2.get_text("blocks")
seal_y0 = None
table_y1 = 0

for b in blocks:
    txt = b[4].strip()
    if "Total Lightship Weight" in txt or "STATUTORY SYNTHESIS" in txt or "1.56" in txt:
        table_y1 = max(table_y1, b[3])
    if "Naval Architect" in txt or "Designer Seal" in txt or "Design Checked By" in txt or "Checked by:" in txt:
        if seal_y0 is None or b[1] < seal_y0:
            seal_y0 = b[1]

print(f"Table bottom y1: {table_y1:.2f} pt")
print(f"Seal top y0: {seal_y0} pt")
if seal_y0:
    clearance = seal_y0 - table_y1
    print(f"Clearance between table and seal: {clearance:.2f} pt")
    assert clearance > 50, f"Insufficient clearance: {clearance} pt"
    print("Clearance check: PASS (clean visual spacing)")
doc.close()

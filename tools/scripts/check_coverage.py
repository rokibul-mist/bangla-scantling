from generate_full_catalog import STRUCTURAL_MEMBERS

# Parse all unique members from vessel_structural_members_3d_list_v5.md
doc_path = r"Resource\vessel_structural_members_3d_list_v5.md"
with open(doc_path, "r", encoding="utf-8") as f:
    text = f.read()

import re

# Extract all table rows across entire document
doc_members = set()
for line in text.splitlines():
    line = line.strip()
    if line.startswith('|') and not line.startswith('|---') and not line.startswith('| #') and not line.startswith('| Member'):
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) >= 2 and parts[0].isdigit():
            doc_members.add(parts[1])

print(f"Total distinct member names in v5 document: {len(doc_members)}")

cat_names = [m['name'].lower() for m in STRUCTURAL_MEMBERS]
cat_ids = [m['id'].lower() for m in STRUCTURAL_MEMBERS]

unmatched = []
for dm in sorted(doc_members):
    dm_clean = re.sub(r'\(.*?\)', '', dm).strip().lower()
    matched = False
    for cn in cat_names:
        if dm_clean in cn or cn in dm_clean:
            matched = True
            break
    if not matched:
        unmatched.append(dm)

print(f"Unmatched document members: {len(unmatched)}")
for u in unmatched:
    print(f"  • {u}")

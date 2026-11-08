import re

doc_path = r"Resource\vessel_structural_members_3d_list_v5.md"
with open(doc_path, "r", encoding="utf-8") as f:
    text = f.read()

# Extract every row in all tables of doc_path
rows = []
for line in text.splitlines():
    line = line.strip()
    if line.startswith('|') and not line.startswith('|---') and not line.startswith('| #') and not line.startswith('| Member'):
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) >= 2 and parts[0].isdigit():
            rows.append({
                'num': parts[0],
                'name': parts[1],
                'table': parts[2] if len(parts) > 2 else ''
            })

# Unique by name
unique_doc = {}
for r in rows:
    name = r['name']
    if name not in unique_doc:
        unique_doc[name] = r

print(f"Total unique documented members: {len(unique_doc)}")
for i, (k, v) in enumerate(unique_doc.items(), 1):
    print(f"{i:3d}. {k:<45} | Table: {v['table']}")

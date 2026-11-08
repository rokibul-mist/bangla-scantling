import re

doc_path = r"Resource\vessel_structural_members_3d_list_v5.md"
with open(doc_path, "r", encoding="utf-8") as f:
    text = f.read()

vessel_blocks = re.findall(r'## (\d+\. [^\n]+)([\s\S]*?)(?=\n## \d+\. |\n\*End of document|\Z)', text)

vessel_members_map = {}

for vb in vessel_blocks:
    name = vb[0].split('(')[0].strip()
    # clean name e.g. "1. Steel Body Cargo Vessel" -> "Steel Body Cargo Vessel"
    vname = re.sub(r'^\d+\.\s*', '', name).strip()
    body = vb[1]
    
    # Extract all rows with digits
    m_list = []
    for line in body.splitlines():
        line = line.strip()
        if line.startswith('|') and not line.startswith('|---') and not line.startswith('| #') and not line.startswith('| Member'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 2 and parts[0].isdigit():
                m_list.append(parts[1])
    vessel_members_map[vname] = m_list
    print(f"'{vname}': {len(m_list)} members defined in document")

# Also Part 1 Hull types
hull_types_map = {
    "Single Hull": [],
    "Double Bottom": [],
    "Double Hull": []
}

# Single Hull: Plating + Stiffeners
sh_match = re.search(r'## 1\. Single Hull[\s\S]*?(?=## 2\. Double Bottom)', text)
if sh_match:
    for line in sh_match.group(0).splitlines():
        line = line.strip()
        if line.startswith('|') and not line.startswith('|---') and not line.startswith('| #') and not line.startswith('| Member'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 2 and parts[0].isdigit():
                hull_types_map["Single Hull"].append(parts[1])

# Double Bottom added
db_match = re.search(r'## 2\. Double Bottom[\s\S]*?(?=## 3\. Double Hull)', text)
if db_match:
    for line in db_match.group(0).splitlines():
        line = line.strip()
        if line.startswith('|') and not line.startswith('|---') and not line.startswith('| #') and not line.startswith('| Member'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 2 and parts[0].isdigit():
                hull_types_map["Double Bottom"].append(parts[1])

# Double Hull added
dh_match = re.search(r'## 3\. Double Hull[\s\S]*?(?=# PART 2:)', text)
if dh_match:
    for line in dh_match.group(0).splitlines():
        line = line.strip()
        if line.startswith('|') and not line.startswith('|---') and not line.startswith('| #') and not line.startswith('| Member'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 2 and parts[0].isdigit():
                hull_types_map["Double Hull"].append(parts[1])

print(f"\nHull Types members in doc:")
print(f"  Single Hull: {len(hull_types_map['Single Hull'])}")
print(f"  Double Bottom (Added): {len(hull_types_map['Double Bottom'])}")
print(f"  Double Hull (Added): {len(hull_types_map['Double Hull'])}")

# -*- coding: utf-8 -*-
"""
Build and synchronize the comprehensive structural catalogs:
1. app/domain/catalog/structural_catalog.py
2. app/structural_catalog.py
3. app/static/js/structural_catalog.js
"""

import json
from generate_full_catalog import STRUCTURAL_MEMBERS

# Ensure every member in catalog has both name/desc and category/group
for m in STRUCTURAL_MEMBERS:
    if "desc" not in m:
        m["desc"] = m["name"]
    if "group" not in m:
        m["group"] = m["category"]

# 1. Generate Python catalog string
py_catalog_content = '''"""
Vessel Structural Members Catalog & Hull Type Rules Engine
Based on statutory Bangladesh Inland Shipping Rules 2001 / SRO 308 / ISO 1976
and Resource/vessel_structural_members_3d_list_v5.md.
"""

# Master Structural Members Catalog
# Every member defines its category, type (plate vs stiffener), governing table,
# applicable hull types, applicable vessel types, welded-on plate mapping,
# and default profile geometry.

STRUCTURAL_MEMBERS = ''' + json.dumps(STRUCTURAL_MEMBERS, indent=4) + '''


def get_active_members(hull_type: str = "Double Bottom", vessel_type: str = "Steel Body Cargo Vessel"):
    """
    Returns the list of active structural members based on hull_type and vessel_type.
    """
    h_clean = "Double Bottom"
    if "single" in (hull_type or "").lower():
        h_clean = "Single Hull"
    elif "double hull" in (hull_type or "").lower():
        h_clean = "Double Hull"

    v_clean = vessel_type or "Steel Body Cargo Vessel"

    active = []
    item_counter = 1
    for m in STRUCTURAL_MEMBERS:
        # Check hull type
        h_app = m.get("applicable_hull_types", ["all"])
        if "all" not in h_app and h_clean not in h_app:
            continue

        # Check vessel type
        v_app = m.get("applicable_vessel_types", ["all"])
        if "all" not in v_app and v_clean not in v_app:
            continue

        item_copy = dict(m)
        item_copy["item"] = item_counter
        item_copy["desc"] = m.get("desc") or m.get("name")
        item_copy["group"] = m.get("group") or m.get("category")
        item_counter += 1
        active.append(item_copy)

    return active
'''

with open("app/domain/catalog/structural_catalog.py", "w", encoding="utf-8") as f:
    f.write(py_catalog_content)

print("Updated app/domain/catalog/structural_catalog.py")

# 2. Update compatibility shim app/structural_catalog.py
py_shim_content = '''"""
Compatibility shim for app.structural_catalog
Re-exports from app.domain.catalog.structural_catalog
"""
from app.domain.catalog.structural_catalog import STRUCTURAL_MEMBERS, get_active_members

__all__ = ["STRUCTURAL_MEMBERS", "get_active_members"]
'''

with open("app/structural_catalog.py", "w", encoding="utf-8") as f:
    f.write(py_shim_content)

print("Updated app/structural_catalog.py")

# 3. Generate JavaScript catalog
js_members_json = json.dumps(STRUCTURAL_MEMBERS, indent=2)
js_catalog_content = f'''/**
 * Vessel Structural Members Catalog & Hull Type Rules Engine (Client-Side)
 * Codifies statutory Bangladesh Inland Shipping Rules 2001 / SRO 308 / ISO 1976
 * and Resource/vessel_structural_members_3d_list_v5.md.
 */

const STRUCTURAL_CATALOG = (function() {{
  const MEMBERS = {js_members_json};

  function getActiveMembers(hullType, vesselType) {{
    let hClean = "Double Bottom";
    const hLower = String(hullType || '').toLowerCase();
    if (hLower.includes('single')) {{
      hClean = "Single Hull";
    }} else if (hLower.includes('double hull')) {{
      hClean = "Double Hull";
    }}

    const vClean = vesselType || "Steel Body Cargo Vessel";

    const active = [];
    let counter = 1;
    MEMBERS.forEach(m => {{
      // Check hull type
      const hApp = m.applicable_hull_types || ["all"];
      if (!hApp.includes("all") && !hApp.includes(hClean)) {{
        return;
      }}

      // Check vessel type
      const vApp = m.applicable_vessel_types || ["all"];
      if (!vApp.includes("all") && !vApp.includes(vClean)) {{
        return;
      }}

      const itemCopy = Object.assign({{}}, m, {{
        item: counter++,
        desc: m.desc || m.name,
        group: m.group || m.category,
        default_profile: m.default_profile ? Object.assign({{}}, m.default_profile) : null
      }});
      active.push(itemCopy);
    }});

    return active;
  }}

  return {{
    MEMBERS,
    getActiveMembers
  }};
}})();

// Export globally
if (typeof window !== 'undefined') {{
  window.STRUCTURAL_CATALOG = STRUCTURAL_CATALOG;
}}
if (typeof module !== 'undefined' && module.exports) {{
  module.exports = STRUCTURAL_CATALOG;
}}
'''

with open("app/static/js/structural_catalog.js", "w", encoding="utf-8") as f:
    f.write(js_catalog_content)

print("Updated app/static/js/structural_catalog.js")

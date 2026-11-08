import json

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

for s in state.get('sheet2_results', [])[:5]:
    print("---", s.get('name'), "---")
    print("table_ref:", s.get('table_ref'))
    deriv = s.get('derivation') or {}
    print("derivation keys:", list(deriv.keys()))
    print("derivation_text:", deriv.get('derivation_text'))
    print("table_no:", deriv.get('table_no'))
    print("formula_desc:", deriv.get('formula_desc'))
    print("baseline:", deriv.get('baseline'), "rreq:", deriv.get('rreq'), "factor:", deriv.get('factor'))
    print("components:", deriv.get('components'))

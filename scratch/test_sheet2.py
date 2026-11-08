import json
from app.services.calculation_service import CalculationService

with open('app/saved_state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

res = CalculationService.compute_all_calculations(state)
s2 = res.get('sheet2_results', [])
print(f"Total sheet2 results: {len(s2)}")
for item in s2:
    print(f"Sheet {item['id']}: {item['name']} ({item['member_id']})")
    print(f"   ptype={item.get('profile_type')}, hw={item.get('web_height')}, tw={item.get('web_thk')}, bf={item.get('flange_width')}, tf={item.get('flange_thk')}")
    print(f"   plate_width={item.get('plate_width')}, plate_thk={item.get('plate_thk')}")
    print(f"   req={item['rreq']}, z_cm3={item['z_cm3']:.2f}, margin={item['margin']:.2f}, status={item['status']}")
    print(f"   ap={item.get('ap')}, aw={item.get('aw')}, af={item.get('af')}, yna={item.get('yna'):.3f}, ina={item.get('ina'):.1f}")

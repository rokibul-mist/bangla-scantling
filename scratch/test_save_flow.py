import urllib.request
import json

payload = {
    "custom_meta": {
        "vessel_name": "M.V. TITAS CARGO - 88",
        "owner": "Titas Shipping Lines",
        "yard_ref": "TSL-2026/102",
        "notes": "Evaluation test of saving vessel from active calculation"
    }
}

req = urllib.request.Request(
    'http://127.0.0.1:8055/api/vessels',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    print("Save Response:", res.get('status'), res.get('message'))
    print("Saved Vessel ID:", res.get('vessel', {}).get('id'))

# Now verify it is in list
req_list = urllib.request.Request('http://127.0.0.1:8055/api/vessels')
with urllib.request.urlopen(req_list) as resp:
    list_res = json.loads(resp.read().decode('utf-8'))
    print("Total vessels in DB now:", list_res.get('total'))
    for v in list_res.get('vessels', []):
        print(f" - {v.get('vessel_name')} ({v.get('vessel_type')}) [ID: {v.get('id')}]")

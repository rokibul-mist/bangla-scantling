import urllib.request
import json

req = urllib.request.Request('http://127.0.0.1:8055/api/vessels')
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print('Status:', data.get('status'), 'Total vessels:', data.get('total'))
        for v in data.get('vessels', []):
            print(f"  {v.get('vessel_name')} [{v.get('id')}]: {v.get('vessel_type')}, L={v.get('particulars', {}).get('lbp')}m")
except Exception as e:
    print("API Error:", e)

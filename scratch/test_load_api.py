import urllib.request
import json

req = urllib.request.Request('http://127.0.0.1:8055/api/vessels/vsl_meghna_express_05/load', data=b'', method='POST')
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    print("Status:", res.get('status'))
    print("Vessel Name:", res.get('state', {}).get('dashboard_inputs', {}).get('vessel_name'))
    print("LBP:", res.get('state', {}).get('dashboard_inputs', {}).get('lbp'))

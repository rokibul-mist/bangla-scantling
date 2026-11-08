import urllib.request
import json

req_del = urllib.request.Request(
    'http://127.0.0.1:8055/api/vessels/vsl_5795e674e861',
    method='DELETE'
)
with urllib.request.urlopen(req_del) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    print("Delete Response:", res)

req_list = urllib.request.Request('http://127.0.0.1:8055/api/vessels')
with urllib.request.urlopen(req_list) as resp:
    list_res = json.loads(resp.read().decode('utf-8'))
    print("Total vessels in DB now:", list_res.get('total'))

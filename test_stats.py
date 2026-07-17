
import urllib.request
import json

req = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/login/', data=json.dumps({'username': 'superadmin', 'password': 'Aymen123'}).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
res = urllib.request.urlopen(req)
token = json.loads(res.read().decode('utf-8'))['access']

req2 = urllib.request.Request('http://127.0.0.1:8000/api/v1/admin/stats/', headers={'Authorization': 'Bearer ' + token})
res2 = urllib.request.urlopen(req2)
print(json.dumps(json.loads(res2.read().decode('utf-8')), indent=2))


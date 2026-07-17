
import urllib.request
import urllib.parse
from http.cookiejar import CookieJar
import json

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def run_test(name, payload):
    req = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/login/', data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
    try:
        res = opener.open(req)
        print(f'{name} Status:', res.getcode())
        print(f'{name} Content:', res.read().decode('utf-8'))
    except Exception as e:
        print(f'{name} Exception:', e.read().decode('utf-8') if hasattr(e, 'read') else e)

run_test('Test 1 (username superadmin)', {'username': 'superadmin', 'password': 'Aymen123'})
run_test('Test 2 (username email)', {'username': 'superadmin@fitna.dz', 'password': 'Aymen123'})
run_test('Test 3 (email field)', {'email': 'superadmin@fitna.dz', 'password': 'Aymen123'})
run_test('Test 4 (email field superadmin)', {'email': 'superadmin', 'password': 'Aymen123'})


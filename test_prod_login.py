import urllib.request, json

BASE = 'https://fitna-backend-production.up.railway.app/api/v1'

creds = [
    ('aymenbounehidja047@gmail.com', 'Admin1234'),
    ('aymenbounehidja047@gmail.com', 'FitnaAdmin2025!'),
    ('superadmin@fitna.dz', 'Admin1234'),
    ('superadmin@fitna.dz', 'FitnaAdmin2025!'),
    ('admin@fitna.dz', 'Admin1234'),
    ('admin_memory@fitna.dz', 'Admin1234'),
    ('admin_memory@fitna.dz', 'FitnaAdmin2025!'),
    ('aymen.bounehidja@gmail.com', 'Admin1234'),
]

for email, pwd in creds:
    try:
        login_data = json.dumps({'username': email, 'password': pwd}).encode()
        req = urllib.request.Request(BASE + '/auth/login/', data=login_data, headers={'Content-Type': 'application/json'})
        r = urllib.request.urlopen(req, timeout=15)
        tokens = json.loads(r.read())
        role = tokens.get('role', '?')
        name = tokens.get('full_name', '?')
        print('SUCCESS:', email, '/ pwd:', pwd, '=> role:', role, 'name:', repr(name))
        with open('prod_token.txt', 'w', encoding='utf-8') as f:
            f.write(tokens.get('access', ''))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print('FAIL:', email, '=> HTTP', e.code, body[:80])
    except Exception as e:
        print('ERROR:', email, '=>', str(e)[:80])

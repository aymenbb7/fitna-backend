import urllib.request, json

BASE = 'https://fitna-backend-production.up.railway.app/api/v1'

# Login as super admin
login_data = json.dumps({'username': 'superadmin@fitna.dz', 'password': 'Admin1234'}).encode()
req = urllib.request.Request(BASE + '/auth/login/', data=login_data, headers={'Content-Type': 'application/json'})
r = urllib.request.urlopen(req, timeout=15)
tokens = json.loads(r.read())
token = tokens.get('access', '')
headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}

assignments = [
    ('quran',           2),
    ('memory',          3),
    ('soroban',         4),
    ('problem-solving', 5),
    ('health',          6),
    ('history',         7),
    ('languages',       8),
    ('talents',         9),
    ('psychology',      10),
]

results = []

for slug, user_id in assignments:
    url = BASE + f'/admin/modules/{slug}/assign-admin/'
    data = json.dumps({'user_id': user_id}).encode()
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        r = urllib.request.urlopen(req, timeout=15)
        resp = json.loads(r.read())
        results.append({'slug': slug, 'user_id': user_id, 'status': 'OK', 'resp': resp})
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        results.append({'slug': slug, 'user_id': user_id, 'status': f'HTTP {e.code}', 'resp': body})
    except Exception as e:
        results.append({'slug': slug, 'user_id': user_id, 'status': 'ERROR', 'resp': str(e)})

# Verify current state
req2 = urllib.request.Request(BASE + '/admin/modules/', headers={'Authorization': 'Bearer ' + token})
r2 = urllib.request.urlopen(req2, timeout=15)
modules_after = json.loads(r2.read())

with open('fix_results.txt', 'w', encoding='utf-8') as f:
    f.write('=== ASSIGNMENT RESULTS ===\n')
    for r in results:
        f.write(f"slug={r['slug']} user_id={r['user_id']} status={r['status']} resp={str(r['resp'])[:120]}\n")
    f.write('\n=== MODULES AFTER FIX ===\n')
    for m in modules_after:
        f.write(f"ID:{m.get('id')} Slug:{m.get('slug')} Admin:{m.get('admin')} Students:{m.get('student_count')}\n")

print('Done. Results in fix_results.txt')

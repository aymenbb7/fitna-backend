import urllib.request, json, time

BASE = 'https://fitna-backend-production.up.railway.app/api/v1'

# Login as memory admin (MODULE_ADMIN)
login_data = json.dumps({'username': 'abderrahimsakeur@gmail.com', 'password': 'Admin1234'}).encode()
req = urllib.request.Request(BASE + '/auth/login/', data=login_data, headers={'Content-Type': 'application/json'})
r = urllib.request.urlopen(req, timeout=10)
tokens = json.loads(r.read())
token = tokens.get('access', '')
headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
print('Logged in, role:', tokens.get('role'))

# Check my modules (the key test)
req = urllib.request.Request(BASE + '/admin/modules/', headers={'Authorization': 'Bearer ' + token})
r = urllib.request.urlopen(req, timeout=10)
modules = json.loads(r.read())
with open('module_admin_modules.txt', 'w', encoding='utf-8') as f:
    f.write(f'=== MODULES VISIBLE TO ADMIN (USER: {tokens.get("full_name")}) ===\n')
    f.write(f'Count: {len(modules)}\n\n')
    for m in modules:
        f.write(f"ID:{m.get('id')} Slug:{m.get('slug')} Name:{m.get('name')} Admin:{m.get('admin')} Students:{m.get('student_count')} Price:{m.get('price')}\n")

print(f'Modules visible: {len(modules)}')

# Test create-by-admin endpoint
test_email2 = f'module_admin_test_{int(time.time())}@test.com'
payload = json.dumps({
    'email': test_email2,
    'full_name': 'Module Admin Created Student',
    'password': 'test12345',
    'module_slugs': ['memory'],
    'payments': [{'module_slug': 'memory', 'method': 'CASH'}]
}).encode()

try:
    req = urllib.request.Request(BASE + '/admin/students/create-by-admin/', data=payload, headers=headers, method='POST')
    r = urllib.request.urlopen(req, timeout=15)
    resp = json.loads(r.read())
    student_id = resp.get('student', {}).get('id')
    print(f'create-by-admin: student ID={student_id}')
    with open('module_admin_modules.txt', 'a', encoding='utf-8') as f:
        f.write(f'\n=== CREATE-BY-ADMIN RESULT ===\n')
        f.write(f'Status: 201 OK\nStudent ID: {student_id}\nEmail: {test_email2}\n')
        f.write(f'Enrolled: {[m["slug"] for m in resp.get("student", {}).get("enrolled_modules", [])]}\n')
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    print(f'create-by-admin FAILED: HTTP {e.code}: {body[:200]}')
    with open('module_admin_modules.txt', 'a', encoding='utf-8') as f:
        f.write(f'\ncreate-by-admin FAILED: HTTP {e.code}: {body}\n')
except Exception as ex:
    print(f'create-by-admin ERROR: {ex}')

print('Done. See module_admin_modules.txt')

import urllib.request, json

BASE = 'https://fitna-backend-production.up.railway.app/api/v1'

# Login
login_data = json.dumps({'username': 'superadmin@fitna.dz', 'password': 'Admin1234'}).encode()
req = urllib.request.Request(BASE + '/auth/login/', data=login_data, headers={'Content-Type': 'application/json'})
r = urllib.request.urlopen(req, timeout=15)
tokens = json.loads(r.read())
token = tokens.get('access', '')
headers = {'Authorization': 'Bearer ' + token}
print('Logged in as:', tokens.get('full_name'), 'role:', tokens.get('role'))

def get(path):
    req = urllib.request.Request(BASE + path, headers=headers)
    r = urllib.request.urlopen(req, timeout=15)
    return json.loads(r.read())

# Get all users
print('\n=== PRODUCTION USERS (MODULE_ADMIN) ===')
users = get('/admin/users/')
module_admins = [u for u in users if u.get('role') == 'MODULE_ADMIN']
with open('prod_db.txt', 'w', encoding='utf-8') as f:
    f.write('=== PRODUCTION MODULE_ADMIN USERS ===\n')
    for u in module_admins:
        f.write(f"ID: {u['id']}, Email: {u['email']}, Name: {u.get('full_name','')}, Role: {u['role']}\n")
    
    # Get all modules
    f.write('\n=== PRODUCTION MODULES ===\n')
    modules = get('/admin/modules/')
    for m in modules:
        f.write(f"ID: {m.get('id','?')}, Slug: {m.get('slug','')}, Name: {m.get('name','')}, Admin: {m.get('admin','?')}\n")
    
    f.write('\n=== ALL USERS ===\n')
    for u in users:
        f.write(f"ID: {u['id']}, Email: {u['email']}, Name: {u.get('full_name','')}, Role: {u['role']}\n")

print('Done. Wrote prod_db.txt')
print('Module admins count:', len(module_admins))
print('Modules count:', len(modules))
for m in modules:
    print(' -', m.get('slug'), '| admin:', m.get('admin'))

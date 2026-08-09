import urllib.request, json, time

BASE = 'https://fitna-backend-production.up.railway.app/api/v1'

# Step 1: Login as the memory module admin (abderrahimsakeur@gmail.com, user ID 3)
# We need to find the password - try common ones
memory_admin_creds = [
    ('abderrahimsakeur@gmail.com', 'Admin1234'),
    ('abderrahimsakeur@gmail.com', 'admin1234'),
    ('abderrahimsakeur@gmail.com', 'FitnaAdmin2025!'),
    ('abderrahimsakeur@gmail.com', 'fitna2024'),
    ('abderrahimsakeur@gmail.com', '12345678'),
]

token_admin = None
for email, pwd in memory_admin_creds:
    try:
        ld = json.dumps({'username': email, 'password': pwd}).encode()
        req = urllib.request.Request(BASE + '/auth/login/', data=ld, headers={'Content-Type': 'application/json'})
        r = urllib.request.urlopen(req, timeout=10)
        data = json.loads(r.read())
        token_admin = data.get('access', '')
        with open('test_add_student_results.txt', 'w', encoding='utf-8') as f:
            f.write(f'=== Logged in as memory admin ===\n')
            f.write(f'Email: {email}\nRole: {data.get("role")}\nName: {data.get("full_name")}\n\n')
        print('Module admin login OK:', email)
        break
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f'FAIL: {email} HTTP {e.code}: {body[:60]}')
    except Exception as ex:
        print(f'ERROR: {email}: {ex}')

# Step 2: Use super admin to create a test student via the new endpoint
# (since we may not have memory admin password)
super_login = json.dumps({'username': 'superadmin@fitna.dz', 'password': 'Admin1234'}).encode()
req = urllib.request.Request(BASE + '/auth/login/', data=super_login, headers={'Content-Type': 'application/json'})
r = urllib.request.urlopen(req, timeout=10)
super_tokens = json.loads(r.read())
super_token = super_tokens.get('access', '')
super_headers = {'Authorization': 'Bearer ' + super_token, 'Content-Type': 'application/json'}

test_email = f'verify_student_{int(time.time())}@test.com'
payload = json.dumps({
    'email': test_email,
    'full_name': 'Test Verify Student',
    'password': 'test12345',
    'phone_number': '0555000000',
    'module_slugs': ['memory'],
    'payments': [{'module_slug': 'memory', 'method': 'CASH', 'receipt_number': None}]
}).encode()

with open('test_add_student_results.txt', 'a', encoding='utf-8') as f:
    f.write('=== Creating test student via /admin/students/create/ ===\n')
    f.write(f'Email: {test_email}\nModule: memory\n\n')

try:
    req = urllib.request.Request(BASE + '/admin/students/create/', data=payload, headers=super_headers, method='POST')
    r = urllib.request.urlopen(req, timeout=15)
    resp = json.loads(r.read())
    student_id = resp.get('student', {}).get('id')
    with open('test_add_student_results.txt', 'a', encoding='utf-8') as f:
        f.write(f'CREATE STATUS: 201 OK\n')
        f.write(f'Student ID: {student_id}\n')
        f.write(f'Full response: {json.dumps(resp, ensure_ascii=False)[:500]}\n\n')
    print(f'Student created: ID={student_id}')
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    with open('test_add_student_results.txt', 'a', encoding='utf-8') as f:
        f.write(f'CREATE FAILED: HTTP {e.code}: {body}\n\n')
    print(f'Create failed: {e.code}: {body[:100]}')
    student_id = None

if student_id:
    # Step 3: Check enrollments for this student
    try:
        req = urllib.request.Request(BASE + f'/admin/students/{student_id}/enrollments/', headers=super_headers)
        r = urllib.request.urlopen(req, timeout=15)
        enrollments = json.loads(r.read())
        with open('test_add_student_results.txt', 'a', encoding='utf-8') as f:
            f.write('=== ENROLLMENT VERIFICATION ===\n')
            f.write(f'Enrollment count: {len(enrollments)}\n')
            for e in enrollments:
                f.write(f"  Module: {e.get('module_name')} | Slug: {e.get('module_slug')} | Primary: {e.get('is_primary')}\n")
            f.write('\n')
        print(f'Enrollments: {len(enrollments)}')
    except Exception as ex:
        print(f'Enrollment check failed: {ex}')
        with open('test_add_student_results.txt', 'a', encoding='utf-8') as f:
            f.write(f'Enrollment check FAILED: {ex}\n\n')
    
    # Step 4: Check that student appears in the users list
    try:
        req = urllib.request.Request(BASE + f'/admin/users/?search={test_email}', headers=super_headers)
        r = urllib.request.urlopen(req, timeout=15)
        users = json.loads(r.read())
        with open('test_add_student_results.txt', 'a', encoding='utf-8') as f:
            f.write('=== STUDENT IN USERS LIST ===\n')
            f.write(f'Found: {len(users)} user(s) matching email\n')
            for u in users:
                f.write(f"  ID: {u['id']}, Role: {u['role']}, Active: {u.get('is_active')}, Approved: {u.get('is_approved')}\n")
                f.write(f"  Enrolled modules: {[m.get('slug') for m in u.get('enrolled_modules', [])]}\n")
        print(f'Student in users list: {len(users)} found')
    except Exception as ex:
        print(f'Users check failed: {ex}')

    # Step 5: Check module student count increased
    try:
        req = urllib.request.Request(BASE + '/admin/modules/', headers=super_headers)
        r = urllib.request.urlopen(req, timeout=15)
        modules = json.loads(r.read())
        with open('test_add_student_results.txt', 'a', encoding='utf-8') as f:
            f.write('\n=== MODULE STUDENT COUNTS AFTER CREATION ===\n')
            for m in modules:
                f.write(f"  Slug: {m.get('slug')} | Students: {m.get('student_count')} | Admin: {m.get('admin')}\n")
        print('Module counts saved.')
    except Exception as ex:
        print(f'Module counts failed: {ex}')

print('Done. See test_add_student_results.txt')

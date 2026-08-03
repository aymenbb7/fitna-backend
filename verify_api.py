import requests

# Login as student - SimpleJWT expects 'username' field (backend maps email->username)
login_data = {'username': 'student@test.com', 'password': 'student123'}
r = requests.post('http://127.0.0.1:8000/api/v1/auth/login/', json=login_data)
print('Login status:', r.status_code)
data = r.json()
token = data.get('access')
if not token:
    print('Login failed:', data)
    exit()

print('Got token! Role:', data.get('role'))
print('Enrolled modules:', [m['slug'] for m in data.get('enrolled_modules', [])])
print()

headers = {'Authorization': f'Bearer {token}'}

# Check each enrolled module
for mod in data.get('enrolled_modules', []):
    slug = mod['slug']
    print(f'=== MODULE: {slug} ===')
    r2 = requests.get(f'http://127.0.0.1:8000/api/v1/modules/{slug}/sections/', headers=headers)
    print(f'  Sections status: {r2.status_code}')
    if r2.status_code != 200:
        print(f'  Error: {r2.text[:200]}')
        continue
    sections = r2.json()
    print(f'  Sections count: {len(sections)}')
    for sec in sections:
        for les in sec.get('lessons', []):
            vids = les.get("videos", [])
            docs = les.get("documents", [])
            voice = les.get("voice_messages", [])
            photos = les.get("photos", [])
            total = len(vids) + len(docs) + len(voice) + len(photos)
            if total > 0:
                print(f'  Lesson: {les["title"]} | videos={len(vids)} docs={len(docs)} voice={len(voice)} photos={len(photos)}')
                for v in vids:
                    print(f'    VIDEO: {v.get("title")} -> file={v.get("video_file")} url={v.get("video_url")}')
                for d in docs:
                    print(f'    DOC: {d.get("title")} -> file={d.get("document_file")} url={d.get("file_url")}')
                for vm in voice:
                    print(f'    VOICE: {vm.get("title")} -> file={vm.get("audio_file")}')
                for p in photos:
                    print(f'    PHOTO: {p.get("title")} -> file={p.get("image_file")}')

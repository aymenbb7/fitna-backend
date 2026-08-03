import requests

def test():
    # Login
    r = requests.post('http://127.0.0.1:8000/api/v1/auth/login/', json={'username': 'student@test.com', 'password': 'student123'})
    token = r.json().get('access')
    if not token:
        print("Login failed")
        return
        
    headers = {'Authorization': f'Bearer {token}'}
    
    # Let's get the list of documents first to find the ID of the PDF
    r_docs = requests.get('http://127.0.0.1:8000/api/v1/modules/quran/documents/', headers=headers)
    docs = r_docs.json()
    if docs:
        doc_id = docs[0]['id']
        # Try downloading
        print(f"Testing download for doc {doc_id}...")
        r_dl = requests.get(f'http://127.0.0.1:8000/api/v1/modules/quran/documents/{doc_id}/download/', headers=headers)
        print("Status:", r_dl.status_code)
        print("Content-Type:", r_dl.headers.get('Content-Type'))
        print("Content-Disposition:", r_dl.headers.get('Content-Disposition'))
        if r_dl.status_code == 200:
            print("Download endpoint works!")
        else:
            print("Download failed:", r_dl.text)
    else:
        print("No documents found.")

test()

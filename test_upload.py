import requests
import json
import os

BASE_URL = 'http://127.0.0.1:8000/api/v1'

def login():
    res = requests.post(f'{BASE_URL}/auth/login/', json={
        'username': 'su2',
        'password': '123'
    })
    try:
        data = res.json()
        print("Login response:", data)
        return data.get('access')
    except:
        print("Login failed:", res.status_code, res.text)
        return None

def create_module_and_lesson(token):
    headers = {'Authorization': f'Bearer {token}'}
    # 1. Create module
    res = requests.post(f'{BASE_URL}/admin/modules/create/', json={
        'name': 'Upload Test Module',
        'slug': 'upload-test-module',
        'price': 100
    }, headers=headers)
    
    if res.status_code != 200 and 'already exists' not in res.text:
        print("Failed to create module:", res.status_code, res.text)
    
    # 2. Create section
    res = requests.post(f'{BASE_URL}/modules/upload-test-module/sections/', json={
        'title': 'Test Section'
    }, headers=headers)
    try:
        section_id = res.json().get('id')
    except:
        print("Failed to create section:", res.status_code, res.text)
        return None
    
    # 3. Create lesson
    res = requests.post(f'{BASE_URL}/modules/upload-test-module/lessons/', json={
        'title': 'Test Lesson',
        'section': section_id
    }, headers=headers)
    try:
        return res.json().get('id')
    except:
        print("Failed to create lesson:", res.status_code, res.text)
        return None

def test_upload(token, lesson_id):
    headers = {'Authorization': f'Bearer {token}'}
    
    # Create a dummy pdf file
    with open('test_dummy.pdf', 'wb') as f:
        f.write(b'%PDF-1.4 dummy content')

    print('Uploading PDF...')
    with open('test_dummy.pdf', 'rb') as f:
        res = requests.post(f'{BASE_URL}/modules/upload-test-module/documents/', data={
            'title': 'Test Upload PDF',
            'lesson': lesson_id,
            'doc_type': 'PDF'
        }, files={
            'document_file': ('test_dummy.pdf', f, 'application/pdf')
        }, headers=headers)
        
    print('Status:', res.status_code)
    try:
        print('Response:', res.json())
    except:
        print('Response Text:', res.text)
    
    os.remove('test_dummy.pdf')

if __name__ == '__main__':
    try:
        token = login()
        if token:
            print("Logged in!")
            lesson_id = create_module_and_lesson(token)
            if lesson_id:
                print(f"Created lesson {lesson_id}")
                test_upload(token, lesson_id)
            else:
                print("Failed to get lesson ID")
        else:
            print("Failed to login.")
    except Exception as e:
        print("Error:", e)

import requests

# Login to get token
login_data = {
    'username': 'admin',
    'password': '123'
}
res = requests.post('http://127.0.0.1:8000/api/v1/auth/login/', json=login_data)
if res.status_code != 200:
    print("Login failed", res.text)
    exit(1)

token = res.json()['access']

# Create module
headers = {
    'Authorization': f'Bearer {token}'
}
data = {
    'name': 'Test Module',
    'slug': 'test-module'
}
res = requests.post('http://127.0.0.1:8000/api/v1/admin/modules/create/', json=data, headers=headers)
print(res.status_code)
print(res.text)

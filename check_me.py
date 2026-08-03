import requests

def test_me():
    base_url = "http://127.0.0.1:8000/api/v1"
    
    # Login as admin
    resp = requests.post(f"{base_url}/auth/login/", json={
        "username": "admin@fitna.com",
        "password": "admin"
    })
    
    if resp.status_code != 200:
        print("Login failed:", resp.json())
        return
        
    data = resp.json()
    token = data.get("access")
    print("Login success, role:", data.get("role"))
    
    # Get /me
    me_resp = requests.get(f"{base_url}/auth/me/", headers={"Authorization": f"Bearer {token}"})
    print("Me response:", me_resp.json())

if __name__ == "__main__":
    test_me()

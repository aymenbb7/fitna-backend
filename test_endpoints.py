import requests
import sys

BASE_URL = "http://127.0.0.1:9090/api/v1"

def test_modules():
    r = requests.get(f"{BASE_URL}/modules/")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert len(data) == 9, f"Expected 9 modules, got {len(data)}"
    print("Test 1 Passed: GET /api/v1/modules/ returned 9 modules.")

def test_register():
    r = requests.post(f"{BASE_URL}/auth/register/", json={
        "email": "student@test.com",
        "password": "test1234",
        "full_name": "Test Student",
        "module_slug": "quran"
    })
    assert r.status_code == 201, f"Expected 201, got {r.status_code} - {r.text}"
    data = r.json()
    assert data['is_approved'] is False, "Expected is_approved to be False"
    print("Test 2 Passed: POST /api/v1/auth/register/ returned success + is_approved: false")

def test_login_admin():
    r = requests.post(f"{BASE_URL}/auth/login/", json={
        "email": "admin@fitna.dz",
        "password": "FitnaAdmin2025!"
    })
    assert r.status_code == 200, f"Expected 200, got {r.status_code} - {r.text}"
    data = r.json()
    assert "access" in data, "Expected access token"
    assert data["role"] == "SUPER_ADMIN", "Expected SUPER_ADMIN role"
    print("Test 3 Passed: POST /api/v1/auth/login/ returned access token + role: SUPER_ADMIN")

if __name__ == "__main__":
    try:
        test_modules()
        test_register()
        test_login_admin()
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test Failed: {e}")
        sys.exit(1)

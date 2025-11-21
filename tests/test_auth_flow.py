import requests
import sys

DASHBOARD_URL = "http://localhost:5004"

def test_auth_flow():
    print("Testing Auth Flow...")
    
    # 1. Try to access protected endpoint without token
    print("1. Accessing protected endpoint without token...")
    try:
        res = requests.post(f"{DASHBOARD_URL}/settings", json={"season_mode": "summer"})
        if res.status_code == 401:
            print("PASS: Access denied as expected (401).")
        else:
            print(f"FAIL: Expected 401, got {res.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Connection error: {e}")
        return False

    # 2. Login
    print("2. Logging in...")
    token = None
    try:
        res = requests.post(f"{DASHBOARD_URL}/api/login", json={"username": "user", "password": "password"})
        if res.status_code == 200:
            data = res.json()
            token = data.get("token")
            if token:
                print("PASS: Login successful, token received.")
            else:
                print("FAIL: Login successful but no token returned.")
                return False
        else:
            print(f"FAIL: Login failed. Status: {res.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Connection error: {e}")
        return False

    # 3. Access protected endpoint WITH token
    print("3. Accessing protected endpoint WITH token...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.post(f"{DASHBOARD_URL}/settings", json={"season_mode": "summer"}, headers=headers)
        if res.status_code == 200:
            print("PASS: Access granted.")
            return True
        else:
            print(f"FAIL: Expected 200, got {res.status_code}. Response: {res.text}")
            return False
    except Exception as e:
        print(f"FAIL: Connection error: {e}")
        return False

if __name__ == "__main__":
    success = test_auth_flow()
    sys.exit(0 if success else 1)

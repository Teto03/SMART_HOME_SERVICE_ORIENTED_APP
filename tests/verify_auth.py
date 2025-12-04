import requests
import time
import os
import sys

# Configuration
AUTH_SERVICE_URL = "http://localhost:5010"
DASHBOARD_URL = "http://localhost:5004"

def test_auth_flow():
    print("Starting Auth Flow Test...")
    
    # 1. Register a new user
    username = f"testuser_{int(time.time())}"
    password = "securepassword123"
    
    print(f"Attempting to register user: {username}")
    try:
        # We test via the Dashboard Proxy to ensure full flow works
        res = requests.post(f"{DASHBOARD_URL}/api/register", json={
            "username": username,
            "password": password
        })
        
        if res.status_code == 201:
            print("✅ Registration successful")
        else:
            print(f"❌ Registration failed: {res.status_code} - {res.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration exception: {e}")
        return False

    # 2. Login with the new user
    print("Attempting to login...")
    token = None
    try:
        res = requests.post(f"{DASHBOARD_URL}/api/login", json={
            "username": username,
            "password": password
        })
        
        if res.status_code == 200:
            data = res.json()
            token = data.get("token")
            if token:
                print("✅ Login successful, token received")
            else:
                print("❌ Login successful but no token received")
                return False
        else:
            print(f"❌ Login failed: {res.status_code} - {res.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login exception: {e}")
        return False

    # 3. Verify Token (Directly with Auth Service)
    print("Verifying token...")
    try:
        res = requests.post(f"{AUTH_SERVICE_URL}/verify", json={"token": token})
        
        if res.status_code == 200 and res.json().get("valid"):
            print("✅ Token verification successful")
        else:
            print(f"❌ Token verification failed: {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print(f"❌ Verification exception: {e}")
        return False

    # 4. Test Invalid Login
    print("Testing invalid login...")
    try:
        res = requests.post(f"{DASHBOARD_URL}/api/login", json={
            "username": username,
            "password": "wrongpassword"
        })
        
        if res.status_code == 401:
            print("✅ Invalid login correctly rejected")
        else:
            print(f"❌ Invalid login should fail but got: {res.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invalid login exception: {e}")
        return False

    print("\n🎉 All Auth Tests Passed!")
    return True

if __name__ == "__main__":
    # Ensure services are running (manual check required or assume running)
    if test_auth_flow():
        sys.exit(0)
    else:
        sys.exit(1)

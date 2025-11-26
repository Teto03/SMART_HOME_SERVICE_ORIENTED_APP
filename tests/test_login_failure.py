import requests
import hashlib

AUTH_URL = "http://localhost:5000/api/login"

def test_login():
    username = "user"
    password = "password"
    
    # 1. Verify Hash
    expected_hash = hashlib.sha256(password.encode()).hexdigest()
    print(f"Password: {password}")
    print(f"Hash: {expected_hash}")
    
    # 2. Try Login
    payload = {"username": username, "password": password}
    print(f"Sending payload: {payload}")
    
    try:
        res = requests.post(AUTH_URL, json=payload)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()

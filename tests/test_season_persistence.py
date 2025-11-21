import requests
import time
import sys

DASHBOARD_URL = "http://localhost:5004"

def test_season_persistence():
    print("Testing Season Persistence...")
    
    # 1. Set Season to Winter
    print("1. Setting season to 'winter'...")
    try:
        res = requests.post(f"{DASHBOARD_URL}/settings", json={"season_mode": "winter"})
        if res.status_code != 200:
            print(f"FAIL: Could not set settings. Status: {res.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Connection error: {e}")
        return False

    # 2. Get Home Status and check season_mode
    print("2. Fetching home status...")
    try:
        res = requests.get(f"{DASHBOARD_URL}/api/home_status")
        if res.status_code != 200:
            print(f"FAIL: Could not get home status. Status: {res.status_code}")
            return False
        
        data = res.json()
        # The bug is that 'season_mode' is likely missing or wrong
        season_mode = data.get("season_mode")
        print(f"   Received season_mode: {season_mode}")
        
        if season_mode == "winter":
            print("PASS: Season mode persisted and returned correctly.")
            return True
        else:
            print(f"FAIL: Expected 'winter', got '{season_mode}'")
            return False
            
    except Exception as e:
        print(f"FAIL: Connection error: {e}")
        return False

if __name__ == "__main__":
    success = test_season_persistence()
    sys.exit(0 if success else 1)

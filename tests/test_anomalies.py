import requests
import json
import sys

# Default URL for Anomaly Service (ensure your Docker container is mapped to this port)
URL = "http://localhost:5003/analyze"

def test_fire_risk():
    print("\n--- Testing FIRE RISK (> 50°C) ---")
    payload = {
        "temp": 55.0,
        "devices": []
    }
    try:
        res = requests.post(URL, json=payload)
        print(f"Input: {payload}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_high_temp():
    print("\n--- Testing HIGH TEMP (> 28°C) ---")
    payload = {
        "temp": 30.0,
        "devices": []
    }
    try:
        res = requests.post(URL, json=payload)
        print(f"Input: {payload}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_conflict():
    print("\n--- Testing CONFLICT (AC + Heater ON) ---")
    payload = {
        "temp": 20.0,
        "devices": [
            {"id": "air_conditioner", "type": "ac", "status": "ON", "value": 1.0},
            {"id": "smart_heater_1", "type": "heater", "status": "ON", "value": 1.0}
        ]
    }
    try:
        res = requests.post(URL, json=payload)
        print(f"Input: {json.dumps(payload, indent=2)}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_waste():
    print("\n--- Testing ENERGY WASTE (Window OPEN + AC ON) ---")
    payload = {
        "temp": 20.0,
        "devices": [
            {"id": "air_conditioner", "type": "ac", "status": "ON", "value": 1.0},
            {"id": "living_room_window", "type": "window", "status": "OPEN", "value": 1.0}
        ]
    }
    try:
        res = requests.post(URL, json=payload)
        print(f"Input: {json.dumps(payload, indent=2)}")
        print(f"Response: {json.dumps(res.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Targeting Anomaly Service at {URL}")
    test_fire_risk()
    test_high_temp()
    test_conflict()
    test_waste()

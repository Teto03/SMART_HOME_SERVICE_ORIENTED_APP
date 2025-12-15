import requests
import os
import time
import random
import sys

DATA_SERVICE_URL = os.environ.get("DATA_SERVICE_URL", "http://localhost:5001")

def simulate_sensor(device_id, device_type, min_val, max_val):
    print(f"Starting simulation for {device_id} ({device_type})...")
    
    # Register device first - retry until successful
    registered = False
    while not registered:
        try:
            requests.post(f"{DATA_SERVICE_URL}/devices", json={
                "device_id": device_id,
                "type": device_type,
                "status": "active"
            }, timeout=2)
            registered = True
            print(f"Registered {device_id}")
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print(f"Data Service not reachable for {device_id}. Retrying in 2s...")
            time.sleep(2)

    while True:
        value = round(random.uniform(min_val, max_val), 2)
        payload = {
            "device_id": device_id,
            "value": value,
            "timestamp": time.time()
        }
        
        try:
            res = requests.post(f"{DATA_SERVICE_URL}/readings", json=payload)
            if res.status_code == 201:
                print(f"Sent {device_id}: {value}")
            else:
                print(f"Error sending data: {res.text}")
        except Exception as e:
            print(f"Connection error: {e}")
            
        time.sleep(60)

if __name__ == "__main__":
    # Run simulations in separate threads
    import threading

    # 1. Temperature Sensor (Random data)
    t1 = threading.Thread(target=simulate_sensor, args=("temp_sensor_01", "temperature", 18.0, 25.0))
    t1.start()

    # 2. Register controllable devices (Windows, Heater, AC)
    # We don't loop random values for these to avoid overwriting user commands constantly.
    # 2. Register controllable devices (Windows, Heater, AC)
    # We don't loop random values for these to avoid overwriting user commands constantly.
    # Retry loop for these devices as well
    devices_to_register = [
        {"device_id": "living_room_window", "type": "window", "status": "CLOSED"},
        {"device_id": "bedroom_window", "type": "window", "status": "CLOSED"},
        {"device_id": "kitchen_window", "type": "window", "status": "CLOSED"},
        {"device_id": "smart_heater_1", "type": "heater", "status": "OFF"},
        {"device_id": "main_heater", "type": "heater", "status": "OFF"},
        {"device_id": "air_conditioner", "type": "ac", "status": "OFF"}
    ]

    for device in devices_to_register:
        registered = False
        while not registered:
            try:
                requests.post(f"{DATA_SERVICE_URL}/devices", json=device, timeout=2)
                print(f"Registered {device['device_id']}")
                registered = True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                print(f"Data Service not reachable for {device['device_id']}. Retrying in 2s...")
                time.sleep(2)
    
    print("All controllable devices registered.")

    t1.join()

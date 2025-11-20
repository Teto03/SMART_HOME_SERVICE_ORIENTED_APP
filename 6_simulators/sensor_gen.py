import requests
import time
import random
import sys

DATA_SERVICE_URL = "http://localhost:5001"

def simulate_sensor(device_id, device_type, min_val, max_val):
    print(f"Starting simulation for {device_id} ({device_type})...")
    
    # Register device first
    try:
        requests.post(f"{DATA_SERVICE_URL}/devices", json={
            "device_id": device_id,
            "type": device_type,
            "status": "active"
        })
    except requests.exceptions.ConnectionError:
        print("Data Service not reachable. Retrying...")
        return

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
            
        time.sleep(5)

if __name__ == "__main__":
    # Run simulations in separate threads
    import threading

    # 1. Temperature Sensor (Random data)
    t1 = threading.Thread(target=simulate_sensor, args=("temp_sensor_01", "temperature", 18.0, 25.0))
    t1.start()

    # 2. Register controllable devices (Windows, Heater, AC)
    # We don't loop random values for these to avoid overwriting user commands constantly.
    try:
        # Windows (3 total)
        requests.post(f"{DATA_SERVICE_URL}/devices", json={"device_id": "living_room_window", "type": "window", "status": "CLOSED"})
        requests.post(f"{DATA_SERVICE_URL}/devices", json={"device_id": "bedroom_window", "type": "window", "status": "CLOSED"})
        requests.post(f"{DATA_SERVICE_URL}/devices", json={"device_id": "kitchen_window", "type": "window", "status": "CLOSED"})
        
        # HVAC Systems
        requests.post(f"{DATA_SERVICE_URL}/devices", json={"device_id": "smart_heater_1", "type": "heater", "status": "OFF"})
        requests.post(f"{DATA_SERVICE_URL}/devices", json={"device_id": "air_conditioner", "type": "ac", "status": "OFF"})
        
        print("Registered 3 Windows, Heater, and AC.")
    except Exception as e:
        print(f"Could not register extra devices: {e}")

    t1.join()

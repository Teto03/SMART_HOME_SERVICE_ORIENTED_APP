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

    # 2. Window Sensor (Initially Closed=0)
    # We don't loop random values for window/heater to avoid overwriting user commands constantly.
    # But we register them.
    try:
        requests.post(f"{DATA_SERVICE_URL}/devices", json={"device_id": "living_room_window", "type": "window", "status": "CLOSE"})
        requests.post(f"{DATA_SERVICE_URL}/devices", json={"device_id": "main_heater", "type": "heater", "status": "OFF"})
        print("Registered Window and Heater.")
    except:
        print("Could not register extra devices.")

    t1.join()

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
    # Default simulation: Temperature Sensor
    # Can be extended to run multiple threads or processes
    simulate_sensor("temp_sensor_01", "temperature", 18.0, 25.0)

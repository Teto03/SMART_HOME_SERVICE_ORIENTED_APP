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

    # 1. Temperature Sensor (Random data w/ spikes)
    def temp_behavior(t_id):
        # Normal range 18-25, but 10% chance of spike > 30 for testing alerts
        while True:
            base_temp = random.uniform(8.0, 25.0)
            if random.random() < 0.15: # 15% spike probability
                base_temp = random.uniform(30.0, 35.0)
                
            simulate_sensor_step(t_id, base_temp)
            time.sleep(5)

    t1 = threading.Thread(target=simulate_sensor, args=("temp_sensor_01", "temperature", 18.0, 25.0))
    # We will override the target for t1 to use a smarter function allowing spikes, 
    # but to keep it simple with existing structure, let's just use the simulate_sensor with a wider range 
    # OR create a dedicated function. Given the instruction to "Occasionally generate high values", 
    # let's write a dedicated simulator function for flexible behavior.
    
    def smart_sensor_loop(device_id, device_type, min_val, max_val, spike_prob=0.0):
        print(f"Starting simulation for {device_id}...")
        register_device(device_id, device_type, "active") # Extract register logic if needed or just use raw req
        
        while True:
            val = round(random.uniform(min_val, max_val), 2)
            # Spike logic
            if spike_prob > 0 and random.random() < spike_prob:
                 val = round(random.uniform(max_val, max_val + 10), 2)
                 
            send_reading(device_id, val)
            time.sleep(10) # Faster updates for testing: 10s default? User said "every minute" for smoke.

    # Refactoring slightly to allow easier reuse.
    # But to minimize diffs, let's just start Threads with inline lambdas or new functions if possible.
    # Actually, I'll rewrite the main block to be cleaner.

    t1 = threading.Thread(target=simulate_sensor, args=("temp_sensor_01", "temperature", 18.0, 32.0)) 
    # Changed max to 32 to ensure we hit > 28 occasionally. 
    t1.start()

    # 1.5 Smoke Sensor
    def smoke_sensor_loop():
        d_id = "smoke_sensor_01"
        print(f"Starting simulation for {d_id}...")
        
        # Register
        requests.post(f"{DATA_SERVICE_URL}/devices", json={"device_id": d_id, "type": "smoke_sensor", "status": "SAFE"})
        
        last_val = 0
        
        while True:
            # Default 0 (Clear)
            val = 0
            # 5% chance of Fire (1)
            if random.random() < 0.05:
                val = 1
                print(f"!!! SMOKE DETECTED GENERATED for {d_id} !!!")
                
            try:
                # Send Reading
                requests.post(f"{DATA_SERVICE_URL}/readings", json={
                    "device_id": d_id, "value": val, "timestamp": time.time()
                })
                
                # Update Status if changed
                if val != last_val:
                    new_status = "SMOKE" if val == 1 else "SAFE"
                    requests.post(f"{DATA_SERVICE_URL}/devices", json={
                        "device_id": d_id, "type": "smoke_sensor", "status": new_status
                    })
                    last_val = val
                    
            except Exception as e: 
                print(f"Error in smoke sim: {e}")
            
            time.sleep(60)

    t_smoke = threading.Thread(target=smoke_sensor_loop)
    t_smoke.start()

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
        {"device_id": "air_conditioner", "type": "ac", "status": "OFF"},
        {"device_id": "smoke_sensor_01", "type": "smoke_sensor", "status": "active"}
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

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
        # Instead of generating locally, call the simulation endpoint
        try:
            res = requests.post(f"{DATA_SERVICE_URL}/devices/simulate_reading", json={"device_id": device_id})
            if res.status_code == 200:
                print(f"Triggered simulation for {device_id}: {res.json().get('value')}")
            else:
                print(f"Error triggering simulation: {res.text}")
        except Exception as e:
            print(f"Connection error: {e}")
            
        time.sleep(60)

if __name__ == "__main__":
    # Run simulations in separate threads
    import threading

    def temp_behavior(t_id):
        while True:
            base_temp = random.uniform(8.0, 25.0)
            if random.random() < 0.15: # 15% spike probability
                base_temp = random.uniform(30.0, 35.0)
                
            simulate_sensor_step(t_id, base_temp)
            time.sleep(5)

    t1 = threading.Thread(target=simulate_sensor, args=("temp_sensor_01", "temperature", 18.0, 25.0))
    
    def smart_sensor_loop(device_id, device_type, min_val, max_val, spike_prob=0.0):
        print(f"Starting simulation for {device_id}...")
        register_device(device_id, device_type, "active") 
        
        while True:
            val = round(random.uniform(min_val, max_val), 2)
            # Spike logic
            if spike_prob > 0 and random.random() < spike_prob:
                 val = round(random.uniform(max_val, max_val + 10), 2)
                 
            send_reading(device_id, val)
            time.sleep(10) 

    t1 = threading.Thread(target=simulate_sensor, args=("temp_sensor_01", "temperature", 18.0, 32.0)) 
    t1.start()

    def smoke_sensor_loop():
        d_id = "smoke_sensor_01"
        print(f"Starting simulation for {d_id}...")
        
        # Register
        requests.post(f"{DATA_SERVICE_URL}/devices", json={"device_id": d_id, "type": "smoke_sensor", "status": "SAFE"})
        
        last_val = 0
        
        while True:
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

import requests
import os
import time
import threading

# Service URLs
# Service URLs
DATA_SERVICE_URL = os.environ.get("DATA_SERVICE_URL", "http://localhost:5001")
ANOMALY_SERVICE_URL = os.environ.get("ANOMALY_SERVICE_URL", "http://localhost:5003")
TELEGRAM_ADAPTER_URL = os.environ.get("TELEGRAM_ADAPTER_URL", "http://localhost:5005")

# State tracking to avoid spam
last_alert_state = {
    "temp_high": False,
    "fire_risk": False,
    "conflict": False,
    "waste": False,
    "devices": {} # Track device status for change notifications
}

def monitor_loop():
    global last_alert_state
    print("Alert Process Started (Orchestrator Mode)...")
    
    while True:
        try:
            # 1. Orchestration Step A: Fetch Data from Data Service
            devices_data = []
            temp_val = None
            
            try:
                # Fetch all devices
                res_devices = requests.get(f"{DATA_SERVICE_URL}/devices")
                if res_devices.status_code == 200:
                   devices_list = res_devices.json()
                   
                   # Hydrate with latest readings
                   for dev in devices_list:
                       d_id = dev.get("id")
                       try: 
                           # Get latest reading for each device
                           r_res = requests.get(f"{DATA_SERVICE_URL}/readings/latest?device_id={d_id}")
                           if r_res.status_code == 200:
                               reading = r_res.json()
                               dev["value"] = reading.get("value")
                               dev["status"] = reading.get("status")
                               dev["timestamp"] = reading.get("timestamp")
                               
                               if dev.get("type") == "temperature":
                                   temp_val = dev.get("value")
                                   
                               devices_data.append(dev)
                       except:
                           pass
            except Exception as e:
                print(f"Error fetching data: {e}")
                time.sleep(2)
                continue

            # 2. Orchestration Step B: Send Data to Anomaly Detection Service (Business Logic)
            try:
                payload = {
                    "temp": temp_val,
                    "devices": devices_data
                }
                res_analysis = requests.post(f"{ANOMALY_SERVICE_URL}/analyze", json=payload)
                analysis = {}
                if res_analysis.status_code == 200:
                    analysis = res_analysis.json()
                else:
                    print(f"Anomaly Service returned {res_analysis.status_code}")
            except Exception as e:
                print(f"Error calling Anomaly Service: {e}")
                analysis = {"has_anomaly": False, "anomalies": []}


            # 3. Orchestration Step C: Process Results & Notify (Telegram Adapter)
            
            # --- Device State Change Notifications (Kept local as it's UI/Feedback related, not strict 'anomaly') ---
            # (Preserving original useful feedback logic)
            for dev in devices_data:
                d_id = dev.get("id")
                d_type = dev.get("type")
                if d_type == "temperature": continue
                
                val = dev.get("value")
                status = dev.get("status")
                
                # Determine logical state
                is_active = (val == 1.0) or (status in ["ON", "OPEN"])
                current_label = "OPEN" if d_type == "window" else "ON"
                if not is_active:
                     current_label = "CLOSED" if d_type == "window" else "OFF"
                
                last_label = last_alert_state["devices"].get(d_id)
                
                if last_label and current_label != last_label:
                    print(f"[{d_id}] State Change: {last_label} -> {current_label}")
                    msg = f"INFO: {d_id.replace('_', ' ').title()} is now {current_label}."
                    # If it turned ON/OPEN, make it look like an alert/notice
                    if is_active:
                        prefix = "SECURITY CHECK:" if d_type == "window" else "ENERGY CHECK:"
                        msg = f"{prefix} {d_id.replace('_', ' ').title()} is {current_label}!"
                    
                    try:
                        requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={"message": msg})
                    except: pass
                
                last_alert_state["devices"][d_id] = current_label


            # --- Anomaly Alerts (Driven by Business Service) ---
            current_anomalies = analysis.get("anomalies", [])
            
            # Reset flags for current loop
            found_high_temp = False
            found_fire = False
            found_conflict = False
            found_waste = False
            
            for anomaly in current_anomalies:
                a_type = anomaly.get("type")
                msg = anomaly.get("message")
                
                if a_type == "FIRE":
                    found_fire = True
                    if not last_alert_state["fire_risk"]:
                        print(f"Sending FIRE alert: {msg}")
                        requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={"message": msg})
                        last_alert_state["fire_risk"] = True
                        
                elif a_type == "HIGH_TEMP":
                    found_high_temp = True
                    if not last_alert_state["temp_high"] and not last_alert_state["fire_risk"]: # Don't spam if fire
                        print(f"Sending Temp alert: {msg}")
                        requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={"message": msg})
                        last_alert_state["temp_high"] = True

                elif a_type == "CONFLICT":
                    found_conflict = True
                    if not last_alert_state["conflict"]:
                        print(f"Sending Conflict alert: {msg}")
                        requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={"message": msg})
                        last_alert_state["conflict"] = True
                        
                elif a_type == "WASTE":
                    found_waste = True
                    if not last_alert_state["waste"]:
                        print(f"Sending Waste alert: {msg}")
                        requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={"message": msg})
                        last_alert_state["waste"] = True

            # Clear states if conditions resolved
            if not found_fire: last_alert_state["fire_risk"] = False
            if not found_high_temp: last_alert_state["temp_high"] = False
            
            if not found_conflict and last_alert_state["conflict"]:
                print("Conflict resolved.")
                requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={"message": "✅ Device conflict resolved."})
                last_alert_state["conflict"] = False
                
            if not found_waste and last_alert_state["waste"]:
                print("Waste resolved.")
                requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={"message": "✅ Energy waste condition resolved."})
                last_alert_state["waste"] = False

        except Exception as e:
            print(f"Error in monitor loop: {e}")
        
        time.sleep(2)

if __name__ == '__main__':
    monitor_loop()

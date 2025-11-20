import requests
import time
import threading

# Service URLs
DATA_SERVICE_URL = "http://localhost:5001"
ANALYTICS_SERVICE_URL = "http://localhost:5003"
TELEGRAM_ADAPTER_URL = "http://localhost:5005"

# State tracking
last_alert_state = {
    "temp": None,
    "anomaly": None,
    "living_room_window": "CLOSED",
    "bedroom_window": "CLOSED",
    "kitchen_window": "CLOSED",
    "smart_heater_1": "OFF",
    "main_heater": "OFF",
    "ac": "OFF"
}

def monitor_loop():
    global last_alert_state
    print("Alert Process Started...")
    
    while True:
        try:
            # 1. Check Temperature (Sensor)
            try:
                res = requests.get(f"{DATA_SERVICE_URL}/readings/latest?device_id=temp_sensor_01")
                if res.status_code == 200:
                    data = res.json()
                    temp = data.get("value")
                    
                    if temp is not None:
                        # High Temp Alert
                        if temp > 28.0 and last_alert_state["temp"] != "HIGH":
                            print(f"ALERT: High Temperature detected: {temp} C")
                            requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={
                                "message": f"ALERT: High Temperature detected: {temp:.1f} C"
                            })
                            last_alert_state["temp"] = "HIGH"
                        elif temp < 28.0 and last_alert_state["temp"] == "HIGH":
                            last_alert_state["temp"] = "NORMAL"
            except Exception as e:
                print(f"Error checking temp: {e}")

            # 2. Dynamic Device Monitoring
            try:
                # Fetch all devices
                res_devices = requests.get(f"{DATA_SERVICE_URL}/devices")
                if res_devices.status_code == 200:
                    devices = res_devices.json()
                    
                    for device in devices:
                        dev_id = device.get("id")
                        dev_type = device.get("type")
                        
                        # Skip sensors, only monitor actuators
                        if dev_type == "temperature":
                            continue
                            
                        # Get latest reading/status
                        try:
                            res_reading = requests.get(f"{DATA_SERVICE_URL}/readings/latest?device_id={dev_id}")
                            if res_reading.status_code == 200:
                                reading_data = res_reading.json()
                                val = reading_data.get("value")
                                status_str = reading_data.get("status")
                                
                                # Determine logical state (ON/OPEN vs OFF/CLOSED)
                                is_active = False
                                active_label = "ON"
                                inactive_label = "OFF"
                                
                                if dev_type == "window":
                                    is_active = (val == 1.0) or (status_str == "OPEN")
                                    active_label = "OPEN"
                                    inactive_label = "CLOSED"
                                elif dev_type in ["heater", "ac"]:
                                    is_active = (val == 1.0) or (status_str == "ON")
                                    active_label = "ON"
                                    inactive_label = "OFF"
                                
                                # Check for state change
                                last_state = last_alert_state.get(dev_id)
                                
                                # Initialize if unknown (assume inactive to avoid startup spam, or fetch current)
                                if last_state is None:
                                    last_alert_state[dev_id] = active_label if is_active else inactive_label
                                    continue # Skip notification on first run
                                
                                current_label = active_label if is_active else inactive_label
                                
                                if current_label != last_state:
                                    print(f"[{dev_id}] STATE CHANGE: {last_state} -> {current_label}")
                                    
                                    # Build Message
                                    dev_name = dev_id.replace("_", " ").title()
                                    msg = ""
                                    
                                    if is_active:
                                        if dev_type == "window":
                                            msg = f"SECURITY ALERT: {dev_name} is {active_label}!"
                                        else:
                                            msg = f"ENERGY ALERT: {dev_name} is {active_label}!"
                                    else:
                                        msg = f"INFO: {dev_name} is now {inactive_label}."
                                    
                                    requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={"message": msg})
                                    last_alert_state[dev_id] = current_label

                        except Exception as e:
                            print(f"Error checking device {dev_id}: {e}")
                            
            except Exception as e:
                print(f"Error fetching devices list: {e}")

            # 3. Complex Logic (AC + Boiler Conflict) - Keep this specific check
            # ... (Logic for specific conflict check can remain or be adapted)
            # For now, let's keep the conflict check simple by querying specific devices if needed, 
            # or relying on the state we just updated.
            
            # Let's re-implement the conflict check using the updated last_alert_state
            ac_on = last_alert_state.get("air_conditioner") == "ON"
            # Check if ANY heater is ON
            heater_on = False
            for key, val in last_alert_state.items():
                if "heater" in key and val == "ON":
                    heater_on = True
                    break
            
            if ac_on and heater_on:
                 if last_alert_state.get("anomaly") != "CONFLICT":
                     print("CRITICAL: AC and HEATER are BOTH ON!")
                     requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={
                        "message": "CRITICAL ENERGY WASTE: Air Conditioner and Heater are BOTH ON! Please turn one off."
                    })
                     last_alert_state["anomaly"] = "CONFLICT"
            elif (not ac_on or not heater_on) and last_alert_state.get("anomaly") == "CONFLICT":
                 last_alert_state["anomaly"] = None

            # 8. Check Energy Waste (Windows Open + HVAC On)
            # Identify open windows
            open_windows = [k for k, v in last_alert_state.items() if "window" in k and v == "OPEN"]
            # Identify active HVAC (Heaters or AC)
            active_hvac = [k for k, v in last_alert_state.items() if k in ["smart_heater_1", "main_heater", "air_conditioner"] and v == "ON"]
            
            if open_windows and active_hvac:
                if last_alert_state.get("waste_alert") != "ACTIVE":
                    hvac_names = ", ".join([d.replace("_", " ").title() for d in active_hvac])
                    win_names = ", ".join([w.replace("_", " ").title() for w in open_windows])
                    msg = f"⚠️ ENERGY WASTE: {hvac_names} is ON while {win_names} is OPEN!"
                    print(f"ALERT: {msg}")
                    requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={"message": msg})
                    last_alert_state["waste_alert"] = "ACTIVE"
            else:
                if last_alert_state.get("waste_alert") == "ACTIVE":
                    print("INFO: Energy waste condition resolved.")
                    requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={
                        "message": "✅ Energy waste condition resolved."
                    })
                    last_alert_state["waste_alert"] = "CLEARED"

        except Exception as e:
            print(f"Error in monitor loop: {e}")
        
        time.sleep(1)  # Check every 1 second for faster alerts

if __name__ == '__main__':
    # Run as a standalone script or service
    monitor_loop()

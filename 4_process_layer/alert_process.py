import requests
import time
import threading

# Service URLs
DATA_SERVICE_URL = "http://localhost:5001"
ANALYTICS_SERVICE_URL = "http://localhost:5003"
TELEGRAM_ADAPTER_URL = "http://localhost:5005"

# State tracking
last_alert_state = {
    "living_room_window": None,
    "bedroom_window": None,
    "kitchen_window": None,
    "boiler": None,
    "ac": None,
    "anomaly": None
}

def monitor_loop():
    print("Starting Alert Monitor Loop...")
    print(f"Monitoring boiler and window status every 1 second...")
    while True:
        try:
            # 1. Get latest data
            res = requests.get(f"{DATA_SERVICE_URL}/readings/latest?device_id=temp_sensor_01")
            if res.status_code == 200:
                data = res.json()
                value = data.get("value")
                
                # 2. Check for anomalies
                payload = {"device_type": "temperature", "value": value}
                res_analytics = requests.post(f"{ANALYTICS_SERVICE_URL}/analyze", json=payload)
                
                if res_analytics.status_code == 200:
                    analytics_data = res_analytics.json()
                    if analytics_data.get("has_anomalies"):
                        anomalies = analytics_data.get("anomalies", [])
                        current_anomaly = str(anomalies)
                        
                        # Only alert if anomaly is new or different
                        if last_alert_state["anomaly"] != current_anomaly:
                            for anomaly in anomalies:
                                print(f"ANOMALY DETECTED: {anomaly}")
                                requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={
                                    "message": f"ALERT: {anomaly} (Value: {value})"
                                })
                            last_alert_state["anomaly"] = current_anomaly
                    else:
                        last_alert_state["anomaly"] = None
            
            # 4. Check All Windows Status
            windows = ["living_room_window", "bedroom_window", "kitchen_window"]
            for window_id in windows:
                try:
                    res_window = requests.get(f"{DATA_SERVICE_URL}/readings/latest?device_id={window_id}")
                    if res_window.status_code == 200:
                        win_data = res_window.json()
                        # Check for OPEN status
                        is_open = win_data.get("value") == 1.0 or win_data.get("status") == "OPEN"
                        
                        if is_open and last_alert_state[window_id] != "OPEN":
                            window_name = window_id.replace("_", " ").title()
                            print(f"ALERT: {window_name} is OPEN!")
                            requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={
                                "message": f"SECURITY ALERT: {window_name} is OPEN!"
                            })
                            last_alert_state[window_id] = "OPEN"
                        elif not is_open:
                            last_alert_state[window_id] = "CLOSED"
                except Exception as e:
                    print(f"Error checking {window_id}: {e}")

            # 5. Check Boiler Status
            res_boiler = requests.get(f"{DATA_SERVICE_URL}/readings/latest?device_id=smart_heater_1")
            if res_boiler.status_code == 200:
                boiler_data = res_boiler.json()
                val = boiler_data.get("value")
                status = boiler_data.get("status")
                
                is_on = (val == 1.0) or (status == "ON")
                
                # Debug logging for state tracking
                current_state = "ON" if is_on else "OFF"
                print(f"[BOILER] Current: {current_state}, Last: {last_alert_state['boiler']}, Value: {val}, Status: {status}")
                
                if is_on and last_alert_state["boiler"] != "ON":
                     print(f"[BOILER] STATE CHANGE DETECTED: {last_alert_state['boiler']} -> ON")
                     print("ALERT: Boiler is ON!")
                     requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={
                        "message": "ENERGY ALERT: Boiler is ON!"
                    })
                     last_alert_state["boiler"] = "ON"
                elif not is_on and last_alert_state["boiler"] != "OFF":
                    print(f"[BOILER] STATE CHANGE DETECTED: {last_alert_state['boiler']} -> OFF")
                    last_alert_state["boiler"] = "OFF"
            
            # 6. Check AC Status
            res_ac = requests.get(f"{DATA_SERVICE_URL}/readings/latest?device_id=air_conditioner")
            if res_ac.status_code == 200:
                ac_data = res_ac.json()
                val = ac_data.get("value")
                status = ac_data.get("status")
                
                is_on = (val == 1.0) or (status == "ON")
                
                if is_on and last_alert_state["ac"] != "ON":
                     print("ALERT: AC is ON!")
                     requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={
                        "message": "ENERGY ALERT: Air Conditioner is ON!"
                    })
                     last_alert_state["ac"] = "ON"
                elif not is_on and last_alert_state["ac"] != "OFF":
                    last_alert_state["ac"] = "OFF"
            
            # 7. Check for critical wastage: AC + Boiler both ON
            if last_alert_state["boiler"] == "ON" and last_alert_state["ac"] == "ON":
                # Only alert once when this state is first detected
                if not last_alert_state.get("ac_boiler_conflict"):
                    print("CRITICAL ALERT: AC and Boiler both ON!")
                    requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={
                        "message": "⚠️ CRITICAL ENERGY WASTE: AC and Boiler are BOTH ON! Turn one off immediately!"
                    })
                    last_alert_state["ac_boiler_conflict"] = True
            else:
                last_alert_state["ac_boiler_conflict"] = False


        except Exception as e:
            print(f"Error in monitor loop: {e}")
            
        time.sleep(1)  # Check every 1 second for faster alerts

if __name__ == '__main__':
    # Run as a standalone script or service
    monitor_loop()

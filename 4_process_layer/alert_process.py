import requests
import time
import threading

# Service URLs
DATA_SERVICE_URL = "http://localhost:5001"
ANALYTICS_SERVICE_URL = "http://localhost:5003"
TELEGRAM_ADAPTER_URL = "http://localhost:5005"

# State tracking
last_alert_state = {
    "window": None,
    "boiler": None,
    "anomaly": None
}

def monitor_loop():
    print("Starting Alert Monitor Loop...")
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
            
            # 4. Check Window Status
            res_window = requests.get(f"{DATA_SERVICE_URL}/readings/latest?device_id=living_room_window")
            if res_window.status_code == 200:
                win_data = res_window.json()
                # Check for OPEN status
                is_open = win_data.get("value") == 1.0 or win_data.get("status") == "OPEN"
                
                if is_open and last_alert_state["window"] != "OPEN":
                    print("ALERT: Window is OPEN!")
                    requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={
                        "message": "SECURITY ALERT: Living Room Window is OPEN!"
                    })
                    last_alert_state["window"] = "OPEN"
                elif not is_open:
                    last_alert_state["window"] = "CLOSED"

            # 5. Check Boiler Status
            res_boiler = requests.get(f"{DATA_SERVICE_URL}/readings/latest?device_id=smart_heater_1")
            if res_boiler.status_code == 200:
                boiler_data = res_boiler.json()
                # Strict check for ON status
                # Some devices might return "off" or 0.0, so we ensure we only match positive ON indicators
                val = boiler_data.get("value")
                status = boiler_data.get("status")
                
                is_on = (val == 1.0) or (status == "ON")
                
                if is_on and last_alert_state["boiler"] != "ON":
                     print("ALERT: Boiler is ON!")
                     requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={
                        "message": "ENERGY ALERT: Boiler is ON!"
                    })
                     last_alert_state["boiler"] = "ON"
                elif not is_on:
                    last_alert_state["boiler"] = "OFF"

        except Exception as e:
            print(f"Error in monitor loop: {e}")
            
        time.sleep(2)  # Check every 2 seconds for faster alerts

if __name__ == '__main__':
    # Run as a standalone script or service
    monitor_loop()

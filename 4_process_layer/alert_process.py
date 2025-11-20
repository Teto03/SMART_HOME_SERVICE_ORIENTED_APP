import requests
import time
import threading

# Service URLs
DATA_SERVICE_URL = "http://localhost:5001"
ANALYTICS_SERVICE_URL = "http://localhost:5003"
TELEGRAM_ADAPTER_URL = "http://localhost:5005"

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
                        for anomaly in anomalies:
                            print(f"ANOMALY DETECTED: {anomaly}")
                            # 3. Send Alert
                            requests.post(f"{TELEGRAM_ADAPTER_URL}/send_message", json={
                                "message": f"ALERT: {anomaly} (Value: {value})"
                            })
        except Exception as e:
            print(f"Error in monitor loop: {e}")
            
        time.sleep(10)

if __name__ == '__main__':
    # Run as a standalone script or service
    monitor_loop()

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Service URLs
DATA_SERVICE_URL = "http://localhost:5001"
ADAPTER_SERVICE_URL = "http://localhost:5002"
BUSINESS_SERVICE_URL = "http://localhost:5006"

@app.route('/api/home_status', methods=['GET'])
def get_home_status():
    response_data = {
        "system_status": "online",
        "data": {},
        "alerts": [],
        "advice": ""
    }
    
    # 1. Get Indoor Temp
    indoor_temp = None
    try:
        res = requests.get(f"{DATA_SERVICE_URL}/readings/latest?device_id=temp_sensor_01")
        if res.status_code == 200:
            data = res.json()
            indoor_temp = data.get("value")
            response_data["data"]["indoor_temp"] = indoor_temp
            response_data["data"]["last_update"] = data.get("timestamp")
        else:
            response_data["alerts"].append("Sensor data unavailable")
    except:
        response_data["alerts"].append("Data Service unreachable")

    # 2. Get Outdoor Temp
    outdoor_temp = None
    try:
        res = requests.get(f"{ADAPTER_SERVICE_URL}/current_weather?city=Milan")
        if res.status_code == 200:
            data = res.json()
            outdoor_temp = data.get("temp_c")
            response_data["data"]["outdoor_temp"] = outdoor_temp
            response_data["data"]["weather_condition"] = data.get("condition")
        else:
            response_data["alerts"].append("Weather data unavailable")
    except:
        response_data["alerts"].append("Weather Adapter unreachable")

    # 3. Get Energy Advice
    if indoor_temp is not None and outdoor_temp is not None:
        try:
            payload = {"indoor_temp": indoor_temp, "outdoor_temp": outdoor_temp}
            res = requests.post(f"{BUSINESS_SERVICE_URL}/optimize_energy", json=payload)
            if res.status_code == 200:
                data = res.json()
                response_data["advice"] = data.get("message")
                response_data["action_required"] = data.get("should_act")
        except:
            response_data["alerts"].append("Business Service unreachable")
            
    return jsonify(response_data)

if __name__ == '__main__':
    print("Starting Dashboard Process on port 5004...")
    app.run(host='0.0.0.0', port=5004, debug=True)

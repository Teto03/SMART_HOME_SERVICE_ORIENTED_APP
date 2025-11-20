import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Service URLs
DATA_SERVICE_URL = "http://localhost:5001"
ADAPTER_SERVICE_URL = "http://localhost:5002"
BUSINESS_SERVICE_URL = "http://localhost:5006"

# Global settings
current_season_mode = "auto"

@app.route('/settings', methods=['POST'])
def update_settings():
    global current_season_mode
    data = request.json
    if 'season_mode' in data:
        current_season_mode = data['season_mode']
    return jsonify({"status": "updated", "season_mode": current_season_mode})

@app.route('/api/home_status', methods=['GET'])
def get_home_status():
    city = request.args.get('city', 'Milan')
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
        res = requests.get(f"{ADAPTER_SERVICE_URL}/current_weather?city={city}")
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
            # Fetch all window states
            window_states = {}
            windows = ["living_room_window", "bedroom_window", "kitchen_window"]
            for window_id in windows:
                try:
                    res_window = requests.get(f"{DATA_SERVICE_URL}/readings/latest?device_id={window_id}")
                    if res_window.status_code == 200:
                        win_data = res_window.json()
                        window_status = win_data.get("status", "UNKNOWN")
                        if window_status == "UNKNOWN":
                            val = win_data.get("value")
                            window_status = "OPEN" if val == 1.0 else "CLOSED" if val == 0.0 else "UNKNOWN"
                        window_states[window_id] = window_status
                    else:
                        window_states[window_id] = "UNKNOWN"
                except:
                    window_states[window_id] = "UNKNOWN"
            
            # Fetch boiler status
            boiler_status = 'UNKNOWN'
            try:
                res_boiler = requests.get(f"{DATA_SERVICE_URL}/readings/latest?device_id=smart_heater_1")
                if res_boiler.status_code == 200:
                    boiler_data = res_boiler.json()
                    boiler_status = boiler_data.get("status", "UNKNOWN")
                    if boiler_status == "UNKNOWN":
                        val = boiler_data.get("value")
                        boiler_status = "ON" if val == 1.0 else "OFF" if val == 0.0 else "UNKNOWN"
            except:
                pass
            
            # Fetch AC status
            ac_status = 'UNKNOWN'
            try:
                res_ac = requests.get(f"{DATA_SERVICE_URL}/readings/latest?device_id=air_conditioner")
                if res_ac.status_code == 200:
                    ac_data = res_ac.json()
                    ac_status = ac_data.get("status", "UNKNOWN")
                    if ac_status == "UNKNOWN":
                        val = ac_data.get("value")
                        ac_status = "ON" if val == 1.0 else "OFF" if val == 0.0 else "UNKNOWN"
            except:
                pass
            
            payload = {
                "indoor_temp": indoor_temp, 
                "outdoor_temp": outdoor_temp,
                "window_states": window_states,
                "boiler_status": boiler_status,
                "ac_status": ac_status,
                "season_mode": current_season_mode # Pass season_mode to the optimizer
            }
            res = requests.post(f"{BUSINESS_SERVICE_URL}/optimize_energy", json=payload)
            if res.status_code == 200:
                data = res.json()
                response_data["advice"] = data.get("message")
                response_data["action_required"] = data.get("should_act")
                response_data["efficiency_score"] = data.get("efficiency_score")
                response_data["energy_details"] = data.get("details")
                response_data["season"] = data.get("season")
                response_data["windows_open_count"] = data.get("windows_open_count")
        except:
            response_data["alerts"].append("Business Service unreachable")
            
    return jsonify(response_data)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    try:
        res = requests.get(f"{DATA_SERVICE_URL}/devices")
        if res.status_code == 200:
            return jsonify(res.json())
        else:
            return jsonify({"error": "Could not fetch devices"}), 500
    except:
        return jsonify({"error": "Data Service unreachable"}), 500

@app.route('/api/devices/command', methods=['POST'])
def send_command():
    try:
        # Proxy the command to Data Service
        res = requests.post(f"{DATA_SERVICE_URL}/devices/command", json=request.json)
        return jsonify(res.json()), res.status_code
    except:
        return jsonify({"error": "Data Service unreachable"}), 500

if __name__ == '__main__':
    print("Starting Dashboard Process on port 5004...")
    app.run(host='0.0.0.0', port=5004, debug=True)

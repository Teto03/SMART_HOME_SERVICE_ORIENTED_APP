from flask import Flask, render_template, jsonify, request
import os
import requests

app = Flask(__name__)

# Process Layer URL
# Process Layer URL
DASHBOARD_PROCESS_URL = os.environ.get("DASHBOARD_PROCESS_URL", "http://localhost:5004/api/home_status")
PROCESS_BASE_URL = os.environ.get("PROCESS_BASE_URL", "http://localhost:5004")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    # Proxy request to Process Layer
    try:
        city = request.args.get('city', 'Milan')
        res = requests.get(f"{DASHBOARD_PROCESS_URL}?city={city}")
        if res.status_code == 200:
            return jsonify(res.json())
        else:
            return jsonify({"error": "Error fetching data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/devices')
def get_devices():
    try:
        # Proxy to Process Layer
        res = requests.get(f"{PROCESS_BASE_URL}/api/devices")
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/devices/command', methods=['POST'])
def send_command():
    try:
        # Proxy to Process Layer
        res = requests.post(f"{PROCESS_BASE_URL}/api/devices/command", json=request.json, headers=request.headers)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login_proxy():
    try:
        res = requests.post(f"{PROCESS_BASE_URL}/api/login", json=request.json)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/settings', methods=['POST'])
def settings_proxy():
    try:
        res = requests.post(f"{PROCESS_BASE_URL}/settings", json=request.json, headers=request.headers)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Web App on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)

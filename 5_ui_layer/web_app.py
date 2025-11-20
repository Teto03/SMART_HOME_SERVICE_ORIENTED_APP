from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# Process Layer URL
DASHBOARD_PROCESS_URL = "http://localhost:5004/api/home_status"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    # Proxy request to Process Layer
    try:
        res = requests.get(DASHBOARD_PROCESS_URL)
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
        res = requests.get(f"http://localhost:5004/api/devices")
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/devices/command', methods=['POST'])
def send_command():
    try:
        # Proxy to Process Layer
        res = requests.post(f"http://localhost:5004/api/devices/command", json=request.json)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Web App on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)

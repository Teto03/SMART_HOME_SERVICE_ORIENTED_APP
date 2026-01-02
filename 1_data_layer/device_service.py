from flask import Flask, request, jsonify
import time
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


DB_ADAPTER_URL = os.getenv('DB_ADAPTER_URL', 'http://localhost:5009')

def call_db_adapter(method, endpoint, data=None, params=None):
    """Helper function to call database adapter"""
    url = f"{DB_ADAPTER_URL}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url, params=params, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=5)
        else:
            return None, {"error": f"Unsupported method: {method}"}, 500
        
        if response.status_code >= 400:
            return None, response.json() if response.content else {"error": "Database adapter error"}, response.status_code
        return response.json(), None, response.status_code
    except requests.exceptions.RequestException as e:
        return None, {"error": f"Database adapter unavailable: {str(e)}"}, 503


def init_db():
    """Initialize database (indexes are handled by database adapter)"""
    # Verify database adapter is available by trying to get settings
    try:
        result, error, status_code = call_db_adapter('GET', '/settings')
        if error:
            print(f"Warning: Database adapter may not be ready. Error: {error.get('error', 'Unknown error')}")
        else:
            print("Database adapter is available and initialized.")
    except Exception as e:
        print(f"Warning: Cannot verify database adapter connection: {str(e)}")
        print("Make sure database adapter is running on port 5009.")


@app.route('/devices', methods=['POST'])
def register_device():
    data = request.json
    device_id = data.get('device_id')
    device_type = data.get('type')
    status = data.get('status', 'active')
    
    if not device_id or not device_type:
        return jsonify({"error": "Missing device_id or type"}), 400
    
    result, error, status_code = call_db_adapter('POST', '/devices', {
        'device_id': device_id,
        'type': device_type,
        'status': status
    })
    
    if error:
        return jsonify(error), status_code
    return jsonify(result), status_code

@app.route('/devices', methods=['GET'])
def get_devices():
    result, error, status_code = call_db_adapter('GET', '/devices')
    
    if error:
        return jsonify(error), status_code
    return jsonify(result), status_code

@app.route('/readings', methods=['POST'])
def add_reading():
    data = request.json
    device_id = data.get('device_id')
    value = data.get('value')
    timestamp = data.get('timestamp', time.time())
    
    if not device_id or value is None:
        return jsonify({"error": "Missing device_id or value"}), 400
    
    result, error, status_code = call_db_adapter('POST', '/readings', {
        'device_id': device_id,
        'value': value,
        'timestamp': timestamp
    })
    
    if error:
        return jsonify(error), status_code
    return jsonify(result), status_code

@app.route('/readings/latest', methods=['GET'])
def get_latest_reading():
    device_id = request.args.get('device_id')
    if not device_id:
        return jsonify({"error": "Missing device_id parameter"}), 400
    
    result, error, status_code = call_db_adapter('GET', '/readings/latest', params={'device_id': device_id})
    
    if error:
        return jsonify(error), status_code
    return jsonify(result), status_code

@app.route('/devices/command', methods=['POST'])
def send_command():
    data = request.json
    device_id = data.get('device_id')
    command = data.get('command')  # e.g., "ON", "OFF", "OPEN", "CLOSE"
    
    if not device_id or not command:
        return jsonify({"error": "Missing device_id or command"}), 400
    
    # Value mapping: ON/OPEN/TRIGGER=1, OFF/CLOSE=0
    val = 1.0 if command in ["ON", "OPEN", "TRIGGER"] else 0.0
    
    # Special handling for TRIGGER -> Status becomes SMOKE
    final_status = command
    if command == "TRIGGER":
        final_status = "SMOKE"
    
    # Update device status
    update_result, update_error, update_status = call_db_adapter('PUT', f'/devices/{device_id}', {
        'status': final_status
    })
    
    if update_error:
        return jsonify(update_error), update_status
    
    # Log as a reading
    reading_result, reading_error, reading_status = call_db_adapter('POST', '/readings', {
        'device_id': device_id,
        'value': val,
        'timestamp': time.time()
    })
    
    if reading_error:
        # Status was updated but reading failed - still return success for command
        return jsonify({
            "message": f"Command {command} sent to {device_id}",
            "new_status": final_status,
            "warning": "Reading log failed"
        })
    
    return jsonify({
        "message": f"Command {command} sent to {device_id}",
        "new_status": final_status
    })

@app.route('/devices/simulate_reading', methods=['POST'])
def simulate_reading():
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({"error": "Missing device_id"}), 400
    
    # Simple simulation logic for temperature
    import random
    value = round(random.uniform(18.0, 25.0), 2)
    
    result, error, status_code = call_db_adapter('POST', '/readings', {
        'device_id': device_id,
        'value': value,
        'timestamp': time.time()
    })
    
    if error:
        return jsonify(error), status_code
    return jsonify({"message": "Reading simulated", "value": value})

@app.route('/settings', methods=['GET'])
def get_settings():
    result, error, status_code = call_db_adapter('GET', '/settings')
    
    if error:
        return jsonify(error), status_code
    return jsonify(result), status_code

@app.route('/settings', methods=['POST'])
def update_settings():
    data = request.json
    result, error, status_code = call_db_adapter('POST', '/settings', data)
    
    if error:
        return jsonify(error), status_code
    return jsonify(result), status_code

if __name__ == '__main__':
    init_db()
    print("Starting Data Service on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)
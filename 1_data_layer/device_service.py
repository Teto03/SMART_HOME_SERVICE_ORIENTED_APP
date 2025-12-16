from flask import Flask, request, jsonify
import time
import os
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'devices_db'

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def init_db():
    # MongoDB creates collections lazily, but we can ensure indexes here if needed
    db = get_db()
    # Ensure device_id is unique in devices collection if we were enforcing it strictly,
    # but `INSERT OR REPLACE` logic suggests we just upsert.
    # We can create an index on timestamp for readings for faster latest reading queries.
    db.readings.create_index([("device_id", 1), ("timestamp", -1)])
    print("Connected to MongoDB.")

@app.route('/devices', methods=['POST'])
def register_device():
    data = request.json
    device_id = data.get('device_id')
    device_type = data.get('type')
    status = data.get('status', 'active')
    
    if not device_id or not device_type:
        return jsonify({"error": "Missing device_id or type"}), 400
        
    db = get_db()
    try:
        db.devices.update_one(
            {"_id": device_id},
            {"$set": {"type": device_type, "status": status}},
            upsert=True
        )
        return jsonify({"message": "Device registered", "device_id": device_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/devices', methods=['GET'])
def get_devices():
    db = get_db()
    devices_cursor = db.devices.find()
    devices = [{"id": d["_id"], "type": d.get("type"), "status": d.get("status")} for d in devices_cursor]
    return jsonify(devices)

@app.route('/readings', methods=['POST'])
def add_reading():
    data = request.json
    device_id = data.get('device_id')
    value = data.get('value')
    timestamp = data.get('timestamp', time.time())
    
    if not device_id or value is None:
        return jsonify({"error": "Missing device_id or value"}), 400
        
    db = get_db()
    
    # Auto-register device if not exists (simulating INSERT OR IGNORE)
    # in mongo updates with upsert=True is easiest, but we only want to set if NEW.
    # $setOnInsert is perfect for this.
    db.devices.update_one(
        {"_id": device_id},
        {"$setOnInsert": {"type": "unknown", "status": "active"}},
        upsert=True
    )
    
    db.readings.insert_one({
        "device_id": device_id,
        "value": value,
        "timestamp": timestamp
    })
    
    return jsonify({"message": "Reading added"}), 201

@app.route('/readings/latest', methods=['GET'])
def get_latest_reading():
    device_id = request.args.get('device_id')
    if not device_id:
        return jsonify({"error": "Missing device_id parameter"}), 400
        
    db = get_db()
    # Get latest reading
    reading = db.readings.find_one(
        {"device_id": device_id},
        sort=[("timestamp", -1)]
    )
    
    # Get device status
    device = db.devices.find_one({"_id": device_id})
    device_status = device.get("status") if device else "unknown"
    
    if reading:
        return jsonify({
            "device_id": reading["device_id"],
            "value": reading["value"],
            "timestamp": reading["timestamp"],
            "status": device_status
        })
    else:
        # Fallback if no readings but device exists
        if device:
             return jsonify({
                "device_id": device["_id"],
                "value": 0.0, # Default value
                "timestamp": time.time(),
                "status": device_status
            })
        return jsonify({"error": "No readings found"}), 404

@app.route('/devices/command', methods=['POST'])
def send_command():
    data = request.json
    device_id = data.get('device_id')
    command = data.get('command') # e.g., "ON", "OFF", "OPEN", "CLOSE"
    
    if not device_id or not command:
        return jsonify({"error": "Missing device_id or command"}), 400
        
    db = get_db()
    
    # Also log as a reading so we can see it in history/latest
    # Value mapping: ON/OPEN/TRIGGER=1, OFF/CLOSE=0
    val = 1.0 if command in ["ON", "OPEN", "TRIGGER"] else 0.0
    
    # Special handling for TRIGGER -> Status becomes SMOKE
    final_status = command
    if command == "TRIGGER":
        final_status = "SMOKE"
    
    # Update status
    db.devices.update_one(
        {"_id": device_id},
        {"$set": {"status": final_status}}
    )

    db.readings.insert_one({
        "device_id": device_id,
        "value": val,
        "timestamp": time.time()
    })
        
    return jsonify({"message": f"Command {command} sent to {device_id}", "new_status": final_status})

@app.route('/devices/simulate_reading', methods=['POST'])
def simulate_reading():
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({"error": "Missing device_id"}), 400
        
    # Simple simulation logic for temperature
    import random
    value = round(random.uniform(18.0, 25.0), 2)
    
    db = get_db()
    db.readings.insert_one({
        "device_id": device_id,
        "value": value,
        "timestamp": time.time()
    })
    
    return jsonify({"message": "Reading simulated", "value": value})

if __name__ == '__main__':
    init_db()
    print("Starting Data Service on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)

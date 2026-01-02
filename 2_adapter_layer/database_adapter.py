from flask import Flask, request, jsonify
import os
from pymongo import MongoClient
from bson.json_util import dumps
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DEVICES_DB_NAME = 'devices_db'
USERS_DB_NAME = 'users_db'

def get_client():
    """Get MongoDB client connection"""
    return MongoClient(MONGO_URI)

def get_devices_db():
    """Get devices database"""
    return get_client()[DEVICES_DB_NAME]

def get_users_db():
    """Get users database"""
    return get_client()[USERS_DB_NAME]

def init_db():
    """Initialize database indexes"""
    devices_db = get_devices_db()
    users_db = get_users_db()
    
    # Create indexes for devices_db
    devices_db.readings.create_index([("device_id", 1), ("timestamp", -1)])
    
    # Create indexes for users_db
    users_db.users.create_index("username", unique=True)
    
    print("Database adapter initialized with MongoDB.")

@app.route('/devices', methods=['POST'])
def create_device():
    """Create or update a device"""
    data = request.json
    device_id = data.get('device_id')
    device_type = data.get('type')
    status = data.get('status', 'active')
    
    if not device_id or not device_type:
        return jsonify({"error": "Missing device_id or type"}), 400
    
    db = get_devices_db()
    try:
        update_op = {
            "$set": {"type": device_type},
            "$setOnInsert": {"status": status}
        }
        db.devices.update_one(
            {"_id": device_id},
            update_op,
            upsert=True
        )
        return jsonify({"message": "Device registered", "device_id": device_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/devices', methods=['GET'])
def get_devices():
    """Get all devices"""
    db = get_devices_db()
    devices_cursor = db.devices.find()
    devices = [{"id": d["_id"], "type": d.get("type"), "status": d.get("status")} for d in devices_cursor]
    return jsonify(devices)

@app.route('/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """Get a specific device by ID"""
    db = get_devices_db()
    device = db.devices.find_one({"_id": device_id})
    
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    return jsonify({
        "id": device["_id"],
        "type": device.get("type"),
        "status": device.get("status")
    })

@app.route('/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    """Update a device"""
    data = request.json
    db = get_devices_db()
    
    update_fields = {}
    if 'type' in data:
        update_fields['type'] = data['type']
    if 'status' in data:
        update_fields['status'] = data['status']
    
    if not update_fields:
        return jsonify({"error": "No fields to update"}), 400
    
    result = db.devices.update_one(
        {"_id": device_id},
        {"$set": update_fields}
    )
    
    if result.matched_count == 0:
        return jsonify({"error": "Device not found"}), 404
    
    return jsonify({"message": "Device updated", "updated": update_fields})

@app.route('/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    """Delete a device"""
    db = get_devices_db()
    result = db.devices.delete_one({"_id": device_id})
    
    if result.deleted_count == 0:
        return jsonify({"error": "Device not found"}), 404
    
    return jsonify({"message": "Device deleted"})


@app.route('/readings', methods=['POST'])
def create_reading():
    """Create a new reading"""
    data = request.json
    device_id = data.get('device_id')
    value = data.get('value')
    timestamp = data.get('timestamp')
    
    if not device_id or value is None:
        return jsonify({"error": "Missing device_id or value"}), 400
    
    import time
    if not timestamp:
        timestamp = time.time()
    
    db = get_devices_db()
    
    # Auto-register device if not exists
    db.devices.update_one(
        {"_id": device_id},
        {"$setOnInsert": {"type": "unknown", "status": "active"}},
        upsert=True
    )
    
    reading_id = db.readings.insert_one({
        "device_id": device_id,
        "value": value,
        "timestamp": timestamp
    }).inserted_id
    
    return jsonify({
        "message": "Reading added",
        "reading_id": str(reading_id)
    }), 201

@app.route('/readings', methods=['GET'])
def get_readings():
    """Get readings with optional filters"""
    device_id = request.args.get('device_id')
    limit = request.args.get('limit', type=int, default=100)
    
    db = get_devices_db()
    query = {}
    if device_id:
        query['device_id'] = device_id
    
    readings = list(db.readings.find(query).sort("timestamp", -1).limit(limit))
    
    # Convert ObjectId to string for JSON serialization
    for reading in readings:
        reading['_id'] = str(reading['_id'])
    
    return jsonify(readings)

@app.route('/readings/latest', methods=['GET'])
def get_latest_reading():
    """Get the latest reading for a device"""
    device_id = request.args.get('device_id')
    if not device_id:
        return jsonify({"error": "Missing device_id parameter"}), 400
    
    import time
    db = get_devices_db()
    
    reading = db.readings.find_one(
        {"device_id": device_id},
        sort=[("timestamp", -1)]
    )
    
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
        if device:
            return jsonify({
                "device_id": device["_id"],
                "value": 0.0,
                "timestamp": time.time(),
                "status": device_status
            })
        return jsonify({"error": "No readings found"}), 404


@app.route('/settings', methods=['GET'])
def get_settings():
    """Get global settings"""
    db = get_devices_db()
    settings = db.settings.find_one({"_id": "global_config"})
    
    if not settings:
        return jsonify({
            "city": "Milan",
            "season_mode": "auto"
        })
    
    return jsonify({
        "city": settings.get("city", "Milan"),
        "season_mode": settings.get("season_mode", "auto")
    })

@app.route('/settings', methods=['POST'])
def update_settings():
    """Update global settings"""
    data = request.json
    db = get_devices_db()
    
    update_fields = {}
    if 'city' in data:
        update_fields['city'] = data['city']
    if 'season_mode' in data:
        update_fields['season_mode'] = data['season_mode']
    
    if not update_fields:
        return jsonify({"message": "No settings to update"}), 200
    
    db.settings.update_one(
        {"_id": "global_config"},
        {"$set": update_fields},
        upsert=True
    )
    
    return jsonify({"message": "Settings updated", "updated": update_fields})


@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), 400
    
    username = data['username']
    password = data['password']
    
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    import hashlib
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    db = get_users_db()
    try:
        user_id = db.users.insert_one({
            "username": username,
            "password_hash": hashed_pw
        }).inserted_id
        return jsonify({
            "message": "User created successfully",
            "user_id": str(user_id)
        }), 201
    except Exception as e:
        if "11000" in str(e):  # Duplicate key error
            return jsonify({"error": "Username already exists"}), 409
        return jsonify({"error": str(e)}), 500


@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    """Get a user by username (without password hash)"""
    db = get_users_db()
    user = db.users.find_one({"username": username})

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": user["username"],
        "_id": str(user["_id"])
})


@app.route('/users/verify_password', methods=['POST'])
def verify_password():
    """Verify a user's password (for authentication)"""
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), 400
    
    username = data['username']
    password = data['password']
    
    import hashlib
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    db = get_users_db()
    user = db.users.find_one({"username": username})
    
    if user and user.get("password_hash") == hashed_pw:
        return jsonify({"valid": True, "username": username})
    
    return jsonify({"valid": False, "error": "Invalid credentials"}), 401

if __name__ == '__main__':
    init_db()
    print("Starting Database Adapter on port 5009...")
    app.run(host='0.0.0.0', port=5009, debug=True)
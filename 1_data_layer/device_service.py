import sqlite3
from flask import Flask, request, jsonify
import time

app = Flask(__name__)
DB_PATH = 'devices.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY,
                type TEXT,
                status TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                value REAL,
                timestamp REAL,
                FOREIGN KEY(device_id) REFERENCES devices(id)
            )
        ''')
        conn.commit()

@app.route('/devices', methods=['POST'])
def register_device():
    data = request.json
    device_id = data.get('device_id')
    device_type = data.get('type')
    status = data.get('status', 'active')
    
    if not device_id or not device_type:
        return jsonify({"error": "Missing device_id or type"}), 400
        
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT OR REPLACE INTO devices (id, type, status) VALUES (?, ?, ?)', 
                           (device_id, device_type, status))
            conn.commit()
            return jsonify({"message": "Device registered", "device_id": device_id}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/devices', methods=['GET'])
def get_devices():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices')
        rows = cursor.fetchall()
        devices = [{"id": r[0], "type": r[1], "status": r[2]} for r in rows]
        return jsonify(devices)

@app.route('/readings', methods=['POST'])
def add_reading():
    data = request.json
    device_id = data.get('device_id')
    value = data.get('value')
    timestamp = data.get('timestamp', time.time())
    
    if not device_id or value is None:
        return jsonify({"error": "Missing device_id or value"}), 400
        
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Auto-register device if not exists (for simplicity in simulation)
        cursor.execute('INSERT OR IGNORE INTO devices (id, type, status) VALUES (?, ?, ?)', 
                       (device_id, 'unknown', 'active'))
        
        cursor.execute('INSERT INTO readings (device_id, value, timestamp) VALUES (?, ?, ?)', 
                       (device_id, value, timestamp))
        conn.commit()
        return jsonify({"message": "Reading added"}), 201

@app.route('/readings/latest', methods=['GET'])
def get_latest_reading():
    device_id = request.args.get('device_id')
    if not device_id:
        return jsonify({"error": "Missing device_id parameter"}), 400
        
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT device_id, value, timestamp FROM readings 
            WHERE device_id = ? 
            ORDER BY timestamp DESC LIMIT 1
        ''', (device_id,))
        row = cursor.fetchone()
        
        if row:
            return jsonify({
                "device_id": row[0],
                "value": row[1],
                "timestamp": row[2]
            })
        else:
            return jsonify({"error": "No readings found"}), 404

@app.route('/devices/command', methods=['POST'])
def send_command():
    data = request.json
    device_id = data.get('device_id')
    command = data.get('command') # e.g., "ON", "OFF", "OPEN", "CLOSE"
    
    if not device_id or not command:
        return jsonify({"error": "Missing device_id or command"}), 400
        
    # In a real scenario, this would talk to the hardware.
    # Here we just update the device status in DB or log it.
    # For simulation purposes, we can treat the command as a status update.
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Update status
        cursor.execute('UPDATE devices SET status = ? WHERE id = ?', (command, device_id))
        
        # Also log as a reading so we can see it in history/latest
        # Value mapping: ON/OPEN=1, OFF/CLOSE=0
        val = 1.0 if command in ["ON", "OPEN"] else 0.0
        cursor.execute('INSERT INTO readings (device_id, value, timestamp) VALUES (?, ?, ?)', 
                       (device_id, val, time.time()))
        conn.commit()
        
    return jsonify({"message": f"Command {command} sent to {device_id}", "new_status": command})

if __name__ == '__main__':
    init_db()
    print("Starting Data Service on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)

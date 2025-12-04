import sqlite3

DB_PATH = 'devices.db'

def check_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("--- DEVICES TABLE ---")
        cursor.execute("SELECT * FROM devices WHERE id='smart_heater_1'")
        row = cursor.fetchone()
        if row:
            print(f"ID: {row[0]}, Type: {row[1]}, Status: {row[2]}")
        else:
            print("Device smart_heater_1 not found in devices table.")

        print("\n--- LATEST READING ---")
        cursor.execute("SELECT * FROM readings WHERE device_id='smart_heater_1' ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            print(f"ID: {row[0]}, DeviceID: {row[1]}, Value: {row[2]}, Timestamp: {row[3]}")
        else:
            print("No readings found for smart_heater_1.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()

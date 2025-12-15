from pymongo import MongoClient
import os

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DEVICES_DB_NAME = 'devices_db'

def check_db():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DEVICES_DB_NAME]
        
        print("--- DEVICES COLLECTION ---")
        devices = db.devices.find()
        for device in devices:
            print(f"ID: {device['_id']}, Type: {device.get('type')}, Status: {device.get('status')}")

        print("\n--- READINGS SAMPLE ---")
        readings = db.readings.find().limit(5)
        for reading in readings:
            print(f"DeviceID: {reading.get('device_id')}, Value: {reading.get('value')}")
            
        print("\n--- USERS COLLECTION (checking users_db) ---")
        user_db = client['users_db']
        user = user_db.users.find_one({"username": "testuser"})
        if user:
            print(f"User found: {user['username']}")
        else:
            print("User testuser not found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()

from flask import Flask, request, jsonify
import jwt
import datetime
import hashlib
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_insecure_secret_key')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'users_db'

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def init_db():
    db = get_db()
    # Create unique index on username
    db.users.create_index("username", unique=True)
    
    # Create default admin if not exists
    if not db.users.find_one({"username": "admin"}):
        admin_pw_hash = hashlib.sha256("admin123".encode()).hexdigest()
        db.users.insert_one({"username": "admin", "password_hash": admin_pw_hash})
        print("Created default admin user.")
    print("Connected to MongoDB for Auth.")

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), 400
    
    username = data['username']
    password = data['password']
    
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
        
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    db = get_db()
    try:
        db.users.insert_one({"username": username, "password_hash": hashed_pw})
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        # duplicate key error code is 11000
        if "11000" in str(e):
            return jsonify({"error": "Username already exists"}), 409
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), 400
    
    username = data['username']
    password = data['password']
    
    # Hash the password to compare
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    db = get_db()
    user = db.users.find_one({"username": username})
    
    if user and user.get("password_hash") == hashed_pw:
        # Generate Token
        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({"token": token})
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    token = data.get('token')
    if not token:
        return jsonify({"valid": False, "error": "Missing token"}), 400
    
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return jsonify({"valid": True, "user": decoded['user']})
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"valid": False, "error": "Invalid token"}), 401

if __name__ == '__main__':
    init_db()
    print("Starting Auth Service on port 5010...")
    app.run(host='0.0.0.0', port=5010, debug=True)

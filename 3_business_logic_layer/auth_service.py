from flask import Flask, request, jsonify
import jwt
import datetime
import hashlib
import os
import requests
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_insecure_secret_key')

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
    # Create default admin if not exists
    user_result, user_error, _ = call_db_adapter('GET', '/users/admin')
    
    if user_error and 'not found' in user_error.get('error', '').lower():
        admin_result, admin_error, _ = call_db_adapter('POST', '/users', {
            'username': 'admin',
            'password': 'admin123'
        })
        if not admin_error:
            print("Created default admin user.")
    print("Auth service initialized.")

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), 400
    
    username = data['username']
    password = data['password']
    
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    # Call database adapter to create user
    result, error, status_code = call_db_adapter('POST', '/users', {
        'username': username,
        'password': password
    })
    
    if error:
        return jsonify(error), status_code
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), 400
    
    username = data['username']
    password = data['password']
    
    # Verify password using database adapter
    result, error, status_code = call_db_adapter('POST', '/users/verify_password', {
        'username': username,
        'password': password
    })
    
    if error or not result.get('valid'):
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Generate Token
    token = jwt.encode({
        'user': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({"token": token})

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
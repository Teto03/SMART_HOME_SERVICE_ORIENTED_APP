from flask import Flask, request, jsonify
import jwt
import datetime
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key_for_demo_only'

# Simple in-memory user store (for demo purposes)
# In a real app, this would be in a database
USERS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "user": hashlib.sha256("password".encode()).hexdigest()
}

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), 400
    
    username = data['username']
    password = data['password']
    
    # Hash the password to compare
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    if username in USERS and USERS[username] == hashed_pw:
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
    print("Starting Auth Service on port 5010...")
    app.run(host='0.0.0.0', port=5010, debug=True)

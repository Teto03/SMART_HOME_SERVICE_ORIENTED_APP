from flask import Flask, request, jsonify
import jwt
import datetime
import hashlib
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_insecure_secret_key')
DB_PATH = 'users.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        
        # Create default admin if not exists
        cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            admin_pw_hash = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('admin', admin_pw_hash))
            print("Created default admin user.")
            
        conn.commit()

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
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_pw))
            conn.commit()
            return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    except Exception as e:
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
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        
        if row and row[0] == hashed_pw:
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

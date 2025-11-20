import requests
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Configuration
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "MOCK_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "123456789")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({"error": "Missing message"}), 400
        
    if TELEGRAM_TOKEN == "MOCK_TOKEN":
        print(f"[MOCK TELEGRAM] Sending to {TELEGRAM_CHAT_ID}: {message}")
        return jsonify({"status": "sent", "mock": True})

    try:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        res = requests.post(TELEGRAM_API_URL, json=payload)
        if res.status_code == 200:
            return jsonify({"status": "sent", "mock": False})
        else:
            return jsonify({"error": "Telegram error", "details": res.text}), res.status_code
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Telegram Adapter on port 5005...")
    # Note: Port 5005 to avoid conflict with others (Data=5001, Weather=5002, Business=5003, Process=5004)
    app.run(host='0.0.0.0', port=5005, debug=True)

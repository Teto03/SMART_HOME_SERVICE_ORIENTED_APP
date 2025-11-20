import requests
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Configuration
OWM_API_KEY = os.environ.get("OWM_API_KEY", "MOCK_KEY")
OWM_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

@app.route('/current_weather', methods=['GET'])
def get_current_weather():
    city = request.args.get('city', 'Milan')
    
    if OWM_API_KEY == "MOCK_KEY":
        # Return mock data if no key provided
        return jsonify({
            "city": city,
            "temp_c": 22.5,
            "condition": "Sunny",
            "mock": True
        })

    try:
        params = {
            "q": city,
            "appid": OWM_API_KEY,
            "units": "metric"
        }
        res = requests.get(OWM_BASE_URL, params=params)
        if res.status_code == 200:
            data = res.json()
            return jsonify({
                "city": data["name"],
                "temp_c": data["main"]["temp"],
                "condition": data["weather"][0]["main"],
                "mock": False
            })
        else:
            return jsonify({"error": "Provider error", "details": res.text}), res.status_code
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Weather Adapter on port 5002...")
    app.run(host='0.0.0.0', port=5002, debug=True)

import requests
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
OWM_API_KEY = os.environ.get("OWM_API_KEY", "MOCK_KEY")
OWM_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

import time

# Caching & Rate Limiting
weather_cache = {} # {city: (timestamp, data)}
CACHE_TTL = 600 # 10 minutes
daily_calls = 0
last_reset = time.time()
DAILY_LIMIT = 800

@app.route('/current_weather', methods=['GET'])
def get_current_weather():
    """Get the current weather for a city and store it in the cache"""
    global daily_calls, last_reset
    
    # Reset counter if 24h passed
    if time.time() - last_reset > 86400:
        daily_calls = 0
        last_reset = time.time()

    city = request.args.get('city', 'Milan')
    
    if city in weather_cache:
        timestamp, data = weather_cache[city]
        if time.time() - timestamp < CACHE_TTL:
            print(f"Returning cached data for {city}")
            data["cached"] = True
            return jsonify(data)

    if OWM_API_KEY == "MOCK_KEY":
        # Return mock data if no key provided
        return jsonify({
            "city": city,
            "temp_c": 22.5,
            "condition": "Sunny",
            "mock": True
        })

    if daily_calls >= DAILY_LIMIT:
        print("Rate limit reached!")
        # Try to return stale cache if available
        if city in weather_cache:
            _, data = weather_cache[city]
            data["cached"] = True
            data["stale"] = True
            return jsonify(data)
        return jsonify({"error": "Daily API limit reached"}), 429

    try:
        params = {
            "q": city,
            "appid": OWM_API_KEY,
            "units": "metric"
        }
        
        daily_calls += 1
        print(f"Calling OWM API for {city}. Daily calls: {daily_calls}/{DAILY_LIMIT}")
        
        res = requests.get(OWM_BASE_URL, params=params)
        if res.status_code == 200:
            data = res.json()
            response_data = {
                "city": data["name"],
                "temp_c": data["main"]["temp"],
                "condition": data["weather"][0]["main"],
                "mock": False,
                "cached": False
            }
            # Update Cache
            weather_cache[city] = (time.time(), response_data)
            return jsonify(response_data)
        else:
            return jsonify({"error": "Provider error", "details": res.text}), res.status_code
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Weather Adapter on port 5002...")
    app.run(host='0.0.0.0', port=5002, debug=True)

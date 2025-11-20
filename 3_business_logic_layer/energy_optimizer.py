from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/optimize_energy', methods=['POST'])
def optimize_energy():
    data = request.json
    indoor_temp = data.get('indoor_temp')
    outdoor_temp = data.get('outdoor_temp')
    
    if indoor_temp is None or outdoor_temp is None:
        return jsonify({"error": "Missing temperature data"}), 400

    advice = "No specific action needed."
    should_act = False
    
    # Logic:
    # If indoor is cold (< 18) and outdoor is warmer (> 20), open windows.
    # If indoor is hot (> 25) and outdoor is cooler (< 22), open windows.
    # If indoor is cold (< 18) and outdoor is cold (< 10), turn on heating.
    
    if indoor_temp < 18:
        if outdoor_temp > 20:
            advice = "It's warmer outside. Open the windows to warm up naturally."
            should_act = True
        elif outdoor_temp < 10:
            advice = "It's cold inside and outside. Turn on the heating."
            should_act = True
    elif indoor_temp > 25:
        if outdoor_temp < 22:
            advice = "It's cooler outside. Open the windows to cool down."
            should_act = True
        else:
            advice = "It's hot. Consider turning on AC."
            should_act = True
            
    return jsonify({
        "message": advice,
        "should_act": should_act
    })

if __name__ == '__main__':
    print("Starting Energy Optimizer on port 5006...")
    # Note: Port 5006 to avoid conflict (Data=5001, Weather=5002, Analytics=5003, Process=5004, Telegram=5005)
    app.run(host='0.0.0.0', port=5006, debug=True)

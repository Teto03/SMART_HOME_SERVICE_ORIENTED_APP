from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/optimize_energy', methods=['POST'])
def optimize_energy():
    data = request.json
    indoor_temp = data.get('indoor_temp')
    outdoor_temp = data.get('outdoor_temp')
    
    if indoor_temp is None or outdoor_temp is None:
        return jsonify({"error": "Missing temperature data"}), 400

    # Enhanced Logic with Comfort Index
    # Mock Humidity (randomized for demo or fixed)
    humidity = 50 
    
    # Calculate "Comfort Index" (Simplified Heat Index)
    comfort_index = indoor_temp + (0.55 - 0.0055 * humidity) * (indoor_temp - 14.5)
    
    efficiency_score = 10
    reasons = []
    
    # Analyze Indoor State
    if 20 <= indoor_temp <= 24:
        reasons.append("Indoor temperature is optimal.")
    elif indoor_temp < 20:
        efficiency_score -= 2
        reasons.append("It's a bit cold inside.")
    else:
        efficiency_score -= 2
        reasons.append("It's a bit warm inside.")
        
    # Analyze Outdoor Context
    if outdoor_temp > 25 and indoor_temp > 25:
        advice = "High outdoor heat. Keep windows closed and use AC sparingly."
        should_act = True
        efficiency_score -= 3
    elif outdoor_temp < 10 and indoor_temp < 18:
        advice = "Cold outside. Ensure insulation is good and heating is efficient."
        should_act = True
        efficiency_score -= 2
    elif 18 <= outdoor_temp <= 25 and indoor_temp > 24:
        advice = "Perfect outdoor weather! Open windows to cool down naturally."
        should_act = True
        efficiency_score += 1 # Bonus for free cooling
    elif 18 <= outdoor_temp <= 25 and indoor_temp < 20:
        advice = "Mild outdoor weather. Open windows to warm up naturally."
        should_act = True
        efficiency_score += 1
    else:
        advice = f"System stable. Comfort Index: {comfort_index:.1f}. Efficiency Score: {efficiency_score}/10."
        should_act = False

    return jsonify({
        "message": advice,
        "should_act": should_act,
        "efficiency_score": efficiency_score,
        "details": reasons
    })

if __name__ == '__main__':
    print("Starting Energy Optimizer on port 5006...")
    # Note: Port 5006 to avoid conflict (Data=5001, Weather=5002, Analytics=5003, Process=5004, Telegram=5005)
    app.run(host='0.0.0.0', port=5006, debug=True)

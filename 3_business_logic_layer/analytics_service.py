from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_data():
    data = request.json
    device_type = data.get('device_type')
    value = data.get('value')
    
    if value is None:
        return jsonify({"error": "Missing value"}), 400

    anomalies = []
    
    # Simple logic: High temperature check
    if device_type == 'temperature':
        if value > 50:
            anomalies.append("CRITICAL: Temperature too high!")
        elif value > 30:
            anomalies.append("WARNING: Temperature is high.")
            
    return jsonify({
        "has_anomalies": len(anomalies) > 0,
        "anomalies": anomalies
    })

if __name__ == '__main__':
    print("Starting Analytics Service on port 5003...")
    # Note: Port 5003
    app.run(host='0.0.0.0', port=5003, debug=True)

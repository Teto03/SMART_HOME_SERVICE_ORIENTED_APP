from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyzes sensor data and device states to detect anomalies.
    """
    data = request.json or {}
    temp = data.get("temp")
    devices = data.get("devices", [])
    
    anomalies = []

    device_map = {}
    for d in devices:
        d_id = d.get("id")
        device_map[d_id] = d

    smoke_detected = False
    for d_id, dev in device_map.items():
        if dev.get("type") == "smoke_sensor" and dev.get("value") == 1:
            smoke_detected = True
            break
            
    if smoke_detected:
        anomalies.append({
            "type": "FIRE",
            "message": "CRITICAL: SMOKE DETECTED! Immediate Action Required!"
        })

    if temp is not None and temp > 28.0:
        anomalies.append({
            "type": "HIGH_TEMP",
            "message": f"ALERT: High Temperature detected: {temp:.1f} C"
        })

    def is_active(d_id):
        dev = device_map.get(d_id)
        if not dev: return False
        val = dev.get("value")
        status = dev.get("status")
        # Check active conditions
        if dev.get("type") == "window":
            return (val == 1.0) or (status == "OPEN")
        if dev.get("type") in ["heater", "ac", "smart_heater", "main_heater"]: # Added aliases just in case
            return (val == 1.0) or (status == "ON")
        return False

    ac_on = is_active("air_conditioner")
    heat_on = is_active("smart_heater_1") or is_active("main_heater")
    
    if ac_on and heat_on:
        anomalies.append({
            "type": "CONFLICT",
            "message": "CRITICAL ENERGY WASTE: Air Conditioner and Heater are BOTH ON! Please turn one off."
        })

    open_windows = []
    for d_id, dev in device_map.items():
        if dev.get("type") == "window" and is_active(d_id):
            open_windows.append(d_id.replace("_", " ").title())
            
    active_hvac = []
    if ac_on: active_hvac.append("Air Conditioner")
    if is_active("smart_heater_1"): active_hvac.append("Smart Heater 1")
    if is_active("main_heater"): active_hvac.append("Main Heater")
    
    if open_windows and active_hvac:
        hvac_str = ", ".join(active_hvac)
        win_str = ", ".join(open_windows)
        anomalies.append({
            "type": "WASTE",
            "message": f"ENERGY WASTE: {hvac_str} is ON while {win_str} is OPEN!"
        })

    return jsonify({
        "has_anomaly": len(anomalies) > 0,
        "anomalies": anomalies
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5003))
    print(f"Starting Anomaly Detection Service on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/optimize_energy', methods=['POST'])
def optimize_energy():
    data = request.json
    indoor_temp = data.get('indoor_temp')
    outdoor_temp = data.get('outdoor_temp')
    
    # Device states
    window_states = data.get('window_states', {})  # Dict of window_id: status
    boiler_status = data.get('boiler_status', 'UNKNOWN')
    ac_status = data.get('ac_status', 'UNKNOWN')
    season_mode = data.get('season_mode', 'auto')  # auto, summer, winter, mild
    
    if indoor_temp is None or outdoor_temp is None:
        return jsonify({"error": "Missing temperature data"}), 400

    # Calculate window metrics
    windows_open_count = sum(1 for status in window_states.values() if status == "OPEN")
    any_window_open = windows_open_count > 0
    all_windows_open = windows_open_count == len(window_states) if window_states else False
    
    # Enhanced Logic with season detection
    humidity = 50  # Mock humidity
    comfort_index = indoor_temp + (0.55 - 0.0055 * humidity) * (indoor_temp - 14.5)
    
    efficiency_score = 10
    reasons = []
    advice = ""
    should_act = False
    
    # Season detection
    if season_mode == 'summer':
        is_summer = True
        is_winter = False
        is_mild = False
    elif season_mode == 'winter':
        is_summer = False
        is_winter = True
        is_mild = False
    elif season_mode == 'mild':
        is_summer = False
        is_winter = False
        is_mild = True
    else: # auto
        is_summer = outdoor_temp > 25
        is_winter = outdoor_temp < 15
        is_mild = 15 <= outdoor_temp <= 25
    
    # ============================================
    # CRITICAL WASTAGE SCENARIOS (Efficiency: 0)
    # ============================================
    
    # 1. AC + Boiler both ON = Heating and Cooling simultaneously
    if ac_status == "ON" and boiler_status == "ON":
        advice = "🚨 CRITICAL WASTE: Heating (Boiler) AND Cooling (AC) running simultaneously! Turn one off immediately!"
        should_act = True
        efficiency_score = 0
        reasons.append("Heating and cooling at the same time wastes massive energy.")
        reasons.append("Decide if you want to heat or cool, not both.")
    
    # 2. AC ON with windows open = Cooling outside air
    elif ac_status == "ON" and any_window_open:
        window_count_msg = f"({windows_open_count} window{'s' if windows_open_count > 1 else ''} open)"
        advice = f"⚠️ CRITICAL WASTE: AC is ON while windows are OPEN {window_count_msg}! Close all windows or turn off AC!"
        should_act = True
        efficiency_score = 1 if windows_open_count == 1 else 0
        reasons.append("Air conditioning cannot work efficiently with open windows.")
        reasons.append("You're cooling the entire neighborhood, not just your home.")
    
    # 3. Boiler ON with multiple windows open = Major heat loss
    elif boiler_status == "ON" and windows_open_count >= 2:
        advice = f"⚠️ SEVERE WASTE: Boiler is ON with {windows_open_count} windows OPEN! Close windows immediately!"
        should_act = True
        efficiency_score = 0
        reasons.append(f"{windows_open_count} open windows cause massive heat loss.")
        reasons.append("Boiler is fighting against open windows - very wasteful.")
    
    # ============================================
    # HIGH PRIORITY WARNINGS (Efficiency: 1-4)
    # ============================================
    
    # 4. Boiler ON with single window open
    elif boiler_status == "ON" and windows_open_count == 1:
        advice = "⚠️ Energy Waste: Boiler is ON but a window is OPEN! Close the window to retain heat."
        should_act = True
        efficiency_score = 3
        reasons.append("Even one open window causes significant heat loss.")
    
    # 5. AC ON when temperature is already optimal
    elif ac_status == "ON" and indoor_temp <= 24:
        advice = "⚠️ AC running unnecessarily! Indoor temperature is already comfortable. Turn off AC."
        should_act = True
        efficiency_score = 3
        reasons.append(f"Indoor temp ({indoor_temp}°C) is already optimal.")
    
    # 6. Boiler ON when temperature is already high
    elif boiler_status == "ON" and indoor_temp >= 24:
        advice = "⚠️ Boiler running unnecessarily! Indoor temperature is already warm. Turn off boiler."
        should_act = True
        efficiency_score = 2
        reasons.append(f"Indoor temp ({indoor_temp}°C) is already high - no heating needed.")
    
    # ============================================
    # SEASON-SPECIFIC RECOMMENDATIONS
    # ============================================
    
    # SUMMER SEASON (Hot outside)
    elif is_summer:
        if indoor_temp > 26 and ac_status != "ON":
            advice = "☀️ Hot day! Indoor temperature is high. Consider turning on AC or opening windows for ventilation."
            should_act = True
            efficiency_score = 5
            reasons.append(f"Outdoor: {outdoor_temp}°C, Indoor: {indoor_temp}°C")
        elif indoor_temp > outdoor_temp and not any_window_open:
            advice = "💡 It's cooler outside! Open windows for free natural cooling instead of using AC."
            should_act = True
            efficiency_score = 6
            reasons.append("Natural ventilation is more efficient than AC.")
        elif any_window_open and ac_status != "ON":
            advice = f"✓ Good! {windows_open_count} window{'s' if windows_open_count > 1 else ''} open for natural ventilation in summer."
            efficiency_score = 9
            reasons.append("Using natural cooling - very efficient!")
        else:
            advice = f"System stable. Summer mode. Indoor: {indoor_temp}°C, Outdoor: {outdoor_temp}°C."
            efficiency_score = 7
    
    # WINTER SEASON (Cold outside)
    elif is_winter:
        if any_window_open and outdoor_temp < 10:
            advice = "🥶 Windows open in cold weather! Close them to prevent heat loss."
            should_act = True
            efficiency_score = 4
            reasons.append(f"Outdoor temperature is {outdoor_temp}°C - too cold for open windows.")
        elif indoor_temp < 19 and boiler_status != "ON":
            advice = "🌡️ Indoor temperature is low. Consider turning on heating."
            should_act = True
            efficiency_score = 6
            reasons.append(f"Indoor: {indoor_temp}°C - below comfortable range.")
        elif boiler_status == "ON" and indoor_temp >= 20:
            advice = "✓ Good! Heating is maintaining comfortable temperature."
            efficiency_score = 8
        else:
            advice = f"System stable. Winter mode. Indoor: {indoor_temp}°C, Outdoor: {outdoor_temp}°C."
            efficiency_score = 7
    
    # MILD WEATHER (Perfect for natural ventilation)
    elif is_mild:
        if any_window_open and boiler_status == "OFF" and ac_status == "OFF":
            advice = f"✅ EXCELLENT! {windows_open_count} window{'s' if windows_open_count > 1 else ''} open for natural ventilation. Both HVAC systems off. Perfect!"
            efficiency_score = 10
            reasons.append("Mild weather + natural ventilation = maximum efficiency!")
            reasons.append("You're using zero energy for climate control.")
        elif not any_window_open and (boiler_status == "ON" or ac_status == "ON"):
            advice = "💡 Perfect weather outside! Turn off HVAC and open windows for free natural comfort."
            should_act = True
            efficiency_score = 4
            reasons.append(f"Outdoor temp ({outdoor_temp}°C) is ideal - no need for heating or cooling.")
        elif indoor_temp > outdoor_temp + 3 and not any_window_open:
            advice = f"💡 It's cooler outside ({outdoor_temp}°C vs {indoor_temp}°C inside). Open windows for free cooling!"
            should_act = True
            efficiency_score = 6
        elif outdoor_temp > indoor_temp + 3 and not any_window_open and indoor_temp < 20:
            advice = f"💡 It's warmer outside ({outdoor_temp}°C vs {indoor_temp}°C inside). Open windows for free warming!"
            should_act = True
            efficiency_score = 6
        else:
            advice = f"System stable. Mild weather - great for natural ventilation! Indoor: {indoor_temp}°C, Outdoor: {outdoor_temp}°C."
            efficiency_score = 8
    
    # ============================================
    # DEFAULT / OPTIMAL STATE
    # ============================================
    else:
        if 20 <= indoor_temp <= 24:
            reasons.append("Indoor temperature is in optimal comfort range.")
            efficiency_score += 1
        elif indoor_temp < 20:
            reasons.append("Indoor temperature is a bit cool.")
        else:
            reasons.append("Indoor temperature is a bit warm.")
        
        advice = f"System stable. Comfort Index: {comfort_index:.1f}. Indoor: {indoor_temp}°C, Outdoor: {outdoor_temp}°C."
        efficiency_score = max(efficiency_score, 7)
    
    # Add window status to details
    if windows_open_count > 0:
        window_names = [k.replace('_', ' ').title() for k, v in window_states.items() if v == "OPEN"]
        reasons.append(f"Windows open: {', '.join(window_names)}")
    
    return jsonify({
        "message": advice,
        "should_act": should_act,
        "efficiency_score": max(0, min(10, efficiency_score)),  # Clamp 0-10
        "details": reasons,
        "season": "summer" if is_summer else ("winter" if is_winter else "mild"),
        "windows_open_count": windows_open_count
    })

if __name__ == '__main__':
    print("Starting Energy Optimizer on port 5006...")
    app.run(host='0.0.0.0', port=5006, debug=True)

#!/bin/bash
echo "Starting all services..."

# Secrets are loaded from .env file by the Python services
# Ensure you have created a .env file based on .env.example

# 1. Data Layer
./venv/bin/python3 1_data_layer/device_service.py > logs_device.txt 2>&1 &
PID_DEVICE=$!
echo "Device Service started (PID: $PID_DEVICE)"

./venv/bin/python3 6_simulators/sensor_gen.py > logs_sensor.txt 2>&1 &
PID_SENSOR=$!
echo "Sensor Gen started (PID: $PID_SENSOR)"

# 2. Adapter Layer
./venv/bin/python3 2_adapter_layer/weather_adapter.py > logs_weather.txt 2>&1 &
PID_WEATHER=$!
echo "Weather Adapter started (PID: $PID_WEATHER)"

./venv/bin/python3 2_adapter_layer/telegram_adapter.py > logs_telegram.txt 2>&1 &
PID_TELEGRAM=$!
echo "Telegram Adapter started (PID: $PID_TELEGRAM)"

# 3. Business Logic Layer
./venv/bin/python3 3_business_logic_layer/analytics_service.py > logs_analytics.txt 2>&1 &
PID_ANALYTICS=$!
echo "Analytics Service started (PID: $PID_ANALYTICS)"

./venv/bin/python3 3_business_logic_layer/energy_optimizer.py > logs_optimizer.txt 2>&1 &
PID_OPTIMIZER=$!
echo "Energy Optimizer started (PID: $PID_OPTIMIZER)"

./venv/bin/python3 3_business_logic_layer/auth_service.py > logs_auth.txt 2>&1 &
PID_AUTH=$!
echo "Auth Service started (PID: $PID_AUTH)"

# 4. Process Layer
./venv/bin/python3 4_process_layer/dashboard_process.py > logs_dashboard.txt 2>&1 &
PID_DASHBOARD=$!
echo "Dashboard Process started (PID: $PID_DASHBOARD)"

./venv/bin/python3 4_process_layer/alert_process.py > logs_alert.txt 2>&1 &
PID_ALERT=$!
echo "Alert Process started (PID: $PID_ALERT)"

# 5. UI Layer
./venv/bin/python3 5_ui_layer/web_app.py > logs_webapp.txt 2>&1 &
PID_WEBAPP=$!
echo "Web App started (PID: $PID_WEBAPP)"

echo "All services running. Press Enter to stop..."
read

kill $PID_DEVICE $PID_SENSOR $PID_WEATHER $PID_TELEGRAM $PID_ANALYTICS $PID_OPTIMIZER $PID_DASHBOARD $PID_WEBAPP $PID_ALERT $PID_AUTH
echo "All services stopped."

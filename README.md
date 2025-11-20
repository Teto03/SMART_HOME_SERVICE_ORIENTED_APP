# SmartHome IoT Simulator

## Overview
This project is a microservices-based SmartHome IoT Simulator. It simulates IoT devices, collects data, interacts with external services (OpenWeatherMap, Telegram), and provides a dashboard for monitoring and energy advice.

## Architecture
The project follows a 4-layer architecture:
1.  **Data Layer**: Manages devices and sensor readings (`device_service.py`).
2.  **Adapter Layer**: Interfaces with external APIs (`weather_adapter.py`, `telegram_adapter.py`).
3.  **Business Logic Layer**: Analyzes data and provides optimization advice (`analytics_service.py`, `energy_optimizer.py`).
4.  **Process Centric Layer**: Orchestrates services for the UI and alerts (`dashboard_process.py`, `alert_process.py`).

## Setup & Running

### Prerequisites
- Python 3.x
- `flask`, `requests`, `python-dotenv` (Install via `pip install -r requirements.txt`)

### Quick Start
Run the startup script to launch all services:
```bash
./start_all.sh
```
Access the dashboard at: `http://localhost:5000`

### API Documentation

#### Data Service (Port 5001)
- `POST /devices`: Register a device.
- `POST /readings`: Add a sensor reading.
- `GET /readings/latest?device_id={id}`: Get latest reading.

#### Weather Adapter (Port 5002)
- `GET /current_weather?city={city}`: Get current weather (Mock or Real).

#### Analytics Service (Port 5003)
- `POST /analyze`: Check for anomalies.

#### Dashboard Process (Port 5004)
- `GET /api/home_status`: Get aggregated home status.

#### Telegram Adapter (Port 5005)
- `POST /send_message`: Send a Telegram message.

#### Energy Optimizer (Port 5006)
- `POST /optimize_energy`: Get energy advice based on indoor/outdoor temp.

## Configuration
Create a `.env` file based on `.env.example` and set the following variables:
- `OWM_API_KEY`: OpenWeatherMap API Key.
- `TELEGRAM_TOKEN`: Telegram Bot Token.
- `TELEGRAM_CHAT_ID`: Target Chat ID.

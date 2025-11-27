# SmartHome IoT Simulator - Project Report

## 1. Introduction
This project implements a SmartHome IoT Simulator designed to monitor indoor conditions, compare them with external weather data, and provide energy optimization advice. The system is built using a microservices architecture, ensuring scalability and modularity.

## 2. Architecture Design
The system is divided into four distinct layers, complying with the project requirements:

### 2.1 Data Layer
- **Service**: `device_service.py`
- **Role**: Acts as the single source of truth for device data. It uses a SQLite database (`devices.db`) to store device registrations and sensor readings.
- **Simulator**: `sensor_gen.py` simulates a physical temperature sensor, generating realistic data and sending it to the Data Service.

### 2.2 Adapter Layer
- **Services**: `weather_adapter.py`, `telegram_adapter.py`
- **Role**: Abstracts external dependencies.
    - The Weather Adapter connects to OpenWeatherMap (or uses a mock) to fetch outdoor conditions.
    - The Telegram Adapter handles notifications, allowing other services to send alerts without knowing Telegram API details.

### 2.3 Business Logic Layer
- **Services**: `analytics_service.py`, `energy_optimizer.py`
- **Role**: Contains the core intelligence.
    - `analytics_service.py` detects anomalies (e.g., temperature > 50°C).
    - `energy_optimizer.py` compares indoor vs. outdoor temperature to suggest actions (e.g., "Open windows").

### 2.4 Process Centric Layer
- **Services**: `dashboard_process.py`, `alert_process.py`
- **Role**: Orchestration.
    - `dashboard_process.py` aggregates data from Data, Adapter, and Business layers to serve the Frontend.
    - `alert_process.py` monitors data streams and triggers Telegram alerts via the Adapter Layer when anomalies are detected.

## 3. Implementation Details
- **Technology**: Python, Flask, SQLite.
- **Communication**: RESTful APIs with JSON payloads.
- **User Interface**: A Web Dashboard (HTML/Bootstrap) that polls the Process Layer for real-time updates.

## 4. Conclusion
The project successfully demonstrates a service-oriented architecture. The decoupling of layers allows for easy maintenance and extension (e.g., adding new sensors or external providers) without affecting the rest of the system.

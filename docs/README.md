# SmartHome IoT Simulator

## Overview
This project is a microservices-based SmartHome IoT Simulator designed to demonstrate a Service-Oriented Architecture (SOA). It simulates IoT devices, collects data, interacts with external services (OpenWeatherMap, Telegram), and provides a dashboard for monitoring and energy advice.

## Architecture
The system is strictly organized into four logical layers, complying with the course requirements:

### 1. Data Services Layer
- **Role**: Handles persistence and retrieval of data.
- **Service**: `device_service.py` (Port 5001)
- **Database**: SQLite (`devices.db`) for device state and history.

### 2. Adapter Services Layer
- **Role**: Connects the application to external APIs.
- **Services**:
    - `weather_adapter.py` (Port 5002): Fetches real-time weather from OpenWeatherMap.
    - `telegram_adapter.py` (Port 5005): Sends notifications via Telegram Bot API.

### 3. Business Logic Services Layer
- **Role**: Core intelligence and decision making.
- **Services**:
    - `energy_optimizer.py` (Port 5006): Compares indoor/outdoor conditions to suggest actions.
    - `auth_service.py` (Port 5010): Manages User Authentication (JWT) and Registration.
    - `analytics_service.py` (Port 5003): Computes usage statistics.

### 4. Process Centric Services Layer
- **Role**: Orchestration and User Gateway.
- **Services**:
    - `dashboard_process.py` (Port 5004): Aggregates data for the Web UI.
    - `alert_process.py` (Port 5007): Monitors streams and triggers alerts.

## Key Features
- **Microservices**: 7 distinct services communicating via REST/JSON.
- **Authentication**: Secure Login and Registration flow using JWT.
- **External Integration**: Real-time integration with OpenWeatherMap and Telegram.
- **Containerization**: Full Docker support for easy deployment.

## Documentation
- **[User Guide (Docker)](docs/GUIDA_COMPLETA.md)**: Detailed instructions on how to run and use the system.
- **[API Documentation](docs/openapi.yaml)**: OpenAPI/Swagger specification.

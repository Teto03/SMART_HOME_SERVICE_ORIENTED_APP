# User Guide - SmartHome IoT Simulator

This guide explains how to install, configure, and run the SmartHome IoT Simulator system.

---

## Method 1: Running with Docker

The cleanest and fastest way to start the project is to use Docker. This isolates the environment and ensures everything works without conflicts.

### Prerequisites

- **Docker Desktop** (or Docker Engine + Docker Compose) installed.

### 1. Automatic Setup (New Installation)

If you are installing the project on a new machine, run this script to configure everything automatically (database creation and .env file):

```bash
./setup_docker.sh
```

### 2. Manual Configuration (Optional)

If you prefer to do it manually or need to modify the keys:

1. Copy the example file:

   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file (optional for testing, required for full functionality):
   - `SECRET_KEY`: A random string for security.
   - `OWM_API_KEY`: Your OpenWeatherMap API key (for real weather).
   - `TELEGRAM_TOKEN`: Your Telegram Bot token (for notifications).

### 2. Startup

From the project root folder, run:

```bash
docker compose up --build --no-attach mongo -d
```

Wait a few moments. Docker will download the necessary images and start all 7 microservices.

### 3. Access

Open your browser and go to:
👉 **<http://localhost:5008>**

### 4. Shutdown

To stop the system, press `Ctrl+C` in the terminal, or run in another terminal:

```bash
docker compose down
```

### 5. Data Persistence

The system uses **MongoDB** as the database.
Data is not saved to a local file (like `users.db`), but in a **Docker Volume** managed internally by Docker.

- **Volume Name**: `mongo_data`
- **Behavior**:
  - If you shut down the system (`docker compose down`): **Data remains saved.**
  - If you restart the computer: **Data remains saved.**
  - Data is deleted **ONLY** if you explicitly run: `docker compose down -v` (with the `-v` flag which stands for volumes).

---

## Usage Guide

### Registration and Login

1. On first access, click on **Login**.
2. Select the **Register** tab.
3. Create a new user (e.g., `admin`, password `password123`).
4. Log in.

### Dashboard

- **Indoor Temp**: Simulated temperature from the internal sensor.
- **Outdoor Weather**: Current weather (from OpenWeatherMap or Mock).
- **Energy Advice**: Smart recommendations based on the comparison between indoor and outdoor (e.g., "Close windows if it's too hot outside").
- **Device Control**: Turn lights and heating on/off, and open/close windows.

### Telegram Notifications

If configured, you will receive notifications for:

- **Safety & Security**:
  - **Fire Alert**: Smoke detected.
  - **High Temperature**: Indoor temperature > 28°C.

- **Energy Efficiency**:
  - **Device Conflict**: Heater and AC running simultaneously.
  - **Energy Waste**: HVAC on with open windows.
  - **Resolution**: When these issues are resolved.

- **Status Updates**:
  - **State Changes**: Real-time alerts when any device (window, heater, AC) changes state (ON/OFF/OPEN/CLOSED).

---

## Troubleshooting

**Error: "Port already in use"**

- Make sure you don't have other services running on ports 5000-5010.
- If you were using Docker, make sure you ran `docker compose down`.

**Error: "Connection Refused"**

- Wait a few seconds after startup; services might still be loading.
- Check logs with `docker compose logs` (if using Docker) or in the `logs/` folder (if local).

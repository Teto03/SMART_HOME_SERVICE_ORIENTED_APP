# Specification Compliance Report

This document details how the **SmartHome IoT Dashboard** project satisfies the requirements for the Final Project of the 2025/2026 SDE course.

## 1. Architectural Compliance

The project strictly follows the **Service-Oriented Architecture (SOA)** pattern, organized into the four required logical layers.

### **Layer 1: Data Services Layer**
*   **Requirement**: Handle persistence, retrieval, and serve data to other modules.
*   **Implementation**:
    *   **`1_data_layer/device_service.py`**: Manages the state and history of IoT devices.
    *   **Database**: Uses an internal SQLite database (`devices.db`) for persistence.
    *   **Function**: Provides REST endpoints (`/devices`, `/readings`) for other services to store and retrieve sensor data.

### **Layer 2: Adapter Services Layer**
*   **Requirement**: Link application to the outside world (external APIs, services).
*   **Implementation**:
    *   **`2_adapter_layer/weather_adapter.py`**: Connects to the **OpenWeatherMap API** to fetch real-time weather data.
    *   **`2_adapter_layer/telegram_adapter.py`**: Connects to the **Telegram API** to send notifications to the user.
    *   **Function**: These adapters abstract external API complexity and expose standardized internal REST endpoints.

### **Layer 3: Business Logic Services Layer**
*   **Requirement**: Data manipulation, decision making, calculations.
*   **Implementation**:
    *   **`3_business_logic_layer/energy_optimizer.py`**: Analyzes indoor/outdoor temperatures and device states to recommend energy-saving actions (e.g., "Close windows to save heat").
    *   **`3_business_logic_layer/auth_service.py`**: Manages user authentication, password hashing, and JWT token generation.
    *   **`3_business_logic_layer/analytics_service.py`**: Computes statistics on device usage (e.g., average daily consumption).

### **Layer 4: Process Centric Services Layer**
*   **Requirement**: Gateway for user requests, orchestration of lower layers.
*   **Implementation**:
    *   **`4_process_layer/dashboard_process.py`**: The main orchestrator for the Web UI. It aggregates data from the *Data Service*, *Weather Adapter*, and *Energy Optimizer* to provide a unified response to the frontend.
    *   **`4_process_layer/alert_process.py`**: Monitors sensor data and orchestrates the *Telegram Adapter* to send alerts when critical thresholds are breached.

---

## 2. General Requirements Compliance

| Requirement | Implementation Details |
| :--- | :--- |
| **Min 4 Services (1 per layer)** | The project implements **7 distinct services** distributed across all 4 layers. |
| **REST-based Services** | All services are implemented using **Flask** and communicate exclusively via **HTTP/REST APIs** (GET/POST) with JSON payloads. |
| **Service Independence** | Services are decoupled. For example, the *Weather Adapter* can be replaced without changing the *Dashboard Process*, as long as the API contract remains. |
| **Data Structures** | **JSON** is used for all inter-service communication. |
| **Internal Database** | **SQLite** is used for device data (`devices.db`) and user data (`users.db`). |
| **Authentication** | Implemented via **`auth_service.py`** using **JWT (JSON Web Tokens)**. Registration and Login flows are fully supported. |

---

## 3. Project Type Compliance

The project aligns with the **3 Students Project** (Prototype System) criteria, which is the most comprehensive:

*   **Visual Interface**: A responsive Web Application (`5_ui_layer`) built with **HTML5, Bootstrap 5, and JavaScript**.
*   **Process Centric Services**:
    1.  **Dashboard Orchestration**: Aggregates weather, device status, and energy advice.
    2.  **Alert Orchestration**: Monitors streams and triggers external notifications.
    3.  **Authentication Flow**: Orchestrates user verification and session management.
*   **Access Control**:
    *   **Authentication**: Users must register and login.
    *   **Authorization**: API endpoints in the *Dashboard Process* are protected by `@require_auth` decorators, ensuring only authenticated users can control devices or view sensitive data.

## 4. Execution & Quality

*   **Deployment**: The project includes a `start_all.sh` script for one-click orchestration of all microservices.
*   **Configuration**: Security keys and external API tokens are managed via a `.env` file, following security best practices.
*   **Code Quality**: The codebase is modular, with clear separation of concerns. Each service resides in its own file/directory structure mirroring the architecture.

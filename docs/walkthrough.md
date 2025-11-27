# Walkthrough: Season Fix & Authentication

I have successfully fixed the season selection bug and implemented the required Authentication system.

## Changes

### 1. Season Bug Fix
- **Issue**: The "Season Mode" selection would reset to "Auto" on page refresh because the backend wasn't returning the stored mode.
- **Fix**: Modified `dashboard_process.py` to always return the `season_mode` in the `/api/home_status` response.
- **Verification**: Created `tests/test_season_persistence.py` which confirms that setting the season to "Winter" persists across requests.

### 2. Authentication Implementation
- **Requirement**: The project required a basic form of authentication for API endpoints.
- **Implementation**:
    - **New Service**: Created `3_business_logic_layer/auth_service.py` handling JWT token generation and verification.
    - **Dashboard Update**: Added `@require_auth` decorator to `dashboard_process.py` to protect `/settings` and `/api/devices/command`.
    - **UI Update**: Added a **Login Modal** to `index.html`.
        - Users must log in (default: `user` / `password`) to access the dashboard.
        - The token is stored in `localStorage` and sent with requests.
- **Verification**: Created `tests/test_auth_flow.py` which confirms:
    - Access is denied (401) without a token.
    - Login returns a valid token.
    - Access is granted (200) with the token.

## How to Run
1.  **Start All Services**:
    ```bash
    ./start_all.sh
    ```
2.  **Access Dashboard**:
    - Open `http://localhost:5000` (or wherever `web_app.py` points, usually port 5000 or 8080, but the dashboard process is on 5004. The UI layer `web_app.py` serves the HTML).
    - **Login Credentials**:
        - Username: `user`
        - Password: `password`

## Architecture Compliance
- The new `auth_service` fits into the **Business Logic Layer**.
- The `dashboard_process` (Process Layer) orchestrates the auth check.
- This fully satisfies the "2 Students" project requirement for authentication.

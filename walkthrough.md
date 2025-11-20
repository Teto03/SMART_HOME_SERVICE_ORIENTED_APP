# Walkthrough - Enforcing Environment Variables

I have updated the project to use `.env` files for managing secrets, enhancing security and configurability.

## Changes

### 1. Security & Configuration
- **Created `.gitignore`**: Added patterns to exclude `.env`, logs, and other sensitive/temporary files from version control.
- **Created `.env`**: Generated the actual environment file with your specific tokens for Telegram and OpenWeatherMap.
- **Created `.env.example`**: Added a template for future reference.

### 2. Codebase Updates
- **Updated `requirements.txt`**: Added `python-dotenv` dependency.
- **Updated Adapters**: Modified `telegram_adapter.py` and `weather_adapter.py` to load environment variables using `dotenv`.
- **Updated `start_all.sh`**: Removed hardcoded secrets.
- **Updated `check_env.sh`**: Added a check for `python-dotenv` and ensured it uses the virtual environment.

### 3. Documentation
- **Updated `GUIDA_COMPLETA.md`**: Revised the configuration section to explain how to use `.env` files.
- **Updated `README.md`**: Updated prerequisites and configuration instructions.

## Verification

### Environment Check
I installed `python-dotenv` and verified the environment using the updated `check_env.sh` script. All checks passed.

### Next Steps
You can now run the system as usual:
```bash
./start_all.sh
```
The services will automatically pick up the credentials from the `.env` file.

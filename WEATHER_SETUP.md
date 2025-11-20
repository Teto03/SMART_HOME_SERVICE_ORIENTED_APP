# Weather API Setup Guide

To get real-time weather data for your SmartHome IoT Simulator, you can configure a free OpenWeatherMap API key.

## 1. Get a Free API Key
1.  Go to [OpenWeatherMap](https://openweathermap.org/) and sign up for a free account.
2.  Navigate to the **API Keys** tab in your profile.
3.  Copy your generated API Key (it looks like a long string of random characters).

## 2. Configure the Simulator
1.  Open the `start_all.sh` file in this directory.
2.  Find the line:
    ```bash
    export OWM_API_KEY="MOCK_KEY"
    ```
3.  Replace `MOCK_KEY` with your actual API Key.
    ```bash
    export OWM_API_KEY="your_actual_api_key_here"
    ```
4.  Save the file.

## 3. Restart
Run `./start_all.sh` again. The dashboard will now show real weather data for any city you select!

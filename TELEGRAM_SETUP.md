# Telegram Bot Setup Guide

To receive notifications from your SmartHome IoT Simulator, you need to create a Telegram Bot and get your Chat ID.

## 1. Create a Bot
1.  Open Telegram and search for **@BotFather**.
2.  Start a chat and send the command `/newbot`.
3.  Follow the instructions to choose a name and username for your bot.
4.  **BotFather** will give you an **API Token** (e.g., `123456789:ABCdefGhI...`).
    *   Save this token. You will use it as the `TELEGRAM_TOKEN` environment variable.

## 2. Get Your Chat ID
1.  Start a chat with your new bot and send a message (e.g., "Hello").
2.  Open your browser and visit:
    `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
    *(Replace `<YOUR_BOT_TOKEN>` with the token you got in step 1)*
3.  Look for the `"chat"` object in the JSON response:
    ```json
    "chat": {
        "id": 123456789,
        "first_name": "Francesco",
        ...
    }
    ```
4.  The number next to `"id"` is your **Chat ID**.
    *   Save this ID. You will use it as the `TELEGRAM_CHAT_ID` environment variable.

## 3. Configure the Simulator
1.  Open the `start_all.sh` file.
2.  Find the **TELEGRAM CONFIGURATION** section at the top.
3.  Replace `MOCK_TOKEN` with your actual Bot Token.
4.  Replace `123456789` with your actual Chat ID.
5.  Save the file.

```bash
./start_all.sh
```

Now, when the system detects an anomaly (like a window opening), you will receive a message on Telegram!

# 🔥 Gatecraft Chaosphere Monitor

📄 **[View the script → Chaosphere_monitor.py](https://github.com/Vlkodlak148/chaosphere-monitor/blob/main/Chaosphere_monitor.py)**

A Python script that watches [dynmap.gatecraft.cz](https://dynmap.gatecraft.cz) in real time and sends you a **Discord notification** whenever an enemy enters the Chaosphere world.

---

## ✨ Features

- ⚔️ Pings you on Discord when enemies are spotted in Chaosphere
- 🧍 No ping if **you** are already in Chaosphere
- 🤝 No ping if only **allies** are present
- 📍 Shows each player's **XYZ coordinates** in the notification
- ✅ Sends an "all clear" message when Chaosphere becomes empty
- 😴 5 minute cooldown to avoid spam, but instantly pings for **new** enemies

---

## 📋 Requirements

- Python 3
- `requests` library

---

## ⚡ Setup

### 1. Install the dependency

**Linux:**
```bash
pip install requests --break-system-packages
```

**Windows:**
```bash
pip install requests
```

### 2. Get a Discord Webhook URL

1. Open the Discord channel you want alerts in
2. Click the ⚙️ gear icon → **Integrations** → **Webhooks** → **New Webhook**
3. Click **Copy Webhook URL**

### 3. Get your Discord User ID *(optional, for @mentions)*

1. Discord **Settings → Advanced → enable Developer Mode**
2. Right-click your username anywhere → **Copy User ID**

### 4. Edit the config at the top of the script

```python
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."  # your webhook
DISCORD_USER_ID     = "123456789012345678"                    # your Discord ID
MY_MINECRAFT_NAME   = "YourNameHere"                          # your MC username
ALLIES = [
    "FriendName1",
    "FriendName2",
]
```

### 5. Run it

**Linux:**
```bash
python3 Chaosphere_monitor
```

**Windows:**
```bash
python gatecraft_monitor.py
```

Keep the terminal open — the script runs continuously. Press `Ctrl+C` to stop.

---

## ⚙️ Configuration Options

| Setting | Description | Default |
|---|---|---|
| `DISCORD_WEBHOOK_URL` | Your Discord webhook URL | *required* |
| `DISCORD_USER_ID` | Your Discord ID for @mentions | `""` (disabled) |
| `CHAOSPHERE_WORLD` | Internal world name on the server | `"world_chaos"` |
| `MY_MINECRAFT_NAME` | Your MC username — suppresses pings when you're online | `"YourNameHere"` |
| `ALLIES` | List of friendly players who won't trigger pings | `[]` |
| `CHECK_INTERVAL` | How often to poll the API in seconds | `30` |
| `NOTIFY_COOLDOWN` | Seconds before re-pinging for the same players | `300` |

---

## 🔔 Ping Behaviour

| Situation | Result |
|---|---|
| Only you in Chaosphere | 😴 No ping |
| You + allies | 😴 No ping |
| You + enemies | 😴 No ping (you're already there) |
| Only allies, no enemies | 🤝 No ping |
| Enemies present, you offline | ⚔️ **Ping!** |
| Enemies + allies, you offline | ⚔️ **Ping!** (only enemies listed) |
| Chaosphere becomes empty | ✅ "All clear" message |

---
 
## ⚠️ Security Warning
 
**Never commit your real `DISCORD_WEBHOOK_URL` to a public repository.** Anyone who gets it can send messages to your Discord channel.
 
If you fork this repo, the webhook URL and Discord User ID fields are intentionally left as placeholders:
```python
DISCORD_WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"
DISCORD_USER_ID     = ""
```
Fill these in **only on your local machine** and never commit that change. A good way to prevent accidentally pushing it is to run:
```bash
git update-index --assume-unchanged Chaosphere_monitor
```
This tells git to ignore local changes to the file so you can't accidentally commit your credentials.
 
---

## 🌐 How It Works

Every 30 seconds the script calls the Gatecraft Dynmap API:
```
https://dynmap.gatecraft.cz/up/world/world/{timestamp}
```
This returns a live list of all online players and which world they are in. The script filters for anyone in `world_chaos`, ignores you and your allies, and fires a Discord webhook if any enemies remain.

---

## 📄 License

This software is distributed under the GNU General Public License v3.0 (GPL-3.0). See [LICENSE](./LICENSE) for details.

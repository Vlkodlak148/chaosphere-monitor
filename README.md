> [!CAUTION]
> **This repository is abandoned.** It is no longer maintained and will likely not receive any future updates.
>
> Looking for a similar tracker? Try [https://gctracker.xyz/](https://gctracker.xyz/). This is a separate project and is not affiliated with me.


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

### 4. Set up your credentials via `.env`

Copy the example file and fill in your values:
```bash
cp .env.example .env
nano .env
```

Your `.env` file should look like this:
```
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
DISCORD_USER_ID=123456789012345678
```

> ⚠️ The `.env` file is in `.gitignore` — it will **never** be uploaded to GitHub.

Then edit the rest of the config (allies, your MC username etc.) at the top of the script:
```python
MY_MINECRAFT_NAME = "YourNameHere"
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

**Never commit your real `.env` file to a public repository.** Anyone who gets your webhook URL can send messages to your Discord channel.

If you fork this repo:
1. The `.env` file is already in `.gitignore` so it can never be accidentally pushed
2. Copy `.env.example` to `.env` and fill in your credentials locally
3. The script itself contains no secrets — only safe placeholders

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

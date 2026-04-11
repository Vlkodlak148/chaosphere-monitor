#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════╗
║   🔥 Gatecraft Chaosphere Monitor                ║
║   Watches dynmap.gatecraft.cz for players        ║
║   in Chaosphere and pings you on Discord         ║
╚══════════════════════════════════════════════════╝

Requirements:
    pip install requests

Usage:
    1. Fill in your DISCORD_WEBHOOK_URL below
    2. Optionally fill in DISCORD_USER_ID for @mentions
    3. python gatecraft_monitor.py
"""

import requests
import time
import json
from datetime import datetime

# ════════════════════════════════════════════════
#  ⚙️  CONFIGURATION — edit these values!
# ════════════════════════════════════════════════

# Your Discord Webhook URL
# How to get one: Discord Server → Settings → Integrations → Webhooks → New Webhook → Copy URL
DISCORD_WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"

# Your Discord User ID (to @mention you). Leave "" to disable pings.
# How to get: Discord Settings → Advanced → Developer Mode ON → right-click your name → Copy User ID
DISCORD_USER_ID = ""  # e.g. "123456789012345678"

# Chaosphere world name in dynmap (confirmed: "world_chaos").
# Set to None to run in discovery mode and print all active world names.
CHAOSPHERE_WORLD = "world_chaos"

# Your Minecraft username — if YOU are in Chaosphere, no ping will be sent.
# Only alerts when someone else is there without you. Leave "" to always ping.
MY_MINECRAFT_NAME = "YourNameHere"

# Allies — players who will NOT trigger a ping (your friends/teammates).
# Add as many as you want. Case-insensitive.
ALLIES = [
    # "FriendName1",
    # "FriendName2",
]

# How often to poll the API (seconds). Don't go below 15 to be respectful.
CHECK_INTERVAL = 30

# Cooldown between repeated notifications for the same players (seconds)
NOTIFY_COOLDOWN = 300  # 5 minutes

# ════════════════════════════════════════════════
#  🌐  API
# ════════════════════════════════════════════════

DYNMAP_BASE = "https://dynmap.gatecraft.cz/up/world/world/{timestamp}"
DYNMAP_LINK = "https://dynmap.gatecraft.cz/"

# ════════════════════════════════════════════════
#  STATE
# ════════════════════════════════════════════════

last_timestamp = 0          # Dynmap uses server timestamps for delta updates
last_notified = set()       # Players we already pinged about
last_notify_time = 0        # When we last sent a Discord message


def ts():
    return datetime.now().strftime("%H:%M:%S")


def fetch_players():
    """
    Poll the Dynmap API and return (all_players, chaosphere_players, worlds_seen).
    all_players      — list of player dicts with name, world, x, y, z
    chaosphere_players — filtered to Chaosphere world only
    worlds_seen      — set of all world names currently active
    """
    global last_timestamp

    url = DYNMAP_BASE.format(timestamp=last_timestamp)
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "GatecraftMonitor/1.0"})
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[{ts()}] ⚠ Fetch error: {e}")
        return [], [], set()

    # Update timestamp for next delta poll
    last_timestamp = data.get("timestamp", 0)

    players = data.get("players", [])
    worlds_seen = {p.get("world", "?") for p in players}

    if CHAOSPHERE_WORLD is None:
        # Discovery mode — show all worlds
        return players, [], worlds_seen

    chaosphere = [p for p in players if p.get("world") == CHAOSPHERE_WORLD]
    return players, chaosphere, worlds_seen


def format_coord(x, y, z):
    return f"X:{int(x)} Y:{int(y)} Z:{int(z)}"


def send_discord(chaosphere_players, all_count):
    """Send a Discord webhook embed when players are in Chaosphere."""
    global last_notify_time

    if DISCORD_WEBHOOK_URL == "YOUR_WEBHOOK_URL_HERE":
        print(f"[{ts()}] ⚠ Set your DISCORD_WEBHOOK_URL in the config!")
        return

    now = time.time()
    if now - last_notify_time < NOTIFY_COOLDOWN:
        # Still in cooldown — but check if there are NEW players we haven't pinged
        new_players = {p["name"] for p in chaosphere_players} - last_notified
        if not new_players:
            return  # Nobody new, skip

    mention = f"<@{DISCORD_USER_ID}> " if DISCORD_USER_ID else ""
    player_count = len(chaosphere_players)

    # Build player list for embed
    player_lines = []
    for p in chaosphere_players:
        name = p.get("name", "Unknown")
        x, y, z = p.get("x", 0), p.get("y", 0), p.get("z", 0)
        player_lines.append(f"⚔️ **{name}** — `{format_coord(x, y, z)}`")

    player_text = "\n".join(player_lines) if player_lines else "*(none)*"

    embed = {
        "title": f"🔥 {player_count} player{'s' if player_count != 1 else ''} in Chaosphere!",
        "description": f"Someone is in the danger zone on **Gatecraft**!",
        "color": 0xE84545,
        "fields": [
            {
                "name": f"Players in Chaosphere ({player_count})",
                "value": player_text,
                "inline": False
            },
            {
                "name": "🌍 Total online",
                "value": str(all_count),
                "inline": True
            },
            {
                "name": "🗺️ Dynmap",
                "value": f"[Open Map]({DYNMAP_LINK})",
                "inline": True
            }
        ],
        "footer": {
            "text": f"Gatecraft Monitor • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }

    payload = {
        "content": f"{mention}⚔️ **Chaosphere alert!**",
        "embeds": [embed]
    }

    try:
        r = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        r.raise_for_status()
        names = [p["name"] for p in chaosphere_players]
        print(f"[{ts()}] ✅ Discord notified! Players: {names}")
        last_notify_time = now
        last_notified.update(p["name"] for p in chaosphere_players)
    except Exception as e:
        print(f"[{ts()}] ❌ Discord error: {e}")


def send_discord_clear():
    """Optionally notify when Chaosphere becomes empty again."""
    global last_notified
    if not last_notified:
        return  # Was already empty

    if DISCORD_WEBHOOK_URL == "YOUR_WEBHOOK_URL_HERE":
        return

    payload = {
        "embeds": [{
            "title": "✅ Chaosphere is empty",
            "description": "No players remain in the danger zone.",
            "color": 0x57F287,
            "footer": {"text": f"Gatecraft Monitor • {datetime.now().strftime('%H:%M:%S')}"}
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        print(f"[{ts()}] ✅ Sent clear notification.")
    except Exception as e:
        print(f"[{ts()}] ❌ Discord error: {e}")

    last_notified.clear()


def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║   🔥 Gatecraft Chaosphere Monitor                ║")
    print("╚══════════════════════════════════════════════════╝")

    if CHAOSPHERE_WORLD is None:
        print("  Mode    : 🔍 DISCOVERY — will list world names")
    else:
        print(f"  Watching : {CHAOSPHERE_WORLD}")

    print(f"  Interval : every {CHECK_INTERVAL}s")
    webhook_set = DISCORD_WEBHOOK_URL != "YOUR_WEBHOOK_URL_HERE"
    print(f"  Discord  : {'✅ configured' if webhook_set else '❌ NOT SET — edit DISCORD_WEBHOOK_URL'}")
    print(f"  Mention  : {'<@' + DISCORD_USER_ID + '>' if DISCORD_USER_ID else '(disabled)'}")
    print()

    consecutive_errors = 0

    while True:
        all_players, chaos_players, worlds = fetch_players()

        if not all_players and last_timestamp == 0:
            consecutive_errors += 1
            if consecutive_errors <= 3:
                print(f"[{ts()}] ⚠ No data — server may be offline or API unreachable")
        else:
            consecutive_errors = 0

        # Discovery mode
        if CHAOSPHERE_WORLD is None:
            if worlds:
                print(f"[{ts()}] 📋 Active worlds: {', '.join(sorted(worlds))}")
                print(f"          Players:")
                for p in all_players:
                    print(f"            {p['name']} → {p['world']}")
            else:
                print(f"[{ts()}] No players online")

        else:
            # Normal monitoring mode
            all_names = [p["name"] for p in chaos_players]

            # Build ignore list: yourself + allies
            ignored = {MY_MINECRAFT_NAME.lower()} if MY_MINECRAFT_NAME else set()
            ignored |= {a.lower() for a in ALLIES}

            # Check if YOU are in Chaosphere
            i_am_there = MY_MINECRAFT_NAME and any(
                p["name"].lower() == MY_MINECRAFT_NAME.lower() for p in chaos_players
            )

            # Allies in Chaosphere (not counting you)
            allies_there = [p for p in chaos_players
                            if p["name"].lower() in {a.lower() for a in ALLIES}]

            # Enemies = everyone not in the ignore list
            enemies = [p for p in chaos_players if p["name"].lower() not in ignored]

            if chaos_players:
                if i_am_there:
                    ally_names = [p["name"] for p in allies_there]
                    enemy_names = [p["name"] for p in enemies]
                    print(f"[{ts()}] 🧍 You are in Chaosphere — no ping. "
                          f"Allies: {ally_names or 'none'}  Enemies: {enemy_names or 'none'}")
                elif not enemies:
                    # Only allies present
                    ally_names = [p["name"] for p in allies_there]
                    print(f"[{ts()}] 🤝 Only allies in Chaosphere: {ally_names} — no ping.")
                else:
                    print(f"[{ts()}] ⚔️  {len(enemies)} ENEMY in Chaosphere: {[p['name'] for p in enemies]}  |  total online: {len(all_players)}")
                    send_discord(enemies, len(all_players))
            else:
                if last_notified:
                    print(f"[{ts()}] ✅ Chaosphere empty. Total online: {len(all_players)}")
                    send_discord_clear()
                else:
                    print(f"[{ts()}] 😴 Chaosphere empty. Total online: {len(all_players)}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped.")

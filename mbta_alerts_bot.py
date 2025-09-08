import os
import discord
import requests
import asyncio

# Load the bot token from environment variables (GitHub Secret: BOT_TOKEN)
DISCORD_BOT_TOKEN = os.getenv("BOT_TOKEN")
if not DISCORD_BOT_TOKEN:
    raise ValueError("❌ No BOT_TOKEN found! Did you set it as a GitHub secret?")

# Your MBTA API key (still hardcoded for now — you can move this to a secret too if you want)
MBTA_API_KEY = "9855ec1725434b0596a273fd9f7cd2b8"

# The Discord channel ID where you want to send alerts
DISCORD_CHANNEL_ID = 1334407890223628349  # Replace with your actual channel ID

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def fetch_mbta_alerts():
    """Fetch MBTA alerts and send them to Discord within message limits."""
    url = "https://api-v3.mbta.com/alerts"
    headers = {"x-api-key": MBTA_API_KEY}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "data" in data and data["data"]:
            alerts = data["data"][:10]  # Get up to 10 alerts
            alert_messages = []

            for alert in alerts:
                title = alert['attributes'].get('header', 'No Title')
                description = alert['attributes'].get('description', '')

                alert_text = f"**{title}**\n{description}"
                alert_messages.append(alert_text)

            full_message = "\n\n".join(alert_messages)

            # Split into multiple messages if over 2000 chars
            messages = []
            while len(full_message) > 2000:
                split_index = full_message[:2000].rfind("\n\n")
                if split_index == -1:
                    split_index = 2000
                messages.append(full_message[:split_index])
                full_message = full_message[split_index:].lstrip()

            messages.append(full_message)

            channel = client.get_channel(DISCORD_CHANNEL_ID)
            if channel:
                for msg in messages:
                    await channel.send(f"🚨 **MBTA Alerts** 🚨\n{msg}")
            else:
                print("⚠️ Could not find the specified channel.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching MBTA alerts: {e}")

async def background_task():
    """Runs MBTA alert fetching in the background."""
    await client.wait_until_ready()
    while not client.is_closed():
        await fetch_mbta_alerts()
        await asyncio.sleep(10800)  # Run every 3 hours (10800s)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    print(f"📡 Connected to {len(client.guilds)} servers.")
    
    for guild in client.guilds:
        print(f"- {guild.name} (ID: {guild.id})")

    if not hasattr(client, "bg_task"):
        client.bg_task = client.loop.create_task(background_task())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower() == "ping":
        await message.channel.send("Pong! 🏓")

client.run(DISCORD_BOT_TOKEN)

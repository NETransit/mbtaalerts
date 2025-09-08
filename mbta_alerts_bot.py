import discord
import requests
import asyncio

# Your bot token from the Discord Developer Portal
DISCORD_BOT_TOKEN = "MTMzNTMwNjc4NTI0MTY5ODMyNQ.GyVEk4.Ig2UYmwZ2BnwjNqE10wSvCOMgf0Bhk2_Ii-aUA"  # Replace with your bot's token

# Your MBTA API key (replace with your actual API key)
MBTA_API_KEY = "9855ec1725434b0596a273fd9f7cd2b8"  # Replace with your MBTA API key

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
        response.raise_for_status()  # Ensure request is successful
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

            # Split messages if they exceed 2000 characters
            messages = []
            while len(full_message) > 2000:
                split_index = full_message[:2000].rfind("\n\n")  # Find a logical split point
                if split_index == -1:
                    split_index = 2000  # Fallback split if no suitable boundary found
                messages.append(full_message[:split_index])
                full_message = full_message[split_index:].lstrip()

            messages.append(full_message)  # Add remaining content

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
        await asyncio.sleep(10800)  # Fetch new alerts every 3 hours

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

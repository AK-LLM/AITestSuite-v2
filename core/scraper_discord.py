import os
import json
import re
from datetime import datetime
import discord
from discord.ext import commands

# CONFIGURATION
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")
CHANNEL_IDS = [1234567890]  # Replace with your Discord channel IDs as integers
LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
DISCORD_OUT = os.path.join(LOGS_DIR, "discord_messages.json")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def extract_claims_from_text(text):
    # Very aggressive—expand as needed
    patterns = [
        r'(prompt injection|jailbreak|exploit|bypass|leak|vuln|chain|autonomous agent|CVE-\d{4}-\d+)',
        r'(api key|token|secret|private key|credential|password)',
        r'(payload:|attack:|demo:|PoC:)',
    ]
    found = []
    for pat in patterns:
        found += re.findall(pat, text, re.I)
    return found

@bot.event
async def on_ready():
    print(f"[discord] Logged in as {bot.user}")
    all_msgs = []
    for chan_id in CHANNEL_IDS:
        chan = bot.get_channel(chan_id)
        if not chan:
            print(f"[discord] Could not access channel: {chan_id}")
            continue
        async for msg in chan.history(limit=2000):
            claims = extract_claims_from_text(msg.content)
            all_msgs.append({
                "author": str(msg.author),
                "channel": str(chan),
                "content": msg.content,
                "claims": claims,
                "timestamp": msg.created_at.isoformat(),
                "attachments": [a.url for a in msg.attachments]
            })
    print(f"[discord] {len(all_msgs)} messages fetched.")
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(DISCORD_OUT, "w") as f:
        json.dump(all_msgs, f, indent=2)
    await bot.close()

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)

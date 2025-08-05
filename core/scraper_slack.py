import os
import json
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN", "PUT_YOUR_SLACK_TOKEN_HERE")
CHANNEL_IDS = ["C12345678"]  # Replace with your channel IDs (strings)
LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
SLACK_OUT = os.path.join(LOGS_DIR, "slack_messages.json")

client = WebClient(token=SLACK_TOKEN)

def extract_claims_from_text(text):
    patterns = [
        r'(prompt injection|jailbreak|exploit|bypass|leak|vuln|chain|autonomous agent|CVE-\d{4}-\d+)',
        r'(api key|token|secret|private key|credential|password)',
        r'(payload:|attack:|demo:|PoC:)',
    ]
    found = []
    for pat in patterns:
        found += re.findall(pat, text, re.I)
    return found

def get_user_map():
    users = {}
    try:
        response = client.users_list()
        for u in response["members"]:
            users[u["id"]] = u["name"]
    except Exception as e:
        print(f"[slack] User fetch failed: {e}")
    return users

def scrape_slack():
    all_msgs = []
    users = get_user_map()
    for chan_id in CHANNEL_IDS:
        try:
            response = client.conversations_history(channel=chan_id, limit=2000)
            for msg in response["messages"]:
                claims = extract_claims_from_text(msg.get("text",""))
                user = users.get(msg.get("user",""), "unknown")
                all_msgs.append({
                    "author": user,
                    "channel": chan_id,
                    "content": msg.get("text",""),
                    "claims": claims,
                    "timestamp": msg.get("ts",""),
                })
            print(f"[slack] Channel {chan_id}: {len(response['messages'])} messages.")
        except SlackApiError as e:
            print(f"[slack] Error: {e}")
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(SLACK_OUT, "w") as f:
        json.dump(all_msgs, f, indent=2)

if __name__ == "__main__":
    scrape_slack()

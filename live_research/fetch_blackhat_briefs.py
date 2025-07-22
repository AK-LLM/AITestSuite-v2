import feedparser
import os
from datetime import datetime

LIVE_RESEARCH_DIR = "./live_research/"
os.makedirs(LIVE_RESEARCH_DIR, exist_ok=True)

# Black Hat Briefings RSS (may update yearly; this is a typical example)
BLACKHAT_RSS = "https://www.blackhat.com/rss/briefings.xml"

feed = feedparser.parse(BLACKHAT_RSS)

for entry in feed.entries:
    title = entry.title.replace(" ", "_").replace("/", "_").replace("\\", "_")
    fname = f"{LIVE_RESEARCH_DIR}BlackHat_{title}_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"Title: {entry.title}\n")
        f.write(f"Summary: {entry.summary}\n")
        f.write(f"Link: {entry.link}\n\n")

print(f"Fetched {len(feed.entries)} Black Hat briefings to {LIVE_RESEARCH_DIR}")

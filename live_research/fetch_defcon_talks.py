import feedparser
import os
from datetime import datetime

LIVE_RESEARCH_DIR = "./live_research/"
os.makedirs(LIVE_RESEARCH_DIR, exist_ok=True)

# DEFCON RSS (change this if DEFCON changes their feed URL)
DEFCON_RSS = "https://defcon.org/rss/"

feed = feedparser.parse(DEFCON_RSS)

for entry in feed.entries:
    title = entry.title.replace(" ", "_").replace("/", "_").replace("\\", "_")
    fname = f"{LIVE_RESEARCH_DIR}DEFCON_{title}_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"Title: {entry.title}\n")
        f.write(f"Summary: {entry.summary}\n")
        f.write(f"Link: {entry.link}\n\n")

print(f"Fetched {len(feed.entries)} DEFCON talks to {LIVE_RESEARCH_DIR}")

import feedparser
import os
from datetime import datetime

LIVE_RESEARCH_DIR = "./live_research/"
os.makedirs(LIVE_RESEARCH_DIR, exist_ok=True)

# Example: OpenAI Research Blog RSS
AI_BLOG_RSS = "https://openai.com/research/rss.xml"

feed = feedparser.parse(AI_BLOG_RSS)

for entry in feed.entries:
    title = entry.title.replace(" ", "_").replace("/", "_").replace("\\", "_")
    fname = f"{LIVE_RESEARCH_DIR}OpenAI_{title}_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"Title: {entry.title}\n")
        f.write(f"Summary: {entry.summary if hasattr(entry, 'summary') else ''}\n")
        f.write(f"Link: {entry.link}\n\n")

print(f"Fetched {len(feed.entries)} AI/Security blog posts to {LIVE_RESEARCH_DIR}")

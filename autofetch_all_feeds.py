import feedparser
import os
from datetime import datetime

STAGING_DIR = "./staging/"
os.makedirs(STAGING_DIR, exist_ok=True)

# --- arXiv
ARXIV_QUERY = "cat:cs.CR+AND+adversarial+attack"
ARXIV_RSS = f"https://export.arxiv.org/api/query?search_query={ARXIV_QUERY}&sortBy=submittedDate&sortOrder=descending&max_results=5"
arxiv = feedparser.parse(ARXIV_RSS)
for entry in arxiv.entries:
    title = entry.title.replace(" ", "_").replace("/", "_").replace("\\", "_")
    fname = f"{STAGING_DIR}arXiv_{title}_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"Source: arXiv\n")
        f.write(f"Title: {entry.title}\n")
        f.write(f"Authors: {entry.author}\n")
        f.write(f"Summary: {entry.summary}\n")
        f.write(f"Link: {entry.link}\n\n")

# --- DEFCON
DEFCON_RSS = "https://defcon.org/rss/"
defcon = feedparser.parse(DEFCON_RSS)
for entry in defcon.entries:
    title = entry.title.replace(" ", "_").replace("/", "_").replace("\\", "_")
    fname = f"{STAGING_DIR}DEFCON_{title}_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"Source: DEFCON\n")
        f.write(f"Title: {entry.title}\n")
        f.write(f"Summary: {entry.summary}\n")
        f.write(f"Link: {entry.link}\n\n")

# --- Black Hat
BLACKHAT_RSS = "https://www.blackhat.com/rss/briefings.xml"
blackhat = feedparser.parse(BLACKHAT_RSS)
for entry in blackhat.entries:
    title = entry.title.replace(" ", "_").replace("/", "_").replace("\\", "_")
    fname = f"{STAGING_DIR}BlackHat_{title}_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"Source: Black Hat\n")
        f.write(f"Title: {entry.title}\n")
        f.write(f"Summary: {entry.summary}\n")
        f.write(f"Link: {entry.link}\n\n")

# --- Example AI/Security Blog (OpenAI, swap RSS as desired)
AI_BLOG_RSS = "https://openai.com/research/rss.xml"
ai_blog = feedparser.parse(AI_BLOG_RSS)
for entry in ai_blog.entries:
    title = entry.title.replace(" ", "_").replace("/", "_").replace("\\", "_")
    fname = f"{STAGING_DIR}OpenAI_{title}_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"Source: OpenAI Research Blog\n")
        f.write(f"Title: {entry.title}\n")
        f.write(f"Summary: {entry.summary if hasattr(entry, 'summary') else ''}\n")
        f.write(f"Link: {entry.link}\n\n")

print(f"All feeds polled. New research staged in {STAGING_DIR}")

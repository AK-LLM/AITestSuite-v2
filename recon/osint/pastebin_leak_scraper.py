import requests
import re

def scrape(keyword):
    url = "https://scrape.pastebin.com/api_scraping.php?limit=50"
    resp = requests.get(url)
    pastes = resp.json()
    for paste in pastes:
        raw = requests.get(paste['scrape_url']).text
        if keyword.lower() in raw.lower():
            print(f"[+] Leak found: {paste['scrape_url']}")

if __name__ == "__main__":
    scrape("openai.com")

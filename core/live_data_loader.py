import requests

def fetch_live_payloads():
    urls = [
        "https://llm-attacks.org/payloads/latest.json",
        # Add your own threat intel endpoints
    ]
    all_payloads = []
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                all_payloads.extend(data if isinstance(data, list) else [data])
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
    return all_payloads

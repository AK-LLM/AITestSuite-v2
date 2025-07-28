import os

def start_tor():
    print("[*] Starting Tor (requires 'tor' installed)...")
    os.system("tor &")
    print("[+] Tor should now be running on 127.0.0.1:9050")

def set_proxy_env():
    os.environ["http_proxy"] = "socks5://127.0.0.1:9050"
    os.environ["https_proxy"] = "socks5://127.0.0.1:9050"
    print("[+] Python environment now routes via Tor.")

if __name__ == "__main__":
    start_tor()
    set_proxy_env()
    print("[*] All traffic will go through Tor. Kill Tor process to stop.")

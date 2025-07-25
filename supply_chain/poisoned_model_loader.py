import requests, os

def download_and_load_model(url, dest="poisoned_model.bin"):
    r = requests.get(url)
    with open(dest, "wb") as f:
        f.write(r.content)
    print(f"Model file saved to {dest}")
    # Now simulate loading (DANGEROUS: don't execute real code)
    print("Simulate: loading model weights and scanning for triggers...")
    # Add code to inspect/check for suspicious layers or backdoors

# Usage: download_and_load_model("http://evil/poisoned_model.bin")

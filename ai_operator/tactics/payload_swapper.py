import os, random

PAYLOAD_DIR = "../../payloads/malware/"
def swap_payload(current):
    files = [f for f in os.listdir(PAYLOAD_DIR) if f.endswith(".py")]
    if not files: return current
    return random.choice(files)

if __name__ == "__main__":
    import sys
    curr = sys.argv[1] if len(sys.argv)>1 else ""
    print(swap_payload(curr))

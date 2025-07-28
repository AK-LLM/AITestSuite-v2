import base64
import random

def get_file():
    try:
        with open('/etc/passwd', 'r') as f:
            data = f.read()
    except Exception:
        data = "SIMULATED_DATA"
    return data

def obfuscate(data):
    # Multi-layer random base64 encoding
    for _ in range(random.randint(2, 5)):
        data = base64.b64encode(data.encode()).decode()
    return data

def main():
    obf = obfuscate(get_file())
    print(f"OBFUSCATED:{obf}")

if __name__ == "__main__":
    main()

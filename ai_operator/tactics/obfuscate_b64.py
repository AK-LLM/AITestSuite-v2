import base64, random

def obfuscate(s):
    for _ in range(random.randint(1, 4)):
        s = base64.b64encode(s.encode()).decode()
    return s

# Example usage
if __name__ == "__main__":
    import sys
    val = sys.argv[1] if len(sys.argv)>1 else "test"
    print(obfuscate(val))

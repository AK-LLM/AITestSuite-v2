import os
import shutil

TARGETS = [
    "../../staging/fuzz_logs/",
    "../../staging/zero_day_logs/",
    "../../ai_operator/history/"
]

for path in TARGETS:
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"[+] Scrubbed: {path}")
    else:
        print(f"[-] Path not found: {path}")

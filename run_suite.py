import os
import requests
import json
from datetime import datetime

# === CONFIGURATION ===
# Replace with your actual LLM/model endpoint:
TARGET_ENDPOINT = "http://localhost:8000/infer"  # EXAMPLE ONLY
PAYLOAD_DIRS = ["./payloads", "./scenarios"]
REPORT_FILE = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# === FUNCTION TO TEST PAYLOADS ===
def test_payload(file_path):
    # Try to infer mode (text or binary) by extension
    is_text = file_path.endswith(('.txt', '.nmea'))
    with open(file_path, 'rb') as f:
        content = f.read()
    try:
        if is_text:
            # Assume your API accepts POST with JSON
            data = {"input": content.decode('utf-8', errors='replace')}
            r = requests.post(TARGET_ENDPOINT, json=data)
        else:
            # For binary (image, wav, zip, etc), use file upload
            r = requests.post(TARGET_ENDPOINT, files={'file': (os.path.basename(file_path), content)})
        response = r.text
    except Exception as e:
        response = f"ERROR: {e}"
    return response

# === MAIN RUN LOOP ===
results = []
for folder in PAYLOAD_DIRS:
    for fname in sorted(os.listdir(folder)):
        full_path = os.path.join(folder, fname)
        if os.path.isfile(full_path):
            print(f"[*] Testing: {full_path}")
            output = test_payload(full_path)
            results.append({
                'file': full_path,
                'response': output[:400],  # Truncate to 400 chars for display
            })

with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"[*] Suite complete! Results saved to {REPORT_FILE}")

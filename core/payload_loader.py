import os

PAYLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "payloads")

def load_payloads():
    payloads = []
    if not os.path.isdir(PAYLOAD_FOLDER):
        print(f"[Payload Loader] Folder missing: {PAYLOAD_FOLDER}")
        return payloads
    for fname in os.listdir(PAYLOAD_FOLDER):
        path = os.path.join(PAYLOAD_FOLDER, fname)
        if fname.startswith("_") or os.path.isdir(path):
            continue
        try:
            with open(path, "rb") as f:
                data = f.read()
            payloads.append({"file": fname, "data": data})
        except Exception as e:
            print(f"[Payload Loader] Skipped {fname} (error: {e})")
    return payloads


import os

def safe_listdir(path):
    try:
        return os.listdir(path)
    except Exception as e:
        print(f"[Utils] Could not listdir {path}: {e}")
        return []

def safe_json_load(fp):
    import json
    try:
        return json.load(fp)
    except Exception as e:
        print(f"[Utils] JSON load error: {e}")
        return None

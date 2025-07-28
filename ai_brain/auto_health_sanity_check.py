import os
import json
import yaml
import traceback
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS_FOLDER = os.path.join(PROJECT_ROOT, "staging", "fuzz_logs")
os.makedirs(LOGS_FOLDER, exist_ok=True)
SUMMARY_LOG = os.path.join(LOGS_FOLDER, f"healthcheck_{datetime.now().strftime('%Y%m%d%H%M%S')}.log.json")

CHECKS = [
    ("Folder", "scenarios", True),
    ("Folder", "plugins", True),
    ("Folder", "payloads", True),
    ("Folder", "polyglot_chains", False),
    ("Folder", "agent_worms", False),
    ("Folder", "ai_brain", False),
    ("Folder", "staging/fuzz_logs", True),
]

def check_folder(path, must_exist=True):
    abs_path = os.path.join(PROJECT_ROOT, path)
    exists = os.path.isdir(abs_path)
    if not exists and must_exist:
        os.makedirs(abs_path, exist_ok=True)
        return False, "Created"
    return exists, "Exists" if exists else "Created"

def check_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            json.load(f)
        return True, "OK"
    except Exception as e:
        return False, str(e)

def check_yaml_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            yaml.safe_load(f)
        return True, "OK"
    except Exception as e:
        return False, str(e)

def check_py_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        # Optional: compile to check for syntax errors
        compile(code, path, "exec")
        # Extra: require METADATA and run
        if "METADATA" not in code or "def run(" not in code:
            return False, "Missing METADATA or run()"
        return True, "OK"
    except Exception as e:
        return False, str(e)

def clean_logs_folder(max_files=1500, min_free_mb=400):
    files = sorted([os.path.join(LOGS_FOLDER, f) for f in os.listdir(LOGS_FOLDER)], key=os.path.getmtime)
    if len(files) > max_files:
        to_remove = files[:len(files)-max_files]
        for f in to_remove:
            try: os.remove(f)
            except: continue
        return False, f"Trimmed logs to {max_files} files"
    # Optional: check disk usage
    statvfs = os.statvfs(LOGS_FOLDER)
    free_mb = (statvfs.f_bavail * statvfs.f_frsize) / 1024 / 1024
    if free_mb < min_free_mb:
        # Just print a warning; don't auto-delete in this version
        return False, f"Low free disk space: {free_mb:.1f} MB"
    return True, "OK"

def main():
    results = []
    # Folder checks
    for ctype, path, must in CHECKS:
        if ctype == "Folder":
            ok, msg = check_folder(path, must)
            results.append({"type": "Folder", "path": path, "status": ok, "msg": msg})
    # File checks
    folders = [p[1] for p in CHECKS]
    for folder in folders:
        abspath = os.path.join(PROJECT_ROOT, folder)
        if not os.path.isdir(abspath): continue
        for fname in os.listdir(abspath):
            path = os.path.join(abspath, fname)
            if fname.endswith(".json"):
                ok, msg = check_json_file(path)
                results.append({"type": "JSON", "path": path, "status": ok, "msg": msg})
            elif fname.endswith((".yaml", ".yml")):
                ok, msg = check_yaml_file(path)
                results.append({"type": "YAML", "path": path, "status": ok, "msg": msg})
            elif fname.endswith(".py"):
                ok, msg = check_py_file(path)
                results.append({"type": "PY", "path": path, "status": ok, "msg": msg})
    # Log cleanup
    ok, msg = clean_logs_folder()
    results.append({"type": "LOGS", "path": LOGS_FOLDER, "status": ok, "msg": msg})
    # Save log
    with open(SUMMARY_LOG, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[health_sanity] {len(results)} items checked. Results logged in: {SUMMARY_LOG}")
    errors = [r for r in results if not r["status"]]
    if errors:
        print("[health_sanity] ERRORS/WARNINGS:")
        for e in errors:
            print(e["path"], "|", e["msg"])
    else:
        print("[health_sanity] ALL OK.")

if __name__ == "__main__":
    main()

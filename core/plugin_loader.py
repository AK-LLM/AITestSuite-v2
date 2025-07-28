import os
import importlib.util
import traceback

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PLUGIN_FOLDER = os.path.join(PROJECT_ROOT, "plugins")

def is_safe_plugin(plugin_path):
    try:
        with open(plugin_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
        # Simple static checks (block dangerous modules)
        banned = ["os.system", "subprocess", "eval(", "exec(", "popen", "open(", "import socket", "import pickle"]
        for bad in banned:
            if bad in code: return False
        return True
    except Exception:
        return False

def discover_plugins():
    plugins = []
    for fname in os.listdir(PLUGIN_FOLDER):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        path = os.path.join(PLUGIN_FOLDER, fname)
        if not is_safe_plugin(path):
            print(f"[plugin_loader] SKIPPED UNSAFE: {fname}")
            continue
        try:
            spec = importlib.util.spec_from_file_location(fname[:-3], path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            # Require: METADATA, run(scenario, endpoint, api_key, mode)
            if not hasattr(mod, "METADATA") or not hasattr(mod, "run"):
                print(f"[plugin_loader] SKIP: {fname} missing METADATA/run()")
                continue
            plugins.append({"name": fname[:-3], "module": mod})
        except Exception as e:
            print(f"[plugin_loader] FAILED: {fname} {e}")
            traceback.print_exc()
    return plugins

# OPTIONAL: Script loader (if you want to expose /scripts/ to the UI)
def discover_scripts():
    SCRIPTS_FOLDER = os.path.join(PROJECT_ROOT, "scripts")
    scripts = []
    if not os.path.exists(SCRIPTS_FOLDER): return scripts
    for fname in os.listdir(SCRIPTS_FOLDER):
        if fname.endswith(".py"):
            scripts.append(fname)
    return scripts

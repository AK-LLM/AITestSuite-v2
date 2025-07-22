import importlib.util
import os

PLUGIN_FOLDER = os.path.join(os.path.dirname(__file__), "..", "plugins")

def discover_plugins():
    registry = []
    if not os.path.isdir(PLUGIN_FOLDER):
        print(f"[Plugin Loader] Folder missing: {PLUGIN_FOLDER}")
        return registry
    for fname in os.listdir(PLUGIN_FOLDER):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        path = os.path.join(PLUGIN_FOLDER, fname)
        module_name = f"plugins.{fname[:-3]}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            meta = getattr(mod, "METADATA", None)
            if meta is None or not hasattr(mod, "run"):
                print(f"[Plugin Loader] Skipped {fname} (missing METADATA or run())")
                continue
            registry.append({
                "module": mod,
                "name": meta.get("name", fname),
                "category": meta.get("category", "uncategorized"),
                "description": meta.get("description", ""),
                "risk": meta.get("risk", ""),
                "references": meta.get("references", []),
                "file": fname
            })
        except Exception as e:
            print(f"[Plugin Loader] Error loading {fname}: {e}")
    if not registry:
        print("[Plugin Loader] No valid plugins found!")
    return registry

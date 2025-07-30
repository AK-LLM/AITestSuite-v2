import os
import importlib.util
import traceback

PLUGIN_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))

def discover_plugins():
    plugins = []
    for fname in os.listdir(PLUGIN_FOLDER):
        # Ignore non-Python or private/dunder files
        if fname.endswith(".py") and not fname.startswith("_"):
            plugin_path = os.path.join(PLUGIN_FOLDER, fname)
            plugin_name = fname[:-3]
            try:
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                # Metadata Extraction
                meta = getattr(mod, "METADATA", {})
                plugin_info = {
                    "name": plugin_name,
                    "module": mod,
                    "meta": meta,
                    "version": meta.get("version", "1.0"),
                    "description": meta.get("description", ""),
                    "tags": meta.get("tags", []),
                    "risk": meta.get("risk", "Unknown"),
                    "author": meta.get("author", ""),
                    "dependencies": meta.get("dependencies", []),
                    "capabilities": meta.get("capabilities", []),
                    "safe": meta.get("safe", None),  # For audit, not for filtering
                    "file": fname,
                    "load_error": None
                }
                plugins.append(plugin_info)
                print(f"[plugin_loader] LOADED: {fname}")
            except Exception as e:
                plugins.append({
                    "name": plugin_name,
                    "module": None,
                    "meta": {},
                    "version": "ERROR",
                    "description": "",
                    "tags": [],
                    "risk": "ImportError",
                    "author": "",
                    "dependencies": [],
                    "capabilities": [],
                    "safe": None,
                    "file": fname,
                    "load_error": f"{e}\n{traceback.format_exc()}"
                })
                print(f"[plugin_loader] FAILED: {fname} with error: {e}")
                print(traceback.format_exc())
    print(f"[plugin_loader] Total plugins loaded: {len(plugins)}")
    return plugins

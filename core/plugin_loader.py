import os
import importlib.util
import traceback

PLUGIN_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))

# --- Optional: Supabase Sync ---
SUPABASE_ENABLED = False
supabase = None
try:
    from supabase import create_client
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        SUPABASE_ENABLED = True
    else:
        print("[plugin_loader] Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY.")
except ImportError:
    print("[plugin_loader] Supabase client not installed. Plugins will NOT sync to Supabase.")

def sync_plugin_to_supabase(plugin_info):
    if not SUPABASE_ENABLED or supabase is None:
        return
    # Prepare DB row from plugin_info (exclude 'module', 'load_error', 'file')
    db_row = {
        "name": plugin_info.get("name"),
        "version": plugin_info.get("version"),
        "description": plugin_info.get("description"),
        "tags": plugin_info.get("tags", []),
        "author": plugin_info.get("author"),
        "risk": plugin_info.get("risk"),
        "dependencies": plugin_info.get("dependencies", []),
        "capabilities": plugin_info.get("capabilities", []),
        "safe": plugin_info.get("safe"),
    }
    try:
        supabase.table("plugins").upsert(db_row).execute()
    except Exception as e:
        print(f"[plugin_loader] Supabase sync failed for {plugin_info.get('name')}: {e}")

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
                    "safe": meta.get("safe", None),  # For audit/report only, not for filtering
                    "file": fname,
                    "load_error": None
                }
                plugins.append(plugin_info)
                print(f"[plugin_loader] LOADED: {fname}")
                # --- Supabase Sync ---
                sync_plugin_to_supabase(plugin_info)
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

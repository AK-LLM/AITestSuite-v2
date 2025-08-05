import os
import importlib.util
import traceback
from supabase import create_client, Client

# --- CONFIG ---
SUPABASE_URL = os.environ.get("SUPABASE_URL") or "https://jpbuvxexmuzfsetslzon.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or "<YOUR_SUPABASE_SERVICE_ROLE_KEY>"  # Use service key for write ops!
PLUGIN_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))

def discover_plugins():
    plugins = []
    for fname in os.listdir(PLUGIN_FOLDER):
        if fname.endswith(".py") and not fname.startswith("_"):
            plugin_path = os.path.join(PLUGIN_FOLDER, fname)
            plugin_name = fname[:-3]
            try:
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                meta = getattr(mod, "METADATA", {})
                plugin_info = {
                    "name": plugin_name,
                    "version": meta.get("version", "1.0"),
                    "description": meta.get("description", ""),
                    "tags": meta.get("tags", []),
                    "author": meta.get("author", ""),
                    "risk": meta.get("risk", "Unknown"),
                    "dependencies": meta.get("dependencies", []),
                    "capabilities": meta.get("capabilities", []),
                    "safe": meta.get("safe", None),
                }
                plugins.append(plugin_info)
            except Exception as e:
                print(f"[db_sync_plugins] FAILED: {fname} with error: {e}")
                print(traceback.format_exc())
    print(f"[db_sync_plugins] Total plugins loaded: {len(plugins)}")
    return plugins

def sync_plugins_to_supabase(plugins, sb: Client):
    for plugin in plugins:
        # Upsert based on name
        print(f"Upserting plugin: {plugin['name']}")
        res = sb.table("plugins").upsert(plugin, on_conflict="name").execute()
        if hasattr(res, "status_code") and res.status_code not in [200, 201]:
            print(f"Error upserting {plugin['name']}: {res}")
        else:
            print(f"Plugin '{plugin['name']}' synced.")

def main():
    if not SUPABASE_URL or not SUPABASE_KEY or "<YOUR_SUPABASE_SERVICE_ROLE_KEY>" in SUPABASE_KEY:
        print("ERROR: Set SUPABASE_URL and SUPABASE_KEY as environment variables or in this file.")
        exit(1)

    # Connect to Supabase
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Scanning plugins...")
    plugins = discover_plugins()
    if not plugins:
        print("No plugins found in the plugins folder.")
        exit(0)
    print(f"Syncing {len(plugins)} plugins to Supabase...")
    sync_plugins_to_supabase(plugins, sb)
    print("Done!")

if __name__ == "__main__":
    main()

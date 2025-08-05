import os
import json

def sync_plugins_with_supabase():
    """
    Sync all plugin metadata from the plugins folder into the Supabase 'plugins' table.
    Returns: status string for UI.
    """
    # --- Supabase Credentials ---
    SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://jpbuvxexmuzfsetslzon.supabase.co"
    SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpwYnV2eGV4bXV6ZnNldHNsem9uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzNjUzNjAsImV4cCI6MjA2OTk0MTM2MH0.ZDG3Hls_I5EUJw3kXYbp8g7ft-k1icYoh3W1rNDvpHw"
    try:
        from supabase import create_client
    except Exception as e:
        return f"Supabase SDK not installed: {e}"

    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return f"Failed to connect to Supabase: {e}"

    # --- Locate plugin files ---
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    PLUGIN_FOLDER = os.path.join(PROJECT_ROOT, "plugins")
    if not os.path.exists(PLUGIN_FOLDER):
        return f"Plugins folder does not exist: {PLUGIN_FOLDER}"

    plugin_files = [f for f in os.listdir(PLUGIN_FOLDER) if f.endswith(".json") or f.endswith(".py")]
    if not plugin_files:
        return "No plugin files found in plugins directory."

    plugins_to_sync = []
    for fname in plugin_files:
        fpath = os.path.join(PLUGIN_FOLDER, fname)
        if fname.endswith(".json"):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    js = json.load(f)
                    if isinstance(js, dict):
                        plugins_to_sync.append(js)
                    elif isinstance(js, list):
                        plugins_to_sync.extend(js)
            except Exception as e:
                continue  # skip malformed JSON
        elif fname.endswith(".py"):
            # Minimal Python plugin record for registry
            plugins_to_sync.append({
                "name": fname.replace(".py", ""),
                "type": "python_plugin",
                "filename": fname
            })

    # --- Upsert each plugin into Supabase ---
    count, failed = 0, 0
    for plugin in plugins_to_sync:
        # Remove any keys Supabase might not accept (callable, etc.)
        plugin_clean = {k: v for k, v in plugin.items() if not callable(v)}
        try:
            supabase.table("plugins").upsert(plugin_clean, on_conflict="name").execute()
            count += 1
        except Exception as e:
            failed += 1

    if count == 0:
        return "No plugins synced. (Check plugin folder and Supabase schema!)"
    if failed > 0:
        return f"Partial success: {count} plugins synced, {failed} failed."
    return f"Success: {count} plugins synced to Supabase."

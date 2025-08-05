# core/db_sync_plugins.py
import os
import json
from supabase import create_client
from core.plugin_loader import discover_plugins

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def sync_plugins():
    plugins = discover_plugins()
    for p in plugins:
        meta = p["meta"]
        record = {
            "name": p["name"],
            "version": meta.get("version", "1.0"),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "author": meta.get("author", ""),
            "risk": meta.get("risk", "Unknown"),
            "dependencies": meta.get("dependencies", []),
            "capabilities": meta.get("capabilities", []),
            "safe": meta.get("safe", None),
        }
        # Insert only if not present
        try:
            existing = supabase.table("plugins").select("name").eq("name", p["name"]).execute()
            if not existing.data:
                supabase.table("plugins").insert(record).execute()
                print(f"Inserted: {p['name']}")
        except Exception as e:
            print(f"Error inserting {p['name']}: {e}")

if __name__ == "__main__":
    sync_plugins()

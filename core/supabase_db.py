import os
from supabase import create_client, Client

SUPABASE_URL = "https://jpbuvxexmuzfsetslzon.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpwYnV2eGV4bXV6ZnNldHNsem9uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzNjUzNjAsImV4cCI6MjA2OTk0MTM2MH0.ZDG3Hls_I5EUJw3kXYbp8g7ft-k1icYoh3W1rNDvpHw"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- SCENARIOS ---
def insert_scenario(scenario):
    return supabase.table("scenarios").insert(scenario).execute()

def get_scenarios():
    return supabase.table("scenarios").select("*").execute().data

# --- PLUGINS ---
def insert_plugin(plugin):
    return supabase.table("plugins").insert(plugin).execute()

def get_plugins():
    return supabase.table("plugins").select("*").execute().data

# --- RESULTS ---
def insert_result(result):
    return supabase.table("results").insert(result).execute()

def get_results(limit=1000):
    return supabase.table("results").select("*").order("run_at", desc=True).limit(limit).execute().data

# --- MUTATIONS ---
def insert_mutation(mutation):
    return supabase.table("mutations").insert(mutation).execute()

def get_mutations():
    return supabase.table("mutations").select("*").order("created_at", desc=True).execute().data

# --- FEEDS ---
def insert_feed(feed):
    return supabase.table("feeds").insert(feed).execute()

def get_feeds(limit=500):
    return supabase.table("feeds").select("*").order("ingested_at", desc=True).limit(limit).execute().data

# --- GENERIC/UTILITY ---
def query_table(table, **kwargs):
    q = supabase.table(table).select("*")
    for k, v in kwargs.items():
        q = q.eq(k, v)
    return q.execute().data

def update_by_id(table, id, update_dict):
    return supabase.table(table).update(update_dict).eq("id", id).execute()

def delete_by_id(table, id):
    return supabase.table(table).delete().eq("id", id).execute()

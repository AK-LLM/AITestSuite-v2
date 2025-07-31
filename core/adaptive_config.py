# Central config for enterprise/adaptive/red team suite
# Adjust values here to tune system behavior, add/remove data sources, or control self-learning

ADAPTIVE_CONFIG = {
    # Fitness/learning parameters
    "GENERATIONS": 3,               # Number of generations in fitness campaign
    "MUTATE_ROUNDS": 2,             # Number of mutation cycles per generation
    "TOP_K_BREED": 8,               # Top performers to use as basis for next gen
    "AUTO_PRUNE_THRESHOLD": -5,     # Plugins/scenarios below this fitness score will be flagged

    # Auto-plugin writer settings
    "NUM_NEW_PLUGINS": 2,           # How many new plugins to auto-generate per campaign
    "LLM_MODEL": "gpt-4o",          # LLM model for code/gen
    "OPENAI_API_KEY": "<YOUR_KEY>", # Replace or set as env variable

    # Zero-day harvester
    "ZERO_DAY_SOURCES": [
        "https://raw.githubusercontent.com/greshake/AITemplates/main/prompts.json",
        # Add your own threat intel/attack sources here
    ],
    "MAX_ZERO_DAY_PER_GEN": 10,     # Max zero-day attacks to inject per campaign round

    # Output/paths
    "PAYLOADS_DIR": "payloads",
    "PLUGINS_DIR": "plugins",
    "LOGS_DIR": "logs",

    # Other advanced/adaptive knobs
    "HEALTHCHECK_ON_EVERY_RUN": True,
    "EXPLAINABILITY_VERBOSE": True,
    "SAVE_ALL_GENERATIONS": True
}

def get(key, default=None):
    return ADAPTIVE_CONFIG.get(key, default)

def set(key, value):
    ADAPTIVE_CONFIG[key] = value

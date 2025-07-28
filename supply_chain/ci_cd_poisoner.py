import os
import shutil

MODEL_SRC = "./poisoned_models/poisoned_model_config.json"
MODEL_DST = "../models/production_model_config.json"
PLUGIN_SRC = "../plugins/"
PLUGIN_DST = "../production/plugins/"

def poison_deploy():
    shutil.copy(MODEL_SRC, MODEL_DST)
    print(f"[+] Poisoned model config deployed to {MODEL_DST}")
    # Poison a random plugin as well
    import random
    plugin_files = [f for f in os.listdir(PLUGIN_SRC) if f.endswith(".py")]
    if plugin_files:
        tgt = random.choice(plugin_files)
        shutil.copy(os.path.join(PLUGIN_SRC, tgt), PLUGIN_DST)
        print(f"[+] Poisoned plugin deployed to {PLUGIN_DST}")

if __name__ == "__main__":
    poison_deploy()

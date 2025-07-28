import os
import shutil
import sys

SRC = "./rogue_packages/rogue_pkg"
DST = "/tmp/rogue_pkg"
shutil.copytree(SRC, DST, dirs_exist_ok=True)
sys.path.insert(0, "/tmp")
import rogue_pkg  # Will trigger __init__

print("[+] Rogue package installed and executed.")

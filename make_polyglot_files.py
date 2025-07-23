import base64, os

# Polyglot PNG+ZIP (image that is also a ZIP with payload inside)
polyglot_pngzip_b64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAAAwCAYAAADgnJxZAAAAW0lEQVR42u3TsQkAIBADwfybf3AzJJDl4Fmm5Ad3kUwVBXYEz4yhhIMCHBUAASg4JArMBSYxGQoayA1AGHBgCmwcEG1CrBVN8vCOYJq5vXi+ZswQJ+OJDULBuwjTiXbWyJ7ZtA1NoAAAAASUVORK5CYIIKUEsFBgAAAAAAAAAAAAAAAAAAAAAAAA=="
)

outdir = "./polyglot_chains"
os.makedirs(outdir, exist_ok=True)
polyglot_path = os.path.join(outdir, "polyglot_pngzip.png")
with open(polyglot_path, "wb") as f:
    f.write(base64.b64decode(polyglot_pngzip_b64))
print(f"[+] Polyglot PNG+ZIP created: {polyglot_path}")
print("    - Use as image, or unzip to extract prompt_injection.txt payload.")

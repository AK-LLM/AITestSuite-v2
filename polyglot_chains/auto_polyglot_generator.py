import os
from datetime import datetime

OUTDIR = os.path.dirname(os.path.abspath(__file__))
pay_base = os.path.join(OUTDIR, "..", "payloads")

# Minimal PNG+ZIP (real polyglot)
def make_pngzip(payload_bytes, filename):
    # Valid PNG header + IEND
    png_head = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00"*13 + b"\x00\x00\x00\x00IEND\xaeB`\x82"
    # Minimal ZIP file containing the payload as a file
    from zipfile import ZipFile
    import io
    buf = io.BytesIO()
    with ZipFile(buf, "w") as z:
        z.writestr("payload.txt", payload_bytes)
    zip_bytes = buf.getvalue()
    # Polyglot: PNG header + ZIP archive (real-world dual-format)
    with open(filename, "wb") as f:
        f.write(png_head + zip_bytes)

def main():
    out_folder = OUTDIR
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    # Use latest .txt or .json payloads in payloads/ folder
    sources = []
    for f in os.listdir(pay_base):
        if f.endswith(".txt") or f.endswith(".json"):
            sources.append(os.path.join(pay_base, f))
    if not sources:
        print("[!] No payload sources found.")
        return
    for src in sources:
        with open(src, "rb") as f:
            payload = f.read()
        fname = os.path.join(out_folder, f"polyglot_{os.path.basename(src).split('.')[0]}_{now}.png")
        make_pngzip(payload, fname)
        print(f"[+] Polyglot PNG+ZIP generated: {fname}")

if __name__ == "__main__":
    main()

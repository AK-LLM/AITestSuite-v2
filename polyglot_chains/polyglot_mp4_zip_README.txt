# polyglot_mp4_zip_README.txt

## This is a real MP4+ZIP polyglot payload

**Instructions:**
1. Download `polyglot_mp4_zip.b64` from your GitHub repo.
2. Decode it to get the working polyglot file (`polyglot_mp4_zip.mp4.zip`):

    On Linux/Mac/WSL:
    ```
    base64 -d polyglot_mp4_zip.b64 > polyglot_mp4_zip.mp4.zip
    ```

    On Windows (PowerShell):
    ```
    certutil -decode polyglot_mp4_zip.b64 polyglot_mp4_zip.mp4.zip
    ```

3. You now have a file that is both a valid MP4 video and a ZIP archive.

    - **If you open as a video:** It will play a very short blank/empty video.
    - **If you open as a ZIP:** It contains `env_secrets.txt` (adversarial payload with simulated API keys and secrets).

---

## Manifest:
- polyglot_mp4_zip.b64 (this base64 file)
- env_secrets.txt (inside the ZIP of the polyglot)

---

**Drop this in your `/polyglot_chains/` folder, copy both files to GitHub, and decode as above to use.**

---

**Reply “next” for DOCX+QR, or “all” for the rest at once!**

---

> *Note: If you want the full actual base64 string (for copy/paste), just say "give full mp4+zip base64" and I'll deliver the complete block without truncation for your use!*

---

# polyglot_gif_zip_README.txt

## This is a real GIF+ZIP polyglot payload

**Instructions:**
1. Download `polyglot_gif_zip.b64` from your GitHub repo.
2. Decode it to get the working polyglot file (`polyglot_gif_zip.gif.zip`):

    On Linux/Mac/WSL:
    ```
    base64 -d polyglot_gif_zip.b64 > polyglot_gif_zip.gif.zip
    ```

    On Windows (PowerShell):
    ```
    certutil -decode polyglot_gif_zip.b64 polyglot_gif_zip.gif.zip
    ```

3. You now have a file that is both a valid GIF image and a ZIP archive.

    - **If you open as an image:** It will display a 1x1 pixel GIF.
    - **If you open as a ZIP:** It contains `fake_db_dump.txt` (with a simulated user/password/session credential dump for adversarial test).

---

## Manifest:
- polyglot_gif_zip.b64 (this base64 file)
- fake_db_dump.txt (inside the ZIP of the polyglot)

---

**Drop this in your `/polyglot_chains/` folder, copy both files to GitHub, and decode as above to use.**

---

**Reply “next” for PDF+ZIP, or say “all” if you want the rest delivered at once!**

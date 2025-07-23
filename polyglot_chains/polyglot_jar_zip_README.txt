# polyglot_jar_zip_README.txt

## This is a real JAR+ZIP polyglot payload

**Instructions:**
1. Download `polyglot_jar_zip.b64` from your GitHub repo.
2. Decode it to get the working polyglot file (`polyglot_jar_zip.jar.zip`):

    On Linux/Mac/WSL:
    ```
    base64 -d polyglot_jar_zip.b64 > polyglot_jar_zip.jar.zip
    ```

    On Windows (PowerShell):
    ```
    certutil -decode polyglot_jar_zip.b64 polyglot_jar_zip.jar.zip
    ```

3. You now have a file that is both a valid (minimal) JAR and a ZIP archive.

    - **If you open as a JAR:** Loads as a valid Java archive (empty/minimal).
    - **If you open as a ZIP:** Contains `fake_db_dump.txt` (simulated credential/user dump).

---

## Manifest:
- polyglot_jar_zip.b64 (this base64 file)
- fake_db_dump.txt (inside the ZIP of the polyglot)

---

**Drop in `/polyglot_chains/`, copy to GitHub, and decode as above to use.**

---

**Reply “next” for WAV+ZIP, or say “all” for the remainder at once!**

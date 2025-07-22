import os
import importlib.util

def check_plugin_health(plugin_folder):
    issues = []
    for fname in os.listdir(plugin_folder):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        path = os.path.join(plugin_folder, fname)
        try:
            spec = importlib.util.spec_from_file_location(fname, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            meta = getattr(mod, "METADATA", None)
            if meta is None:
                issues.append((fname, "Missing METADATA"))
            elif not hasattr(mod, "run"):
                issues.append((fname, "Missing run()"))
        except Exception as e:
            issues.append((fname, f"Error: {e}"))
    return issues


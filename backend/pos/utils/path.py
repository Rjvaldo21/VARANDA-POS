import os
import sys
from pathlib import Path

def get_user_data_path(app_name="VARANDA_POS"):
    if getattr(sys, 'frozen', False):
        # Electron (.exe)
        if sys.platform == "win32":
            base_path = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
        elif sys.platform == "darwin":
            base_path = os.path.expanduser("~/Library/Application Support")
        else:
            base_path = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        path = os.path.join(base_path, app_name)
        os.makedirs(path, exist_ok=True)
        return path
    else:
        # Dev mode: D:/pos-frontend/backend/
        return str(Path(__file__).resolve().parent.parent.parent)
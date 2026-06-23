"""ZFAutofill — automated score entry tool for the 正方教务系统 family.

Usage::

    python main.py

This is the entry point.  ``config.json`` is read from the same directory
as the script (or the exe when frozen by PyInstaller).
"""

import json
import os
import shutil
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from gui import MainWindow
from i18n import I18n, detect_language


def _resolve_config_path() -> str:
    """Return the absolute path to config.json.

    When running from a PyInstaller --onefile bundle the bundled copy is
    extracted to a *temporary* directory (``sys._MEIPASS``).  We don't want
    the user to edit a temp file that disappears on exit, so:

    1. If config.json exists next to the **executable** → use it.
    2. Otherwise copy the bundled default next to the executable so the
       user has a permanent copy to edit.
    3. If writing next to the executable fails (read-only directory, etc.)
       fall back to the bundled copy (read-only).

    When running from source the config simply lives next to main.py.
    """
    if getattr(sys, "frozen", False):
        # --- PyInstaller frozen bundle ---
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        target = os.path.join(exe_dir, "config.json")

        if os.path.isfile(target):
            return target

        # First run — copy bundled default next to the exe
        bundled = os.path.join(sys._MEIPASS, "config.json")
        try:
            if os.path.isfile(bundled):
                shutil.copy2(bundled, target)
            else:
                # No bundled copy; create a minimal default
                with open(target, "w", encoding="utf-8") as f:
                    json.dump({"base_url": "about:blank"}, f, indent=2)
            return target
        except OSError:
            # Read-only location — use the bundled / temp copy
            return bundled if os.path.isfile(bundled) else target

    # --- Running from source ---
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def main():
    app = QApplication(sys.argv)

    i18n = I18n(detect_language())

    config_path = _resolve_config_path()
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {}
    if not config.get("base_url"):
        config["base_url"] = "about:blank"

    w = MainWindow(i18n, config, config_path)
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

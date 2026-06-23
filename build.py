#!/usr/bin/env python3
"""Local build script — mirrors what GitHub Actions does.

Usage::

    python build.py          # default: onefile + windowed
    python build.py --dir    # faster: one-dir build (no compression)

Output goes to ``dist/``.
"""

import os
import shutil
import subprocess
import sys
import venv

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(PROJECT_DIR, "dist")
BUILD_DIR = os.path.join(PROJECT_DIR, "build")
VENV_DIR = os.path.join(PROJECT_DIR, ".venv_build")

MODULES = [
    "main.py",
    "gui.py",
    "icons.py",
    "i18n.py",
    "excel_dialog.py",
    "file_reader.py",
    "run_scores.py",
]


def get_python():
    """Return the python executable to use (inside venv if needed)."""
    venv_python = os.path.join(VENV_DIR, "bin", "python")
    if os.path.isfile(venv_python):
        return venv_python
    return sys.executable


def ensure_env():
    """Create a build venv and install dependencies if necessary."""
    venv_python = os.path.join(VENV_DIR, "bin", "python")

    if os.path.isfile(venv_python):
        print(f"Using existing venv: {VENV_DIR}")
        return venv_python

    # Check if we can install system-wide
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--dry-run", "pyinstaller"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        # If dry-run succeeds, system pip works
        print("Installing PyInstaller system-wide...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return sys.executable
    except Exception:
        pass

    # System pip blocked — create a venv
    print(f"Creating build venv in {VENV_DIR} ...")
    venv.create(VENV_DIR, with_pip=True)

    pip_cmd = [venv_python, "-m", "pip", "install", "--quiet"]
    print("Installing dependencies in venv...")
    subprocess.check_call(pip_cmd + ["-r", os.path.join(PROJECT_DIR, "requirements.txt")])
    subprocess.check_call(pip_cmd + ["pyinstaller"])

    return venv_python


def clean():
    for d in (BUILD_DIR, DIST_DIR):
        if os.path.isdir(d):
            shutil.rmtree(d)
    for spec in os.listdir(PROJECT_DIR):
        if spec.endswith(".spec"):
            os.remove(os.path.join(PROJECT_DIR, spec))


def build(python, onefile=True):
    # Platform separator: ":" for bash (Linux/macOS), ";" for Windows CMD
    sep = ";" if sys.platform == "win32" else ":"
    cmd = [
        python, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name", "ZFAutofill",
        "--add-data", f"config.json{sep}.",
        "--collect-all", "PyQt5",
        "--collect-all", "PyQtWebEngine",
    ]
    if onefile:
        cmd.append("--onefile")
    # Hidden imports for our modules (PyInstaller only takes one script)
    for m in MODULES:
        cmd.extend(["--hidden-import", m.replace(".py", "")])
    cmd.append("main.py")  # entry point

    print(f"\nRunning: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=PROJECT_DIR)

    if result.returncode != 0:
        print(f"\nBuild FAILED (exit code {result.returncode})")
        sys.exit(result.returncode)

    # Show result
    print("\n" + "=" * 60)
    print("Build succeeded!  Output:")
    print("=" * 60)
    if onefile:
        for f in os.listdir(DIST_DIR):
            fp = os.path.join(DIST_DIR, f)
            size_mb = os.path.getsize(fp) / 1024 / 1024
            print(f"  dist/{f}  ({size_mb:.1f} MB)")
    else:
        entry = os.path.join(DIST_DIR, "ZFAutofill", "ZFAutofill")
        if sys.platform == "win32":
            entry += ".exe"
        if os.path.isfile(entry):
            print(f"  dist/ZFAutofill/{os.path.basename(entry)}")
        else:
            print(f"  dist/ZFAutofill/")

    ext = ".exe" if sys.platform == "win32" else ""
    print(f"\nTo test:  cd dist && ./ZFAutofill{ext}")


if __name__ == "__main__":
    onefile = "--dir" not in sys.argv
    python = ensure_env()
    clean()
    build(python, onefile=onefile)

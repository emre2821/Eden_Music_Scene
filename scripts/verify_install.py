"""Verify built wheel by installing into a temporary target dir and importing entry modules.

This avoids creating virtual environments on systems lacking `venv`.

Usage:
    python scripts/verify_install.py
"""

import glob
import os
import subprocess
import sys
import tempfile


def run(cmd):
    print("$", " ".join(cmd))
    subprocess.check_call(cmd)


def main():
    wheels = glob.glob(os.path.join("dist", "*.whl"))
    if not wheels:
        print("No wheel found in dist/. Run build first.")
        sys.exit(2)
    wheel = wheels[0]

    with tempfile.TemporaryDirectory() as td:
        print("Installing wheel into temporary target:", td)
        run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"]) 
        run([sys.executable, "-m", "pip", "install", "--target", td, wheel])

        # Add target to sys.path and try importing entry modules
        sys.path.insert(0, td)
        # Try a few likely import prefixes because packaging layouts can vary
        tried = []
        candidates = [
            "apps.frontend.runner",
            "apps.backend.EchoDJ.dj_agent",
            "apps.backend.EdenOS_EchoShare.echoplay_prequel_complete_build",
            "eden_music_scene.apps.frontend.runner",
            "eden_music_scene.apps.backend.EchoDJ.dj_agent",
        ]
        success = True
        for mod in candidates:
            tried.append(mod)
            try:
                __import__(mod)
                print(f"Imported {mod}")
            except Exception as e:
                print(f"Could not import {mod}: {e}")
                success = False

        if not success:
            raise ImportError(f"Import checks failed for candidates: {tried}")
        print("Import checks passed for core entry modules.")


if __name__ == "__main__":
    main()

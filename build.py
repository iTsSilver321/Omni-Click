"""
Build OmniClick as a single-file .exe using PyInstaller.

Usage:
    pip install pyinstaller
    python build.py

Output: dist/OmniClick.exe
"""

import subprocess
import sys

ARGS = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--name", "OmniClick",
    "--clean",
    # Hidden imports that PyInstaller misses
    "--hidden-import", "pynput.keyboard._win32",
    "--hidden-import", "pynput.mouse._win32",
    "--hidden-import", "pystray._win32",
    # Entry point
    "main.py",
]

# Add icon if it exists
import os
if os.path.exists("assets/icon.ico"):
    ARGS.insert(-1, "--icon")
    ARGS.insert(-1, "assets/icon.ico")

if __name__ == "__main__":
    print("Building OmniClick.exe...")
    result = subprocess.run(ARGS, cwd=os.path.dirname(os.path.abspath(__file__)))
    if result.returncode == 0:
        print("\n✅ Build complete! → dist/OmniClick.exe")
    else:
        print(f"\n❌ Build failed (exit code {result.returncode})")
    sys.exit(result.returncode)

"""Compatibility entry point for the relocated build script."""

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parent / "scripts" / "build_pyinstaller.py"),
        run_name="__main__",
    )
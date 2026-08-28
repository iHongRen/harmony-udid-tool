"""Compatibility entry point for launching the application from the project root."""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from harmony_udid_tool.app import HdcUdidApp

if __name__ == "__main__":
    app = HdcUdidApp()
    app.mainloop()

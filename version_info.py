"""Compatibility exports for the relocated version module."""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from harmony_udid_tool.version import *  # noqa: F401,F403,E402

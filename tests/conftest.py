# -*- coding: utf-8 -*-
"""Host-safe tkinter stub so pytest can import main.py without a display."""

import sys
import types


def _install_tkinter_stub():
    try:
        import tkinter  # noqa: F401
        import tkinter.ttk  # noqa: F401
        return
    except (ImportError, ModuleNotFoundError):
        pass

    tk = types.ModuleType("tkinter")
    tk.Tk = type("Tk", (), {})
    tk.NORMAL = "normal"
    tk.DISABLED = "disabled"
    tk.END = "end"
    tk.WORD = "word"
    tk.FLAT = "flat"
    tk.LEFT = "left"
    tk.RIGHT = "right"
    tk.BOTH = "both"
    tk.Menu = type("Menu", (), {})
    tk.Frame = type("Frame", (), {})
    tk.Label = type("Label", (), {})
    tk.Text = type("Text", (), {})
    tk.Toplevel = type("Toplevel", (), {})
    tk.PhotoImage = type("PhotoImage", (), {})
    tk.TclError = type("TclError", (Exception,), {})
    tk.StringVar = type("StringVar", (), {})

    ttk = types.ModuleType("tkinter.ttk")
    ttk.Style = type("Style", (), {})
    ttk.Button = type("Button", (), {})
    ttk.Combobox = type("Combobox", (), {})
    tk.ttk = ttk

    sys.modules["tkinter"] = tk
    sys.modules["tkinter.ttk"] = ttk


_install_tkinter_stub()

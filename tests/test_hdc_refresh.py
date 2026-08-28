# -*- coding: utf-8 -*-
"""Host-runnable hdc refresh tests. No Harmony device required."""

import tkinter as tk
from unittest.mock import MagicMock

from harmony_udid_tool.app import HdcUdidApp, parse_hdc_device_list


class FakeVar:
    def __init__(self, value=""):
        self.value = value

    def set(self, value):
        self.value = value

    def get(self):
        return self.value


def _make_app():
    """Build a UI-less app that still runs the real worker/update methods."""
    app = HdcUdidApp.__new__(HdcUdidApp)
    app.status_value = FakeVar("正在刷新设备列表...")
    app.device_combobox = MagicMock()
    app.device_combobox.get.return_value = ""
    app.refresh_button = MagicMock()
    app.copy_button = MagicMock()
    app.udid_text_value = "正在刷新..."
    app.update_ui_text = lambda text: setattr(app, "udid_text_value", text)
    app.on_device_select = MagicMock()
    app.after = lambda _ms, func, *args: func(*args)
    return app


def test_parse_hdc_device_list_none_is_error():
    devices, status = parse_hdc_device_list(None, "hdc missing")
    assert devices == []
    assert "刷新失败" in status
    assert "hdc missing" in status


def test_parse_hdc_device_list_empty_is_error():
    devices, status = parse_hdc_device_list("", "")
    assert devices == []
    assert status.startswith("刷新失败")


def test_parse_hdc_device_list_empty_marker():
    devices, status = parse_hdc_device_list("[Empty]", "")
    assert devices == []
    assert "未检测" in status


def test_failed_hdc_list_does_not_raise_and_leaves_refreshing_state():
    app = _make_app()
    app.run_hdc_command = MagicMock(return_value=(None, "hdc missing"))

    HdcUdidApp.fetch_devices_task(app)

    assert "正在刷新" not in app.status_value.get()
    assert "hdc missing" in app.status_value.get()
    assert "正在刷新" not in app.udid_text_value
    app.refresh_button.config.assert_called_with(state=tk.NORMAL)


def test_failed_udid_fetch_surfaces_hdc_error():
    app = _make_app()
    app.run_hdc_command = MagicMock(return_value=(None, "hdc missing"))

    HdcUdidApp.fetch_udid_task(app, "DEVICE123")

    assert app.status_value.get() != "正在刷新设备列表..."
    assert "hdc missing" in app.status_value.get()
    assert "失败" in app.udid_text_value


def test_closing_device_dropdown_keeps_current_selection():
    app = _make_app()
    app.device_combobox.get.return_value = "DEVICE123"
    app.fetch_udid_task = MagicMock()
    app.focus = MagicMock()

    HdcUdidApp.on_device_select(app, None)

    assert app.device_combobox.get() == "DEVICE123"
    app.device_combobox.selection_clear.assert_not_called()
    app.device_combobox.icursor.assert_not_called()

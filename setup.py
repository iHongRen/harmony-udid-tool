# -*- coding: utf-8 -*-
from setuptools import setup

APP = ['main.py']
DATA_FILES = ["hdc","libusb_shared.dylib"]
OPTIONS = {
    "iconfile": "icon.icns",
    "plist": {
        "CFBundleName": "UDID-Tool",
        "CFBundleDisplayName": "UDID-Tool",
        "CFBundleGetInfoString": "UDID",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
         # 禁用沙盒
        'com.apple.security.app-sandbox': False,
        # 允许执行未签名代码（如 hdc）
        'com.apple.security.cs.allow-unsigned-executable-memory': True,
    },
    "packages": [],
    'includes': ['tkinter'],
    "excludes": ["wheel"],
    "resources": ["hdc","libusb_shared.dylib"],  # 添加这一行
    "strip": False
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    author="仙银",
    author_email="iamhongren@gmail.com",
    description="HarmonyOS UDID 获取工具",
    keywords="harmonyos udid tool",
     install_requires=[
        'jaraco.text',  # 添加缺失的依赖
        # 其他依赖...
    ],
)
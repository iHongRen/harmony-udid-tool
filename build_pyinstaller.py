#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller 打包脚本
使用方法: python build_pyinstaller.py
"""

import os
import platform
import subprocess
import sys
from version_info import VERSION, AUTHOR, DESCRIPTION, PRODUCT_NAME, create_version_file

def build_simple():
    """简单的 PyInstaller 打包，避免架构问题"""
    
    print(f"📦 开始打包 {PRODUCT_NAME} v{VERSION}")
    print(f"👤 作者: {AUTHOR}")
    print(f"📝 描述: {DESCRIPTION}")
    
    cmd = [
        'pyinstaller',
        '--onedir',
        '--windowed',
        f'--name={PRODUCT_NAME}',
        '--clean',
        '--add-data=hdc:.',
        '--add-data=libusb_shared.dylib:.',
        '--add-data=icon.png:.',
    ]
    
    # 根据平台添加图标和版本信息
    if platform.system() == "Darwin":
        cmd.extend(['--icon=icon.icns', '--add-data=icon.icns:.'])
    elif platform.system() == "Windows":
        # Windows 需要先创建版本信息文件
        print("🔧 创建 Windows 版本信息文件...")
        create_version_file()
        cmd.extend([
            '--icon=icon.ico', 
            '--add-data=icon.ico:.',
            '--version-file=version_info.txt'  # 添加版本信息
        ])
    
    cmd.append('main.py')
    
    print("\n开始打包...")
    print("执行命令:", ' '.join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ 打包成功!")
        print(f"📁 输出目录: dist/{PRODUCT_NAME}/")
        
        # 显示版本信息
        print(f"\n📋 应用信息:")
        print(f"   名称: {PRODUCT_NAME}")
        print(f"   版本: {VERSION}")
        print(f"   作者: {AUTHOR}")
        print(f"   描述: {DESCRIPTION}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败: {e}")
        return False

def build_app_bundle():
    """创建 macOS .app 包"""
    if platform.system() != "Darwin":
        print("App Bundle 只支持 macOS")
        return False
        
    print("\n开始创建 .app 包...")
    cmd = ['pyinstaller', 'UDID-Tool.spec', '--clean']
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ .app 包创建成功!")
        print(f"输出目录: dist/UDID-Tool.app")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ .app 包创建失败: {e}")
        return False

def main():
    print("PyInstaller 打包工具")
    print("1. 简单打包 (推荐)")
    print("2. 创建 .app 包 (仅 macOS)")
    
    choice = input("\n请选择打包方式 (1/2): ").strip()
    
    if choice == "1":
        build_simple()
    elif choice == "2":
        if build_simple():
            build_app_bundle()
    else:
        print("直接执行简单打包...")
        build_simple()

if __name__ == "__main__":
    main()
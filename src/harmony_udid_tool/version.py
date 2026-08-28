# -*- coding: utf-8 -*-
"""
版本信息模块
包含应用程序的版本信息和 Windows 版本文件生成功能
"""

import os
import platform

# 应用程序基本信息
VERSION = "1.1.0"
AUTHOR = "仙银"
PRODUCT_NAME = "HarmonyOS-UDID-Tool"
DESCRIPTION = "HarmonyOS UDID 获取工具"
COPYRIGHT = "Copyright © 2025 仙银. All rights reserved."
COMPANY_NAME = "仙银工作室"
INTERNAL_NAME = "hdc-udid-tool"
ORIGINAL_FILENAME = "HarmonyOS-UDID-Tool.exe"

# 版本号解析
VERSION_PARTS = VERSION.split('.')
MAJOR_VERSION = int(VERSION_PARTS[0]) if len(VERSION_PARTS) > 0 else 1
MINOR_VERSION = int(VERSION_PARTS[1]) if len(VERSION_PARTS) > 1 else 0
PATCH_VERSION = int(VERSION_PARTS[2]) if len(VERSION_PARTS) > 2 else 0
BUILD_VERSION = 1

def create_version_file():
    """创建 Windows 版本信息文件"""
    if platform.system() != "Windows":
        print("⚠️  版本文件仅在 Windows 平台需要")
        return
    
    version_info_content = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=({MAJOR_VERSION}, {MINOR_VERSION}, {PATCH_VERSION}, {BUILD_VERSION}),
    prodvers=({MAJOR_VERSION}, {MINOR_VERSION}, {PATCH_VERSION}, {BUILD_VERSION}),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{COMPANY_NAME}'),
        StringStruct(u'FileDescription', u'{DESCRIPTION}'),
        StringStruct(u'FileVersion', u'{VERSION}'),
        StringStruct(u'InternalName', u'{INTERNAL_NAME}'),
        StringStruct(u'LegalCopyright', u'{COPYRIGHT}'),
        StringStruct(u'OriginalFilename', u'{ORIGINAL_FILENAME}'),
        StringStruct(u'ProductName', u'{PRODUCT_NAME}'),
        StringStruct(u'ProductVersion', u'{VERSION}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    try:
        with open('version_info.txt', 'w', encoding='utf-8') as f:
            f.write(version_info_content)
        print("✅ Windows 版本信息文件创建成功: version_info.txt")
    except Exception as e:
        print(f"❌ 创建版本信息文件失败: {e}")

def get_version_info():
    """获取版本信息字典"""
    return {
        'version': VERSION,
        'author': AUTHOR,
        'product_name': PRODUCT_NAME,
        'description': DESCRIPTION,
        'copyright': COPYRIGHT,
        'company_name': COMPANY_NAME,
        'internal_name': INTERNAL_NAME,
        'original_filename': ORIGINAL_FILENAME,
        'major_version': MAJOR_VERSION,
        'minor_version': MINOR_VERSION,
        'patch_version': PATCH_VERSION,
        'build_version': BUILD_VERSION
    }

def print_version_info():
    """打印版本信息"""
    info = get_version_info()
    print(f"📋 应用信息:")
    print(f"   产品名称: {info['product_name']}")
    print(f"   版本: {info['version']}")
    print(f"   作者: {info['author']}")
    print(f"   描述: {info['description']}")
    print(f"   版权: {info['copyright']}")

if __name__ == "__main__":
    print_version_info()
    if platform.system() == "Windows":
        create_version_file()
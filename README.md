# HarmonyOS UDID 获取工具

<div align="center">

<img src="icon.png" width="200">


**一个简单易用的 HarmonyOS 设备 UDID 获取工具**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)]()

[功能特性](#功能特性) • [安装使用](#安装使用) • [常见问题](#常见问题) 

</div>

## 📖 简介

HarmonyOS UDID 获取工具是一个跨平台的图形界面应用程序，专门用于获取 HarmonyOS 设备的 UDID（Unique Device Identifier）。该工具基于华为官方的 HDC命令行工具，提供了友好的图形界面，让非开发者能够轻松获取设备的唯一标识符。

## ✨ 功能特性

- 🖥️ **跨平台支持** - 支持 Windows、macOS 和 Linux 系统
- 🔍 **自动设备检测** - 自动扫描并列出连接的 HarmonyOS 设备
- 📋 **一键复制** - 支持一键复制 UDID 到剪贴板
- 🎨 **现代化界面** - 简洁美观的图形用户界面
- 🔄 **实时刷新** - 支持实时刷新设备列表
- 📱 **多设备支持** - 同时管理多个连接的设备
- 🛡️ **安全可靠** - 基于华为官方 HDC 工具，安全可信

## 🚀 安装使用

### 方式一：下载预编译版本（推荐）

1. 前往 [Releases](https://github.com/iHongRen/hdc-uuid-tool/releases) 页面
2. 下载适合你系统的版本：
   - **Windows**: `HarmonyOS-UDID-Tool-Windows.zip`
   - **macOS**: `HarmonyOS-UDID-Tool-macOS.zip`
   - **Linux**: `HarmonyOS-UDID-Tool-Linux.zip`
3. 解压并运行应用程序

### 方式二：从源码运行

#### 环境要求

- Python 3.7 或更高版本
- tkinter（通常随 Python 一起安装）

#### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/iHongRen/hdc-uuid-tool.git
cd hdc-uuid-tool

# 直接运行应用
python main.py

# 安装打包工具
pip install pyinstaller
```



### 构建可执行文件

使用提供的一键打包脚本：

```bash
# 一键自动打包（推荐）
python build_pyinstaller.py
```

脚本会自动：
- 🔍 检测你的操作系统
- 🧹 清理旧的构建文件
- 📦 选择最适合的打包方式
- ✅ 验证打包结果
- 🔧 修复版本信息

#### 打包结果

- 生成 `dist/` 目录


### 项目结构

```
hdc-uuid-tool/
├── main.py                 # 主程序入口
├── version_info.py         # 版本信息管理
├── build_pyinstaller.py    # 一键打包脚本
├── hdc                     # HDC 可执行文件
├── libusb_shared.dylib     # macOS 动态库
├── icon.png                # 应用图标 (PNG)
├── icon.ico                # Windows 图标
├── icon.icns               # macOS 图标
├── README.md               # 项目说明
└── LICENSE                 # 开源协议
```

## 📱 使用说明

### 基本操作

1. **连接设备**
   - 使用 USB 数据线连接 HarmonyOS 设备到电脑
   - 确保设备已开启开发者模式和 USB 调试

2. **获取 UDID**
   - 启动应用程序
   - 点击"刷新设备"按钮扫描连接的设备
   - 从下拉列表中选择目标设备
   - UDID 将自动显示在文本框中

3. **复制 UDID**
   - 点击"复制 UDID"按钮
   - 或者右键点击 UDID 文本框选择复制

### 设备连接要求

- ✅ HarmonyOS 设备已连接到电脑
- ✅ 设备已开启开发者模式
- ✅ 设备已开启 USB 调试

## ❓ 常见问题

### Q: 为什么检测不到设备？

**A:** 请检查以下几点：
- 确保设备已正确连接到电脑
- 确认设备已开启开发者模式和 USB 调试
- 检查是否已授权电脑的连接请求
- 尝试重新连接设备或更换 USB 数据线

### Q: 支持哪些 HarmonyOS 版本？

**A:** 理论上支持所有支持 HDC 调试的 HarmonyOS 版本，包括：
- HarmonyOS 2.0+
- HarmonyOS NEXT
- 其他基于 HarmonyOS 的设备

### Q: 如何开启 HarmonyOS 开发者模式？

**A:** 
1. 进入"设置" > "关于本机"
2. 连续点击"软件版本" 7 次
3. 返回"设置" > "系统" > "开发者选项"
4. 开启"USB 调试"


<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐️**

</div>
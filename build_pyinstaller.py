# -*- coding: utf-8 -*-
"""
PyInstaller 一键打包脚本
使用方法: python build_pyinstaller.py

功能:
- 自动检测系统环境并选择最佳打包方式
- 自动生成版本信息文件
- 清理旧的打包文件
- 验证打包结果
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from version_info import VERSION, AUTHOR, DESCRIPTION, PRODUCT_NAME, create_version_file, print_version_info

def clean_build_files():
    """清理旧的构建文件"""
    print("🧹 清理旧的构建文件...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec', 'version_info.txt']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   删除目录: {dir_name}")
    
    # 清理 spec 文件和版本信息文件
    for pattern in files_to_clean:
        if pattern == '*.spec':
            for spec_file in Path('.').glob('*.spec'):
                spec_file.unlink()
                print(f"   删除文件: {spec_file}")
        else:
            if os.path.exists(pattern):
                os.remove(pattern)
                print(f"   删除文件: {pattern}")

def check_dependencies():
    """检查打包依赖"""
    print("🔍 检查打包依赖...")
    
    # 检查 PyInstaller
    try:
        result = subprocess.run(['pyinstaller', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"   PyInstaller: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller 未安装，请运行: pip install pyinstaller")
        return False
    
    # macOS 特定依赖检查
    if platform.system() == "Darwin":
        # 检查 hdiutil 命令（创建 DMG 包需要）
        try:
            subprocess.run(['hdiutil', 'help'], 
                          capture_output=True, text=True, check=True)
            print("   hdiutil: 可用")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ hdiutil 命令不可用，无法创建 DMG 包")
            return False
    
    # 检查必要文件
    required_files = ['main.py', 'hdc', 'icon.png', 'donate.png']
    if platform.system() == "Darwin":
        required_files.extend(['icon.icns', 'libusb_shared.dylib'])
    elif platform.system() == "Windows":
        required_files.append('icon.ico')
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    print("✅ 依赖检查通过")
    return True

def build_simple():
    """简单的 PyInstaller 打包，避免架构问题"""
    
    print_version_info()
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 清理旧文件
    clean_build_files()
    
    print(f"\n📦 开始打包 {PRODUCT_NAME} v{VERSION}")
    
    cmd = [
        'pyinstaller',
        '--onedir',
        '--windowed',
        f'--name={PRODUCT_NAME}',
        '--clean',
        '--noconfirm',  # 不询问覆盖
        '--add-data=hdc:.',
        '--add-data=icon.png:.',
        '--add-data=donate.png:.',
    ]
    
    # 根据平台添加特定配置
    if platform.system() == "Darwin":
        cmd.extend([
            '--icon=icon.icns', 
            '--add-data=icon.icns:.',
            '--add-data=libusb_shared.dylib:.'
        ])
    elif platform.system() == "Windows":
        # Windows 需要先创建版本信息文件
        print("🔧 创建 Windows 版本信息文件...")
        create_version_file()
        cmd.extend([
            '--icon=icon.ico', 
            '--add-data=icon.ico:.',
            '--version-file=version_info.txt'
        ])
    elif platform.system() == "Linux":
        cmd.extend([
            '--add-data=icon.png:.'
        ])
    
    cmd.append('main.py')
    
    print("\n🚀 执行打包命令...")
    print(f"命令: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ 打包成功!")
        
        # 验证打包结果
        verify_build()
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败: {e}")
        return False

def verify_build():
    """验证打包结果"""
    print("\n🔍 验证打包结果...")
    
    dist_dir = Path(f"dist/{PRODUCT_NAME}")
    if not dist_dir.exists():
        print("❌ 打包目录不存在")
        return False
    
    # 检查主执行文件
    if platform.system() == "Windows":
        exe_file = dist_dir / f"{PRODUCT_NAME}.exe"
    else:
        exe_file = dist_dir / PRODUCT_NAME
    
    if not exe_file.exists():
        print(f"❌ 主执行文件不存在: {exe_file}")
        return False
    
    # 检查资源文件
    required_resources = ['hdc', 'icon.png', 'donate.png']
    if platform.system() == "Darwin":
        required_resources.extend(['icon.icns', 'libusb_shared.dylib'])
    elif platform.system() == "Windows":
        required_resources.append('icon.ico')
    
    missing_resources = []
    for resource in required_resources:
        if not (dist_dir / resource).exists():
            missing_resources.append(resource)
    
    if missing_resources:
        print(f"⚠️  缺少资源文件: {', '.join(missing_resources)}")
    
    # 计算打包大小
    total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    
    print(f"✅ 打包验证完成")
    print(f"📁 输出目录: {dist_dir}")
    print(f"📊 打包大小: {size_mb:.1f} MB")
    print(f"🎯 主执行文件: {exe_file.name}")
    
    return True



def create_app_bundle():
    """创建 macOS .app 包"""
    if platform.system() != "Darwin":
        print("❌ App Bundle 只支持 macOS")
        return False
    
    print_version_info()
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 清理旧文件
    clean_build_files()
    
    print(f"\n📦 开始创建 macOS .app 包 {PRODUCT_NAME} v{VERSION}")
    
    cmd = [
        'pyinstaller',
        '--onedir',
        '--windowed',
        f'--name={PRODUCT_NAME}',
        '--clean',
        '--noconfirm',
        '--icon=icon.icns',
        '--add-data=hdc:.',
        '--add-data=icon.png:.',
        '--add-data=donate.png:.',
        '--add-data=icon.icns:.',
        '--add-data=libusb_shared.dylib:.',
        # macOS 特定选项
        '--osx-bundle-identifier=com.xianyin.harmonyos-udid-tool',
        'main.py'
    ]
    
    print("\n🚀 执行 .app 包创建命令...")
    print(f"命令: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ .app 包创建成功!")
        
        # 验证 .app 包
        if verify_app_bundle():
            # 创建 DMG 包
            return create_dmg_package()
        
        return False
    except subprocess.CalledProcessError as e:
        print(f"\n❌ .app 包创建失败: {e}")
        return False

def fix_app_version():
    """修复 macOS .app 包中的版本信息"""
    print("� 修复 . app 包版本信息...")
    
    app_path = Path(f"dist/{PRODUCT_NAME}.app")
    info_plist_path = app_path / "Contents" / "Info.plist"
    
    if not info_plist_path.exists():
        print("❌ Info.plist 文件不存在")
        return False
    
    try:
        # 读取 Info.plist 文件
        with open(info_plist_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换版本信息
        content = content.replace(
            '<key>CFBundleShortVersionString</key>\n\t<string>0.0.0</string>',
            f'<key>CFBundleShortVersionString</key>\n\t<string>{VERSION}</string>'
        )
        
        # 添加 CFBundleVersion 如果不存在
        if 'CFBundleVersion' not in content:
            # 在 CFBundleShortVersionString 后添加 CFBundleVersion
            content = content.replace(
                f'<key>CFBundleShortVersionString</key>\n\t<string>{VERSION}</string>',
                f'<key>CFBundleShortVersionString</key>\n\t<string>{VERSION}</string>\n\t<key>CFBundleVersion</key>\n\t<string>{VERSION}</string>'
            )
        
        # 写回文件
        with open(info_plist_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 版本信息已更新为 {VERSION}")
        return True
        
    except Exception as e:
        print(f"❌ 修复版本信息失败: {e}")
        return False

def verify_app_bundle():
    """验证 macOS .app 包"""
    print("\n🔍 验证 .app 包...")
    
    app_path = Path(f"dist/{PRODUCT_NAME}.app")
    if not app_path.exists():
        print("❌ .app 包不存在")
        return False
    
    # 检查 .app 包结构
    contents_path = app_path / "Contents"
    macos_path = contents_path / "MacOS"
    resources_path = contents_path / "Resources"
    
    if not all([contents_path.exists(), macos_path.exists(), resources_path.exists()]):
        print("❌ .app 包结构不完整")
        return False
    
    # 检查主执行文件
    exe_file = macos_path / PRODUCT_NAME
    if not exe_file.exists():
        print(f"❌ 主执行文件不存在: {exe_file}")
        return False
    
    # 修复版本信息
    fix_app_version()
    
    # 计算 .app 包大小
    total_size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    
    print(f"✅ .app 包验证完成")
    print(f"📁 输出包: {app_path}")
    print(f"📊 包大小: {size_mb:.1f} MB")
    print(f"🎯 主执行文件: {exe_file}")
    
    return True

def create_dmg_package():
    """创建 macOS .dmg 安装包"""
    print("\n📦 开始创建 .dmg 安装包...")
    
    app_path = Path(f"dist/{PRODUCT_NAME}.app")
    dmg_name = f"{PRODUCT_NAME}-{VERSION}.dmg"
    dmg_path = Path(f"dist/{dmg_name}")
    temp_dmg_dir = Path("dist/dmg_temp")
    
    try:
        # 创建临时目录用于 DMG 内容
        if temp_dmg_dir.exists():
            shutil.rmtree(temp_dmg_dir)
        temp_dmg_dir.mkdir(parents=True)
        
        # 复制 .app 到临时目录
        print("📋 复制 .app 包到临时目录...")
        shutil.copytree(app_path, temp_dmg_dir / f"{PRODUCT_NAME}.app")
        
        # 创建 Applications 文件夹的符号链接
        print("🔗 创建 Applications 快捷方式...")
        applications_link = temp_dmg_dir / "Applications"
        subprocess.run(['ln', '-s', '/Applications', str(applications_link)], check=True)
        
        # 删除旧的 DMG 文件（如果存在）
        if dmg_path.exists():
            dmg_path.unlink()
        
        # 创建 DMG 包
        print("🔨 创建 DMG 包...")
        create_dmg_cmd = [
            'hdiutil', 'create',
            '-volname', f"{PRODUCT_NAME} {VERSION}",
            '-srcfolder', str(temp_dmg_dir),
            '-ov',
            '-format', 'UDZO',
            str(dmg_path)
        ]
        
        print(f"命令: {' '.join(create_dmg_cmd)}")
        subprocess.run(create_dmg_cmd, check=True)
        
        # 清理临时目录
        shutil.rmtree(temp_dmg_dir)
        
        # 验证 DMG 包
        if verify_dmg_package(dmg_path):
            print(f"\n✅ DMG 包创建成功: {dmg_path}")
            return True
        else:
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建 DMG 包失败: {e}")
        # 清理临时目录
        if temp_dmg_dir.exists():
            shutil.rmtree(temp_dmg_dir)
        return False
    except Exception as e:
        print(f"❌ 创建 DMG 包时发生错误: {e}")
        # 清理临时目录
        if temp_dmg_dir.exists():
            shutil.rmtree(temp_dmg_dir)
        return False

def verify_dmg_package(dmg_path):
    """验证 DMG 包"""
    print("\n🔍 验证 DMG 包...")
    
    if not dmg_path.exists():
        print("❌ DMG 包不存在")
        return False
    
    try:
        # 检查 DMG 包信息
        info_cmd = ['hdiutil', 'imageinfo', str(dmg_path)]
        result = subprocess.run(info_cmd, capture_output=True, text=True, check=True)
        
        # 计算 DMG 包大小
        dmg_size = dmg_path.stat().st_size / (1024 * 1024)
        
        print(f"✅ DMG 包验证完成")
        print(f"📁 DMG 文件: {dmg_path}")
        print(f"📊 文件大小: {dmg_size:.1f} MB")
        print(f"💡 安装说明: 双击 DMG 文件，将 {PRODUCT_NAME}.app 拖拽到 Applications 文件夹")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ DMG 包验证失败: {e}")
        return False

def show_build_info():
    """显示构建环境信息"""
    print("🔧 构建环境信息:")
    print(f"   操作系统: {platform.system()} {platform.release()}")
    print(f"   架构: {platform.machine()}")
    print(f"   Python 版本: {sys.version.split()[0]}")
    
    # 检查 PyInstaller 版本
    try:
        result = subprocess.run(['pyinstaller', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"   PyInstaller: {result.stdout.strip()}")
    except:
        print("   PyInstaller: 未安装")
    
    print()



def auto_build():
    """自动检测系统环境并选择最佳打包方式"""
    print("=" * 50)
    print(f"🚀 {PRODUCT_NAME} 一键自动打包工具")
    print("=" * 50)
    
    # 显示构建环境信息
    show_build_info()
    
    # 根据系统自动选择打包方式
    system = platform.system()
    print(f"🔍 检测到系统: {system}")
    
    if system == "Windows":
        print("📦 Windows 环境 - 使用标准目录打包")
        return build_simple()
    elif system == "Darwin":
        print("📦 macOS 环境 - 创建 .app 包")
        return create_app_bundle()
    elif system == "Linux":
        print("📦 Linux 环境 - 使用标准目录打包")
        return build_simple()
    else:
        print(f"⚠️  未知系统 {system} - 使用标准打包")
        return build_simple()

def main():
    """主函数 - 一键自动打包"""
    try:
        success = auto_build()
        if success:
            print("\n🎉 打包完成!")
        else:
            print("\n❌ 打包失败!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Linux/Unix Agent Tool 安装脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        print(f"   当前版本: {sys.version}")
        return False
    
    print(f"✅ Python版本: {sys.version.split()[0]}")
    return True


def install_dependencies():
    """安装依赖包"""
    print("\n📦 安装依赖包...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ 依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False


def create_executable():
    """创建可执行文件链接"""
    print("\n🔗 创建可执行文件...")
    
    script_dir = Path(__file__).parent.absolute()
    main_script = script_dir / "main.py"
    
    if os.name == 'posix':  # Linux/macOS
        # 创建bash脚本
        executable_content = f'''#!/bin/bash
cd "{script_dir}"
python3 main.py "$@"
'''
        executable_path = Path.home() / "bin" / "agent-tool"
        
        # 确保~/bin目录存在
        executable_path.parent.mkdir(exist_ok=True)
        
        # 写入脚本
        with open(executable_path, 'w') as f:
            f.write(executable_content)
        
        # 设置可执行权限
        executable_path.chmod(0o755)
        
        print(f"✅ 创建可执行文件: {executable_path}")
        print("   请确保 ~/bin 在您的PATH环境变量中")
        print("   可以运行以下命令添加到PATH:")
        print('   echo \'export PATH="$HOME/bin:$PATH"\' >> ~/.bashrc')
        
    else:  # Windows
        # 创建批处理文件
        executable_content = f'''@echo off
cd /d "{script_dir}"
python main.py %*
'''
        executable_path = script_dir / "agent-tool.bat"
        
        with open(executable_path, 'w') as f:
            f.write(executable_content)
        
        print(f"✅ 创建可执行文件: {executable_path}")
        print("   您可以将此目录添加到系统PATH环境变量中")


def setup_config():
    """设置初始配置"""
    print("\n⚙️ 配置初始化...")
    
    choice = input("是否现在进行配置初始化？(y/n) [n]: ").lower().strip()
    
    if choice in ['y', 'yes']:
        try:
            subprocess.run([sys.executable, "main.py", "--setup"])
        except KeyboardInterrupt:
            print("\n配置初始化已取消")
    else:
        print("跳过配置初始化，请稍后运行: python main.py --setup")


def show_completion_message():
    """显示安装完成信息"""
    print("\n" + "="*60)
    print("🎉 Agent Tool 安装完成！")
    print("="*60)
    
    print("\n📋 后续步骤:")
    print("1. 运行配置初始化:")
    print("   python main.py --setup")
    print()
    print("2. 启动程序:")
    print("   python main.py")
    print()
    print("3. 查看帮助:")
    print("   python main.py --help")
    print()
    
    print("📚 更多信息请查看 README.md 文件")
    print("="*60)


def main():
    """主安装流程"""
    print("🤖 Linux/Unix Agent Tool 安装程序")
    print("="*50)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 安装依赖
    if not install_dependencies():
        return False
    
    # 创建可执行文件
    create_executable()
    
    # 配置初始化
    setup_config()
    
    # 显示完成信息
    show_completion_message()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n安装已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中发生错误: {e}")
        sys.exit(1)

# -*- coding: utf-8 -*-
"""
启动器诊断工具
用于快速检查环境配置和依赖是否正常
"""
import sys
import os
from pathlib import Path

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50)

def check_python():
    """检查Python版本"""
    print(f"\n✅ Python版本: {sys.version}")
    print(f"   可执行文件: {sys.executable}")

def check_dependencies():
    """检查依赖模块"""
    print("\n检查依赖模块...")
    
    modules = {
        "pandas": "数据处理",
        "openpyxl": "Excel文件处理",
        "fuzzywuzzy": "模糊匹配",
        "numpy": "数值计算",
        "tkinter": "图形界面",
        "xlrd": "旧版Excel支持"
    }
    
    all_ok = True
    for module, desc in modules.items():
        try:
            __import__(module)
            print(f"  ✅ {module:20s} - {desc}")
        except ImportError as e:
            print(f"  ❌ {module:20s} - 缺失!")
            all_ok = False
    
    return all_ok

def check_tools():
    """检查工具文件"""
    print("\n检查工具文件...")
    
    tools_dir = Path("tools")
    if not tools_dir.exists():
        print("  ❌ tools目录不存在!")
        return False
    
    tools = [
        "merge_tool_gui.py",
        "cross_merge_gui.py",
        "deduplicate_tool.py",
        "check_join_fields.py"
    ]
    
    all_ok = True
    for tool in tools:
        tool_path = tools_dir / tool
        if tool_path.exists():
            size = tool_path.stat().st_size
            print(f"  ✅ {tool:25s} ({size:,} 字节)")
        else:
            print(f"  ❌ {tool:25s} - 不存在!")
            all_ok = False
    
    return all_ok

def check_venv():
    """检查虚拟环境"""
    print("\n检查虚拟环境...")
    
    venv_path = Path(".venv")
    if venv_path.exists():
        print(f"  ✅ 虚拟环境存在: {venv_path.absolute()}")
        
        # 检查Python可执行文件
        python_exe = venv_path / "Scripts" / "python.exe"
        if python_exe.exists():
            print(f"  ✅ Python可执行文件: {python_exe}")
            return True
        else:
            print(f"  ❌ Python可执行文件不存在!")
            return False
    else:
        print(f"  ⚠️  未使用虚拟环境（使用系统Python）")
        return True

def main():
    print_header("早发冠心病数据处理工具集 - 环境诊断")
    
    print("\n当前工作目录:", os.getcwd())
    
    # 检查各项配置
    check_python()
    venv_ok = check_venv()
    deps_ok = check_dependencies()
    tools_ok = check_tools()
    
    # 总结
    print_header("诊断总结")
    
    if venv_ok and deps_ok and tools_ok:
        print("\n✅ 所有检查通过！环境配置正常。")
        print("\n可以正常使用以下方式启动：")
        print("  1. 双击 启动工具.bat")
        print("  2. 运行 python launcher.py")
    else:
        print("\n❌ 发现问题，请按以下步骤修复：")
        
        if not venv_ok:
            print("\n虚拟环境问题：")
            print("  python -m venv .venv")
            print("  .venv\\Scripts\\activate")
        
        if not deps_ok:
            print("\n依赖模块问题：")
            print("  pip install -r requirements.txt")
        
        if not tools_ok:
            print("\n工具文件缺失，请检查项目完整性")
    
    print("\n" + "=" * 50)
    input("\n按回车键退出...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 诊断过程中出错: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
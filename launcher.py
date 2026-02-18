# -*- coding: utf-8 -*-
import sys
import os
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 设置无缓冲输出
sys.stdout.reconfigure(line_buffering=True)

def test_imports():
    """测试所有必需的模块是否都能正常导入"""
    print("正在检查依赖模块...")
    
    modules = [
        ("pandas", "数据处理"),
        ("openpyxl", "Excel文件处理"),
        ("fuzzywuzzy", "模糊匹配"),
        ("numpy", "数值计算"),
        ("tkinter", "图形界面")
    ]
    
    all_ok = True
    for module, desc in modules:
        try:
            __import__(module)
            print(f"✅ {module} ({desc}) - 正常")
        except ImportError as e:
            print(f"❌ {module} ({desc}) - 缺失: {e}")
            all_ok = False
    
    return all_ok

def show_menu():
    """显示主菜单"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("========================================", flush=True)
    print("  早发冠心病数据处理工具集", flush=True)
    print("========================================", flush=True)
    print(flush=True)
    print("请选择要使用的工具：", flush=True)
    print(flush=True)
    print("  1. 单文件多Sheet合并工具", flush=True)
    print("  2. 跨文件合并工具", flush=True)
    print("  3. 重复记录去重工具", flush=True) 
    print("  4. 字段唯一性检查工具", flush=True)
    print("  5. 检查依赖模块", flush=True)
    print("  6. 退出", flush=True)
    print(flush=True)

def run_tool(tool_bat, tool_name):
    """运行指定的工具"""
    print(f"\n{'=' * 50}", flush=True)
    print(f"正在启动: {tool_name}", flush=True)
    print(f"{'=' * 50}", flush=True)
    print(f"\n⚠️  重要提示：", flush=True)
    print(f"   • 工具将在新窗口中打开", flush=True)
    print(f"   • 请在弹出的窗口中进行操作", flush=True)
    print(f"   • 如果看不到窗口，请检查任务栏！", flush=True)
    print(f"\n启动中...\n", flush=True)
    
    # 调用包装批处理文件，它会设置好编码
    cmd = f'start "" {tool_bat}'
    result = os.system(cmd)
    
    if result != 0:
        print(f"⚠️ 启动时遇到问题 (错误代码: {result})", flush=True)
    else:
        print(f"✅ 工具已在新窗口中启动", flush=True)
        print(f"   请切换到新打开的命令提示符窗口", flush=True)

def main():
    # 立即显示启动信息
    print("初始化中...", flush=True)
    
    while True:
        show_menu()
        print("请输入选项 (1-6): ", end='', flush=True)
        choice = input().strip()
        
        if choice == "1":
            run_tool("run_tool1.bat", "单文件多Sheet合并工具")
            print("\n按回车键返回主菜单...", end='', flush=True)
            input()
            
        elif choice == "2":
            run_tool("run_tool2.bat", "跨文件合并工具")
            print("\n按回车键返回主菜单...", end='', flush=True)
            input()
            
        elif choice == "3":
            run_tool("run_tool3.bat", "重复记录去重工具")
            print("\n按回车键返回主菜单...", end='', flush=True)
            input()
            
        elif choice == "4":
            run_tool("run_tool4.bat", "字段唯一性检查工具")
            print("\n按回车键返回主菜单...", end='', flush=True)
            input()
            
        elif choice == "5":
            print(flush=True)
            if test_imports():
                print("\n✅ 所有依赖模块检查通过!", flush=True)
            else:
                print("\n❌ 存在缺失的依赖模块，请运行以下命令安装：", flush=True)
                print("pip install -r requirements.txt", flush=True)
            print("\n按回车键返回主菜单...", end='', flush=True)
            input()
            
        elif choice == "6":
            print("\n再见！", flush=True)
            break
            
        else:
            print("\n无效选项，请重新选择。", flush=True)
            print("按回车键继续...", end='', flush=True)
            input()

if __name__ == "__main__":
    main()
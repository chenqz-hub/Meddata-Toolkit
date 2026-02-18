"""
早发冠心病数据处理工具集 - 主启动器
直接在VSCode中运行，无需bat脚本
"""

import os
import sys
from pathlib import Path


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_menu():
    """显示菜单"""
    clear_screen()
    print("=" * 50)
    print("   早发冠心病数据处理工具集")
    print("=" * 50)
    print()
    print("请选择要使用的工具：")
    print()
    print("  1. 单文件多Sheet合并工具")
    print("  2. 跨文件合并工具 (经典版)")
    print("  3. 跨文件合并工具 (增强版)")
    print("  4. 跨文件合并工具 (专业版) 🌟 全功能")
    print("  5. 重复记录去重工具")
    print("  6. 字段唯一性检查工具")
    print("  7. 填充 Case 数据工具")
    print("  8. 快速清理项目")
    print("  9. 退出")
    print()


def run_tool(tool_name):
    """运行指定的工具"""
    tool_path = Path(__file__).parent / "tools" / tool_name

    if not tool_path.exists():
        print(f"\n✗ 工具文件不存在: {tool_path}")
        input("\n按回车键返回...")
        return

    print(f"\n正在启动 {tool_name}...")
    print(f"Python解释器: {sys.executable}")
    print("-" * 50)

    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, str(tool_path)],
            cwd=str(Path(__file__).parent)
        )

        if result.returncode != 0:
            print(f"\n✗ 工具退出码: {result.returncode}")
    except Exception as e:
        print(f"\n✗ 运行工具时出错: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "-" * 50)
    input("\n按回车键返回主菜单...")


def run_cleanup():
    """运行清理工具"""
    cleanup_path = Path(__file__).parent / "快速清理.py"

    if not cleanup_path.exists():
        print(f"\n✗ 清理工具不存在: {cleanup_path}")
        input("\n按回车键返回...")
        return

    print(f"\n正在启动清理工具...")
    print("-" * 50)

    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, str(cleanup_path)],
            cwd=str(Path(__file__).parent)
        )

        if result.returncode != 0:
            print(f"\n✗ 清理工具退出码: {result.returncode}")
    except Exception as e:
        print(f"\n✗ 运行清理工具时出错: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "-" * 50)
    input("\n按回车键返回主菜单...")


def main():
    """主函数"""
    while True:
        show_menu()

        try:
            choice = input("请输入选项 (1-9): ").strip()

            if choice == "1":
                run_tool("merge_tool_gui.py")
            elif choice == "2":
                run_tool("cross_merge_gui.py")
            elif choice == "3":
                run_tool("advanced_merge_gui.py")
            elif choice == "4":
                run_tool("professional_merge_gui.py")
            elif choice == "5":
                run_tool("deduplicate_tool.py")
            elif choice == "6":
                run_tool("check_join_fields.py")
            elif choice == "7":
                run_tool("fill_case_data.py")
            elif choice == "8":
                run_cleanup()
            elif choice == "9":
                print("\n再见！")
                break
            else:
                print("\n✗ 无效选项，请输入 1-9")
                input("\n按回车键继续...")

        except KeyboardInterrupt:
            print("\n\n已取消操作")
            break
        except Exception as e:
            print(f"\n✗ 发生错误: {e}")
            input("\n按回车键继续...")


if __name__ == "__main__":
    main()

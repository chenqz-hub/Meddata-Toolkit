"""
快速清理 - 自动清理不需要的文件
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def main():
    root = Path(__file__).parent
    
    print("="*70)
    print("   快速清理工具")
    print("="*70)
    
    deleted = []
    
    # 1. 删除旧bat脚本
    print("\n清理旧bat脚本...")
    for bat in ['启动工具.bat', '清理项目.bat']:
        bat_path = root / bat
        if bat_path.exists():
            try:
                bat_path.unlink()
                print(f"  ✓ 已删除: {bat}")
                deleted.append(bat)
            except Exception as e:
                print(f"  ✗ 失败: {bat} - {e}")
    
    # 2. 删除根目录临时Excel
    print("\n清理临时Excel文件...")
    for excel in root.glob('*.xlsx'):
        if 'merged' in excel.name.lower() or 'psm' in excel.name.lower():
            try:
                excel.unlink()
                print(f"  ✓ 已删除: {excel.name}")
                deleted.append(excel.name)
            except Exception as e:
                print(f"  ✗ 失败: {excel.name} - {e}")
    
    # 3. 清理docs下的临时合并文件
    docs_dir = root / 'docs'
    if docs_dir.exists():
        for excel in docs_dir.glob('*.xlsx'):
            if any(kw in excel.name.lower() for kw in ['merged', 'cross_merge', '合并结果']):
                try:
                    excel.unlink()
                    print(f"  ✓ 已删除: docs/{excel.name}")
                    deleted.append(f"docs/{excel.name}")
                except Exception as e:
                    print(f"  ✗ 失败: {excel.name} - {e}")
    
    # 4. 清理docs/新建文件夹
    temp_folder = docs_dir / '新建文件夹'
    if temp_folder.exists():
        print("\n清理 docs/新建文件夹...")
        
        # 备份诊断报告
        report = temp_folder / '合并问题诊断报告.md'
        if report.exists():
            archive_dir = root / 'archive'
            archive_dir.mkdir(exist_ok=True)
            backup = archive_dir / f'合并问题诊断报告_{datetime.now().strftime("%Y%m%d")}.md'
            if not backup.exists():
                shutil.copy2(report, backup)
                print(f"  ✓ 已备份: 合并问题诊断报告.md")
        
        # 删除整个目录
        try:
            shutil.rmtree(temp_folder)
            print(f"  ✓ 已删除目录: docs/新建文件夹/")
            deleted.append("docs/新建文件夹/")
        except Exception as e:
            print(f"  ✗ 失败: {e}")
    
    # 5. 清理Python缓存
    print("\n清理Python缓存...")
    cache_count = 0
    for pycache in root.rglob('__pycache__'):
        try:
            shutil.rmtree(pycache)
            cache_count += 1
        except:
            pass
    
    for pyc in root.rglob('*.pyc'):
        try:
            pyc.unlink()
            cache_count += 1
        except:
            pass
    
    if cache_count > 0:
        print(f"  ✓ 已删除 {cache_count} 个缓存文件/目录")
        deleted.append(f"{cache_count} 个Python缓存")
    
    # 总结
    print("\n" + "="*70)
    print(f"清理完成! 共删除 {len(deleted)} 项")
    print("="*70)
    
    if deleted:
        print("\n已删除的文件:")
        for item in deleted[:10]:  # 最多显示10项
            print(f"  - {item}")
        if len(deleted) > 10:
            print(f"  ... 还有 {len(deleted)-10} 项")
    
    # 记录到日志
    log_file = root / '清理记录.md'
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n## 快速清理 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"删除项目: {len(deleted)}\n\n")
        for item in deleted:
            f.write(f"- {item}\n")
        f.write("\n")
    
    print(f"\n清理记录已保存到: 清理记录.md")
    print("\n✨ 项目已清理完毕！")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按回车键退出...")

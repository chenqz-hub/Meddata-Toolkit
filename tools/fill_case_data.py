"""
填充 Case 数据工具

功能：
从原始表格中查找匹配的 case，将原始表格中的数据填充到合并表中对应 case 的缺失字段。

使用场景：
合并表中有部分 case 的某些字段是空值，但这些字段的数据在原始表中存在。
通过匹配键字段（如 patient_id），将原始表中的数据填充到合并表的空白处。

示例：
    合并表：
    patient_id | name | age | diagnosis | blood_pressure
    P001       | 张三  | 45  | 冠心病     | (空)
    
    原始表：
    patient_id | name | age | diagnosis | blood_pressure
    P001       | 张三  | 45  | 冠心病     | 130/85
    
    填充后：
    patient_id | name | age | diagnosis | blood_pressure
    P001       | 张三  | 45  | 冠心病     | 130/85
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import sys

try:
    import tkinter as tk
    from tkinter import filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


def choose_file_via_dialog(title='选择文件'):
    """使用文件对话框选择文件"""
    if not TKINTER_AVAILABLE:
        return None
    
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    p = filedialog.askopenfilename(
        title=title,
        filetypes=[('Excel files', '*.xlsx *.xls'), ('CSV files', '*.csv'), ('All files', '*.*')]
    )
    
    root.destroy()
    return p if p else None


def load_table(file_path: Path):
    """加载表格文件"""
    ext = file_path.suffix.lower()
    if ext in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    elif ext == '.csv':
        return pd.read_csv(file_path)
    else:
        raise ValueError(f'不支持的文件格式: {ext}')


def save_table(df: pd.DataFrame, out_path: Path):
    """保存表格文件"""
    ext = out_path.suffix.lower()
    if ext in ['.xlsx', '.xls']:
        df.to_excel(out_path, index=False)
    elif ext == '.csv':
        df.to_csv(out_path, index=False, encoding='utf-8-sig')
    else:
        raise ValueError(f'不支持的输出格式: {ext}')


def is_empty(value):
    """判断值是否为空"""
    if pd.isna(value):
        return True
    if isinstance(value, str) and value.strip() == '':
        return True
    return False


def fill_case_data(merged_df: pd.DataFrame, source_df: pd.DataFrame, merged_key_col: str, source_key_col: str = None):
    """
    从原始表填充合并表中的缺失数据
    
    参数:
        merged_df: 合并表（需要填充的表）
        source_df: 原始表（数据来源）
        merged_key_col: 合并表中用于匹配的键字段
        source_key_col: 原始表中用于匹配的键字段（如果为None，则使用merged_key_col）
    
    返回:
        filled_df: 填充后的数据框
        stats: 填充统计信息
    """
    if source_key_col is None:
        source_key_col = merged_key_col
    
    # 复制数据框，避免修改原始数据
    filled_df = merged_df.copy()
    
    # 统计信息
    stats = {
        'total_cases': len(filled_df),
        'matched_cases': 0,
        'fields_filled': {},  # 每个字段的填充次数
        'total_cells_filled': 0
    }
    
    # 创建字段映射（标准化后的字段名 -> 实际字段名）
    def normalize_col_name(name):
        """标准化字段名：去空格、去下划线、转小写"""
        return name.strip().replace(' ', '').replace('_', '').lower()
    
    # 建立合并表和原始表的字段映射
    merged_norm_map = {normalize_col_name(col): col for col in merged_df.columns}
    source_norm_map = {normalize_col_name(col): col for col in source_df.columns}
    
    # 找出共同字段（基于标准化后的名称）
    common_norm_cols = set(merged_norm_map.keys()) & set(source_norm_map.keys())
    # 移除键字段
    common_norm_cols.discard(normalize_col_name(merged_key_col))
    common_norm_cols.discard(normalize_col_name(source_key_col))
    
    if not common_norm_cols:
        return filled_df, stats
    
    # 为原始表创建索引，方便快速查找
    source_indexed = source_df.set_index(source_key_col)
    
    # 遍历合并表的每一行
    for idx, row in filled_df.iterrows():
        key_value = row[merged_key_col]
        
        # 跳过键值为空的行
        if is_empty(key_value):
            continue
        
        # 在原始表中查找匹配的 case
        if key_value not in source_indexed.index:
            continue
        
        stats['matched_cases'] += 1
        source_row = source_indexed.loc[key_value]
        
        # 如果原始表中有多行匹配，取第一行
        if isinstance(source_row, pd.DataFrame):
            source_row = source_row.iloc[0]
        
        # 遍历共同字段（使用标准化名称），填充空值
        for norm_col in common_norm_cols:
            merged_col = merged_norm_map[norm_col]
            source_col = source_norm_map[norm_col]
            
            # 如果合并表中该字段为空，且原始表中有值
            if is_empty(filled_df.at[idx, merged_col]) and not is_empty(source_row[source_col]):
                filled_df.at[idx, merged_col] = source_row[source_col]
                
                # 更新统计
                if merged_col not in stats['fields_filled']:
                    stats['fields_filled'][merged_col] = 0
                stats['fields_filled'][merged_col] += 1
                stats['total_cells_filled'] += 1
    
    return filled_df, stats


def print_stats(stats):
    """打印填充统计信息"""
    print("\n" + "=" * 60)
    print("✓ 填充完成！")
    print("=" * 60)
    print(f"\n总 case 数: {stats['total_cases']}")
    print(f"匹配到的 case 数: {stats['matched_cases']}")
    print(f"总共填充单元格数: {stats['total_cells_filled']}")
    
    if stats['fields_filled']:
        print("\n各字段填充情况:")
        for col, count in sorted(stats['fields_filled'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {col}: {count} 个值")
    else:
        print("\n未填充任何数据（可能所有字段都已有值）")


def main(argv=None):
    # 确保输出使用UTF-8编码
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    parser = argparse.ArgumentParser(
        description='从原始表格填充合并表中缺失的字段数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 交互式选择文件
    python fill_case_data.py
    
    # 命令行指定文件
    python fill_case_data.py --merged merged.xlsx --source original.xlsx --key patient_id
        """
    )
    parser.add_argument('--merged', '-m', help='合并后的表格文件（需要填充的表）')
    parser.add_argument('--source', '-s', help='原始表格文件（数据来源）')
    parser.add_argument('--key', '-k', help='用于匹配 case 的键字段名（如 patient_id）')
    parser.add_argument('--output', '-o', help='输出文件路径（可选）')
    args = parser.parse_args(argv)
    
    print("=" * 60)
    print("  填充 Case 数据工具")
    print("=" * 60)
    print()
    
    # 1. 获取合并表文件
    merged_path = args.merged
    if not merged_path:
        print("请选择【合并表】（需要填充数据的表）...")
        merged_path = choose_file_via_dialog('选择合并表')
        if not merged_path:
            print('\n✗ 未选择合并表文件，退出。')
            return 1
    
    merged_path = Path(merged_path)
    if not merged_path.exists():
        print(f'\n✗ 合并表文件不存在: {merged_path}')
        return 2
    
    # 2. 获取原始表文件
    source_path = args.source
    if not source_path:
        print("\n请选择【原始表】（数据来源表）...")
        source_path = choose_file_via_dialog('选择原始表')
        if not source_path:
            print('\n✗ 未选择原始表文件，退出。')
            return 1
    
    source_path = Path(source_path)
    if not source_path.exists():
        print(f'\n✗ 原始表文件不存在: {source_path}')
        return 2
    
    # 3. 加载表格
    print(f'\n加载合并表: {merged_path.name}')
    try:
        merged_df = load_table(merged_path)
        print(f'  ✓ 共 {len(merged_df)} 行，{len(merged_df.columns)} 列')
        print(f'    字段: {", ".join(merged_df.columns[:5])}{"..." if len(merged_df.columns) > 5 else ""}')
    except Exception as e:
        print(f'✗ 加载合并表失败: {e}')
        return 3
    
    print(f'\n加载原始表: {source_path.name}')
    try:
        source_df = load_table(source_path)
        print(f'  ✓ 共 {len(source_df)} 行，{len(source_df.columns)} 列')
        print(f'    字段: {", ".join(source_df.columns[:5])}{"..." if len(source_df.columns) > 5 else ""}')
    except Exception as e:
        print(f'✗ 加载原始表失败: {e}')
        return 3
    
    # 4. 获取键字段
    key_col = args.key
    if not key_col:
        print('\n合并表的字段:')
        for i, col in enumerate(merged_df.columns, 1):
            print(f'  {i}. [{col}]')  # 用方括号显示，便于看清空格
        
        print('\n原始表的字段:')
        for i, col in enumerate(source_df.columns, 1):
            print(f'  {i}. [{col}]')  # 用方括号显示，便于看清空格
        
        key_col = input('\n请输入用于匹配 case 的键字段名（如 patient_id 或 Patient ID）: ').strip()
        if not key_col:
            print('\n✗ 必须指定键字段名')
            return 4
    
    # 去除可能的前后空格
    key_col = key_col.strip()
    
    # 创建字段名映射（处理大小写、空格、下划线的差异）
    def normalize_col_name(name):
        """标准化字段名：去空格、去下划线、转小写"""
        return name.strip().replace(' ', '').replace('_', '').lower()
    
    # 验证键字段 - 先尝试精确匹配
    merged_key_col = None
    source_key_col = None
    
    if key_col in merged_df.columns:
        merged_key_col = key_col
    else:
        # 尝试模糊匹配
        normalized_input = normalize_col_name(key_col)
        for col in merged_df.columns:
            if normalize_col_name(col) == normalized_input:
                merged_key_col = col
                print(f'\n提示: 合并表中匹配到字段 "{col}" (您输入的是 "{key_col}")')
                break
    
    if not merged_key_col:
        print(f'\n✗ 合并表中不存在字段: {key_col}')
        print('可用的字段:', ', '.join([f'[{c}]' for c in merged_df.columns[:10]]))
        return 5
    
    if key_col in source_df.columns:
        source_key_col = key_col
    else:
        # 尝试模糊匹配
        normalized_input = normalize_col_name(key_col)
        for col in source_df.columns:
            if normalize_col_name(col) == normalized_input:
                source_key_col = col
                print(f'\n提示: 原始表中匹配到字段 "{col}" (您输入的是 "{key_col}")')
                break
    
    if not source_key_col:
        print(f'\n✗ 原始表中不存在字段: {key_col}')
        print('可用的字段:', ', '.join([f'[{c}]' for c in source_df.columns[:10]]))
        return 5
    
    # 如果两个表的字段名不完全一致，给出警告
    if merged_key_col != source_key_col:
        print(f'\n⚠️  注意: 两个表中该字段的名称不完全一致:')
        print(f'  合并表: [{merged_key_col}]')
        print(f'  原始表: [{source_key_col}]')
        print(f'  将使用各自表中的字段名进行匹配。')
    
    # 5. 分析共同字段（使用标准化匹配）
    def normalize_col_name(name):
        """标准化字段名：去空格、去下划线、转小写"""
        return name.strip().replace(' ', '').replace('_', '').lower()
    
    merged_norm_map = {normalize_col_name(col): col for col in merged_df.columns}
    source_norm_map = {normalize_col_name(col): col for col in source_df.columns}
    
    common_norm_cols = set(merged_norm_map.keys()) & set(source_norm_map.keys())
    # 移除键字段
    common_norm_cols.discard(normalize_col_name(merged_key_col))
    common_norm_cols.discard(normalize_col_name(source_key_col))
    
    print(f'\n找到 {len(common_norm_cols)} 个共同字段（可用于填充）:')
    count = 0
    for norm_col in sorted(common_norm_cols):
        if count >= 10:
            break
        merged_col = merged_norm_map[norm_col]
        source_col = source_norm_map[norm_col]
        # 统计该字段在合并表中的空值数量
        empty_count = merged_df[merged_col].isna().sum() + (merged_df[merged_col] == '').sum()
        if merged_col == source_col:
            print(f'  {count+1}. [{merged_col}] (合并表中有 {empty_count} 个空值)')
        else:
            print(f'  {count+1}. [{merged_col}] ←→ [{source_col}] (合并表中有 {empty_count} 个空值)')
        count += 1
    if len(common_norm_cols) > 10:
        print(f'  ... 还有 {len(common_norm_cols) - 10} 个字段')
    
    if not common_norm_cols:
        print('\n✗ 没有共同字段可以填充！')
        return 6
    
    # 6. 确认是否继续
    confirm = input(f'\n是否使用 [{merged_key_col}] ←→ [{source_key_col}] 匹配并填充数据？(y/n): ').strip().lower()
    if confirm != 'y':
        print('\n已取消操作')
        return 0
    
    # 7. 填充数据
    print('\n正在填充数据...')
    filled_df, stats = fill_case_data(merged_df, source_df, merged_key_col, source_key_col)
    
    # 8. 保存结果
    output_path = args.output
    if not output_path:
        output_path = merged_path.parent / f"{merged_path.stem}_已填充{merged_path.suffix}"
    else:
        output_path = Path(output_path)
    
    try:
        save_table(filled_df, output_path)
        print(f'\n✓ 已保存到: {output_path}')
    except Exception as e:
        print(f'\n✗ 保存失败: {e}')
        return 7
    
    # 9. 显示统计信息
    print_stats(stats)
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\n\n已取消操作')
        sys.exit(1)
    except Exception as e:
        print(f'\n✗ 发生错误: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

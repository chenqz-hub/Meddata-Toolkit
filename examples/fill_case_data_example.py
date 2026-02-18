"""
填充 Case 数据工具 - 测试示例

演示如何使用 fill_case_data.py 从原始表填充合并表中的缺失数据
"""

import pandas as pd
from pathlib import Path
import subprocess
import sys

print("=" * 60)
print("  填充 Case 数据工具 - 测试示例")
print("=" * 60)
print()

# 1. 创建合并表（有些字段是空的）
print("1. 创建合并表（模拟部分字段缺失的情况）...")
merged_data = {
    'patient_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
    'name': ['张三', '李四', '王五', '赵六', '陈七'],
    'age': [45, 52, None, 55, 50],  # P003的年龄缺失
    'diagnosis': ['冠心病', '心肌梗死', '心绞痛', '冠心病', None],  # P005的诊断缺失
    'blood_pressure': [None, None, '125/80', None, '120/75'],  # 多个血压缺失
    'cholesterol': [220, None, 210, None, 230]  # 多个胆固醇缺失
}
merged_df = pd.DataFrame(merged_data)
merged_file = Path('examples/test_merged.xlsx')
merged_df.to_excel(merged_file, index=False)
print(f"   ✓ 创建合并表: {merged_file}")
print(f"     包含 {len(merged_df)} 个 case")
print("\n   合并表数据预览（缺失字段用 NaN 表示）:")
print(merged_df.to_string(index=False))
print()

# 2. 创建原始表（包含完整数据）
print("2. 创建原始表（包含完整数据）...")
original_data = {
    'patient_id': ['P001', 'P002', 'P003', 'P004', 'P005', 'P006'],
    'name': ['张三', '李四', '王五', '赵六', '陈七', '孙八'],
    'age': [45, 52, 48, 55, 50, 58],
    'diagnosis': ['冠心病', '心肌梗死', '心绞痛', '冠心病', '冠心病', '心肌梗死'],
    'blood_pressure': ['130/85', '140/90', '125/80', '135/88', '120/75', '145/95'],
    'cholesterol': [220, 245, 210, 240, 230, 260],
    'extra_field': ['A', 'B', 'C', 'D', 'E', 'F']  # 原始表独有的字段
}
original_df = pd.DataFrame(original_data)
original_file = Path('examples/test_original.xlsx')
original_df.to_excel(original_file, index=False)
print(f"   ✓ 创建原始表: {original_file}")
print(f"     包含 {len(original_df)} 个 case")
print("\n   原始表数据预览:")
print(original_df.to_string(index=False))
print()

# 3. 分析缺失情况
print("3. 分析合并表中的缺失数据...")
for col in merged_df.columns:
    if col == 'patient_id':
        continue
    missing_count = merged_df[col].isna().sum()
    if missing_count > 0:
        missing_cases = merged_df[merged_df[col].isna()]['patient_id'].tolist()
        print(f"   {col}: {missing_count} 个缺失 (case: {', '.join(missing_cases)})")
print()

# 4. 运行填充工具
print("4. 使用 fill_case_data.py 工具填充...")
print("   执行命令:")
print(f"   python tools/fill_case_data.py \\")
print(f"       --merged {merged_file} \\")
print(f"       --source {original_file} \\")
print(f"       --key patient_id")
print()

result = subprocess.run(
    [
        sys.executable,
        'tools/fill_case_data.py',
        '--merged', str(merged_file),
        '--source', str(original_file),
        '--key', 'patient_id',
        '--output', 'examples/test_merged_已填充.xlsx'
    ],
    input='y\n',  # 自动确认
    text=True,
    capture_output=True,
    encoding='utf-8',
    errors='replace'
)

print(result.stdout)
if result.returncode != 0:
    print("错误输出:")
    print(result.stderr)
else:
    # 5. 验证结果
    print()
    print("5. 验证填充结果...")
    result_file = Path('examples/test_merged_已填充.xlsx')
    if result_file.exists():
        result_df = pd.read_excel(result_file)
        print(f"   ✓ 填充后的文件: {result_file}")
        print()
        print("   填充后的数据:")
        print(result_df.to_string(index=False))
        print()
        
        # 比较填充前后
        print("   对比分析:")
        for col in ['age', 'diagnosis', 'blood_pressure', 'cholesterol']:
            before_missing = merged_df[col].isna().sum()
            after_missing = result_df[col].isna().sum()
            filled = before_missing - after_missing
            print(f"   {col}: 填充前 {before_missing} 个空值 → 填充后 {after_missing} 个空值 (填充了 {filled} 个)")
        
        print()
        print("   ✓ 填充成功！所有能匹配到的缺失数据已从原始表填充。")
    else:
        print(f"   ✗ 未找到输出文件: {result_file}")

print()
print("=" * 60)
print("  示例完成")
print("=" * 60)
print()
print("提示:")
print("  - 使用 GUI 模式: python tools/fill_case_data.py")
print("  - 从主菜单启动: python 启动工具.py -> 选项 7")
print("  - 快速启动: run_fill_data.bat")

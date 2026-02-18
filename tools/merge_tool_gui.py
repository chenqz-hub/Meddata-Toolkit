import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("单文件多Sheet合并工具", flush=True)
print("=" * 50, flush=True)

# Create main tkinter window
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)  # 确保对话框在最前面
root.update()

# Select Excel file
print("\n⚠️  请注意：文件选择对话框已打开！", flush=True)
print("如果看不到对话框，请检查任务栏或最小化的窗口。", flush=True)
print("\n等待选择文件...", flush=True)

file_path = filedialog.askopenfilename(
    title="选择Excel文件进行Sheet合并",
    filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
    initialdir=".",
    parent=root
)

if not file_path:
    print("未选择文件，退出程序。")
    root.destroy()
    exit()

selected_file = Path(file_path)
print(f"已选择: {selected_file.name}")

try:
    print(f"\n正在处理: {selected_file.name}")
    
    # Load all sheets and analyze fields
    excel_file = pd.ExcelFile(selected_file)
    all_field_counts = {}
    sheet_data = {}
    
    print("\n分析工作表...", flush=True)
    for sheet_name in excel_file.sheet_names:
        try:
            df = pd.read_excel(selected_file, sheet_name=sheet_name)
            headers = [col for col in df.columns if not (
                str(col).startswith('Unnamed') or str(col).strip() == '' or pd.isna(col)
            )]
            
            if headers:
                sheet_data[sheet_name] = {'df': df, 'fields': headers}
                for field in headers:
                    all_field_counts[field] = all_field_counts.get(field, 0) + 1
                print(f"  {sheet_name}: {len(df)} 行 x {len(headers)} 列", flush=True)
        except:
            continue
    
    # Identify common and unique fields
    common_fields = {field for field, count in all_field_counts.items() if count > 1}
    print(f"\n检测到公共字段: {len(common_fields)}", flush=True)
    
    # Select master sheet (largest with most common fields)
    master_sheet = max(sheet_data.keys(), 
                      key=lambda s: len(sheet_data[s]['fields']) + 
                                  len([f for f in sheet_data[s]['fields'] if f in common_fields]))
    
    print(f"主工作表: {master_sheet}", flush=True)
    
    # Start with master sheet
    merged_df = sheet_data[master_sheet]['df']
    
    # Find join field
    master_common = [f for f in sheet_data[master_sheet]['fields'] if f in common_fields]
    join_field = None
    for field in master_common:
        if any(kw in field.lower() for kw in ['id', 'subjid']):
            join_field = field
            break
    if not join_field and master_common:
        join_field = master_common[0]
    
    print(f"连接字段: {join_field}", flush=True)
    
    # Merge other sheets
    print("\n合并工作表...", flush=True)
    added_fields = 0
    for sheet_name, info in sheet_data.items():
        if sheet_name == master_sheet or join_field not in info['fields']:
            continue
            
        # Only merge unique fields
        unique_fields = [f for f in info['fields'] if f not in common_fields]
        if not unique_fields:
            continue
            
        merge_fields = [join_field] + unique_fields
        detail_df = info['df'][merge_fields]
        
        before_cols = merged_df.shape[1]
        merged_df = pd.merge(merged_df, detail_df, on=join_field, how='left')
        added_fields += merged_df.shape[1] - before_cols
        
        print(f"  已合并 {sheet_name}: +{merged_df.shape[1] - before_cols} 个字段", flush=True)
    
    # Select output location
    print("\n" + "=" * 50, flush=True)
    print("请选择保存位置...", flush=True)
    print("⚠️  文件保存对话框已打开！", flush=True)
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    default_name = f"{selected_file.stem}_merged_{timestamp}.xlsx"
    
    output_path = filedialog.asksaveasfilename(
        title="Save Merged File As",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialdir=str(selected_file.parent),
        initialfile=default_name
    )
    
    if not output_path:
        output_path = default_name
        print(f"未选择位置，保存到: {output_path}", flush=True)
    
    # Save result
    print("\n正在保存合并后的文件...", flush=True)
    merged_df.to_excel(output_path, index=False)
    
    print("\n" + "=" * 50, flush=True)
    print("✅ 成功！", flush=True)
    print(f"输出文件: {output_path}", flush=True)
    print(f"最终结果: {merged_df.shape[0]} 行 x {merged_df.shape[1]} 列", flush=True)
    print(f"添加的字段数: {added_fields}", flush=True)
    
    # Check for duplicates
    duplicates = [col for col in merged_df.columns if merged_df.columns.tolist().count(col) > 1]
    print(f"重复字段: {len(duplicates)} (应该为 0)", flush=True)
    
    # Offer to open the file
    print("\n是否立即打开合并后的文件?", flush=True)
    print("请输入 y 或 n，然后按回车: ", end='', flush=True)
    
    try:
        open_choice = input().strip().lower()
        if open_choice == 'y':
            import os
            print("正在打开文件...", flush=True)
            os.startfile(output_path)
        else:
            print("文件已保存，可以稍后打开。", flush=True)
    except Exception as e:
        print(f"输入错误或无法打开文件: {e}", flush=True)
        print("文件已保存，您可以手动打开它。", flush=True)
    
except Exception as e:
    print(f"\n❌ 错误: {e}", flush=True)
    import traceback
    traceback.print_exc()
    print("\n程序遇到错误，请检查上面的错误信息。", flush=True)
finally:
    root.destroy()
    print("\n工具已结束运行。", flush=True)

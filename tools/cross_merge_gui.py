import pandas as pd
from pathlib import Path
from fuzzywuzzy import fuzz
import tkinter as tk
from tkinter import filedialog
import sys
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("跨文件合并工具", flush=True)
print("=" * 50, flush=True)

# Create main tkinter window
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)  # 确保对话框在最前面
root.update()

# Select first file
print("\n⚠️  请注意：文件选择对话框已打开！", flush=True)
print("第一步：请选择第一个Excel文件...", flush=True)
print("如果看不到对话框，请检查任务栏。\n", flush=True)

file1_path = filedialog.askopenfilename(
    title="选择第一个Excel文件",
    filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
    initialdir=".",
    parent=root
)

if not file1_path:
    print("未选择文件，退出程序。", flush=True)
    exit()

file1 = Path(file1_path)
print(f"已选择第一个文件: {file1.name}", flush=True)

# Select second file
print("\n第二步：请选择第二个Excel文件...", flush=True)
file2_path = filedialog.askopenfilename(
    title="Select Second Excel File",
    filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
    initialdir=str(file1.parent)
)

if not file2_path:
    print("No file selected. Exiting.")
    exit()

file2 = Path(file2_path)
print(f"Selected: {file2.name}")

if file1 == file2:
    print("Cannot merge a file with itself!")
    exit()

try:
    # Analyze both files
    print("\n" + "=" * 50)
    print("Analyzing File 1...")
    excel1 = pd.ExcelFile(file1)
    print(f"  File: {file1.name}")
    print(f"  Sheets ({len(excel1.sheet_names)}): {', '.join(excel1.sheet_names)}")
    
    print("\nAnalyzing File 2...")
    excel2 = pd.ExcelFile(file2)
    print(f"  File: {file2.name}")
    print(f"  工作表 ({len(excel2.sheet_names)}): {', '.join(excel2.sheet_names)}", flush=True)
    
    # Select sheet from file 1
    print("\n" + "=" * 50, flush=True)
    print(f"从文件1选择工作表 (1-{len(excel1.sheet_names)}):", flush=True)
    for i, sheet in enumerate(excel1.sheet_names, 1):
        print(f"   {i}. {sheet}", flush=True)
    print(f"\n请输入工作表编号 (1-{len(excel1.sheet_names)}): ", end='', flush=True)
    sheet1_idx = int(input()) - 1
    if not (0 <= sheet1_idx < len(excel1.sheet_names)):
        print("❌ 无效选择", flush=True)
        exit()
    sheet1_name = excel1.sheet_names[sheet1_idx]
    print(f"✅ 已选择: {sheet1_name}", flush=True)
    
    # Select sheet from file 2
    print(f"\n从文件2选择工作表 (1-{len(excel2.sheet_names)}):", flush=True)
    for i, sheet in enumerate(excel2.sheet_names, 1):
        print(f"   {i}. {sheet}", flush=True)
    print(f"\n请输入工作表编号 (1-{len(excel2.sheet_names)}): ", end='', flush=True)
    sheet2_idx = int(input()) - 1
    if not (0 <= sheet2_idx < len(excel2.sheet_names)):
        print("❌ 无效选择", flush=True)
        exit()
    sheet2_name = excel2.sheet_names[sheet2_idx]
    print(f"✅ 已选择: {sheet2_name}", flush=True)
    
    # Load data
    print("\n" + "=" * 50, flush=True)
    print("正在加载数据...", flush=True)
    df1 = pd.read_excel(file1, sheet_name=sheet1_name)
    df2 = pd.read_excel(file2, sheet_name=sheet2_name)
    
    print(f"\n文件1 [{sheet1_name}]: {df1.shape[0]} 行 x {df1.shape[1]} 列", flush=True)
    print(f"文件2 [{sheet2_name}]: {df2.shape[0]} 行 x {df2.shape[1]} 列", flush=True)
    
    # Analyze fields
    print("\n" + "=" * 50)
    print("Analyzing matching fields...")
    fields1 = [col for col in df1.columns if not str(col).startswith('Unnamed')]
    fields2 = [col for col in df2.columns if not str(col).startswith('Unnamed')]
    
    print(f"File 1 has {len(fields1)} fields")
    print(f"File 2 has {len(fields2)} fields")
    
    # Find exact matches
    exact_matches = sorted(list(set(fields1) & set(fields2)))
    print(f"\nExact field matches: {len(exact_matches)}")
    if exact_matches:
        print("Common fields:")
        for i, field in enumerate(exact_matches, 1):
            if i <= 10:
                print(f"   {field}")
            elif i == 11:
                print(f"   ... and {len(exact_matches) - 10} more")
                break
    
    # Find fuzzy matches
    if len(exact_matches) < 5:
        print("\nSearching for similar field names (fuzzy matching)...")
        fuzzy_matches = []
        for f1 in fields1:
            if f1 in exact_matches:
                continue
            for f2 in fields2:
                if f2 in exact_matches:
                    continue
                similarity = fuzz.ratio(f1.lower(), f2.lower())
                if similarity > 75:
                    fuzzy_matches.append((f1, f2, similarity))
        
        fuzzy_matches.sort(key=lambda x: x[2], reverse=True)
        if fuzzy_matches:
            print(f"Potential matches (>75% similar):")
            for f1, f2, sim in fuzzy_matches[:8]:
                print(f"   {f1} <-> {f2} ({sim}%)")
    
    # Select join field
    print("\n" + "=" * 50)
    if exact_matches:
        # Prioritize ID-like fields
        id_fields = [f for f in exact_matches if any(kw in f.lower() for kw in ['id', 'subjid', 'patient', '编号'])]
        other_fields = [f for f in exact_matches if f not in id_fields]
        
        # Create numbered list for selection
        field_options = []
        
        if id_fields:
            print("Recommended join fields (ID-like):")
            for field in id_fields:
                field_options.append(field)
                print(f"   {len(field_options)}. {field}")
            
            if other_fields:
                print(f"\nOther exact matches ({len(other_fields)}):")
                for field in other_fields:
                    field_options.append(field)
                    print(f"   {len(field_options)}. {field}")
        else:
            print("Select join field from exact matches:")
            for field in exact_matches:
                field_options.append(field)
                print(f"   {len(field_options)}. {field}")
        
        print(f"\n   0. Use DIFFERENT field names (manual entry)")
        
        join_idx = int(input(f"\nJoin field number (0-{len(field_options)}): "))
        
        if join_idx == 0:
            # Manual entry for different field names
            print("\nManual field selection:")
            print(f"\nFile 1 fields (first 20): {', '.join(fields1[:20])}")
            join_field1 = input("Enter join field name from File 1: ").strip()
            
            print(f"\nFile 2 fields (first 20): {', '.join(fields2[:20])}")
            join_field2 = input("Enter join field name from File 2: ").strip()
            
            if join_field1 not in fields1:
                print(f"Field '{join_field1}' not found in File 1!")
                exit()
            if join_field2 not in fields2:
                print(f"Field '{join_field2}' not found in File 2!")
                exit()
            
            # Rename for merge
            df2 = df2.rename(columns={join_field2: join_field1})
            join_field = join_field1
            print(f"Will merge on: {join_field1} (File 1) = {join_field2} (File 2)")
        elif 1 <= join_idx <= len(field_options):
            join_field = field_options[join_idx - 1]
            print(f"Using join field: {join_field}")
        else:
            print("Invalid selection")
            exit()
        
    else:
        print("No exact field matches found!")
        print("\nOption 1: Enter field names manually")
        print("Option 2: Exit and check your files")
        choice = input("Continue with manual entry? (y/n): ").lower()
        if choice != 'y':
            exit()
        
        print(f"\nFile 1 fields: {', '.join(fields1[:5])}...")
        join_field1 = input("Enter join field name from File 1: ")
        
        print(f"\nFile 2 fields: {', '.join(fields2[:5])}...")
        join_field2 = input("Enter join field name from File 2: ")
        
        if join_field1 not in fields1:
            print(f"Field '{join_field1}' not found in File 1!")
            exit()
        if join_field2 not in fields2:
            print(f"Field '{join_field2}' not found in File 2!")
            exit()
        
        # Rename for merge
        df2 = df2.rename(columns={join_field2: join_field1})
        join_field = join_field1
        print(f"Will merge on: {join_field1} (File 1) = {join_field2} (File 2)")
    
    # Select merge type
    print("\n" + "=" * 50)
    
    # Check uniqueness of join field before merging
    print("Checking join field uniqueness...")
    total1 = df1[join_field].notna().sum()
    unique1 = df1[join_field].nunique()
    total2 = df2[join_field].notna().sum()
    unique2 = df2[join_field].nunique()
    
    print(f"\nFile 1 '{join_field}':")
    print(f"  Total: {total1}, Unique: {unique1}, Duplicates: {total1 - unique1}")
    print(f"\nFile 2 '{join_field}':")
    print(f"  Total: {total2}, Unique: {unique2}, Duplicates: {total2 - unique2}")
    
    if total1 != unique1 or total2 != unique2:
        print("\n" + "!" * 50)
        print("⚠️  WARNING: Join field has DUPLICATE values!")
        print("!" * 50)
        print("\nThis will cause CARTESIAN PRODUCT (many-to-many join)!")
        print("Example: If File1 has 2 records with ID=001 and")
        print("         File2 has 3 records with ID=001")
        print("         Result will have 2x3=6 records for ID=001")
        print("\nRecommendation: Use a UNIQUE identifier field instead.")
        print("!" * 50)
        
        proceed = input("\nDo you want to proceed anyway? (yes/no): ").lower()
        if proceed not in ['yes', 'y']:
            print("Merge cancelled. Please check your data and try again.")
            exit()
    else:
        print("\n✓ Join field is unique in both files - good!")
    
    print("\n" + "=" * 50)
    print("Select merge type:")
    print("   1. Left join  - Keep all rows from File 1")
    print("   2. Right join - Keep all rows from File 2")
    print("   3. Inner join - Only keep matching rows")
    print("   4. Outer join - Keep all rows from both files")
    merge_choice = input("Choice (1-4, default=1): ").strip() or "1"
    merge_types = {"1": "left", "2": "right", "3": "inner", "4": "outer"}
    merge_type = merge_types.get(merge_choice, "left")
    
    # Perform merge
    print("\n" + "=" * 50)
    print(f"Merging on '{join_field}' using {merge_type.upper()} join...")
    
    merged_df = pd.merge(df1, df2, on=join_field, how=merge_type, suffixes=('_file1', '_file2'))
    
    print(f"\nMerge complete!")
    print(f"  Result: {merged_df.shape[0]} rows x {merged_df.shape[1]} columns")
    
    # Analyze merge results
    overlap_count = len([c for c in merged_df.columns if c.endswith('_file1') or c.endswith('_file2')])
    unique_cols = merged_df.shape[1] - overlap_count
    
    print(f"  Unique columns: {unique_cols}")
    print(f"  Overlapping columns: {overlap_count // 2} (with _file1/_file2 suffixes)")
    
    # Check for null values
    null_counts = merged_df.isnull().sum().sum()
    print(f"  Total null values: {null_counts}")
    
    # Select output location
    print("\n" + "=" * 50)
    print("Select output location...")
    output_path = filedialog.asksaveasfilename(
        title="Save Merged File As",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialdir=".",
        initialfile=f"cross_merge_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )
    
    if not output_path:
        output_path = f"cross_merge_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        print(f"No location selected. Saving to: {output_path}")
    
    # Save result
    print("\nSaving merged file...")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        merged_df.to_excel(writer, sheet_name='Merged Data', index=False)
        
        # Save merge info
        info_df = pd.DataFrame([{
            'Item': 'File 1',
            'Value': file1.name,
            'Sheet': sheet1_name,
            'Size': f'{df1.shape[0]}x{df1.shape[1]}'
        }, {
            'Item': 'File 2',
            'Value': file2.name,
            'Sheet': sheet2_name,
            'Size': f'{df2.shape[0]}x{df2.shape[1]}'
        }, {
            'Item': 'Join Field',
            'Value': join_field,
            'Sheet': merge_type.upper() + ' join',
            'Size': '-'
        }, {
            'Item': 'Result',
            'Value': Path(output_path).name,
            'Sheet': 'Merged Data',
            'Size': f'{merged_df.shape[0]}x{merged_df.shape[1]}'
        }, {
            'Item': 'Null Values',
            'Value': str(null_counts),
            'Sheet': '-',
            'Size': '-'
        }])
        info_df.to_excel(writer, sheet_name='Merge Info', index=False)
    
    print("\n" + "=" * 50)
    print("SUCCESS!")
    print(f"Output file: {output_path}")
    print(f"Final result: {merged_df.shape[0]} rows x {merged_df.shape[1]} columns")
    
    # Offer to open the file
    open_choice = input("\nOpen the merged file now? (y/n): ").lower()
    if open_choice == 'y':
        import os
        os.startfile(output_path)
    
except ValueError as e:
    print(f"\nInput error: {e}")
except Exception as e:
    print(f"\nError occurred: {e}")
    import traceback
    traceback.print_exc()
finally:
    root.destroy()

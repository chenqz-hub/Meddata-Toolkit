import pandas as pd
import tkinter as tk
from tkinter import filedialog

print("Field Uniqueness Checker")
print("=" * 50)

root = tk.Tk()
root.withdraw()

# Select first file
print("\nSelect FIRST file to check...")
file1_path = filedialog.askopenfilename(
    title="Select First File",
    filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
)

if not file1_path:
    print("No file selected")
    exit()

# Select second file
print("Select SECOND file to check...")
file2_path = filedialog.askopenfilename(
    title="Select Second File",
    filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
)

if not file2_path:
    print("No file selected")
    exit()

try:
    # Load files
    print("\n" + "=" * 50)
    print("FILE 1:", file1_path.split('\\')[-1])
    excel1 = pd.ExcelFile(file1_path)
    print(f"Sheets: {excel1.sheet_names}")
    
    sheet1 = excel1.sheet_names[0] if len(excel1.sheet_names) == 1 else input(f"Select sheet (default={excel1.sheet_names[0]}): ") or excel1.sheet_names[0]
    df1 = pd.read_excel(file1_path, sheet_name=sheet1)
    
    print("\n" + "=" * 50)
    print("FILE 2:", file2_path.split('\\')[-1])
    excel2 = pd.ExcelFile(file2_path)
    print(f"Sheets: {excel2.sheet_names}")
    
    sheet2 = excel2.sheet_names[0] if len(excel2.sheet_names) == 1 else input(f"Select sheet (default={excel2.sheet_names[0]}): ") or excel2.sheet_names[0]
    df2 = pd.read_excel(file2_path, sheet_name=sheet2)
    
    print("\n" + "=" * 50)
    print("UNIQUENESS ANALYSIS")
    print("=" * 50)
    
    # Find common fields
    fields1 = set(df1.columns)
    fields2 = set(df2.columns)
    common_fields = sorted(list(fields1 & fields2))
    
    print(f"\nCommon fields: {len(common_fields)}")
    
    # Check uniqueness for each common field
    print("\nField uniqueness check:")
    print(f"{'Field':<40} {'File1 Total':<15} {'File1 Unique':<15} {'File2 Total':<15} {'File2 Unique':<15} {'Suitable?':<10}")
    print("-" * 120)
    
    suitable_fields = []
    
    for field in common_fields:
        # Skip unnamed columns
        if 'Unnamed' in str(field):
            continue
            
        total1 = df1[field].notna().sum()
        unique1 = df1[field].nunique()
        total2 = df2[field].notna().sum()
        unique2 = df2[field].nunique()
        
        # Check if suitable (unique in both files)
        is_unique1 = (total1 == unique1 and total1 > 0)
        is_unique2 = (total2 == unique2 and total2 > 0)
        
        suitable = "✓ YES" if (is_unique1 and is_unique2) else ""
        
        if is_unique1 and is_unique2:
            suitable_fields.append(field)
        
        # Only show fields with good uniqueness or common ID-like names
        if is_unique1 or is_unique2 or any(kw in str(field).lower() for kw in ['id', 'subj', 'patient', 'name', '编号', '姓名', 'case']):
            print(f"{str(field):<40} {total1:<15} {unique1:<15} {total2:<15} {unique2:<15} {suitable:<10}")
    
    print("\n" + "=" * 50)
    print("RECOMMENDATION:")
    print("=" * 50)
    
    if suitable_fields:
        print(f"\n✓ Found {len(suitable_fields)} suitable join field(s):")
        for field in suitable_fields:
            print(f"   - {field}")
        print("\nThese fields are UNIQUE in both files (no duplicates)")
        print("→ Use one of these as join field to avoid cartesian product!")
    else:
        print("\n✗ No suitable join field found!")
        print("\nPossible reasons:")
        print("  1. No common unique identifier between files")
        print("  2. Files may have different ID field names")
        print("  3. Data quality issues (duplicates in ID fields)")
        
        print("\nSuggestions:")
        print("  - Check if files have 'subjid', 'patient_id', 'case_number', etc.")
        print("  - Clean source data to remove duplicate IDs")
        print("  - Create a unique identifier if needed")

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
finally:
    root.destroy()

import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

print("MDIP Single File Sheet Merger with File Picker")
print("=" * 50)

# Hide the main tkinter window
root = tk.Tk()
root.withdraw()

# Select Excel file
print("\nPlease select an Excel file to merge sheets...")
file_path = filedialog.askopenfilename(
    title="Select Excel File to Merge Sheets",
    filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
    initialdir="."
)

if not file_path:
    print("No file selected. Exiting.")
    root.destroy()
    exit()

selected_file = Path(file_path)
print(f"Selected: {selected_file.name}")

try:
    print(f"\nProcessing: {selected_file.name}")
    
    # Load all sheets and analyze fields
    excel_file = pd.ExcelFile(selected_file)
    all_field_counts = {}
    sheet_data = {}
    
    print("\nAnalyzing sheets...")
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
                print(f"  {sheet_name}: {len(df)} rows x {len(headers)} cols")
        except:
            continue
    
    # Identify common and unique fields
    common_fields = {field for field, count in all_field_counts.items() if count > 1}
    print(f"\nCommon fields detected: {len(common_fields)}")
    
    # Select master sheet (largest with most common fields)
    master_sheet = max(sheet_data.keys(), 
                      key=lambda s: len(sheet_data[s]['fields']) + 
                                  len([f for f in sheet_data[s]['fields'] if f in common_fields]))
    
    print(f"Master sheet: {master_sheet}")
    
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
    
    print(f"Join field: {join_field}")
    
    # Merge other sheets
    print("\nMerging sheets...")
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
        
        print(f"  Merged {sheet_name}: +{merged_df.shape[1] - before_cols} fields")
    
    # Select output location
    print("\n" + "=" * 50)
    print("Select output location...")
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
        print(f"No location selected. Saving to: {output_path}")
    
    # Save result
    print("\nSaving merged file...")
    merged_df.to_excel(output_path, index=False)
    
    print("\n" + "=" * 50)
    print("SUCCESS!")
    print(f"Output file: {output_path}")
    print(f"Final result: {merged_df.shape[0]} rows x {merged_df.shape[1]} columns")
    print(f"Added fields: {added_fields}")
    
    # Check for duplicates
    duplicates = [col for col in merged_df.columns if merged_df.columns.tolist().count(col) > 1]
    print(f"Duplicate fields: {len(duplicates)} (should be 0)")
    
    # Offer to open the file
    open_choice = input("\nOpen the merged file now? (y/n): ").lower()
    if open_choice == 'y':
        import os
        os.startfile(output_path)
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
finally:
    root.destroy()

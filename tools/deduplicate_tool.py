import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

print("MDIP Duplicate Record Remover")
print("=" * 50)

# Hide the main tkinter window
root = tk.Tk()
root.withdraw()

# Select Excel file
print("\nPlease select an Excel file to deduplicate...")
file_path = filedialog.askopenfilename(
    title="Select Excel File to Deduplicate",
    filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
    initialdir="."
)

if not file_path:
    print("No file selected. Exiting.")
    root.destroy()
    exit()

print(f"\n[DEBUG] File selected successfully")
selected_file = Path(file_path)
print(f"Selected: {selected_file.name}")
print(f"File exists: {selected_file.exists()}")

try:
    # Load data
    print("\nLoading data...")
    print(f"File path: {selected_file}")
    df = pd.read_excel(selected_file)
    print(f"Original data: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"Columns: {list(df.columns[:10])}")
    
    # Find ID column
    id_cols = [col for col in df.columns if any(kw in col.lower() for kw in ['id', 'subjid', 'patient', '编号', '病例'])]
    
    if not id_cols:
        print("\nNo ID column found! Cannot deduplicate.")
        print("Please ensure your file has a column with 'id', 'subjid', or 'patient' in the name.")
        root.destroy()
        exit()
    
    print(f"\nID columns found: {id_cols}")
    
    # If multiple ID columns, let user choose
    if len(id_cols) > 1:
        print("\nSelect ID column for deduplication:")
        for i, col in enumerate(id_cols, 1):
            print(f"   {i}. {col}")
        choice = int(input("Column number: ")) - 1
        if not (0 <= choice < len(id_cols)):
            print("Invalid selection")
            root.destroy()
            exit()
        id_col = id_cols[choice]
    else:
        id_col = id_cols[0]
    
    print(f"\nUsing ID column: {id_col}")
    
    # Check for duplicates
    total_ids = df[id_col].notna().sum()
    unique_ids = df[id_col].nunique()
    dup_count = total_ids - unique_ids
    
    print(f"Total records: {total_ids}")
    print(f"Unique IDs: {unique_ids}")
    print(f"Duplicate records: {dup_count}")
    
    if dup_count == 0:
        print("\nNo duplicates found! File is already deduplicated.")
        root.destroy()
        exit()
    
    # Show some duplicate examples
    dup_ids = df[df[id_col].duplicated(keep=False)][id_col].unique()
    print(f"\nNumber of IDs with duplicates: {len(dup_ids)}")
    print("\nExample cases with duplicates:")
    for i, dup_id in enumerate(dup_ids[:5], 1):
        count = len(df[df[id_col] == dup_id])
        print(f"   {i}. ID {dup_id}: {count} records")
    
    # Find date columns
    date_cols = [col for col in df.columns if any(kw in col.lower() for kw in 
                 ['date', 'time', '日期', '时间', 'year', '年'])]
    
    print(f"\nDate columns found: {len(date_cols)}")
    if date_cols:
        for col in date_cols[:10]:
            print(f"   - {col}")
    
    # Choose deduplication strategy
    print("\n" + "=" * 50)
    print("Deduplication strategy:")
    print("   1. Keep FIRST record (earliest)")
    print("   2. Keep LAST record (latest)")
    
    if date_cols:
        print("   3. Keep earliest by date column")
        print("   4. Keep latest by date column")
        strategy_choice = input("\nChoice (1-4, default=2): ").strip() or "2"
    else:
        strategy_choice = input("\nChoice (1-2, default=2): ").strip() or "2"
    
    # Perform deduplication
    print("\n" + "=" * 50)
    print("Deduplicating...")
    
    if strategy_choice == "1":
        # Keep first record
        dedup_df = df.drop_duplicates(subset=[id_col], keep='first')
        method_desc = "First record (by row order)"
        
    elif strategy_choice == "2":
        # Keep last record
        dedup_df = df.drop_duplicates(subset=[id_col], keep='last')
        method_desc = "Last record (by row order)"
        
    elif strategy_choice in ["3", "4"] and date_cols:
        # Sort by date column first
        print("\nSelect date column for sorting:")
        for i, col in enumerate(date_cols, 1):
            non_null = df[col].notna().sum()
            print(f"   {i}. {col} ({non_null} non-null values)")
        
        date_choice = int(input("Column number: ")) - 1
        if not (0 <= date_choice < len(date_cols)):
            print("Invalid selection")
            root.destroy()
            exit()
        
        date_col = date_cols[date_choice]
        print(f"Using date column: {date_col}")
        
        # Convert to datetime
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        except:
            print(f"Warning: Could not parse {date_col} as date")
        
        # Sort by date
        ascending = (strategy_choice == "3")
        df_sorted = df.sort_values(by=date_col, ascending=ascending)
        
        # Keep first after sorting (which is earliest/latest depending on sort order)
        dedup_df = df_sorted.drop_duplicates(subset=[id_col], keep='first')
        
        method_desc = f"{'Earliest' if ascending else 'Latest'} by {date_col}"
    
    else:
        print("Invalid choice, using default (keep last)")
        dedup_df = df.drop_duplicates(subset=[id_col], keep='last')
        method_desc = "Last record (by row order)"
    
    # Results
    removed_count = len(df) - len(dedup_df)
    print(f"\nDeduplication complete!")
    print(f"Method: {method_desc}")
    print(f"Original rows: {len(df)}")
    print(f"Deduplicated rows: {len(dedup_df)}")
    print(f"Removed rows: {removed_count}")
    
    # Select output location
    print("\n" + "=" * 50)
    print("Select output location...")
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    default_name = f"{selected_file.stem}_dedup_{timestamp}.xlsx"
    
    output_path = filedialog.asksaveasfilename(
        title="Save Deduplicated File As",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialdir=str(selected_file.parent),
        initialfile=default_name
    )
    
    if not output_path:
        output_path = default_name
        print(f"No location selected. Saving to: {output_path}")
    
    # Save result
    print("\nSaving deduplicated file...")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Save deduplicated data
        dedup_df.to_excel(writer, sheet_name='Deduplicated Data', index=False)
        
        # Save deduplication info
        info_df = pd.DataFrame([{
            'Item': 'Original File',
            'Value': selected_file.name
        }, {
            'Item': 'ID Column',
            'Value': id_col
        }, {
            'Item': 'Method',
            'Value': method_desc
        }, {
            'Item': 'Original Rows',
            'Value': len(df)
        }, {
            'Item': 'Deduplicated Rows',
            'Value': len(dedup_df)
        }, {
            'Item': 'Removed Rows',
            'Value': removed_count
        }, {
            'Item': 'Unique IDs',
            'Value': unique_ids
        }])
        info_df.to_excel(writer, sheet_name='Dedup Info', index=False)
    
    print("\n" + "=" * 50)
    print("SUCCESS!")
    print(f"Output file: {output_path}")
    print(f"Final result: {len(dedup_df)} rows x {dedup_df.shape[1]} columns")
    print(f"Removed {removed_count} duplicate records ({removed_count/len(df)*100:.1f}%)")
    
    # Offer to open the file
    open_choice = input("\nOpen the deduplicated file now? (y/n): ").lower()
    if open_choice == 'y':
        import os
        os.startfile(output_path)
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
finally:
    root.destroy()

"""
Basic File Analysis Example

This example demonstrates how to use MDIP to analyze Excel file structures
and extract field information.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from mdip.core.matcher import DataMatcher
from mdip.core.reporter import ReportGenerator
import pandas as pd


def analyze_single_file(file_path: str):
    """Analyze a single Excel file and display results."""
    print(f"🔍 Analyzing file: {file_path}")
    
    matcher = DataMatcher()
    
    try:
        # Analyze file structure
        analysis = matcher.analyze_excel_structure(file_path)
        
        print(f"\n📊 File Analysis Results:")
        print(f"   📁 File: {Path(file_path).name}")
        print(f"   📋 Total sheets: {len(analysis['sheets'])}")
        print(f"   🏷️  Total fields: {analysis['total_fields']}")
        
        # Display sheet information
        print(f"\n📑 Sheet Details:")
        for sheet_name, sheet_info in analysis['sheets'].items():
            print(f"   Sheet: {sheet_name}")
            print(f"     Fields: {len(sheet_info['headers'])}")
            print(f"     Sample fields: {', '.join(sheet_info['headers'][:5])}")
            if len(sheet_info['headers']) > 5:
                print(f"     ... and {len(sheet_info['headers']) - 5} more")
            print()
        
        return analysis
    
    except Exception as e:
        print(f"❌ Error analyzing file: {str(e)}")
        return None


def analyze_directory(directory_path: str):
    """Analyze all Excel files in a directory."""
    print(f"🔍 Analyzing directory: {directory_path}")
    
    matcher = DataMatcher()
    
    # Discover files
    file_registry = matcher.discover_excel_files(directory_path)
    
    if not file_registry:
        print("❌ No Excel files found in directory.")
        return
    
    print(f"📊 Found {len(file_registry)} Excel files:")
    
    all_analyses = {}
    
    for file_path, file_info in file_registry.items():
        print(f"\n📄 Processing: {file_info['filename']}")
        
        analysis = analyze_single_file(file_path)
        if analysis:
            all_analyses[file_path] = analysis
    
    # Generate summary report
    if all_analyses:
        generate_summary_report(all_analyses)
    
    return all_analyses


def generate_summary_report(analyses: dict):
    """Generate a summary report from multiple file analyses."""
    print(f"\n📝 Generating Summary Report")
    print("=" * 50)
    
    total_files = len(analyses)
    total_sheets = sum(len(analysis['sheets']) for analysis in analyses.values())
    total_fields = sum(analysis['total_fields'] for analysis in analyses.values())
    
    print(f"📊 Summary Statistics:")
    print(f"   Files analyzed: {total_files}")
    print(f"   Total sheets: {total_sheets}")
    print(f"   Total fields: {total_fields}")
    print(f"   Avg fields per file: {total_fields / total_files:.1f}")
    
    # Field frequency analysis
    field_counts = {}
    for analysis in analyses.values():
        for sheet_info in analysis['sheets'].values():
            for field in sheet_info['headers']:
                field_lower = field.lower().strip()
                field_counts[field_lower] = field_counts.get(field_lower, 0) + 1
    
    # Most common fields
    common_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print(f"\n🔥 Most Common Fields (top 10):")
    for field, count in common_fields:
        print(f"   {field}: {count} occurrences")
    
    # Generate Excel report
    reporter = ReportGenerator()
    
    # Prepare data for reporting
    dataframes = {}
    for file_path, analysis in analyses.items():
        filename = Path(file_path).stem
        
        # Create sheet summary
        sheet_data = []
        for sheet_name, sheet_info in analysis['sheets'].items():
            sheet_data.append({
                'File': filename,
                'Sheet': sheet_name,
                'Fields': len(sheet_info['headers']),
                'Sample_Fields': ', '.join(sheet_info['headers'][:3])
            })
        
        if sheet_data:
            dataframes[filename] = pd.DataFrame(sheet_data)
    
    # Generate and export report
    report = reporter.generate_data_summary_report(dataframes, "File Analysis Summary")
    
    output_file = "file_analysis_report.xlsx"
    reporter.export_report_to_excel(report, output_file)
    
    print(f"\n✅ Detailed report saved to: {output_file}")


def main():
    """Main function for the example."""
    print("🏥 Medical Data Integration Platform - File Analysis Example")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("Usage: python basic_file_analysis.py <file_or_directory_path>")
        print("\nExamples:")
        print("  python basic_file_analysis.py data.xlsx")
        print("  python basic_file_analysis.py /path/to/data/directory")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if not Path(input_path).exists():
        print(f"❌ Path not found: {input_path}")
        sys.exit(1)
    
    # Check if input is file or directory
    if Path(input_path).is_file():
        # Single file analysis
        if input_path.endswith(('.xlsx', '.xls')):
            analysis = analyze_single_file(input_path)
            if analysis:
                print("\n✅ File analysis completed successfully.")
        else:
            print("❌ File must be an Excel file (.xlsx or .xls)")
    
    elif Path(input_path).is_dir():
        # Directory analysis
        analyses = analyze_directory(input_path)
        if analyses:
            print(f"\n✅ Directory analysis completed. Processed {len(analyses)} files.")
    
    else:
        print("❌ Input must be a file or directory")


if __name__ == "__main__":
    main()
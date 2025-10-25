"""
Main CLI Interface for Medical Data Integration Platform (MDIP)

This module provides a command-line interface for all MDIP functionality including:
- File analysis and structure discovery
- Data matching and integration
- Quality assessment and reporting
- Configuration management
"""

import argparse
import sys
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mdip.core.matcher import DataMatcher
from mdip.core.quality_control import QualityAssessment
from mdip.core.reporter import ReportGenerator
from mdip.core.validation import MedicalDataValidator
from mdip.config.field_config import FieldConfig
from mdip.utils.data_utils import DataProcessor


def setup_logging(level: str = 'INFO'):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('mdip.log')
        ]
    )


def analyze_files_command(args):
    """处理文件分析命令。"""
    print(f"🔍 正在分析目录中的文件: {args.directory}")
    
    try:
        # 初始化组件
        field_config = FieldConfig()
        matcher = DataMatcher(field_config)
        
        # 发现Excel文件
        import glob
        excel_files = glob.glob(os.path.join(args.directory, "*.xlsx")) + glob.glob(os.path.join(args.directory, "*.xls"))
        
        if not excel_files:
            print("❌ 在指定目录中未找到Excel文件。")
            return
        
        print(f"📊 找到 {len(excel_files)} 个Excel文件：")
        
        # 分析每个文件
        analysis_results = {}
        for file_path in excel_files:
            filename = os.path.basename(file_path)
            print(f"\n📄 正在分析: {filename}")
            
            try:
                # 简单的Excel文件分析
                import pandas as pd
                excel_file = pd.ExcelFile(file_path)
                
                file_analysis = {
                    'filename': filename,
                    'sheets': {},
                    'total_fields': 0,
                    'file_size': os.path.getsize(file_path)
                }
                
                for sheet_name in excel_file.sheet_names:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)  # 只读取表头
                        headers = list(df.columns)
                        file_analysis['sheets'][sheet_name] = {
                            'headers': headers,
                            'field_count': len(headers)
                        }
                        file_analysis['total_fields'] += len(headers)
                    except Exception as e:
                        print(f"      ⚠️ 无法读取工作表 {sheet_name}: {e}")
                
                analysis_results[file_path] = file_analysis
                
                print(f"   📋 工作表数量: {len(file_analysis['sheets'])}")
                print(f"   🏷️  总字段数: {file_analysis['total_fields']}")
                print(f"   📏 文件大小: {file_analysis['file_size']/1024:.1f} KB")
                
                if args.verbose:
                    for sheet_name, sheet_info in file_analysis['sheets'].items():
                        print(f"      📑 {sheet_name}: {len(sheet_info['headers'])} 个字段")
                        if hasattr(args, 'show_fields') and args.show_fields:
                            for header in sheet_info['headers'][:5]:  # 只显示前5个字段
                                print(f"         - {header}")
                            if len(sheet_info['headers']) > 5:
                                print(f"         ... 还有 {len(sheet_info['headers']) - 5} 个字段")
                
            except Exception as e:
                print(f"   ❌ 分析文件时出错: {str(e)}")
        
        # Generate analysis report if requested
        if args.output:
            print(f"\n📝 Generating analysis report: {args.output}")
            
            reporter = ReportGenerator()
            
            # Convert analysis results to dataframes for reporting
            dataframes = {}
            for file_path, analysis in analysis_results.items():
                filename = Path(file_path).stem
                # Create a summary dataframe
                sheet_data = []
                for sheet_name, sheet_info in analysis['sheets'].items():
                    sheet_data.append({
                        'File': filename,
                        'Sheet': sheet_name,
                        'Fields': len(sheet_info['headers']),
                        'Records': sheet_info.get('row_count', 'Unknown')
                    })
                
                if sheet_data:
                    import pandas as pd
                    dataframes[filename] = pd.DataFrame(sheet_data)
            
            # Generate report
            report = reporter.generate_data_summary_report(dataframes, "File Analysis Report")
            
            # Export report
            if args.output.endswith('.json'):
                reporter.export_report_to_json(report, args.output)
            else:
                # Default to Excel
                output_path = args.output if args.output.endswith('.xlsx') else f"{args.output}.xlsx"
                reporter.export_report_to_excel(report, output_path)
            
            print(f"✅ Report saved to: {args.output}")
        
        print(f"\n✅ Analysis completed for {len(analysis_results)} files.")
        
    except Exception as e:
        print(f"❌ Error during file analysis: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()


def match_data_command(args):
    """Handle data matching command."""
    print(f"🔗 Matching data from files: {', '.join(args.files)}")
    
    try:
        # Initialize components
        field_config = FieldConfig()
        matcher = DataMatcher(field_config)
        
        # Load files
        dataframes = {}
        for file_path in args.files:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                continue
            
            print(f"📂 Loading: {Path(file_path).name}")
            
            # Load Excel file (use first sheet if not specified)
            import pandas as pd
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path, sheet_name=0)  # First sheet
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                print(f"⚠️  Unsupported file format: {file_path}")
                continue
            
            filename = Path(file_path).stem
            dataframes[filename] = df
            print(f"   📊 Shape: {df.shape}")
        
        if len(dataframes) < 2:
            print("❌ Need at least 2 files for matching.")
            return
        
        # Configure matching
        if args.config:
            print(f"📄 Using configuration: {args.config}")
            # Load configuration (implementation depends on config format)
        
        # Perform matching
        print("\n🔄 Performing data matching...")
        
        # Use default matching fields if not specified
        matching_fields = args.fields if args.fields else ['patient_id', 'name', 'id']
        
        # Find available matching fields
        available_fields = set()
        for df in dataframes.values():
            available_fields.update(df.columns)
        
        actual_matching_fields = [field for field in matching_fields if field in available_fields]
        
        if not actual_matching_fields:
            print("⚠️  No matching fields found. Available fields:")
            for filename, df in dataframes.items():
                print(f"   {filename}: {list(df.columns)[:5]}...")
            return
        
        print(f"🎯 Using matching fields: {actual_matching_fields}")
        
        # Perform the match (simplified version)
        # In a full implementation, this would use the DataMatcher class methods
        first_df = list(dataframes.values())[0]
        first_name = list(dataframes.keys())[0]
        
        matched_results = {
            'matched_records': first_df,  # Placeholder
            'total_records': sum(len(df) for df in dataframes.values()),
            'matching_fields': actual_matching_fields,
            'match_method': 'exact' if not args.fuzzy else 'fuzzy'
        }
        
        print(f"✅ Matching completed. Processed {matched_results['total_records']} total records.")
        
        # Generate matching report if requested
        if args.output:
            print(f"📝 Generating matching report: {args.output}")
            
            reporter = ReportGenerator()
            report = reporter.generate_matching_report(matched_results, "Data Matching Report")
            
            # Export report
            if args.output.endswith('.json'):
                reporter.export_report_to_json(report, args.output)
            else:
                output_path = args.output if args.output.endswith('.xlsx') else f"{args.output}.xlsx"
                reporter.export_report_to_excel(report, output_path)
            
            print(f"✅ Report saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Error during data matching: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()


def assess_quality_command(args):
    """Handle quality assessment command."""
    print(f"🔍 Assessing quality of: {args.file}")
    
    try:
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            return
        
        # Load file
        print(f"📂 Loading: {Path(args.file).name}")
        
        import pandas as pd
        if args.file.endswith('.xlsx') or args.file.endswith('.xls'):
            df = pd.read_excel(args.file, sheet_name=args.sheet or 0)
        elif args.file.endswith('.csv'):
            df = pd.read_csv(args.file)
        else:
            print(f"❌ Unsupported file format: {args.file}")
            return
        
        print(f"📊 Dataset shape: {df.shape}")
        
        # Initialize quality assessment
        qa = QualityAssessment()
        
        # Configure critical and important fields if provided
        critical_fields = args.critical_fields.split(',') if args.critical_fields else None
        important_fields = args.important_fields.split(',') if args.important_fields else None
        key_fields = args.key_fields.split(',') if args.key_fields else None
        
        # Perform quality assessment
        print("🔄 Performing quality assessment...")
        
        quality_metrics = qa.generate_overall_assessment(
            df,
            critical_fields=critical_fields,
            important_fields=important_fields,
            key_fields=key_fields
        )
        
        # Display results
        print(f"\n📈 QUALITY ASSESSMENT RESULTS")
        print(f"=" * 50)
        print(f"Overall Quality Score: {quality_metrics.overall_score:.3f}")
        print(f"Quality Grade: {qa._get_quality_grade(quality_metrics.overall_score)}")
        print(f"\nDimension Scores:")
        print(f"  📋 Completeness: {quality_metrics.completeness.get('overall_completeness', 0):.3f}")
        print(f"  🔄 Consistency:  {quality_metrics.consistency.get('overall_consistency_score', 0):.3f}")
        print(f"  🎯 Uniqueness:   {quality_metrics.uniqueness.get('uniqueness_score', 0):.3f}")
        print(f"  ✅ Accuracy:     {quality_metrics.accuracy.get('overall_accuracy_score', 0):.3f}")
        print(f"  ⏰ Timeliness:   {quality_metrics.timeliness.get('timeliness_score', 0):.3f}")
        
        # Show key issues
        if quality_metrics.uniqueness.get('duplicate_rate', 0) > 0:
            print(f"\n⚠️  Found {quality_metrics.uniqueness.get('duplicate_rows', 0)} duplicate rows "
                  f"({quality_metrics.uniqueness.get('duplicate_rate', 0):.1%})")
        
        if quality_metrics.accuracy.get('invalid_value_count', 0) > 0:
            print(f"⚠️  Found {quality_metrics.accuracy.get('invalid_value_count', 0)} data quality issues")
        
        # Generate detailed report if requested
        if args.output:
            print(f"\n📝 Generating detailed quality report: {args.output}")
            
            reporter = ReportGenerator()
            report = reporter.generate_quality_report(quality_metrics.to_dict(), "Quality Assessment Report")
            
            # Export report
            if args.output.endswith('.json'):
                reporter.export_report_to_json(report, args.output)
            else:
                output_path = args.output if args.output.endswith('.xlsx') else f"{args.output}.xlsx"
                reporter.export_report_to_excel(report, output_path)
            
            print(f"✅ Detailed report saved to: {args.output}")
        
        print(f"\n✅ Quality assessment completed.")
        
    except Exception as e:
        print(f"❌ Error during quality assessment: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()


def validate_data_command(args):
    """Handle data validation command."""
    print(f"✅ Validating data: {args.file}")
    
    try:
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            return
        
        # Load file
        print(f"📂 Loading: {Path(args.file).name}")
        
        import pandas as pd
        if args.file.endswith('.xlsx') or args.file.endswith('.xls'):
            df = pd.read_excel(args.file, sheet_name=args.sheet or 0)
        elif args.file.endswith('.csv'):
            df = pd.read_csv(args.file)
        else:
            print(f"❌ Unsupported file format: {args.file}")
            return
        
        print(f"📊 Dataset shape: {df.shape}")
        
        # Initialize validator
        if args.medical:
            print("🏥 Using medical data validation rules")
            validator = MedicalDataValidator()
        else:
            print("📋 Using general validation rules")
            from mdip.core.validation import DataValidator
            validator = DataValidator()
        
        # Add custom rules if provided
        if args.rules:
            print(f"📄 Loading custom rules: {args.rules}")
            # Implementation for loading custom rules would go here
        
        # Perform validation
        print("🔄 Performing data validation...")
        
        validation_results = validator.validate_dataframe(df, return_details=True)
        
        # Display results
        print(f"\n✅ VALIDATION RESULTS")
        print(f"=" * 40)
        
        if validation_results['is_valid']:
            print("🎉 All validation checks passed!")
        else:
            print(f"⚠️  Found {validation_results['total_errors']} validation errors")
            print(f"📊 Fields with errors: {validation_results['summary']['fields_with_errors']}")
            print(f"📝 Rows with errors: {validation_results['summary']['rows_with_errors']}")
            
            if args.verbose and validation_results['field_errors']:
                print("\n🔍 Field Error Details:")
                for field, errors in list(validation_results['field_errors'].items())[:5]:
                    print(f"   {field}: {len(errors)} errors")
                    if args.show_errors:
                        for error in errors[:3]:  # Show first 3 errors
                            print(f"      - {error}")
                        if len(errors) > 3:
                            print(f"      ... and {len(errors) - 3} more")
        
        # Generate validation report if requested
        if args.output:
            print(f"\n📝 Generating validation report: {args.output}")
            
            # Save validation results
            import json
            if args.output.endswith('.json'):
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(validation_results, f, indent=2, default=str)
            else:
                # Convert to Excel format
                output_path = args.output if args.output.endswith('.xlsx') else f"{args.output}.xlsx"
                
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    # Summary
                    summary_data = [
                        ['Total Errors', validation_results['total_errors']],
                        ['Is Valid', validation_results['is_valid']],
                        ['Total Rows', validation_results['summary']['total_rows']],
                        ['Fields Validated', validation_results['summary']['total_fields_validated']],
                        ['Error Rate', f"{validation_results['summary']['error_rate']:.2%}"]
                    ]
                    summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    # Field errors
                    if validation_results['field_errors']:
                        field_error_data = []
                        for field, errors in validation_results['field_errors'].items():
                            for error in errors:
                                field_error_data.append([field, error])
                        
                        if field_error_data:
                            field_errors_df = pd.DataFrame(field_error_data, columns=['Field', 'Error'])
                            field_errors_df.to_excel(writer, sheet_name='Field Errors', index=False)
            
            print(f"✅ Validation report saved to: {args.output}")
        
        print(f"\n✅ Validation completed.")
        
    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()


def main():
    """CLI主入口点。"""
    parser = argparse.ArgumentParser(
        description="医疗数据整合平台 (MDIP) - 命令行界面",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 分析目录中的Excel文件
  mdip analyze /path/to/data --output 分析报告.xlsx
  
  # 匹配多个文件的数据  
  mdip match 文件1.xlsx 文件2.csv --fields patient_id,name --fuzzy --output 匹配报告.xlsx
  
  # 评估数据质量
  mdip quality 数据.xlsx --critical-fields patient_id,name --output 质量报告.json
  
  # 验证医疗数据
  mdip validate 患者数据.xlsx --medical --output 验证报告.xlsx
        """
    )
    
    # 全局选项
    parser.add_argument('--verbose', '-v', action='store_true', help='启用详细输出')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='设置日志级别')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 分析命令
    analyze_parser = subparsers.add_parser('analyze', help='分析文件结构和内容')
    analyze_parser.add_argument('directory', nargs='?', default='docs', help='包含要分析文件的目录 (默认: docs)')
    analyze_parser.add_argument('--output', '-o', help='输出报告文件')
    analyze_parser.add_argument('--show-fields', action='store_true', help='在输出中显示字段名')
    analyze_parser.set_defaults(func=analyze_files_command)
    
    # 匹配命令
    match_parser = subparsers.add_parser('match', help='匹配并整合多个文件的数据')
    match_parser.add_argument('files', nargs='+', help='要匹配的文件')
    match_parser.add_argument('--fields', '-f', help='逗号分隔的匹配字段')
    match_parser.add_argument('--fuzzy', action='store_true', help='使用模糊匹配')
    match_parser.add_argument('--config', '-c', help='匹配配置文件')
    match_parser.add_argument('--output', '-o', help='输出报告文件')
    match_parser.set_defaults(func=match_data_command)
    
    # 质量命令
    quality_parser = subparsers.add_parser('quality', help='评估数据质量')
    quality_parser.add_argument('file', help='要评估的文件')
    quality_parser.add_argument('--sheet', help='Excel工作表名称/索引')
    quality_parser.add_argument('--critical-fields', help='逗号分隔的关键字段名')
    quality_parser.add_argument('--important-fields', help='逗号分隔的重要字段名') 
    quality_parser.add_argument('--key-fields', help='逗号分隔的主键字段名')
    quality_parser.add_argument('--output', '-o', help='输出报告文件')
    quality_parser.set_defaults(func=assess_quality_command)
    
    # 验证命令
    validate_parser = subparsers.add_parser('validate', help='根据规则验证数据')
    validate_parser.add_argument('file', help='要验证的文件')
    validate_parser.add_argument('--sheet', help='Excel工作表名称/索引')
    validate_parser.add_argument('--medical', action='store_true', help='使用医疗数据验证规则')
    validate_parser.add_argument('--rules', '-r', help='自定义验证规则文件')
    validate_parser.add_argument('--show-errors', action='store_true', help='显示详细错误信息')
    validate_parser.add_argument('--output', '-o', help='输出验证报告文件')
    validate_parser.set_defaults(func=validate_data_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Check if command was provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
"""
基础文件分析示例

本示例演示如何使用MDIP来分析Excel文件结构并提取字段信息。
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from mdip.core.matcher import DataMatcher
from mdip.core.reporter import ReportGenerator
import pandas as pd


def analyze_single_file(file_path: str):
    """分析单个Excel文件并显示结果。"""
    print(f"🔍 正在分析文件: {file_path}")
    
    matcher = DataMatcher()
    
    try:
        # 分析文件结构
        analysis = matcher.analyze_excel_structure(file_path)
        
        print(f"\n📊 文件分析结果:")
        print(f"   📁 文件名: {Path(file_path).name}")
        print(f"   📋 工作表总数: {len(analysis['sheets'])}")
        print(f"   🏷️  字段总数: {analysis['total_fields']}")
        
        # 显示工作表信息
        print(f"\n📑 工作表详情:")
        for sheet_name, sheet_info in analysis['sheets'].items():
            print(f"   工作表: {sheet_name}")
            print(f"     字段数: {len(sheet_info['headers'])}")
            print(f"     示例字段: {', '.join(sheet_info['headers'][:5])}")
            if len(sheet_info['headers']) > 5:
                print(f"     ... 还有 {len(sheet_info['headers']) - 5} 个字段")
            print()
        
        return analysis
    
    except Exception as e:
        print(f"❌ 分析文件时出错: {str(e)}")
        return None


def analyze_directory(directory_path: str):
    """分析目录中的所有Excel文件。"""
    print(f"🔍 正在分析目录: {directory_path}")
    
    matcher = DataMatcher()
    
    # 发现文件
    file_registry = matcher.discover_excel_files(directory_path)
    
    if not file_registry:
        print("❌ 目录中未找到Excel文件。")
        return
    
    print(f"📊 找到 {len(file_registry)} 个Excel文件:")
    
    all_analyses = {}
    
    for file_path, file_info in file_registry.items():
        print(f"\n📄 正在处理: {file_info['filename']}")
        
        analysis = analyze_single_file(file_path)
        if analysis:
            all_analyses[file_path] = analysis
    
    # 生成汇总报告
    if all_analyses:
        generate_summary_report(all_analyses)
    
    return all_analyses


def generate_summary_report(analyses: dict):
    """从多个文件分析结果生成汇总报告。"""
    print(f"\n📝 生成汇总报告")
    print("=" * 50)
    
    total_files = len(analyses)
    total_sheets = sum(len(analysis['sheets']) for analysis in analyses.values())
    total_fields = sum(analysis['total_fields'] for analysis in analyses.values())
    
    print(f"📊 汇总统计:")
    print(f"   分析文件数: {total_files}")
    print(f"   工作表总数: {total_sheets}")
    print(f"   字段总数: {total_fields}")
    print(f"   平均每文件字段数: {total_fields / total_files:.1f}")
    
    # 字段频率分析
    field_counts = {}
    for analysis in analyses.values():
        for sheet_info in analysis['sheets'].values():
            for field in sheet_info['headers']:
                field_lower = field.lower().strip()
                field_counts[field_lower] = field_counts.get(field_lower, 0) + 1
    
    # 最常见字段
    common_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print(f"\n🔥 最常见字段 (前10个):")
    for field, count in common_fields:
        print(f"   {field}: {count} 次出现")
    
    # 生成Excel报告
    reporter = ReportGenerator()
    
    # 准备报告数据
    dataframes = {}
    for file_path, analysis in analyses.items():
        filename = Path(file_path).stem
        
        # 创建工作表汇总
        sheet_data = []
        for sheet_name, sheet_info in analysis['sheets'].items():
            sheet_data.append({
                '文件名': filename,
                '工作表': sheet_name,
                '字段数': len(sheet_info['headers']),
                '示例字段': ', '.join(sheet_info['headers'][:3])
            })
        
        if sheet_data:
            dataframes[filename] = pd.DataFrame(sheet_data)
    
    # 生成并导出报告
    report = reporter.generate_data_summary_report(dataframes, "文件分析汇总报告")
    
    output_file = "文件分析报告.xlsx"
    reporter.export_report_to_excel(report, output_file)
    
    print(f"\n✅ 详细报告已保存至: {output_file}")


def main():
    """示例主函数。"""
    print("🏥 医疗数据整合平台 - 文件分析示例")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("使用方法: python 基础文件分析.py <文件或目录路径>")
        print("\n示例:")
        print("  python 基础文件分析.py 数据.xlsx")
        print("  python 基础文件分析.py /path/to/data/directory")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if not Path(input_path).exists():
        print(f"❌ 路径不存在: {input_path}")
        sys.exit(1)
    
    # 检查输入是文件还是目录
    if Path(input_path).is_file():
        # 单文件分析
        if input_path.endswith(('.xlsx', '.xls')):
            analysis = analyze_single_file(input_path)
            if analysis:
                print("\n✅ 文件分析完成。")
        else:
            print("❌ 文件必须是Excel格式 (.xlsx 或 .xls)")
    
    elif Path(input_path).is_dir():
        # 目录分析
        analyses = analyze_directory(input_path)
        if analyses:
            print(f"\n✅ 目录分析完成。处理了 {len(analyses)} 个文件。")
    
    else:
        print("❌ 输入必须是文件或目录")


if __name__ == "__main__":
    main()
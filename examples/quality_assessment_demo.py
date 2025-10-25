"""
数据质量评估演示

本示例演示如何使用MDIP进行全面的数据质量评估。
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from mdip.core.quality_control import QualityAssessment
from mdip.core.reporter import ReportGenerator
import pandas as pd


def assess_file_quality(file_path: str, sheet_name: str = None):
    """评估文件中数据的质量。"""
    print(f"🔍 正在评估数据质量: {file_path}")
    
    try:
        # 加载数据
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path, sheet_name=sheet_name or 0)
        
        print(f"📊 数据集规模: {df.shape}")
        print(f"📋 列名: {list(df.columns)}")
        
        # 初始化质量评估
        qa = QualityAssessment()
        
        # 定义医疗数据的字段类别
        critical_fields = ['patient_id', 'name', 'id', 'subject_id']
        important_fields = ['age', 'gender', 'date_of_birth', 'admission_date']
        key_fields = ['patient_id', 'id', 'subject_id']
        date_fields = [col for col in df.columns if 'date' in col.lower()]
        
        # 筛选实际存在的字段
        critical_fields = [f for f in critical_fields if f in df.columns]
        important_fields = [f for f in important_fields if f in df.columns]
        key_fields = [f for f in key_fields if f in df.columns]
        
        print(f"🎯 关键字段: {critical_fields}")
        print(f"📌 重要字段: {important_fields}")
        print(f"🔑 主键字段: {key_fields}")
        print(f"📅 日期字段: {date_fields}")
        
        # 执行全面评估
        print("\n🔄 正在执行质量评估...")
        
        quality_metrics = qa.generate_overall_assessment(
            df,
            critical_fields=critical_fields,
            important_fields=important_fields,
            key_fields=key_fields,
            date_fields=date_fields
        )
        
        # 显示结果
        display_quality_results(quality_metrics)
        
        # 生成详细报告
        generate_quality_report(quality_metrics, file_path)
        
        return quality_metrics
        
    except Exception as e:
        print(f"❌ Error assessing quality: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def display_quality_results(quality_metrics):
    """显示质量评估结果。"""
    print(f"\n📈 数据质量评估结果")
    print("=" * 60)
    
    # 总体评分
    overall_score = quality_metrics.overall_score
    grade = _get_quality_grade(overall_score)
    
    print(f"🎯 总体质量评分: {overall_score:.3f} (等级: {grade})")
    
    # 维度评分
    print(f"\n📊 质量维度:")
    dimensions = [
        ("完整性", quality_metrics.completeness.get('overall_completeness', 0)),
        ("一致性", quality_metrics.consistency.get('overall_consistency_score', 0)),
        ("唯一性", quality_metrics.uniqueness.get('uniqueness_score', 0)),
        ("准确性", quality_metrics.accuracy.get('overall_accuracy_score', 0)),
        ("时效性", quality_metrics.timeliness.get('timeliness_score', 0))
    ]
    
    for dim_name, score in dimensions:
        grade = _get_quality_grade(score)
        bar = "█" * int(score * 20)  # 20字符进度条
        print(f"  {dim_name:12} {score:.3f} [{bar:<20}] {grade}")
    
    # 关键发现
    print(f"\n🔍 关键发现:")
    
    # 完整性问题
    completeness = quality_metrics.completeness.get('overall_completeness', 1)
    if completeness < 0.8:
        print(f"  ⚠️  数据完整性较低: {completeness:.1%}")
    
    # 重复问题
    duplicate_rate = quality_metrics.uniqueness.get('duplicate_rate', 0)
    if duplicate_rate > 0:
        duplicate_count = quality_metrics.uniqueness.get('duplicate_rows', 0)
        print(f"  ⚠️  发现 {duplicate_count} 个重复行 ({duplicate_rate:.1%})")
    
    # 准确性问题
    invalid_count = quality_metrics.accuracy.get('invalid_value_count', 0)
    if invalid_count > 0:
        print(f"  ⚠️  发现 {invalid_count} 个数据准确性问题")
    
    # 字段完整性详情
    field_completeness = quality_metrics.completeness.get('field_completeness', {})
    if field_completeness:
        print(f"\n📋 字段完整性 (最低5个):")
        sorted_fields = sorted(
            field_completeness.items(),
            key=lambda x: x[1].get('rate', 0)
        )[:5]
        
        for field, stats in sorted_fields:
            rate = stats.get('rate', 0)
            missing = stats.get('missing_count', 0)
            grade = stats.get('quality_grade', 'F')
            print(f"  {field:20} {rate:.1%} ({missing} 个缺失) [{grade}]")
    
    # 建议
    if hasattr(quality_metrics, 'recommendations'):
        recommendations = quality_metrics.recommendations
    else:
        recommendations = _generate_recommendations(quality_metrics)
    
    if recommendations:
        print(f"\n💡 改进建议:")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"  {i}. {rec}")


def generate_quality_report(quality_metrics, file_path):
    """Generate detailed quality report."""
    print(f"\n📝 Generating detailed quality report...")
    
    try:
        reporter = ReportGenerator()
        
        # Convert quality metrics to dict for reporting
        metrics_dict = quality_metrics.to_dict()
        
        # Generate comprehensive report
        report = reporter.generate_quality_report(
            metrics_dict,
            f"Quality Assessment Report - {Path(file_path).name}"
        )
        
        # Export to Excel
        output_file = f"quality_report_{Path(file_path).stem}.xlsx"
        reporter.export_report_to_excel(report, output_file)
        
        print(f"✅ Detailed report saved to: {output_file}")
        
        # Also export to JSON for programmatic access
        json_file = f"quality_report_{Path(file_path).stem}.json"
        reporter.export_report_to_json(report, json_file)
        
        print(f"📄 JSON report saved to: {json_file}")
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")


def _get_quality_grade(score: float) -> str:
    """Convert quality score to letter grade."""
    if score >= 0.9:
        return 'A'
    elif score >= 0.8:
        return 'B'
    elif score >= 0.7:
        return 'C'
    elif score >= 0.6:
        return 'D'
    else:
        return 'F'


def _generate_recommendations(quality_metrics):
    """Generate improvement recommendations."""
    recommendations = []
    
    # Completeness recommendations
    completeness = quality_metrics.completeness.get('overall_completeness', 1)
    if completeness < 0.8:
        recommendations.append(
            "Improve data completeness through better data collection processes"
        )
    
    # Uniqueness recommendations
    duplicate_rate = quality_metrics.uniqueness.get('duplicate_rate', 0)
    if duplicate_rate > 0.05:
        recommendations.append(
            "Implement deduplication procedures to reduce duplicate records"
        )
    
    # Accuracy recommendations
    accuracy = quality_metrics.accuracy.get('overall_accuracy_score', 1)
    if accuracy < 0.9:
        recommendations.append(
            "Add validation rules and data entry checks to improve accuracy"
        )
    
    # Consistency recommendations
    consistency = quality_metrics.consistency.get('overall_consistency_score', 1)
    if consistency < 0.8:
        recommendations.append(
            "Standardize data formats and establish consistent coding practices"
        )
    
    return recommendations


def demo_with_sample_data():
    """Demonstrate quality assessment with generated sample data."""
    print("🧪 Generating sample medical data for demonstration...")
    
    import numpy as np
    from datetime import datetime, timedelta
    
    # Generate sample medical data with known quality issues
    np.random.seed(42)
    n_patients = 1000
    
    # Create sample data with intentional quality issues
    data = {
        'patient_id': [f'P{i:04d}' for i in range(n_patients)],
        'name': [f'Patient {i}' for i in range(n_patients)],
        'age': np.random.normal(65, 15, n_patients).astype(int),
        'gender': np.random.choice(['M', 'F', 'Unknown'], n_patients, p=[0.45, 0.45, 0.1]),
        'admission_date': [
            datetime.now() - timedelta(days=np.random.randint(0, 365))
            for _ in range(n_patients)
        ],
        'cholesterol': np.random.normal(200, 50, n_patients),
        'blood_pressure_systolic': np.random.normal(140, 20, n_patients),
        'diagnosis': np.random.choice(['CAD', 'MI', 'Angina', ''], n_patients, p=[0.3, 0.2, 0.2, 0.3])
    }
    
    # Introduce quality issues
    # 1. Missing values
    missing_indices = np.random.choice(n_patients, size=int(0.15 * n_patients), replace=False)
    for idx in missing_indices:
        data['cholesterol'][idx] = np.nan
    
    # 2. Duplicates
    duplicate_indices = np.random.choice(n_patients//2, size=50, replace=False)
    for idx in duplicate_indices:
        # Duplicate some records
        data['patient_id'][idx + n_patients//2] = data['patient_id'][idx]
        data['name'][idx + n_patients//2] = data['name'][idx]
    
    # 3. Outliers
    outlier_indices = np.random.choice(n_patients, size=20, replace=False)
    for idx in outlier_indices:
        data['age'][idx] = np.random.choice([-5, 150, 999])  # Invalid ages
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save sample data
    sample_file = 'sample_medical_data.xlsx'
    df.to_excel(sample_file, index=False)
    
    print(f"✅ Sample data created: {sample_file}")
    print(f"📊 Sample data shape: {df.shape}")
    
    # Assess quality
    print(f"\n🔄 Assessing quality of sample data...")
    quality_metrics = assess_file_quality(sample_file)
    
    return quality_metrics


def main():
    """Main function for the quality assessment demo."""
    print("🏥 Medical Data Integration Platform - Quality Assessment Demo")
    print("=" * 70)
    
    if len(sys.argv) < 2:
        print("No input file provided. Running demonstration with sample data...")
        demo_with_sample_data()
    else:
        file_path = sys.argv[1]
        sheet_name = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        
        quality_metrics = assess_file_quality(file_path, sheet_name)
        
        if quality_metrics:
            print("\n✅ Quality assessment completed successfully.")
        else:
            print("❌ Quality assessment failed.")


if __name__ == "__main__":
    main()
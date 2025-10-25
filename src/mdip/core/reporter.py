"""
Reporting Module

Generate comprehensive reports for medical data integration and analysis.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate various types of reports for medical data integration."""
    
    def __init__(self):
        """Initialize report generator."""
        self.report_history = []
    
    def generate_data_summary_report(
        self,
        dataframes: Dict[str, pd.DataFrame],
        title: str = "Data Summary Report"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive data summary report.
        
        Args:
            dataframes: Dictionary of DataFrames to summarize
            title: Report title
            
        Returns:
            Dictionary containing report data
        """
        report = {
            'title': title,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_datasets': len(dataframes),
                'total_records': sum(len(df) for df in dataframes.values()),
                'total_fields': sum(len(df.columns) for df in dataframes.values())
            },
            'datasets': {},
            'field_analysis': {},
            'recommendations': []
        }
        
        # Analyze each dataset
        for name, df in dataframes.items():
            dataset_info = {
                'name': name,
                'shape': df.shape,
                'memory_usage': df.memory_usage(deep=True).sum(),
                'columns': list(df.columns),
                'data_types': df.dtypes.to_dict(),
                'missing_data': df.isnull().sum().to_dict(),
                'completeness_rate': (1 - df.isnull().sum().sum() / df.size) if df.size > 0 else 0
            }
            
            # Add descriptive statistics for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                dataset_info['numeric_summary'] = df[numeric_cols].describe().to_dict()
            
            report['datasets'][name] = dataset_info
        
        # Field analysis across datasets
        all_fields = set()
        for df in dataframes.values():
            all_fields.update(df.columns)
        
        for field in all_fields:
            field_info = {
                'appears_in': [],
                'total_occurrences': 0,
                'data_types': set(),
                'avg_completeness': 0
            }
            
            completeness_rates = []
            for dataset_name, df in dataframes.items():
                if field in df.columns:
                    field_info['appears_in'].append(dataset_name)
                    field_info['total_occurrences'] += 1
                    field_info['data_types'].add(str(df[field].dtype))
                    
                    completeness = 1 - (df[field].isnull().sum() / len(df)) if len(df) > 0 else 0
                    completeness_rates.append(completeness)
            
            if completeness_rates:
                field_info['avg_completeness'] = np.mean(completeness_rates)
            
            field_info['data_types'] = list(field_info['data_types'])
            report['field_analysis'][field] = field_info
        
        # Generate recommendations
        report['recommendations'] = self._generate_data_recommendations(report)
        
        return report
    
    def generate_matching_report(
        self,
        match_results: Dict[str, Any],
        title: str = "Data Matching Report"
    ) -> Dict[str, Any]:
        """
        Generate report for data matching operations.
        
        Args:
            match_results: Results from data matching operation
            title: Report title
            
        Returns:
            Dictionary containing matching report
        """
        report = {
            'title': title,
            'generated_at': datetime.now().isoformat(),
            'matching_summary': {},
            'match_statistics': {},
            'quality_metrics': {},
            'recommendations': []
        }
        
        # Extract matching summary
        if 'matched_records' in match_results:
            matched_df = match_results['matched_records']
            report['matching_summary'] = {
                'total_matched_records': len(matched_df),
                'matching_fields_used': match_results.get('matching_fields', []),
                'match_method': match_results.get('match_method', 'unknown'),
                'confidence_threshold': match_results.get('confidence_threshold', 'not specified')
            }
        
        # Match statistics
        if 'match_scores' in match_results:
            scores = match_results['match_scores']
            report['match_statistics'] = {
                'avg_match_score': np.mean(scores) if scores else 0,
                'median_match_score': np.median(scores) if scores else 0,
                'min_match_score': np.min(scores) if scores else 0,
                'max_match_score': np.max(scores) if scores else 0,
                'score_distribution': {
                    'high_confidence': len([s for s in scores if s >= 0.9]),
                    'medium_confidence': len([s for s in scores if 0.7 <= s < 0.9]),
                    'low_confidence': len([s for s in scores if s < 0.7])
                }
            }
        
        # Quality metrics
        if 'unmatched_records' in match_results:
            unmatched_count = len(match_results['unmatched_records'])
            total_records = match_results.get('total_records', 0)
            
            report['quality_metrics'] = {
                'match_rate': (total_records - unmatched_count) / total_records if total_records > 0 else 0,
                'unmatched_records': unmatched_count,
                'data_quality_issues': match_results.get('quality_issues', [])
            }
        
        # Generate matching recommendations
        report['recommendations'] = self._generate_matching_recommendations(report)
        
        return report
    
    def generate_quality_report(
        self,
        quality_metrics: Dict[str, Any],
        title: str = "Data Quality Report"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive data quality report.
        
        Args:
            quality_metrics: Quality assessment results
            title: Report title
            
        Returns:
            Dictionary containing quality report
        """
        report = {
            'title': title,
            'generated_at': datetime.now().isoformat(),
            'executive_summary': {},
            'detailed_analysis': quality_metrics,
            'quality_grades': {},
            'improvement_plan': [],
            'risk_assessment': {}
        }
        
        # Executive summary
        overall_score = quality_metrics.get('overall_score', 0)
        report['executive_summary'] = {
            'overall_quality_score': overall_score,
            'quality_grade': self._get_quality_grade(overall_score),
            'assessment_date': datetime.now().isoformat(),
            'key_strengths': [],
            'key_concerns': [],
            'priority_actions': []
        }
        
        # Quality grades for each dimension
        dimensions = ['completeness', 'consistency', 'uniqueness', 'accuracy', 'timeliness']
        for dim in dimensions:
            if dim in quality_metrics:
                score_key = f'{dim}_score' if f'{dim}_score' in quality_metrics[dim] else 'overall_completeness' if dim == 'completeness' else f'overall_{dim}_score'
                score = quality_metrics[dim].get(score_key, 0)
                report['quality_grades'][dim] = {
                    'score': score,
                    'grade': self._get_quality_grade(score)
                }
        
        # Risk assessment
        report['risk_assessment'] = self._assess_data_risks(quality_metrics)
        
        # Improvement plan
        report['improvement_plan'] = self._create_improvement_plan(quality_metrics)
        
        return report
    
    def generate_integration_report(
        self,
        integration_results: Dict[str, Any],
        title: str = "Data Integration Report"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive integration report.
        
        Args:
            integration_results: Results from data integration process
            title: Report title
            
        Returns:
            Dictionary containing integration report
        """
        report = {
            'title': title,
            'generated_at': datetime.now().isoformat(),
            'integration_summary': {},
            'source_analysis': {},
            'transformation_log': [],
            'validation_results': {},
            'performance_metrics': {}
        }
        
        # Integration summary
        report['integration_summary'] = {
            'source_datasets': integration_results.get('source_count', 0),
            'total_records_processed': integration_results.get('records_processed', 0),
            'successful_integrations': integration_results.get('successful_matches', 0),
            'failed_integrations': integration_results.get('failed_matches', 0),
            'data_quality_score': integration_results.get('final_quality_score', 0),
            'integration_method': integration_results.get('method', 'unknown')
        }
        
        # Source analysis
        if 'source_analysis' in integration_results:
            report['source_analysis'] = integration_results['source_analysis']
        
        # Transformation log
        if 'transformations' in integration_results:
            report['transformation_log'] = integration_results['transformations']
        
        # Validation results
        if 'validation' in integration_results:
            report['validation_results'] = integration_results['validation']
        
        # Performance metrics
        if 'performance' in integration_results:
            report['performance_metrics'] = integration_results['performance']
        
        return report
    
    def export_report_to_excel(
        self,
        report: Dict[str, Any],
        filename: str,
        include_raw_data: bool = False
    ) -> str:
        """
        Export report to Excel file.
        
        Args:
            report: Report dictionary
            filename: Output filename
            include_raw_data: Whether to include raw data sheets
            
        Returns:
            Path to exported file
        """
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = []
                
                if 'executive_summary' in report:
                    summary_data.extend([
                        ['Executive Summary', ''],
                        ['Overall Score', report['executive_summary'].get('overall_quality_score', 'N/A')],
                        ['Quality Grade', report['executive_summary'].get('quality_grade', 'N/A')],
                        ['Assessment Date', report.get('generated_at', 'N/A')],
                        ['', '']
                    ])
                
                if 'summary' in report:
                    summary_data.extend([
                        ['Data Summary', ''],
                        ['Total Datasets', report['summary'].get('total_datasets', 'N/A')],
                        ['Total Records', report['summary'].get('total_records', 'N/A')],
                        ['Total Fields', report['summary'].get('total_fields', 'N/A')],
                        ['', '']
                    ])
                
                if summary_data:
                    summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Quality grades sheet (if available)
                if 'quality_grades' in report:
                    grades_data = []
                    for dimension, metrics in report['quality_grades'].items():
                        grades_data.append([
                            dimension.title(),
                            metrics.get('score', 0),
                            metrics.get('grade', 'N/A')
                        ])
                    
                    grades_df = pd.DataFrame(grades_data, columns=['Dimension', 'Score', 'Grade'])
                    grades_df.to_excel(writer, sheet_name='Quality Grades', index=False)
                
                # Datasets sheet (if available)
                if 'datasets' in report:
                    datasets_data = []
                    for name, info in report['datasets'].items():
                        datasets_data.append([
                            name,
                            info['shape'][0],
                            info['shape'][1],
                            f"{info.get('completeness_rate', 0):.2%}",
                            f"{info.get('memory_usage', 0) / 1024 / 1024:.2f} MB"
                        ])
                    
                    datasets_df = pd.DataFrame(
                        datasets_data,
                        columns=['Dataset', 'Rows', 'Columns', 'Completeness', 'Memory Usage']
                    )
                    datasets_df.to_excel(writer, sheet_name='Datasets', index=False)
                
                # Recommendations sheet
                recommendations = report.get('recommendations', []) or report.get('improvement_plan', [])
                if recommendations:
                    rec_data = [[i+1, rec] for i, rec in enumerate(recommendations)]
                    rec_df = pd.DataFrame(rec_data, columns=['#', 'Recommendation'])
                    rec_df.to_excel(writer, sheet_name='Recommendations', index=False)
            
            logger.info(f"Report exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting report to Excel: {str(e)}")
            raise
    
    def export_report_to_json(self, report: Dict[str, Any], filename: str) -> str:
        """
        Export report to JSON file.
        
        Args:
            report: Report dictionary
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        try:
            # Convert numpy types to native Python types for JSON serialization
            json_report = self._convert_for_json(report)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Report exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting report to JSON: {str(e)}")
            raise
    
    def _generate_data_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate data quality recommendations."""
        recommendations = []
        
        # Check for datasets with low completeness
        if 'datasets' in report:
            for name, info in report['datasets'].items():
                completeness = info.get('completeness_rate', 1)
                if completeness < 0.8:
                    recommendations.append(
                        f"Dataset '{name}' has low completeness ({completeness:.1%}). "
                        "Consider data collection improvements or imputation strategies."
                    )
        
        # Check for inconsistent field types
        if 'field_analysis' in report:
            for field, info in report['field_analysis'].items():
                if len(info['data_types']) > 1:
                    recommendations.append(
                        f"Field '{field}' has inconsistent data types across datasets: "
                        f"{', '.join(info['data_types'])}. Standardize data types for better integration."
                    )
        
        # Check for fields with low coverage
        if 'field_analysis' in report:
            total_datasets = report['summary']['total_datasets']
            for field, info in report['field_analysis'].items():
                coverage = info['total_occurrences'] / total_datasets
                if coverage < 0.5 and info['avg_completeness'] > 0.8:
                    recommendations.append(
                        f"Field '{field}' appears in only {coverage:.1%} of datasets but has good completeness. "
                        "Consider expanding this field to other datasets for better integration."
                    )
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _generate_matching_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate matching quality recommendations."""
        recommendations = []
        
        # Check match rate
        match_rate = report.get('quality_metrics', {}).get('match_rate', 0)
        if match_rate < 0.8:
            recommendations.append(
                f"Low match rate ({match_rate:.1%}). Consider using fuzzy matching "
                "or additional matching fields to improve coverage."
            )
        
        # Check confidence distribution
        stats = report.get('match_statistics', {})
        if 'score_distribution' in stats:
            dist = stats['score_distribution']
            low_confidence = dist.get('low_confidence', 0)
            total_matches = sum(dist.values())
            
            if total_matches > 0 and low_confidence / total_matches > 0.2:
                recommendations.append(
                    "High proportion of low-confidence matches. "
                    "Review matching criteria and consider manual validation for low-confidence matches."
                )
        
        return recommendations
    
    def _assess_data_risks(self, quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess data quality risks."""
        risks = {
            'high_risk': [],
            'medium_risk': [],
            'low_risk': [],
            'overall_risk_level': 'low'
        }
        
        # Check completeness risks
        completeness = quality_metrics.get('completeness', {}).get('overall_completeness', 1)
        if completeness < 0.6:
            risks['high_risk'].append("Critical data completeness issues may impact analysis reliability")
        elif completeness < 0.8:
            risks['medium_risk'].append("Moderate completeness issues may affect some analyses")
        
        # Check uniqueness risks
        duplicate_rate = quality_metrics.get('uniqueness', {}).get('duplicate_rate', 0)
        if duplicate_rate > 0.1:
            risks['high_risk'].append("High duplicate rate may lead to biased analysis results")
        elif duplicate_rate > 0.05:
            risks['medium_risk'].append("Moderate duplicate rate requires attention")
        
        # Check accuracy risks
        accuracy = quality_metrics.get('accuracy', {}).get('overall_accuracy_score', 1)
        if accuracy < 0.8:
            risks['high_risk'].append("Data accuracy issues may compromise research validity")
        elif accuracy < 0.9:
            risks['medium_risk'].append("Minor accuracy issues detected")
        
        # Determine overall risk level
        if risks['high_risk']:
            risks['overall_risk_level'] = 'high'
        elif risks['medium_risk']:
            risks['overall_risk_level'] = 'medium'
        
        return risks
    
    def _create_improvement_plan(self, quality_metrics: Dict[str, Any]) -> List[str]:
        """Create data quality improvement plan."""
        improvements = []
        
        # Completeness improvements
        completeness = quality_metrics.get('completeness', {}).get('overall_completeness', 1)
        if completeness < 0.8:
            improvements.append(
                "1. Data Collection Enhancement: Implement mandatory field validation "
                "and improve data entry processes to increase completeness"
            )
        
        # Accuracy improvements
        accuracy = quality_metrics.get('accuracy', {}).get('overall_accuracy_score', 1)
        if accuracy < 0.9:
            improvements.append(
                "2. Data Validation: Implement automated validation rules and "
                "regular data quality checks to improve accuracy"
            )
        
        # Uniqueness improvements
        duplicate_rate = quality_metrics.get('uniqueness', {}).get('duplicate_rate', 0)
        if duplicate_rate > 0.05:
            improvements.append(
                "3. Duplicate Management: Establish deduplication procedures and "
                "unique identifier management protocols"
            )
        
        # Consistency improvements
        consistency = quality_metrics.get('consistency', {}).get('overall_consistency_score', 1)
        if consistency < 0.8:
            improvements.append(
                "4. Standardization: Implement data standardization procedures "
                "for formats, codes, and naming conventions"
            )
        
        return improvements
    
    def _get_quality_grade(self, score: float) -> str:
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
    
    def _convert_for_json(self, obj: Any) -> Any:
        """Convert numpy types to JSON-serializable types."""
        if isinstance(obj, dict):
            return {k: self._convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_for_json(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        else:
            return obj
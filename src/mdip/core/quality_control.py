"""
Quality Control Module

Comprehensive quality control and assessment functions for medical data integration.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class QualityMetrics:
    """Container for quality metrics."""
    
    def __init__(self):
        """Initialize quality metrics container."""
        self.completeness = {}
        self.accuracy = {}
        self.consistency = {}
        self.uniqueness = {}
        self.timeliness = {}
        self.overall_score = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'completeness': self.completeness,
            'accuracy': self.accuracy,
            'consistency': self.consistency,
            'uniqueness': self.uniqueness,
            'timeliness': self.timeliness,
            'overall_score': self.overall_score
        }


class QualityAssessment:
    """Quality assessment for datasets."""
    
    def __init__(self):
        """Initialize quality assessment."""
        self.assessment_history = []
    
    def assess_completeness(
        self,
        df: pd.DataFrame,
        critical_fields: Optional[List[str]] = None,
        important_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Assess data completeness.
        
        Args:
            df: DataFrame to assess
            critical_fields: List of critical field names
            important_fields: List of important field names
            
        Returns:
            Completeness assessment results
        """
        total_rows = len(df)
        completeness_results = {
            'overall_completeness': 0.0,
            'field_completeness': {},
            'critical_completeness': 0.0,
            'important_completeness': 0.0,
            'row_completeness': []
        }
        
        if total_rows == 0:
            return completeness_results
        
        # Field-level completeness
        for col in df.columns:
            non_null_count = df[col].notna().sum()
            completeness_rate = non_null_count / total_rows
            completeness_results['field_completeness'][col] = {
                'rate': completeness_rate,
                'missing_count': total_rows - non_null_count,
                'quality_grade': self._get_quality_grade(completeness_rate)
            }
        
        # Overall completeness
        total_cells = df.size
        non_null_cells = df.notna().sum().sum()
        completeness_results['overall_completeness'] = non_null_cells / total_cells if total_cells > 0 else 0
        
        # Critical fields completeness
        if critical_fields:
            critical_cols = [col for col in critical_fields if col in df.columns]
            if critical_cols:
                critical_completeness = df[critical_cols].notna().all(axis=1).mean()
                completeness_results['critical_completeness'] = critical_completeness
        
        # Important fields completeness
        if important_fields:
            important_cols = [col for col in important_fields if col in df.columns]
            if important_cols:
                important_non_null = df[important_cols].notna().sum().sum()
                important_total = len(important_cols) * total_rows
                completeness_results['important_completeness'] = important_non_null / important_total if important_total > 0 else 0
        
        # Row-level completeness distribution
        row_completeness = df.notna().sum(axis=1) / len(df.columns)
        completeness_results['row_completeness'] = {
            'mean': row_completeness.mean(),
            'median': row_completeness.median(),
            'min': row_completeness.min(),
            'max': row_completeness.max(),
            'std': row_completeness.std()
        }
        
        return completeness_results
    
    def assess_consistency(
        self,
        df: pd.DataFrame,
        consistency_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess data consistency.
        
        Args:
            df: DataFrame to assess
            consistency_rules: Dictionary of consistency rules
            
        Returns:
            Consistency assessment results
        """
        consistency_results = {
            'data_type_consistency': {},
            'format_consistency': {},
            'range_consistency': {},
            'relationship_consistency': {},
            'overall_consistency_score': 0.0
        }
        
        # Data type consistency
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if numeric values are consistently formatted
                non_null_values = df[col].dropna().astype(str)
                if not non_null_values.empty:
                    numeric_pattern_count = non_null_values.str.match(r'^\d+\.?\d*$').sum()
                    consistency_rate = numeric_pattern_count / len(non_null_values)
                    consistency_results['data_type_consistency'][col] = consistency_rate
            
        # Format consistency for date fields
        date_columns = df.select_dtypes(include=['datetime64']).columns
        for col in date_columns:
            # Check for consistent date formats
            non_null_dates = df[col].dropna()
            if not non_null_dates.empty:
                # Analyze date format consistency (implementation can be expanded)
                consistency_results['format_consistency'][col] = 1.0  # Placeholder
        
        # Calculate overall consistency score
        all_scores = []
        all_scores.extend(consistency_results['data_type_consistency'].values())
        all_scores.extend(consistency_results['format_consistency'].values())
        
        if all_scores:
            consistency_results['overall_consistency_score'] = np.mean(all_scores)
        
        return consistency_results
    
    def assess_uniqueness(
        self,
        df: pd.DataFrame,
        key_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Assess data uniqueness.
        
        Args:
            df: DataFrame to assess
            key_fields: List of fields that should be unique
            
        Returns:
            Uniqueness assessment results
        """
        uniqueness_results = {
            'duplicate_rows': 0,
            'duplicate_rate': 0.0,
            'field_uniqueness': {},
            'key_field_duplicates': {},
            'uniqueness_score': 0.0
        }
        
        total_rows = len(df)
        if total_rows == 0:
            return uniqueness_results
        
        # Overall duplicate detection
        duplicate_rows = df.duplicated().sum()
        uniqueness_results['duplicate_rows'] = duplicate_rows
        uniqueness_results['duplicate_rate'] = duplicate_rows / total_rows
        
        # Field-level uniqueness
        for col in df.columns:
            unique_count = df[col].nunique()
            total_count = df[col].notna().sum()
            uniqueness_rate = unique_count / total_count if total_count > 0 else 0
            
            uniqueness_results['field_uniqueness'][col] = {
                'unique_count': unique_count,
                'total_count': total_count,
                'uniqueness_rate': uniqueness_rate,
                'duplicate_count': total_count - unique_count
            }
        
        # Key field duplicate analysis
        if key_fields:
            for field in key_fields:
                if field in df.columns:
                    field_duplicates = df[df[field].duplicated(keep=False)]
                    uniqueness_results['key_field_duplicates'][field] = {
                        'duplicate_count': len(field_duplicates),
                        'unique_values_with_duplicates': field_duplicates[field].nunique()
                    }
        
        # Calculate uniqueness score
        uniqueness_score = 1 - uniqueness_results['duplicate_rate']
        uniqueness_results['uniqueness_score'] = uniqueness_score
        
        return uniqueness_results
    
    def assess_accuracy(
        self,
        df: pd.DataFrame,
        accuracy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess data accuracy using validation rules.
        
        Args:
            df: DataFrame to assess
            accuracy_rules: Dictionary of accuracy validation rules
            
        Returns:
            Accuracy assessment results
        """
        accuracy_results = {
            'field_accuracy': {},
            'overall_accuracy_score': 0.0,
            'invalid_value_count': 0,
            'total_value_count': 0
        }
        
        total_values = 0
        invalid_values = 0
        
        # Basic accuracy checks
        for col in df.columns:
            field_accuracy = {
                'invalid_count': 0,
                'total_count': 0,
                'accuracy_rate': 1.0,
                'issues': []
            }
            
            non_null_values = df[col].dropna()
            field_accuracy['total_count'] = len(non_null_values)
            total_values += len(non_null_values)
            
            if not non_null_values.empty:
                # Check for obvious data issues
                if pd.api.types.is_numeric_dtype(df[col]):
                    # Check for infinite values
                    inf_count = np.isinf(non_null_values).sum()
                    if inf_count > 0:
                        field_accuracy['invalid_count'] += inf_count
                        field_accuracy['issues'].append(f"Infinite values: {inf_count}")
                    
                    # Check for extreme outliers (basic check)
                    if len(non_null_values) > 10:
                        Q1 = non_null_values.quantile(0.25)
                        Q3 = non_null_values.quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 3 * IQR
                        upper_bound = Q3 + 3 * IQR
                        
                        outliers = ((non_null_values < lower_bound) | 
                                  (non_null_values > upper_bound)).sum()
                        if outliers > 0:
                            field_accuracy['issues'].append(f"Extreme outliers: {outliers}")
                
                elif df[col].dtype == 'object':
                    # Check for inconsistent string formatting
                    string_values = non_null_values.astype(str)
                    
                    # Check for excessive whitespace
                    whitespace_issues = (string_values != string_values.str.strip()).sum()
                    if whitespace_issues > 0:
                        field_accuracy['issues'].append(f"Whitespace issues: {whitespace_issues}")
                    
                    # Check for empty strings
                    empty_strings = (string_values.str.strip() == '').sum()
                    if empty_strings > 0:
                        field_accuracy['invalid_count'] += empty_strings
                        field_accuracy['issues'].append(f"Empty strings: {empty_strings}")
            
            # Calculate accuracy rate for this field
            if field_accuracy['total_count'] > 0:
                field_accuracy['accuracy_rate'] = (
                    1 - field_accuracy['invalid_count'] / field_accuracy['total_count']
                )
            
            invalid_values += field_accuracy['invalid_count']
            accuracy_results['field_accuracy'][col] = field_accuracy
        
        # Overall accuracy score
        accuracy_results['total_value_count'] = total_values
        accuracy_results['invalid_value_count'] = invalid_values
        
        if total_values > 0:
            accuracy_results['overall_accuracy_score'] = 1 - (invalid_values / total_values)
        
        return accuracy_results
    
    def assess_timeliness(
        self,
        df: pd.DataFrame,
        date_fields: Optional[List[str]] = None,
        reference_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Assess data timeliness.
        
        Args:
            df: DataFrame to assess
            date_fields: List of date field names
            reference_date: Reference date for timeliness assessment
            
        Returns:
            Timeliness assessment results
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        timeliness_results = {
            'date_field_analysis': {},
            'data_age_distribution': {},
            'timeliness_score': 0.0
        }
        
        if not date_fields:
            # Try to identify date fields automatically
            date_fields = []
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    date_fields.append(col)
                elif 'date' in col.lower() or 'time' in col.lower():
                    date_fields.append(col)
        
        timeliness_scores = []
        
        for field in date_fields:
            if field not in df.columns:
                continue
            
            field_analysis = {
                'min_date': None,
                'max_date': None,
                'avg_age_days': None,
                'records_within_year': 0,
                'records_within_month': 0,
                'timeliness_score': 0.0
            }
            
            date_series = pd.to_datetime(df[field], errors='coerce').dropna()
            
            if not date_series.empty:
                field_analysis['min_date'] = date_series.min()
                field_analysis['max_date'] = date_series.max()
                
                # Calculate average age
                age_days = (reference_date - date_series).dt.days
                field_analysis['avg_age_days'] = age_days.mean()
                
                # Count recent records
                one_year_ago = reference_date - pd.Timedelta(days=365)
                one_month_ago = reference_date - pd.Timedelta(days=30)
                
                field_analysis['records_within_year'] = (date_series >= one_year_ago).sum()
                field_analysis['records_within_month'] = (date_series >= one_month_ago).sum()
                
                # Calculate timeliness score (more recent data scores higher)
                max_age = age_days.max()
                if max_age > 0:
                    normalized_ages = age_days / max_age
                    field_analysis['timeliness_score'] = (1 - normalized_ages.mean())
                    timeliness_scores.append(field_analysis['timeliness_score'])
            
            timeliness_results['date_field_analysis'][field] = field_analysis
        
        # Overall timeliness score
        if timeliness_scores:
            timeliness_results['timeliness_score'] = np.mean(timeliness_scores)
        
        return timeliness_results
    
    def generate_overall_assessment(
        self,
        df: pd.DataFrame,
        critical_fields: Optional[List[str]] = None,
        important_fields: Optional[List[str]] = None,
        key_fields: Optional[List[str]] = None,
        date_fields: Optional[List[str]] = None
    ) -> QualityMetrics:
        """
        Generate comprehensive quality assessment.
        
        Args:
            df: DataFrame to assess
            critical_fields: List of critical field names
            important_fields: List of important field names
            key_fields: List of key field names for uniqueness
            date_fields: List of date field names
            
        Returns:
            QualityMetrics object with comprehensive assessment
        """
        metrics = QualityMetrics()
        
        # Assess all quality dimensions
        logger.info("Assessing data completeness...")
        metrics.completeness = self.assess_completeness(df, critical_fields, important_fields)
        
        logger.info("Assessing data consistency...")
        metrics.consistency = self.assess_consistency(df)
        
        logger.info("Assessing data uniqueness...")
        metrics.uniqueness = self.assess_uniqueness(df, key_fields)
        
        logger.info("Assessing data accuracy...")
        metrics.accuracy = self.assess_accuracy(df)
        
        logger.info("Assessing data timeliness...")
        metrics.timeliness = self.assess_timeliness(df, date_fields)
        
        # Calculate overall quality score
        dimension_scores = [
            metrics.completeness.get('overall_completeness', 0) * 0.25,
            metrics.consistency.get('overall_consistency_score', 0) * 0.20,
            metrics.uniqueness.get('uniqueness_score', 0) * 0.20,
            metrics.accuracy.get('overall_accuracy_score', 0) * 0.25,
            metrics.timeliness.get('timeliness_score', 0) * 0.10
        ]
        
        metrics.overall_score = sum(dimension_scores)
        
        # Store assessment in history
        self.assessment_history.append({
            'timestamp': datetime.now(),
            'dataframe_shape': df.shape,
            'quality_metrics': metrics,
            'overall_score': metrics.overall_score
        })
        
        logger.info(f"Quality assessment completed. Overall score: {metrics.overall_score:.3f}")
        
        return metrics
    
    def _get_quality_grade(self, score: float) -> str:
        """
        Convert quality score to letter grade.
        
        Args:
            score: Quality score (0-1)
            
        Returns:
            Letter grade (A, B, C, D, F)
        """
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
    
    def generate_quality_report(self, metrics: QualityMetrics) -> str:
        """
        Generate human-readable quality report.
        
        Args:
            metrics: QualityMetrics object
            
        Returns:
            Formatted quality report string
        """
        report_lines = [
            "=" * 60,
            "DATA QUALITY ASSESSMENT REPORT",
            "=" * 60,
            "",
            f"Overall Quality Score: {metrics.overall_score:.3f} ({self._get_quality_grade(metrics.overall_score)})",
            "",
            "DIMENSION SCORES:",
            f"  Completeness: {metrics.completeness.get('overall_completeness', 0):.3f}",
            f"  Consistency:  {metrics.consistency.get('overall_consistency_score', 0):.3f}",
            f"  Uniqueness:   {metrics.uniqueness.get('uniqueness_score', 0):.3f}",
            f"  Accuracy:     {metrics.accuracy.get('overall_accuracy_score', 0):.3f}",
            f"  Timeliness:   {metrics.timeliness.get('timeliness_score', 0):.3f}",
            "",
            "KEY FINDINGS:",
        ]
        
        # Add key findings based on scores
        if metrics.completeness.get('overall_completeness', 0) < 0.8:
            report_lines.append(f"  ⚠️  Low completeness rate: {metrics.completeness.get('overall_completeness', 0):.1%}")
        
        if metrics.uniqueness.get('duplicate_rate', 0) > 0.05:
            report_lines.append(f"  ⚠️  High duplicate rate: {metrics.uniqueness.get('duplicate_rate', 0):.1%}")
        
        if metrics.accuracy.get('overall_accuracy_score', 0) < 0.9:
            report_lines.append(f"  ⚠️  Accuracy issues detected: {metrics.accuracy.get('invalid_value_count', 0)} invalid values")
        
        report_lines.extend([
            "",
            "=" * 60
        ])
        
        return "\n".join(report_lines)
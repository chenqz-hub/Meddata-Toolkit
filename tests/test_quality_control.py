"""
Tests for Quality Control functionality.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from mdip.core.quality_control import QualityAssessment, QualityMetrics


class TestQualityAssessment:
    """Test cases for QualityAssessment class."""
    
    def test_initialization(self):
        """Test QualityAssessment initialization."""
        qa = QualityAssessment()
        
        assert qa is not None
        assert hasattr(qa, 'assessment_history')
        assert isinstance(qa.assessment_history, list)
    
    def test_assess_completeness_basic(self, sample_medical_data):
        """Test basic completeness assessment."""
        qa = QualityAssessment()
        
        completeness = qa.assess_completeness(sample_medical_data)
        
        assert isinstance(completeness, dict)
        assert 'overall_completeness' in completeness
        assert 'field_completeness' in completeness
        
        # Should be high completeness for clean sample data
        assert completeness['overall_completeness'] >= 0.9
    
    def test_assess_completeness_with_missing_data(self, sample_data_with_issues):
        """Test completeness assessment with missing data."""
        qa = QualityAssessment()
        
        completeness = qa.assess_completeness(sample_data_with_issues)
        
        assert isinstance(completeness, dict)
        
        # Should detect missing values
        field_completeness = completeness['field_completeness']
        assert 'cholesterol' in field_completeness
        
        cholesterol_completeness = field_completeness['cholesterol']['rate']
        assert cholesterol_completeness < 1.0  # Has missing values
    
    def test_assess_completeness_critical_fields(self, sample_medical_data):
        """Test completeness assessment with critical fields."""
        qa = QualityAssessment()
        
        critical_fields = ['patient_id', 'name']
        
        completeness = qa.assess_completeness(
            sample_medical_data,
            critical_fields=critical_fields
        )
        
        assert 'critical_completeness' in completeness
        assert completeness['critical_completeness'] >= 0.0
    
    def test_assess_uniqueness_basic(self, sample_medical_data):
        """Test basic uniqueness assessment."""
        qa = QualityAssessment()
        
        uniqueness = qa.assess_uniqueness(sample_medical_data)
        
        assert isinstance(uniqueness, dict)
        assert 'duplicate_rows' in uniqueness
        assert 'duplicate_rate' in uniqueness
        assert 'field_uniqueness' in uniqueness
        
        # Clean sample data should have no duplicates
        assert uniqueness['duplicate_rows'] == 0
        assert uniqueness['duplicate_rate'] == 0.0
    
    def test_assess_uniqueness_with_duplicates(self, sample_data_with_issues):
        """Test uniqueness assessment with duplicates."""
        qa = QualityAssessment()
        
        uniqueness = qa.assess_uniqueness(sample_data_with_issues)
        
        assert isinstance(uniqueness, dict)
        
        # Should detect duplicates
        assert uniqueness['duplicate_rows'] > 0
        assert uniqueness['duplicate_rate'] > 0.0
    
    def test_assess_uniqueness_key_fields(self, sample_data_with_issues):
        """Test uniqueness assessment with key fields."""
        qa = QualityAssessment()
        
        key_fields = ['patient_id']
        
        uniqueness = qa.assess_uniqueness(
            sample_data_with_issues,
            key_fields=key_fields
        )
        
        assert 'key_field_duplicates' in uniqueness
        assert 'patient_id' in uniqueness['key_field_duplicates']
    
    def test_assess_consistency_basic(self, sample_medical_data):
        """Test basic consistency assessment."""
        qa = QualityAssessment()
        
        consistency = qa.assess_consistency(sample_medical_data)
        
        assert isinstance(consistency, dict)
        assert 'data_type_consistency' in consistency
        assert 'format_consistency' in consistency
        assert 'overall_consistency_score' in consistency
    
    def test_assess_accuracy_basic(self, sample_medical_data):
        """Test basic accuracy assessment."""
        qa = QualityAssessment()
        
        accuracy = qa.assess_accuracy(sample_medical_data)
        
        assert isinstance(accuracy, dict)
        assert 'field_accuracy' in accuracy
        assert 'overall_accuracy_score' in accuracy
        assert 'invalid_value_count' in accuracy
        
        # Clean data should have high accuracy
        assert accuracy['overall_accuracy_score'] >= 0.8
    
    def test_assess_accuracy_with_issues(self, sample_data_with_issues):
        """Test accuracy assessment with data issues."""
        qa = QualityAssessment()
        
        accuracy = qa.assess_accuracy(sample_data_with_issues)
        
        assert isinstance(accuracy, dict)
        
        # Should detect accuracy issues
        assert accuracy['invalid_value_count'] > 0
        assert accuracy['overall_accuracy_score'] < 1.0
    
    def test_assess_timeliness_basic(self, sample_medical_data):
        """Test basic timeliness assessment."""
        qa = QualityAssessment()
        
        date_fields = ['admission_date']
        
        timeliness = qa.assess_timeliness(
            sample_medical_data,
            date_fields=date_fields
        )
        
        assert isinstance(timeliness, dict)
        assert 'date_field_analysis' in timeliness
        assert 'timeliness_score' in timeliness
        
        if 'admission_date' in sample_medical_data.columns:
            assert 'admission_date' in timeliness['date_field_analysis']
    
    def test_generate_overall_assessment(self, sample_medical_data):
        """Test comprehensive quality assessment."""
        qa = QualityAssessment()
        
        critical_fields = ['patient_id', 'name']
        important_fields = ['age', 'gender']
        key_fields = ['patient_id']
        date_fields = ['admission_date']
        
        metrics = qa.generate_overall_assessment(
            sample_medical_data,
            critical_fields=critical_fields,
            important_fields=important_fields,
            key_fields=key_fields,
            date_fields=date_fields
        )
        
        assert isinstance(metrics, QualityMetrics)
        assert hasattr(metrics, 'overall_score')
        assert hasattr(metrics, 'completeness')
        assert hasattr(metrics, 'uniqueness')
        assert hasattr(metrics, 'accuracy')
        assert hasattr(metrics, 'consistency')
        assert hasattr(metrics, 'timeliness')
        
        # Overall score should be between 0 and 1
        assert 0 <= metrics.overall_score <= 1
    
    def test_quality_grade_calculation(self):
        """Test quality grade calculation."""
        qa = QualityAssessment()
        
        # Test different score ranges
        assert qa._get_quality_grade(0.95) == 'A'
        assert qa._get_quality_grade(0.85) == 'B'
        assert qa._get_quality_grade(0.75) == 'C'
        assert qa._get_quality_grade(0.65) == 'D'
        assert qa._get_quality_grade(0.55) == 'F'
    
    def test_generate_quality_report(self, sample_medical_data):
        """Test quality report generation."""
        qa = QualityAssessment()
        
        metrics = qa.generate_overall_assessment(sample_medical_data)
        report = qa.generate_quality_report(metrics)
        
        assert isinstance(report, str)
        assert "DATA QUALITY ASSESSMENT REPORT" in report
        assert "Overall Quality Score" in report
        assert "DIMENSION SCORES" in report
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrames."""
        qa = QualityAssessment()
        
        empty_df = pd.DataFrame()
        
        # Should handle empty DataFrames gracefully
        completeness = qa.assess_completeness(empty_df)
        assert completeness['overall_completeness'] == 0
        
        uniqueness = qa.assess_uniqueness(empty_df)
        assert uniqueness['duplicate_rows'] == 0
        
        accuracy = qa.assess_accuracy(empty_df)
        assert accuracy['overall_accuracy_score'] == 0
    
    def test_assessment_history_tracking(self, sample_medical_data):
        """Test that assessment history is properly tracked."""
        qa = QualityAssessment()
        
        initial_history_count = len(qa.assessment_history)
        
        # Perform assessment
        qa.generate_overall_assessment(sample_medical_data)
        
        # Should add to history
        assert len(qa.assessment_history) == initial_history_count + 1
        
        # History entry should contain required fields
        latest_entry = qa.assessment_history[-1]
        assert 'timestamp' in latest_entry
        assert 'dataframe_shape' in latest_entry
        assert 'quality_metrics' in latest_entry
        assert 'overall_score' in latest_entry


class TestQualityMetrics:
    """Test cases for QualityMetrics class."""
    
    def test_initialization(self):
        """Test QualityMetrics initialization."""
        metrics = QualityMetrics()
        
        assert hasattr(metrics, 'completeness')
        assert hasattr(metrics, 'accuracy')
        assert hasattr(metrics, 'consistency')
        assert hasattr(metrics, 'uniqueness')
        assert hasattr(metrics, 'timeliness')
        assert hasattr(metrics, 'overall_score')
        
        assert isinstance(metrics.completeness, dict)
        assert isinstance(metrics.accuracy, dict)
        assert metrics.overall_score == 0.0
    
    def test_to_dict_conversion(self):
        """Test conversion of metrics to dictionary."""
        metrics = QualityMetrics()
        
        # Set some test values
        metrics.overall_score = 0.85
        metrics.completeness = {'overall_completeness': 0.9}
        metrics.accuracy = {'overall_accuracy_score': 0.8}
        
        metrics_dict = metrics.to_dict()
        
        assert isinstance(metrics_dict, dict)
        assert 'overall_score' in metrics_dict
        assert 'completeness' in metrics_dict
        assert 'accuracy' in metrics_dict
        
        assert metrics_dict['overall_score'] == 0.85
        assert metrics_dict['completeness']['overall_completeness'] == 0.9


class TestQualityAssessmentIntegration:
    """Integration tests for quality assessment functionality."""
    
    def test_end_to_end_quality_assessment(self, sample_data_with_issues):
        """Test complete quality assessment workflow."""
        qa = QualityAssessment()
        
        # Perform comprehensive assessment
        metrics = qa.generate_overall_assessment(
            sample_data_with_issues,
            critical_fields=['patient_id', 'name'],
            key_fields=['patient_id']
        )
        
        # Verify all components are assessed
        assert metrics.overall_score > 0
        assert metrics.completeness
        assert metrics.uniqueness
        assert metrics.accuracy
        assert metrics.consistency
        
        # Should detect the issues we introduced
        assert metrics.uniqueness['duplicate_rate'] > 0
        assert metrics.accuracy['invalid_value_count'] > 0
        
        # Generate report
        report = qa.generate_quality_report(metrics)
        assert isinstance(report, str)
        assert len(report) > 0
    
    def test_comparative_quality_assessment(self, sample_medical_data, sample_data_with_issues):
        """Test comparing quality between clean and problematic data."""
        qa = QualityAssessment()
        
        # Assess clean data
        clean_metrics = qa.generate_overall_assessment(sample_medical_data)
        
        # Assess problematic data
        problem_metrics = qa.generate_overall_assessment(sample_data_with_issues)
        
        # Clean data should have better quality scores
        assert clean_metrics.overall_score > problem_metrics.overall_score
        assert clean_metrics.uniqueness['duplicate_rate'] <= problem_metrics.uniqueness['duplicate_rate']
        assert clean_metrics.accuracy['overall_accuracy_score'] >= problem_metrics.accuracy['overall_accuracy_score']
    
    def test_quality_assessment_performance(self, sample_medical_data):
        """Test performance of quality assessment on larger datasets."""
        # Create larger dataset
        large_df = pd.concat([sample_medical_data] * 10, ignore_index=True)
        
        qa = QualityAssessment()
        
        import time
        start_time = time.time()
        
        metrics = qa.generate_overall_assessment(large_df)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete in reasonable time (adjust threshold as needed)
        assert execution_time < 30  # seconds
        assert metrics.overall_score > 0
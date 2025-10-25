"""
Tests for DataMatcher core functionality.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from mdip.core.matcher import DataMatcher
from mdip.config.field_config import FieldConfig
from mdip.config.match_config import MatchConfig


class TestDataMatcher:
    """Test cases for DataMatcher class."""
    
    def test_initialization(self):
        """Test DataMatcher initialization."""
        matcher = DataMatcher()
        
        assert matcher is not None
        assert hasattr(matcher, 'field_config')
        assert hasattr(matcher, 'match_config')
    
    def test_discover_excel_files(self, temp_directory, sample_excel_file):
        """Test Excel file discovery."""
        # Copy sample file to temp directory
        import shutil
        temp_file = Path(temp_directory) / "test_data.xlsx"
        shutil.copy2(sample_excel_file, temp_file)
        
        matcher = DataMatcher()
        file_registry = matcher.discover_excel_files(temp_directory)
        
        assert isinstance(file_registry, dict)
        assert len(file_registry) >= 1
        
        # Check that our test file is found
        found_files = [info['filename'] for info in file_registry.values()]
        assert "test_data.xlsx" in found_files
    
    def test_analyze_excel_structure(self, sample_excel_file):
        """Test Excel structure analysis."""
        matcher = DataMatcher()
        analysis = matcher.analyze_excel_structure(sample_excel_file)
        
        assert isinstance(analysis, dict)
        assert 'sheets' in analysis
        assert 'total_fields' in analysis
        
        # Check for expected sheets
        assert 'Patients' in analysis['sheets']
        assert 'Lab_Results' in analysis['sheets']
        
        # Check field counts
        assert analysis['total_fields'] > 0
        
        # Check sheet details
        patients_sheet = analysis['sheets']['Patients']
        assert 'headers' in patients_sheet
        assert len(patients_sheet['headers']) > 0
    
    def test_load_dataframe_excel(self, sample_excel_file):
        """Test loading DataFrame from Excel file."""
        matcher = DataMatcher()
        
        # Load first sheet
        df = matcher.load_dataframe(sample_excel_file, sheet_name='Patients')
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'patient_id' in df.columns
        assert 'name' in df.columns
    
    def test_load_dataframe_csv(self, sample_csv_file):
        """Test loading DataFrame from CSV file."""
        matcher = DataMatcher()
        
        df = matcher.load_dataframe(sample_csv_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'patient_id' in df.columns
    
    def test_prepare_matching_fields(self, sample_medical_data):
        """Test matching field preparation."""
        matcher = DataMatcher()
        
        matching_fields = ['patient_id', 'name']
        prepared_df = matcher.prepare_matching_fields(sample_medical_data, matching_fields)
        
        assert isinstance(prepared_df, pd.DataFrame)
        assert len(prepared_df) == len(sample_medical_data)
        
        # Check that matching fields are prepared
        for field in matching_fields:
            if field in sample_medical_data.columns:
                assert field in prepared_df.columns
    
    def test_find_exact_matches(self):
        """Test exact matching functionality."""
        # Create test data with known matches
        df1 = pd.DataFrame({
            'patient_id': ['P001', 'P002', 'P003'],
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'age': [65, 45, 55]
        })
        
        df2 = pd.DataFrame({
            'patient_id': ['P001', 'P002', 'P004'],
            'name': ['John Doe', 'Jane Smith', 'Alice Brown'],
            'diagnosis': ['CAD', 'MI', 'Angina']
        })
        
        matcher = DataMatcher()
        
        matches = matcher.find_exact_matches(df1, df2, ['patient_id'])
        
        assert isinstance(matches, pd.DataFrame)
        assert len(matches) == 2  # P001 and P002 should match
        assert 'P001' in matches['patient_id'].values
        assert 'P002' in matches['patient_id'].values
    
    def test_find_fuzzy_matches(self):
        """Test fuzzy matching functionality."""
        # Create test data with slight variations
        df1 = pd.DataFrame({
            'patient_id': ['P001', 'P002'],
            'name': ['John Doe', 'Jane Smith']
        })
        
        df2 = pd.DataFrame({
            'patient_id': ['P001', 'P002'],
            'name': ['John  Doe', 'Jane Smith ']  # Extra spaces
        })
        
        matcher = DataMatcher()
        
        matches = matcher.find_fuzzy_matches(
            df1, df2, ['name'], similarity_threshold=0.8
        )
        
        assert isinstance(matches, pd.DataFrame)
        assert len(matches) >= 1  # Should find at least some matches
    
    def test_calculate_match_confidence(self):
        """Test match confidence calculation."""
        record1 = {
            'patient_id': 'P001',
            'name': 'John Doe',
            'age': 65
        }
        
        record2 = {
            'patient_id': 'P001',
            'name': 'John Doe',
            'age': 65
        }
        
        matcher = DataMatcher()
        
        confidence = matcher.calculate_match_confidence(
            record1, record2, ['patient_id', 'name']
        )
        
        assert isinstance(confidence, (int, float))
        assert 0 <= confidence <= 1
        assert confidence == 1.0  # Perfect match
    
    def test_integration_workflow(self, sample_medical_data):
        """Test complete integration workflow."""
        # Create two related datasets
        df1 = sample_medical_data[['patient_id', 'name', 'age', 'gender']].copy()
        df2 = sample_medical_data[['patient_id', 'diagnosis', 'cholesterol']].copy()
        
        # Add some noise to make it more realistic
        df2.loc[5:9, 'patient_id'] = df2.loc[5:9, 'patient_id'] + '_MOD'
        
        matcher = DataMatcher()
        
        # Test the integration process
        try:
            matches = matcher.find_exact_matches(df1, df2, ['patient_id'])
            assert isinstance(matches, pd.DataFrame)
            
            # Should have fewer matches due to modified IDs
            assert len(matches) < len(df1)
            
        except Exception as e:
            pytest.fail(f"Integration workflow failed: {str(e)}")
    
    def test_error_handling_invalid_file(self):
        """Test error handling for invalid files."""
        matcher = DataMatcher()
        
        with pytest.raises((FileNotFoundError, Exception)):
            matcher.load_dataframe("nonexistent_file.xlsx")
    
    def test_error_handling_invalid_sheet(self, sample_excel_file):
        """Test error handling for invalid sheet names."""
        matcher = DataMatcher()
        
        with pytest.raises((ValueError, KeyError, Exception)):
            matcher.load_dataframe(sample_excel_file, sheet_name='NonexistentSheet')
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrames."""
        matcher = DataMatcher()
        
        empty_df = pd.DataFrame()
        result = matcher.prepare_matching_fields(empty_df, ['patient_id'])
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_missing_columns_handling(self, sample_medical_data):
        """Test handling of missing columns."""
        matcher = DataMatcher()
        
        # Try to match on non-existent columns
        result = matcher.prepare_matching_fields(
            sample_medical_data, 
            ['nonexistent_column']
        )
        
        assert isinstance(result, pd.DataFrame)
        # Should handle gracefully without crashing


class TestDataMatcherConfiguration:
    """Test DataMatcher configuration and customization."""
    
    def test_custom_field_config(self):
        """Test using custom field configuration."""
        custom_config = FieldConfig()
        custom_config.add_field_group("test_group", ["test_field1", "test_field2"])
        
        matcher = DataMatcher(field_config=custom_config)
        
        assert matcher.field_config == custom_config
        assert "test_group" in matcher.field_config.field_groups
    
    def test_custom_match_config(self):
        """Test using custom match configuration."""
        custom_config = MatchConfig()
        custom_config.fuzzy_threshold = 0.7
        custom_config.exact_match_fields = ["custom_id"]
        
        matcher = DataMatcher(match_config=custom_config)
        
        assert matcher.match_config == custom_config
        assert matcher.match_config.fuzzy_threshold == 0.7
    
    def test_configuration_integration(self):
        """Test integration of custom configurations."""
        field_config = FieldConfig()
        field_config.add_field_group("identifiers", ["id", "patient_id"])
        
        match_config = MatchConfig()
        match_config.exact_match_fields = ["id", "patient_id"]
        match_config.fuzzy_match_fields = ["name"]
        
        matcher = DataMatcher(
            field_config=field_config,
            match_config=match_config
        )
        
        assert "identifiers" in matcher.field_config.field_groups
        assert "name" in matcher.match_config.fuzzy_match_fields
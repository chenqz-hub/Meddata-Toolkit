"""
Test Configuration for MDIP

This module contains test configuration and utilities.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os


@pytest.fixture
def sample_medical_data():
    """Create sample medical data for testing."""
    np.random.seed(42)
    n_patients = 100
    
    data = {
        'patient_id': [f'P{i:04d}' for i in range(n_patients)],
        'name': [f'Patient_{i}' for i in range(n_patients)],
        'age': np.random.randint(18, 90, n_patients),
        'gender': np.random.choice(['M', 'F'], n_patients),
        'admission_date': pd.date_range('2020-01-01', periods=n_patients, freq='D'),
        'cholesterol': np.random.normal(200, 50, n_patients),
        'systolic_bp': np.random.normal(140, 20, n_patients),
        'diastolic_bp': np.random.normal(90, 10, n_patients),
        'diagnosis': np.random.choice(['CAD', 'MI', 'Angina'], n_patients)
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_excel_file(sample_medical_data, tmp_path):
    """Create a temporary Excel file with sample data."""
    file_path = tmp_path / "sample_data.xlsx"
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        sample_medical_data.to_excel(writer, sheet_name='Patients', index=False)
        
        # Add a second sheet with different data
        lab_data = pd.DataFrame({
            'patient_id': sample_medical_data['patient_id'][:50],
            'test_date': pd.date_range('2020-01-01', periods=50, freq='D'),
            'glucose': np.random.normal(100, 20, 50),
            'creatinine': np.random.normal(1.0, 0.3, 50)
        })
        lab_data.to_excel(writer, sheet_name='Lab_Results', index=False)
    
    return str(file_path)


@pytest.fixture
def sample_csv_file(sample_medical_data, tmp_path):
    """Create a temporary CSV file with sample data."""
    file_path = tmp_path / "sample_data.csv"
    sample_medical_data.to_csv(file_path, index=False)
    return str(file_path)


@pytest.fixture
def sample_data_with_issues():
    """Create sample data with known quality issues."""
    np.random.seed(42)
    n_records = 50
    
    data = {
        'patient_id': [f'P{i:04d}' for i in range(n_records)],
        'name': [f'Patient_{i}' for i in range(n_records)],
        'age': np.random.randint(18, 90, n_records),
        'cholesterol': np.random.normal(200, 50, n_records)
    }
    
    df = pd.DataFrame(data)
    
    # Introduce quality issues
    # 1. Missing values
    df.loc[5:9, 'cholesterol'] = np.nan
    
    # 2. Duplicates
    df.loc[15] = df.loc[10].copy()
    df.loc[16] = df.loc[11].copy()
    
    # 3. Invalid values
    df.loc[20, 'age'] = -5  # Invalid age
    df.loc[21, 'cholesterol'] = 999999  # Extreme outlier
    
    # 4. Inconsistent formats
    df.loc[25, 'name'] = '  Patient_25  '  # Extra spaces
    
    return df


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestConfig:
    """Test configuration constants."""
    
    # Test data parameters
    DEFAULT_SAMPLE_SIZE = 100
    SMALL_SAMPLE_SIZE = 10
    LARGE_SAMPLE_SIZE = 1000
    
    # Quality thresholds for testing
    MIN_COMPLETENESS_THRESHOLD = 0.8
    MIN_ACCURACY_THRESHOLD = 0.9
    MAX_DUPLICATE_RATE = 0.05
    
    # Field categories for testing
    CRITICAL_FIELDS = ['patient_id', 'name']
    IMPORTANT_FIELDS = ['age', 'gender', 'admission_date']
    OPTIONAL_FIELDS = ['diagnosis', 'notes']
    
    # File formats for testing
    SUPPORTED_FORMATS = ['.xlsx', '.xls', '.csv']
    
    # Expected columns in test data
    EXPECTED_PATIENT_COLUMNS = [
        'patient_id', 'name', 'age', 'gender', 'admission_date',
        'cholesterol', 'systolic_bp', 'diastolic_bp', 'diagnosis'
    ]
    
    EXPECTED_LAB_COLUMNS = [
        'patient_id', 'test_date', 'glucose', 'creatinine'
    ]
"""
Data Validation Module

Comprehensive validation functions for data quality and integrity checks.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, date
import re
import logging

logger = logging.getLogger(__name__)


class ValidationRule:
    """Base class for validation rules."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize validation rule.
        
        Args:
            name: Rule name
            description: Rule description
        """
        self.name = name
        self.description = description
    
    def validate(self, data: Any) -> Tuple[bool, str]:
        """
        Validate data against rule.
        
        Args:
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        raise NotImplementedError


class NumericRangeRule(ValidationRule):
    """Validate numeric values are within specified range."""
    
    def __init__(self, min_val: Optional[float] = None, max_val: Optional[float] = None):
        """
        Initialize numeric range rule.
        
        Args:
            min_val: Minimum allowed value
            max_val: Maximum allowed value
        """
        super().__init__(
            "numeric_range",
            f"Value must be between {min_val} and {max_val}"
        )
        self.min_val = min_val
        self.max_val = max_val
    
    def validate(self, data: Any) -> Tuple[bool, str]:
        """Validate numeric range."""
        if pd.isna(data):
            return True, ""
        
        try:
            value = float(data)
            
            if self.min_val is not None and value < self.min_val:
                return False, f"Value {value} is below minimum {self.min_val}"
            
            if self.max_val is not None and value > self.max_val:
                return False, f"Value {value} is above maximum {self.max_val}"
            
            return True, ""
        
        except (ValueError, TypeError):
            return False, f"Value {data} is not numeric"


class DateRangeRule(ValidationRule):
    """Validate dates are within specified range."""
    
    def __init__(
        self,
        min_date: Optional[Union[str, datetime, date]] = None,
        max_date: Optional[Union[str, datetime, date]] = None,
        date_format: str = '%Y-%m-%d'
    ):
        """
        Initialize date range rule.
        
        Args:
            min_date: Minimum allowed date
            max_date: Maximum allowed date
            date_format: Expected date format
        """
        super().__init__(
            "date_range",
            f"Date must be between {min_date} and {max_date}"
        )
        self.min_date = self._parse_date(min_date, date_format)
        self.max_date = self._parse_date(max_date, date_format)
        self.date_format = date_format
    
    def _parse_date(self, date_val: Any, date_format: str) -> Optional[datetime]:
        """Parse date from various formats."""
        if date_val is None:
            return None
        
        if isinstance(date_val, datetime):
            return date_val
        
        if isinstance(date_val, date):
            return datetime.combine(date_val, datetime.min.time())
        
        if isinstance(date_val, str):
            try:
                return datetime.strptime(date_val, date_format)
            except ValueError:
                return None
        
        return None
    
    def validate(self, data: Any) -> Tuple[bool, str]:
        """Validate date range."""
        if pd.isna(data):
            return True, ""
        
        parsed_date = self._parse_date(data, self.date_format)
        
        if parsed_date is None:
            return False, f"Invalid date format: {data}"
        
        if self.min_date and parsed_date < self.min_date:
            return False, f"Date {parsed_date} is before minimum {self.min_date}"
        
        if self.max_date and parsed_date > self.max_date:
            return False, f"Date {parsed_date} is after maximum {self.max_date}"
        
        return True, ""


class PatternRule(ValidationRule):
    """Validate values match a regular expression pattern."""
    
    def __init__(self, pattern: str, description: str = ""):
        """
        Initialize pattern rule.
        
        Args:
            pattern: Regular expression pattern
            description: Human-readable description
        """
        super().__init__(
            "pattern_match",
            description or f"Value must match pattern: {pattern}"
        )
        self.pattern = re.compile(pattern)
    
    def validate(self, data: Any) -> Tuple[bool, str]:
        """Validate pattern match."""
        if pd.isna(data):
            return True, ""
        
        try:
            str_data = str(data)
            if self.pattern.match(str_data):
                return True, ""
            else:
                return False, f"Value '{str_data}' does not match required pattern"
        
        except Exception as e:
            return False, f"Error validating pattern: {str(e)}"


class RequiredFieldRule(ValidationRule):
    """Validate that required fields are not empty."""
    
    def __init__(self):
        """Initialize required field rule."""
        super().__init__(
            "required_field",
            "Field is required and cannot be empty"
        )
    
    def validate(self, data: Any) -> Tuple[bool, str]:
        """Validate field is not empty."""
        if pd.isna(data):
            return False, "Required field is missing"
        
        if isinstance(data, str) and data.strip() == "":
            return False, "Required field is empty"
        
        return True, ""


class UniqueValueRule(ValidationRule):
    """Validate values are unique within a dataset."""
    
    def __init__(self, existing_values: set):
        """
        Initialize unique value rule.
        
        Args:
            existing_values: Set of existing values to check against
        """
        super().__init__(
            "unique_value",
            "Value must be unique"
        )
        self.existing_values = existing_values
    
    def validate(self, data: Any) -> Tuple[bool, str]:
        """Validate value uniqueness."""
        if pd.isna(data):
            return True, ""
        
        if data in self.existing_values:
            return False, f"Duplicate value: {data}"
        
        return True, ""


class DataValidator:
    """Main data validation class."""
    
    def __init__(self):
        """Initialize data validator."""
        self.rules: Dict[str, List[ValidationRule]] = {}
        self.validation_history: List[Dict] = []
    
    def add_rule(self, field_name: str, rule: ValidationRule):
        """
        Add validation rule for a field.
        
        Args:
            field_name: Name of the field to validate
            rule: ValidationRule instance
        """
        if field_name not in self.rules:
            self.rules[field_name] = []
        self.rules[field_name].append(rule)
    
    def add_numeric_range_rule(
        self,
        field_name: str,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ):
        """Add numeric range validation rule."""
        rule = NumericRangeRule(min_val, max_val)
        self.add_rule(field_name, rule)
    
    def add_date_range_rule(
        self,
        field_name: str,
        min_date: Optional[str] = None,
        max_date: Optional[str] = None,
        date_format: str = '%Y-%m-%d'
    ):
        """Add date range validation rule."""
        rule = DateRangeRule(min_date, max_date, date_format)
        self.add_rule(field_name, rule)
    
    def add_pattern_rule(self, field_name: str, pattern: str, description: str = ""):
        """Add pattern validation rule."""
        rule = PatternRule(pattern, description)
        self.add_rule(field_name, rule)
    
    def add_required_rule(self, field_name: str):
        """Add required field validation rule."""
        rule = RequiredFieldRule()
        self.add_rule(field_name, rule)
    
    def validate_dataframe(
        self,
        df: pd.DataFrame,
        return_details: bool = False
    ) -> Union[bool, Dict[str, Any]]:
        """
        Validate entire DataFrame.
        
        Args:
            df: DataFrame to validate
            return_details: Whether to return detailed results
            
        Returns:
            Boolean or detailed validation results
        """
        validation_results = {
            'is_valid': True,
            'total_errors': 0,
            'field_errors': {},
            'row_errors': {},
            'summary': {}
        }
        
        for field_name, rules in self.rules.items():
            if field_name not in df.columns:
                validation_results['field_errors'][field_name] = [
                    f"Field '{field_name}' not found in DataFrame"
                ]
                validation_results['is_valid'] = False
                continue
            
            field_errors = []
            row_errors = {}
            
            # Validate each value in the field
            for idx, value in df[field_name].items():
                for rule in rules:
                    is_valid, error_message = rule.validate(value)
                    if not is_valid:
                        field_errors.append(f"Row {idx}: {error_message}")
                        if idx not in row_errors:
                            row_errors[idx] = []
                        row_errors[idx].append({
                            'field': field_name,
                            'rule': rule.name,
                            'message': error_message
                        })
                        validation_results['is_valid'] = False
            
            if field_errors:
                validation_results['field_errors'][field_name] = field_errors
                validation_results['total_errors'] += len(field_errors)
            
            # Update row errors
            for row_idx, errors in row_errors.items():
                if row_idx not in validation_results['row_errors']:
                    validation_results['row_errors'][row_idx] = []
                validation_results['row_errors'][row_idx].extend(errors)
        
        # Generate summary
        validation_results['summary'] = {
            'total_rows': len(df),
            'total_fields_validated': len(self.rules),
            'fields_with_errors': len(validation_results['field_errors']),
            'rows_with_errors': len(validation_results['row_errors']),
            'error_rate': validation_results['total_errors'] / (len(df) * len(self.rules)) if len(df) > 0 and len(self.rules) > 0 else 0
        }
        
        # Store in history
        self.validation_history.append({
            'timestamp': datetime.now(),
            'dataframe_shape': df.shape,
            'validation_results': validation_results
        })
        
        if return_details:
            return validation_results
        else:
            return validation_results['is_valid']
    
    def validate_row(self, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single row of data.
        
        Args:
            row_data: Dictionary with field names and values
            
        Returns:
            Validation results for the row
        """
        row_results = {
            'is_valid': True,
            'errors': [],
            'field_errors': {}
        }
        
        for field_name, rules in self.rules.items():
            field_value = row_data.get(field_name)
            field_errors = []
            
            for rule in rules:
                is_valid, error_message = rule.validate(field_value)
                if not is_valid:
                    field_errors.append({
                        'rule': rule.name,
                        'message': error_message
                    })
                    row_results['is_valid'] = False
            
            if field_errors:
                row_results['field_errors'][field_name] = field_errors
                row_results['errors'].extend(field_errors)
        
        return row_results
    
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Generate validation report from history.
        
        Returns:
            Comprehensive validation report
        """
        if not self.validation_history:
            return {'message': 'No validation history available'}
        
        latest_validation = self.validation_history[-1]
        
        report = {
            'validation_summary': latest_validation['validation_results']['summary'],
            'rules_configured': len(self.rules),
            'field_rules': {
                field: [rule.description for rule in rules]
                for field, rules in self.rules.items()
            },
            'validation_history_count': len(self.validation_history),
            'latest_validation': {
                'timestamp': latest_validation['timestamp'].isoformat(),
                'dataframe_shape': latest_validation['dataframe_shape'],
                'is_valid': latest_validation['validation_results']['is_valid']
            }
        }
        
        return report
    
    def clear_rules(self, field_name: Optional[str] = None):
        """
        Clear validation rules.
        
        Args:
            field_name: Specific field to clear rules for, or None to clear all
        """
        if field_name:
            if field_name in self.rules:
                del self.rules[field_name]
        else:
            self.rules.clear()


class MedicalDataValidator(DataValidator):
    """Specialized validator for medical data."""
    
    def __init__(self):
        """Initialize medical data validator with common rules."""
        super().__init__()
        self._add_medical_rules()
    
    def _add_medical_rules(self):
        """Add common medical data validation rules."""
        # Age validation
        self.add_numeric_range_rule('age', min_val=0, max_val=120)
        
        # BMI validation
        self.add_numeric_range_rule('bmi', min_val=10, max_val=80)
        
        # Heart rate validation
        self.add_numeric_range_rule('heart_rate', min_val=20, max_val=300)
        self.add_numeric_range_rule('hr', min_val=20, max_val=300)
        
        # Blood pressure validation
        self.add_numeric_range_rule('systolic_bp', min_val=50, max_val=300)
        self.add_numeric_range_rule('diastolic_bp', min_val=30, max_val=200)
        self.add_numeric_range_rule('sbp', min_val=50, max_val=300)
        self.add_numeric_range_rule('dbp', min_val=30, max_val=200)
        
        # Laboratory values (common ranges)
        self.add_numeric_range_rule('cholesterol', min_val=50, max_val=1000)
        self.add_numeric_range_rule('ldl', min_val=20, max_val=500)
        self.add_numeric_range_rule('hdl', min_val=10, max_val=200)
        self.add_numeric_range_rule('triglycerides', min_val=20, max_val=2000)
        self.add_numeric_range_rule('glucose', min_val=20, max_val=1000)
        self.add_numeric_range_rule('creatinine', min_val=0.1, max_val=20)
        
        # Date patterns for medical records
        self.add_pattern_rule(
            'patient_id',
            r'^[A-Za-z0-9\-_]+$',
            'Patient ID should contain only alphanumeric characters, hyphens, and underscores'
        )
    
    def add_ejection_fraction_rule(self, field_name: str = 'ejection_fraction'):
        """Add ejection fraction validation rule (0-100%)."""
        self.add_numeric_range_rule(field_name, min_val=0, max_val=100)
    
    def add_procedure_date_rule(
        self,
        field_name: str,
        min_year: int = 1990,
        max_year: Optional[int] = None
    ):
        """
        Add procedure date validation rule.
        
        Args:
            field_name: Name of the date field
            min_year: Minimum allowed year
            max_year: Maximum allowed year (defaults to current year)
        """
        if max_year is None:
            max_year = datetime.now().year
        
        min_date = f"{min_year}-01-01"
        max_date = f"{max_year}-12-31"
        
        self.add_date_range_rule(field_name, min_date, max_date)
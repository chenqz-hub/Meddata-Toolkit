"""
Data Processing Utilities

Common data processing and transformation functions.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import pandas as pd
import numpy as np
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Utility class for data processing operations."""
    
    def __init__(self):
        """Initialize the data processor."""
        self.date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d', 
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S'
        ]
    
    def clean_basic_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply basic data cleaning operations.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        cleaned_df = df.copy()
        
        # Remove completely empty rows
        cleaned_df = cleaned_df.dropna(how='all')
        
        # Strip whitespace from string columns
        string_columns = cleaned_df.select_dtypes(include=['object']).columns
        for col in string_columns:
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
            # Replace empty strings with NaN
            cleaned_df[col] = cleaned_df[col].replace('', np.nan)
        
        # Clean numeric columns
        numeric_columns = cleaned_df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            # Remove infinite values
            cleaned_df[col] = cleaned_df[col].replace([np.inf, -np.inf], np.nan)
        
        logger.info(f"Basic cleaning completed. Shape: {cleaned_df.shape}")
        return cleaned_df
    
    def standardize_id_fields(self, df: pd.DataFrame, id_columns: List[str]) -> pd.DataFrame:
        """
        Standardize ID field formats.
        
        Args:
            df: Input DataFrame
            id_columns: List of ID column names
            
        Returns:
            DataFrame with standardized ID fields
        """
        result_df = df.copy()
        
        for col in id_columns:
            if col in result_df.columns:
                # Convert to string and clean
                result_df[col] = result_df[col].astype(str)
                result_df[col] = result_df[col].str.strip()
                result_df[col] = result_df[col].str.upper()
                
                # Remove special characters except letters, numbers, and hyphens
                result_df[col] = result_df[col].str.replace(r'[^\w\-]', '', regex=True)
                
                # Replace 'nan' string with actual NaN
                result_df[col] = result_df[col].replace(['nan', 'NAN', 'None'], np.nan)
        
        return result_df
    
    def standardize_names(self, df: pd.DataFrame, name_columns: List[str]) -> pd.DataFrame:
        """
        Standardize name field formats for better matching.
        
        Args:
            df: Input DataFrame
            name_columns: List of name column names
            
        Returns:
            DataFrame with standardized name fields
        """
        result_df = df.copy()
        
        for col in name_columns:
            if col in result_df.columns:
                # Convert to string and basic cleaning
                result_df[col] = result_df[col].astype(str)
                result_df[col] = result_df[col].str.strip()
                
                # Remove extra spaces
                result_df[col] = result_df[col].str.replace(r'\s+', ' ', regex=True)
                
                # Standardize case (you might want to adjust based on language)
                result_df[col] = result_df[col].str.title()
                
                # Replace 'nan' string with actual NaN
                result_df[col] = result_df[col].replace(['nan', 'NAN', 'None'], np.nan)
        
        return result_df
    
    def convert_date_columns(
        self,
        df: pd.DataFrame,
        date_columns: List[str],
        target_format: str = '%Y-%m-%d'
    ) -> pd.DataFrame:
        """
        Convert date columns to standard format.
        
        Args:
            df: Input DataFrame
            date_columns: List of date column names
            target_format: Target date format
            
        Returns:
            DataFrame with converted date columns
        """
        result_df = df.copy()
        
        for col in date_columns:
            if col not in result_df.columns:
                continue
                
            # Try to parse dates using multiple formats
            parsed_dates = pd.Series(index=result_df.index, dtype='datetime64[ns]')
            
            for date_format in self.date_formats:
                try:
                    # Try parsing with current format
                    mask = parsed_dates.isna()
                    if mask.any():
                        temp_dates = pd.to_datetime(
                            result_df.loc[mask, col],
                            format=date_format,
                            errors='coerce'
                        )
                        parsed_dates.loc[mask] = temp_dates
                except:
                    continue
            
            # Convert to target format
            if not parsed_dates.isna().all():
                result_df[col] = parsed_dates.dt.strftime(target_format)
            
        return result_df
    
    def normalize_numeric_columns(
        self,
        df: pd.DataFrame,
        columns: List[str],
        method: str = 'minmax'
    ) -> pd.DataFrame:
        """
        Normalize numeric columns.
        
        Args:
            df: Input DataFrame
            columns: List of numeric column names
            method: Normalization method ('minmax', 'zscore')
            
        Returns:
            DataFrame with normalized columns
        """
        result_df = df.copy()
        
        for col in columns:
            if col not in result_df.columns:
                continue
                
            if not pd.api.types.is_numeric_dtype(result_df[col]):
                continue
            
            if method == 'minmax':
                # Min-max normalization
                min_val = result_df[col].min()
                max_val = result_df[col].max()
                if max_val != min_val:
                    result_df[col] = (result_df[col] - min_val) / (max_val - min_val)
            
            elif method == 'zscore':
                # Z-score normalization
                mean_val = result_df[col].mean()
                std_val = result_df[col].std()
                if std_val != 0:
                    result_df[col] = (result_df[col] - mean_val) / std_val
        
        return result_df
    
    def detect_and_convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Automatically detect and convert column data types.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with optimized data types
        """
        result_df = df.copy()
        
        for col in result_df.columns:
            # Skip if already datetime
            if pd.api.types.is_datetime64_any_dtype(result_df[col]):
                continue
            
            # Try to convert to numeric
            if result_df[col].dtype == 'object':
                # Try numeric conversion
                numeric_converted = pd.to_numeric(result_df[col], errors='coerce')
                if not numeric_converted.isna().all():
                    # If more than 70% of values can be converted to numeric
                    conversion_rate = (1 - numeric_converted.isna().mean())
                    if conversion_rate > 0.7:
                        result_df[col] = numeric_converted
                        continue
                
                # Try datetime conversion
                try:
                    datetime_converted = pd.to_datetime(result_df[col], errors='coerce')
                    if not datetime_converted.isna().all():
                        conversion_rate = (1 - datetime_converted.isna().mean())
                        if conversion_rate > 0.7:
                            result_df[col] = datetime_converted
                            continue
                except:
                    pass
        
        return result_df
    
    def create_composite_key(
        self,
        df: pd.DataFrame,
        key_columns: List[str],
        separator: str = '|'
    ) -> pd.Series:
        """
        Create composite key from multiple columns.
        
        Args:
            df: Input DataFrame
            key_columns: List of columns to combine
            separator: Separator character
            
        Returns:
            Series with composite keys
        """
        available_columns = [col for col in key_columns if col in df.columns]
        
        if not available_columns:
            return pd.Series(index=df.index, dtype='object')
        
        # Fill NaN values with empty string for key creation
        key_parts = df[available_columns].fillna('').astype(str)
        
        # Create composite key
        composite_key = key_parts.apply(lambda x: separator.join(x), axis=1)
        
        # Replace keys that are only separators with NaN
        empty_pattern = f"^{re.escape(separator)}*$"
        composite_key = composite_key.replace(empty_pattern, np.nan, regex=True)
        
        return composite_key
    
    def calculate_completeness_score(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        """
        Calculate data completeness score for each row.
        
        Args:
            df: Input DataFrame
            columns: List of columns to consider
            
        Returns:
            Series with completeness scores (0-1)
        """
        available_columns = [col for col in columns if col in df.columns]
        
        if not available_columns:
            return pd.Series(0, index=df.index)
        
        # Calculate completeness for each row
        completeness = df[available_columns].notna().sum(axis=1) / len(available_columns)
        
        return completeness
    
    def remove_duplicates_advanced(
        self,
        df: pd.DataFrame,
        key_columns: List[str],
        keep: str = 'first',
        similarity_threshold: float = 0.95
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Remove duplicates with advanced detection.
        
        Args:
            df: Input DataFrame
            key_columns: Columns to use for duplicate detection
            keep: Which duplicate to keep ('first', 'last', 'none')
            similarity_threshold: Similarity threshold for fuzzy duplicates
            
        Returns:
            Tuple of (cleaned DataFrame, duplicates DataFrame)
        """
        # First, handle exact duplicates
        duplicates_mask = df.duplicated(subset=key_columns, keep=False)
        exact_duplicates = df[duplicates_mask].copy()
        
        if keep == 'none':
            clean_df = df[~duplicates_mask].copy()
        else:
            clean_df = df.drop_duplicates(subset=key_columns, keep=keep)
        
        return clean_df, exact_duplicates


class FieldAnalyzer:
    """Analyze field characteristics and suggest optimal processing."""
    
    def __init__(self):
        """Initialize field analyzer."""
        pass
    
    def analyze_field_quality(self, series: pd.Series) -> Dict[str, Any]:
        """
        Analyze quality metrics for a single field.
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            Dictionary with quality metrics
        """
        total_count = len(series)
        non_null_count = series.notna().sum()
        null_count = series.isna().sum()
        
        quality_metrics = {
            'total_count': total_count,
            'non_null_count': non_null_count,
            'null_count': null_count,
            'completeness_rate': non_null_count / total_count if total_count > 0 else 0,
            'data_type': str(series.dtype),
            'unique_count': series.nunique(),
            'uniqueness_rate': series.nunique() / non_null_count if non_null_count > 0 else 0
        }
        
        # Add type-specific metrics
        if pd.api.types.is_numeric_dtype(series):
            quality_metrics.update({
                'mean': series.mean(),
                'median': series.median(),
                'std': series.std(),
                'min': series.min(),
                'max': series.max(),
                'outlier_count': self._count_outliers(series)
            })
        
        elif pd.api.types.is_string_dtype(series) or series.dtype == 'object':
            quality_metrics.update({
                'avg_length': series.astype(str).str.len().mean(),
                'max_length': series.astype(str).str.len().max(),
                'empty_string_count': (series == '').sum(),
                'whitespace_only_count': series.astype(str).str.strip().eq('').sum()
            })
        
        return quality_metrics
    
    def _count_outliers(self, series: pd.Series, method: str = 'iqr') -> int:
        """Count outliers in a numeric series."""
        if not pd.api.types.is_numeric_dtype(series):
            return 0
        
        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = (series < lower_bound) | (series > upper_bound)
            return outliers.sum()
        
        return 0
    
    def suggest_matching_fields(
        self,
        dataframes: Dict[str, pd.DataFrame]
    ) -> Dict[str, List[str]]:
        """
        Suggest potential matching fields across dataframes.
        
        Args:
            dataframes: Dictionary of DataFrames to analyze
            
        Returns:
            Dictionary with suggested matching field categories
        """
        suggestions = {
            'exact_match_candidates': [],
            'fuzzy_match_candidates': [],
            'composite_match_candidates': []
        }
        
        if len(dataframes) < 2:
            return suggestions
        
        # Find common columns
        all_columns = [set(df.columns) for df in dataframes.values()]
        common_columns = set.intersection(*all_columns)
        
        # Analyze each common column
        for col in common_columns:
            # Check if suitable for exact matching (high uniqueness, good completeness)
            uniqueness_rates = []
            completeness_rates = []
            
            for df in dataframes.values():
                quality = self.analyze_field_quality(df[col])
                uniqueness_rates.append(quality['uniqueness_rate'])
                completeness_rates.append(quality['completeness_rate'])
            
            avg_uniqueness = np.mean(uniqueness_rates)
            avg_completeness = np.mean(completeness_rates)
            
            # Categorize based on quality metrics
            if avg_uniqueness > 0.8 and avg_completeness > 0.8:
                suggestions['exact_match_candidates'].append(col)
            elif avg_completeness > 0.6:
                if 'name' in col.lower() or 'patient' in col.lower():
                    suggestions['fuzzy_match_candidates'].append(col)
                else:
                    suggestions['composite_match_candidates'].append(col)
        
        return suggestions
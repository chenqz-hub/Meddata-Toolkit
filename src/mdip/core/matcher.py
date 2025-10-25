"""
Data Matcher Module

Core engine for matching and merging data from multiple sources.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

from ..config.match_config import MatchConfig
from ..config.field_config import FieldConfig
from ..utils.data_utils import DataProcessor
from .validation import DataValidator
from .quality_control import QualityAssessment

logger = logging.getLogger(__name__)


class DataMatcher:
    """
    Main class for data matching and merging operations.
    
    Supports multiple matching strategies:
    - Exact matching by ID fields
    - Fuzzy matching by name similarity
    - Multi-field composite matching
    """
    
    def __init__(
        self,
        field_config: FieldConfig,
        match_config: Optional[MatchConfig] = None,
        quality_controller: Optional[QualityAssessment] = None
    ):
        """
        Initialize the DataMatcher.
        
        Args:
            field_config: Configuration for field mapping and extraction
            match_config: Configuration for matching strategies
            quality_controller: Quality control component
        """
        self.field_config = field_config
        self.match_config = match_config or MatchConfig()
        self.quality_controller = quality_controller or QualityAssessment()
        
        self.data_processor = DataProcessor()
        self.validator = DataValidator()
        
        self.loaded_files: Dict[str, pd.DataFrame] = {}
        self.file_metadata: Dict[str, Dict[str, Any]] = {}
        self.match_results: Optional[pd.DataFrame] = None
        
        logger.info("DataMatcher initialized successfully")
    
    def add_file(
        self,
        file_path: Union[str, Path],
        file_key: str,
        sheet_name: Optional[str] = None,
        file_type: str = "primary",
        group_name: Optional[str] = None
    ) -> None:
        """
        Add a data file to be processed.
        
        Args:
            file_path: Path to the data file
            sheet_name: Name of Excel sheet (if applicable)
            file_key: Unique identifier for this file
            file_type: Type of file ('primary', 'secondary', 'reference')
            group_name: Group identifier (e.g., 'CAG', 'PCI')
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Load data based on file type
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            # Store the data and metadata
            self.loaded_files[file_key] = df
            self.file_metadata[file_key] = {
                'path': str(file_path),
                'sheet_name': sheet_name,
                'file_type': file_type,
                'group_name': group_name,
                'rows': len(df),
                'columns': len(df.columns),
                'loaded_at': datetime.now()
            }
            
            logger.info(f"Loaded file {file_key}: {len(df)} rows, {len(df.columns)} columns")
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {str(e)}")
            raise
    
    def get_file_info(self) -> pd.DataFrame:
        """Get summary information about loaded files."""
        if not self.file_metadata:
            return pd.DataFrame()
        
        info_data = []
        for file_key, metadata in self.file_metadata.items():
            info_data.append({
                'File Key': file_key,
                'Path': metadata['path'],
                'Type': metadata['file_type'],
                'Group': metadata['group_name'],
                'Rows': metadata['rows'],
                'Columns': metadata['columns'],
                'Loaded At': metadata['loaded_at']
            })
        
        return pd.DataFrame(info_data)
    
    def match_and_merge(
        self,
        strategy: str = "auto",
        primary_key: Optional[str] = None,
        output_path: Optional[Union[str, Path]] = None
    ) -> pd.DataFrame:
        """
        Execute the matching and merging process.
        
        Args:
            strategy: Matching strategy ('exact', 'fuzzy', 'composite', 'auto')
            primary_key: Primary matching key (if not using auto-detection)
            output_path: Path to save results (optional)
            
        Returns:
            Merged DataFrame
        """
        if len(self.loaded_files) < 2:
            raise ValueError("At least 2 files required for matching")
        
        logger.info(f"Starting match and merge with strategy: {strategy}")
        
        try:
            # Step 1: Prepare data for matching
            prepared_data = self._prepare_data_for_matching()
            
            # Step 2: Execute matching strategy
            if strategy == "auto":
                strategy = self._detect_best_strategy(prepared_data)
                logger.info(f"Auto-detected strategy: {strategy}")
            
            matched_data = self._execute_matching_strategy(prepared_data, strategy, primary_key)
            
            # Step 3: Quality control
            quality_report = self.quality_controller.assess_match_quality(matched_data)
            
            # Step 4: Apply field configuration
            final_data = self._apply_field_configuration(matched_data)
            
            # Step 5: Save results if path provided
            if output_path:
                self._save_results(final_data, quality_report, output_path)
            
            self.match_results = final_data
            logger.info(f"Matching completed successfully. Final dataset: {len(final_data)} rows")
            
            return final_data
            
        except Exception as e:
            logger.error(f"Error during matching: {str(e)}")
            raise
    
    def _prepare_data_for_matching(self) -> Dict[str, pd.DataFrame]:
        """Prepare loaded data for matching process."""
        prepared = {}
        
        for file_key, df in self.loaded_files.items():
            # Apply basic cleaning
            cleaned_df = self.data_processor.clean_basic_data(df)
            
            # Validate data
            validation_result = self.validator.validate_dataframe(cleaned_df)
            if not validation_result.is_valid:
                logger.warning(f"Data validation issues in {file_key}: {validation_result.errors}")
            
            prepared[file_key] = cleaned_df
        
        return prepared
    
    def _detect_best_strategy(self, data: Dict[str, pd.DataFrame]) -> str:
        """Automatically detect the best matching strategy."""
        # Simple heuristic: check for common ID fields
        common_id_fields = ['subjid', 'patientid', 'patient_id', 'id']
        
        for field in common_id_fields:
            field_found_in_all = all(
                field in df.columns for df in data.values()
            )
            if field_found_in_all:
                # Check data quality of ID field
                id_completeness = min(
                    df[field].notna().mean() for df in data.values()
                )
                if id_completeness > 0.8:  # 80% complete
                    return "exact"
        
        # If no good ID field, try composite matching
        return "composite"
    
    def _execute_matching_strategy(
        self,
        data: Dict[str, pd.DataFrame],
        strategy: str,
        primary_key: Optional[str] = None
    ) -> pd.DataFrame:
        """Execute the specified matching strategy."""
        
        if strategy == "exact":
            return self._exact_matching(data, primary_key)
        elif strategy == "fuzzy":
            return self._fuzzy_matching(data)
        elif strategy == "composite":
            return self._composite_matching(data)
        else:
            raise ValueError(f"Unknown matching strategy: {strategy}")
    
    def _exact_matching(
        self, 
        data: Dict[str, pd.DataFrame], 
        primary_key: Optional[str] = None
    ) -> pd.DataFrame:
        """Perform exact matching based on primary key."""
        
        if primary_key is None:
            # Auto-detect primary key
            common_keys = ['subjid', 'patientid', 'patient_id']
            for key in common_keys:
                if all(key in df.columns for df in data.values()):
                    primary_key = key
                    break
            
            if primary_key is None:
                raise ValueError("No common primary key found for exact matching")
        
        logger.info(f"Performing exact matching on key: {primary_key}")
        
        # Start with first dataset
        file_keys = list(data.keys())
        result_df = data[file_keys[0]].copy()
        result_df['_source_files'] = file_keys[0]
        
        # Merge with subsequent datasets
        for i in range(1, len(file_keys)):
            file_key = file_keys[i]
            df = data[file_key].copy()
            
            # Add source tracking
            df['_source_files'] = file_key
            
            # Perform merge
            result_df = pd.merge(
                result_df, df,
                on=primary_key,
                how='outer',
                suffixes=('', f'_{file_key}')
            )
            
            # Update source tracking
            result_df['_source_files'] = result_df['_source_files'].fillna('') + f';{file_key}'
        
        return result_df
    
    def _fuzzy_matching(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Perform fuzzy matching based on name similarity."""
        # Implementation for fuzzy matching
        # This would use fuzzywuzzy for string similarity
        raise NotImplementedError("Fuzzy matching not yet implemented")
    
    def _composite_matching(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Perform composite matching using multiple fields."""
        # Implementation for composite matching
        # This would use multiple fields with different weights
        raise NotImplementedError("Composite matching not yet implemented")
    
    def _apply_field_configuration(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply field configuration to select and rename columns."""
        if self.field_config is None:
            return data
        
        # Apply field selection and renaming based on configuration
        return self.field_config.apply_to_dataframe(data)
    
    def _save_results(
        self,
        data: pd.DataFrame,
        quality_report: Dict[str, Any],
        output_path: Union[str, Path]
    ) -> None:
        """Save matching results and quality report."""
        output_path = Path(output_path)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main results
            data.to_excel(writer, sheet_name='Merged_Data', index=False)
            
            # Quality report
            if quality_report:
                quality_df = pd.DataFrame([quality_report])
                quality_df.to_excel(writer, sheet_name='Quality_Report', index=False)
            
            # File info
            file_info = self.get_file_info()
            file_info.to_excel(writer, sheet_name='Source_Files', index=False)
        
        logger.info(f"Results saved to: {output_path}")


class MatchResult:
    """Container for matching results and metadata."""
    
    def __init__(
        self,
        data: pd.DataFrame,
        quality_metrics: Dict[str, Any],
        match_strategy: str,
        source_files: List[str]
    ):
        self.data = data
        self.quality_metrics = quality_metrics
        self.match_strategy = match_strategy
        self.source_files = source_files
        self.created_at = datetime.now()
    
    def to_excel(self, output_path: Union[str, Path]) -> None:
        """Save results to Excel file."""
        output_path = Path(output_path)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            self.data.to_excel(writer, sheet_name='Data', index=False)
            
            # Metadata sheet
            metadata = pd.DataFrame([{
                'Match Strategy': self.match_strategy,
                'Source Files': '; '.join(self.source_files),
                'Total Rows': len(self.data),
                'Total Columns': len(self.data.columns),
                'Created At': self.created_at,
                **self.quality_metrics
            }])
            metadata.to_excel(writer, sheet_name='Metadata', index=False)
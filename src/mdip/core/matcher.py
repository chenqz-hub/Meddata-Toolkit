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
        field_config: Optional[FieldConfig] = None,
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
        self.field_config = field_config or FieldConfig()
        self.match_config = match_config or MatchConfig()
        self.quality_controller = quality_controller or QualityAssessment()
        
        self.data_processor = DataProcessor()
        self.validator = DataValidator()
        
        self.loaded_files: Dict[str, pd.DataFrame] = {}
        self.file_metadata: Dict[str, Dict[str, Any]] = {}
        self.match_results: Optional[pd.DataFrame] = None
        
        logger.info("DataMatcher initialized successfully")

    def discover_excel_files(self, directory: Union[str, Path]) -> Dict[str, Dict[str, Any]]:
        """Discover Excel files in a directory and return basic registry info."""
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        files = sorted(list(directory.glob("*.xlsx")) + list(directory.glob("*.xls")))
        file_registry: Dict[str, Dict[str, Any]] = {}
        for index, file_path in enumerate(files):
            file_registry[f"file_{index}"] = {
                "filename": file_path.name,
                "path": str(file_path),
                "size": file_path.stat().st_size,
            }
        return file_registry

    def analyze_excel_structure(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Analyze workbook sheet headers and field counts."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        excel_file = pd.ExcelFile(file_path)
        analysis: Dict[str, Any] = {
            "filename": file_path.name,
            "sheets": {},
            "total_fields": 0,
        }

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)
            headers = list(df.columns)
            analysis["sheets"][sheet_name] = {
                "headers": headers,
                "field_count": len(headers),
            }
            analysis["total_fields"] += len(headers)

        return analysis

    def load_dataframe(
        self,
        file_path: Union[str, Path],
        sheet_name: Optional[Union[str, int]] = None,
    ) -> pd.DataFrame:
        """Load CSV/Excel file into DataFrame."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()
        if suffix == ".csv":
            return pd.read_csv(file_path)
        if suffix in [".xlsx", ".xls"]:
            target_sheet = 0 if sheet_name is None else sheet_name
            return pd.read_excel(file_path, sheet_name=target_sheet)

        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def prepare_matching_fields(
        self,
        df: pd.DataFrame,
        matching_fields: List[str],
    ) -> pd.DataFrame:
        """Prepare fields for matching with normalization and graceful fallback."""
        if df.empty:
            return df.copy()

        result = df.copy()
        for field in matching_fields:
            if field in result.columns:
                series = result[field]
                if series.dtype == "object":
                    result[field] = series.astype(str).str.strip()
        return result

    def find_exact_matches(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        match_fields: List[str],
    ) -> pd.DataFrame:
        """Find exact matches across two DataFrames by specified fields."""
        available_fields = [field for field in match_fields if field in df1.columns and field in df2.columns]
        if not available_fields:
            return pd.DataFrame()

        left = self.prepare_matching_fields(df1, available_fields)
        right = self.prepare_matching_fields(df2, available_fields)
        return pd.merge(left, right, on=available_fields, how="inner")

    def find_fuzzy_matches(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        match_fields: List[str],
        similarity_threshold: float = 0.8,
    ) -> pd.DataFrame:
        """Find fuzzy matches with simple row-wise similarity scoring."""
        available_fields = [field for field in match_fields if field in df1.columns and field in df2.columns]
        if not available_fields:
            return pd.DataFrame()

        if not 0 <= similarity_threshold <= 1:
            raise ValueError("similarity_threshold must be between 0 and 1")

        left = self.prepare_matching_fields(df1, available_fields)
        right = self.prepare_matching_fields(df2, available_fields)

        from fuzzywuzzy import fuzz

        matches: List[Dict[str, Any]] = []
        for _, row_left in left.iterrows():
            best_score = -1
            best_row: Optional[pd.Series] = None
            for _, row_right in right.iterrows():
                scores = [
                    fuzz.ratio(str(row_left[field]), str(row_right[field])) / 100
                    for field in available_fields
                ]
                avg_score = sum(scores) / len(scores)
                if avg_score > best_score:
                    best_score = avg_score
                    best_row = row_right

            if best_row is not None and best_score >= similarity_threshold:
                merged_row = {**row_left.to_dict(), **{f"right_{k}": v for k, v in best_row.to_dict().items()}}
                merged_row["similarity_score"] = best_score
                matches.append(merged_row)

        return pd.DataFrame(matches)

    def calculate_match_confidence(
        self,
        record1: Dict[str, Any],
        record2: Dict[str, Any],
        match_fields: List[str],
    ) -> float:
        """Calculate confidence score between two records based on field equality."""
        valid_fields = [field for field in match_fields if field in record1 and field in record2]
        if not valid_fields:
            return 0.0

        matched = 0
        for field in valid_fields:
            value1 = str(record1[field]).strip() if record1[field] is not None else ""
            value2 = str(record2[field]).strip() if record2[field] is not None else ""
            if value1 == value2:
                matched += 1

        return matched / len(valid_fields)
    
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
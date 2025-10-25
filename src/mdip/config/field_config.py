"""
Field Configuration Module

Manages field selection, mapping, and transformation configurations.
"""

from typing import Dict, List, Optional, Union, Any
import pandas as pd
from dataclasses import dataclass
from pathlib import Path
import yaml
import json


@dataclass
class FieldMapping:
    """Represents a field mapping configuration."""
    source_field: str
    target_field: str
    field_type: str = "string"
    required: bool = False
    default_value: Any = None
    validation_rules: Optional[Dict[str, Any]] = None
    description: str = ""


class FieldConfig:
    """
    Configuration manager for field selection and mapping.
    
    Handles:
    - Field selection from source files
    - Field renaming and mapping
    - Data type conversions
    - Validation rules
    """
    
    def __init__(self, config_data: Optional[Dict[str, Any]] = None):
        """
        Initialize field configuration.
        
        Args:
            config_data: Configuration dictionary
        """
        self.field_mappings: Dict[str, FieldMapping] = {}
        self.selected_fields: List[str] = []
        self.field_categories: Dict[str, List[str]] = {}
        self.priority_levels: Dict[str, int] = {}
        
        if config_data:
            self._load_from_dict(config_data)
    
    @classmethod
    def from_excel(cls, config_path: Union[str, Path], sheet_name: str = "完整字段配置") -> "FieldConfig":
        """
        Load configuration from Excel file.
        
        Args:
            config_path: Path to Excel configuration file
            sheet_name: Name of configuration sheet
            
        Returns:
            FieldConfig instance
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        df = pd.read_excel(config_path, sheet_name=sheet_name)
        
        instance = cls()
        instance._load_from_dataframe(df)
        return instance
    
    @classmethod
    def from_yaml(cls, config_path: Union[str, Path]) -> "FieldConfig":
        """Load configuration from YAML file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        return cls(config_data)
    
    @classmethod
    def from_json(cls, config_path: Union[str, Path]) -> "FieldConfig":
        """Load configuration from JSON file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return cls(config_data)
    
    @classmethod
    def from_template(cls, template_name: str) -> "FieldConfig":
        """
        Create configuration from predefined template.
        
        Available templates:
        - basic_medical_fields: Essential medical data fields
        - extended_clinical: Extended clinical data fields
        - research_complete: Complete research dataset fields
        """
        templates = {
            "basic_medical_fields": {
                "field_mappings": {
                    "patient_id": {
                        "source_field": "subjid",
                        "target_field": "患者ID",
                        "field_type": "string",
                        "required": True,
                        "description": "患者唯一标识符"
                    },
                    "patient_name": {
                        "source_field": "stname", 
                        "target_field": "患者姓名",
                        "field_type": "string",
                        "required": True,
                        "description": "患者姓名"
                    },
                    "gender": {
                        "source_field": "stsex",
                        "target_field": "性别",
                        "field_type": "category",
                        "required": True,
                        "description": "患者性别"
                    },
                    "age": {
                        "source_field": "sys_currentage",
                        "target_field": "年龄",
                        "field_type": "numeric",
                        "required": True,
                        "validation_rules": {"min": 0, "max": 120},
                        "description": "患者年龄"
                    }
                },
                "field_categories": {
                    "基本信息": ["patient_id", "patient_name", "gender", "age"],
                },
                "priority_levels": {
                    "patient_id": 1,
                    "patient_name": 1, 
                    "gender": 1,
                    "age": 1
                }
            }
        }
        
        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        return cls(templates[template_name])
    
    def _load_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Load configuration from dictionary."""
        
        # Load field mappings
        if "field_mappings" in config_data:
            for key, mapping_data in config_data["field_mappings"].items():
                self.field_mappings[key] = FieldMapping(**mapping_data)
        
        # Load field categories
        if "field_categories" in config_data:
            self.field_categories = config_data["field_categories"]
        
        # Load priority levels
        if "priority_levels" in config_data:
            self.priority_levels = config_data["priority_levels"]
        
        # Load selected fields
        if "selected_fields" in config_data:
            self.selected_fields = config_data["selected_fields"]
        else:
            # Default: select all mapped fields
            self.selected_fields = list(self.field_mappings.keys())
    
    def _load_from_dataframe(self, df: pd.DataFrame) -> None:
        """Load configuration from DataFrame (Excel format)."""
        
        # Filter selected fields
        selected_df = df[df["是否选择"].str.upper() == "YES"].copy()
        
        for _, row in selected_df.iterrows():
            field_key = self._generate_field_key(row["字段名称"])
            
            mapping = FieldMapping(
                source_field=row["字段名称"],
                target_field=row.get("输出字段名", row["字段名称"]),
                field_type=self._infer_field_type(row.get("数据类型", "object")),
                required=row.get("是否必需", "否") == "是",
                description=row.get("备注", "")
            )
            
            self.field_mappings[field_key] = mapping
            self.selected_fields.append(field_key)
            
            # Set priority
            priority = row.get("优先级", 5)
            self.priority_levels[field_key] = priority
            
            # Add to category
            category = row.get("字段分类", "其他")
            if category not in self.field_categories:
                self.field_categories[category] = []
            self.field_categories[category].append(field_key)
    
    def _generate_field_key(self, field_name: str) -> str:
        """Generate a clean field key from field name."""
        # Simple key generation - could be more sophisticated
        key = field_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        return key
    
    def _infer_field_type(self, pandas_dtype: str) -> str:
        """Infer field type from pandas dtype."""
        dtype_lower = str(pandas_dtype).lower()
        
        if "int" in dtype_lower or "float" in dtype_lower:
            return "numeric"
        elif "datetime" in dtype_lower or "timestamp" in dtype_lower:
            return "datetime"
        elif "bool" in dtype_lower:
            return "boolean"
        else:
            return "string"
    
    def add_field_mapping(
        self,
        field_key: str,
        source_field: str,
        target_field: str,
        field_type: str = "string",
        required: bool = False,
        priority: int = 5,
        category: str = "其他"
    ) -> None:
        """Add a new field mapping."""
        
        mapping = FieldMapping(
            source_field=source_field,
            target_field=target_field,
            field_type=field_type,
            required=required
        )
        
        self.field_mappings[field_key] = mapping
        self.priority_levels[field_key] = priority
        
        if category not in self.field_categories:
            self.field_categories[category] = []
        self.field_categories[category].append(field_key)
        
        if field_key not in self.selected_fields:
            self.selected_fields.append(field_key)
    
    def select_fields(self, field_keys: List[str]) -> None:
        """Select specific fields for processing."""
        valid_keys = [key for key in field_keys if key in self.field_mappings]
        self.selected_fields = valid_keys
    
    def select_by_category(self, categories: List[str]) -> None:
        """Select all fields in specified categories."""
        selected = []
        for category in categories:
            if category in self.field_categories:
                selected.extend(self.field_categories[category])
        self.selected_fields = list(set(selected))
    
    def select_by_priority(self, max_priority: int = 3) -> None:
        """Select fields with priority level <= max_priority."""
        selected = [
            key for key, priority in self.priority_levels.items()
            if priority <= max_priority
        ]
        self.selected_fields = selected
    
    def apply_to_dataframe(self, df: pd.DataFrame, source_prefix: str = "") -> pd.DataFrame:
        """
        Apply field configuration to a DataFrame.
        
        Args:
            df: Input DataFrame
            source_prefix: Prefix for source field names (for handling merged data)
            
        Returns:
            Processed DataFrame with selected and renamed fields
        """
        result_df = df.copy()
        columns_to_keep = []
        rename_mapping = {}
        
        for field_key in self.selected_fields:
            if field_key not in self.field_mappings:
                continue
                
            mapping = self.field_mappings[field_key]
            source_col = source_prefix + mapping.source_field
            
            # Check if source column exists
            if source_col in result_df.columns:
                columns_to_keep.append(source_col)
                rename_mapping[source_col] = mapping.target_field
            else:
                # Try without prefix
                if mapping.source_field in result_df.columns:
                    columns_to_keep.append(mapping.source_field)
                    rename_mapping[mapping.source_field] = mapping.target_field
        
        # Select and rename columns
        if columns_to_keep:
            result_df = result_df[columns_to_keep]
            result_df = result_df.rename(columns=rename_mapping)
        
        return result_df
    
    def get_selected_mappings(self) -> Dict[str, FieldMapping]:
        """Get mappings for selected fields only."""
        return {
            key: mapping for key, mapping in self.field_mappings.items()
            if key in self.selected_fields
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary."""
        return {
            "total_mappings": len(self.field_mappings),
            "selected_fields": len(self.selected_fields),
            "categories": list(self.field_categories.keys()),
            "priority_distribution": self._get_priority_distribution()
        }
    
    def _get_priority_distribution(self) -> Dict[int, int]:
        """Get distribution of fields by priority level."""
        distribution = {}
        for priority in self.priority_levels.values():
            distribution[priority] = distribution.get(priority, 0) + 1
        return distribution
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "field_mappings": {
                key: {
                    "source_field": mapping.source_field,
                    "target_field": mapping.target_field,
                    "field_type": mapping.field_type,
                    "required": mapping.required,
                    "default_value": mapping.default_value,
                    "validation_rules": mapping.validation_rules,
                    "description": mapping.description
                }
                for key, mapping in self.field_mappings.items()
            },
            "selected_fields": self.selected_fields,
            "field_categories": self.field_categories,
            "priority_levels": self.priority_levels
        }
    
    def save_to_yaml(self, output_path: Union[str, Path]) -> None:
        """Save configuration to YAML file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)
    
    def save_to_json(self, output_path: Union[str, Path]) -> None:
        """Save configuration to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
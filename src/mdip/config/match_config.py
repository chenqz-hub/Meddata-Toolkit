"""
Match Configuration Module

Manages matching strategies and parameters.
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum


class MatchStrategy(Enum):
    """Available matching strategies."""
    EXACT = "exact"
    FUZZY = "fuzzy"
    COMPOSITE = "composite"
    AUTO = "auto"


@dataclass
class MatchingRule:
    """Configuration for a single matching rule."""
    field_name: str
    weight: float = 1.0
    threshold: float = 0.8
    is_required: bool = False
    preprocessing: Optional[str] = None  # 'lowercase', 'strip', 'normalize'


class MatchConfig:
    """
    Configuration manager for data matching strategies.
    
    Handles:
    - Matching strategy selection
    - Field weights and thresholds
    - Duplicate handling rules
    - Quality control parameters
    """
    
    def __init__(self, config_data: Optional[Dict[str, Any]] = None):
        """Initialize match configuration."""
        
        # Default configuration
        self.strategy = MatchStrategy.AUTO
        self.primary_keys: List[str] = ["subjid", "patientid", "patient_id"]
        self.fallback_keys: List[str] = ["stname", "patient_name"]
        self.matching_rules: Dict[str, MatchingRule] = {}
        
        # Fuzzy matching settings
        self.fuzzy_threshold = 0.8
        self.fuzzy_method = "token_sort_ratio"  # fuzzywuzzy method
        
        # Composite matching settings
        self.composite_min_fields = 2
        self.composite_weights = {}
        
        # Duplicate handling
        self.duplicate_strategy = "keep_first"  # 'keep_first', 'keep_last', 'merge', 'flag'
        self.duplicate_threshold = 0.95
        
        # Quality control
        self.min_match_confidence = 0.7
        self.require_id_match = True
        
        if config_data:
            self._load_from_dict(config_data)
    
    def _load_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Load configuration from dictionary."""
        
        if "strategy" in config_data:
            self.strategy = MatchStrategy(config_data["strategy"])
        
        if "primary_keys" in config_data:
            self.primary_keys = config_data["primary_keys"]
        
        if "fallback_keys" in config_data:
            self.fallback_keys = config_data["fallback_keys"]
        
        if "fuzzy_threshold" in config_data:
            self.fuzzy_threshold = config_data["fuzzy_threshold"]
        
        if "matching_rules" in config_data:
            for field, rule_data in config_data["matching_rules"].items():
                self.matching_rules[field] = MatchingRule(**rule_data)
    
    @classmethod
    def create_exact_match_config(
        cls,
        primary_key: str = "subjid",
        fallback_keys: Optional[List[str]] = None
    ) -> "MatchConfig":
        """Create configuration for exact matching."""
        
        config = cls()
        config.strategy = MatchStrategy.EXACT
        config.primary_keys = [primary_key]
        config.fallback_keys = fallback_keys or []
        config.require_id_match = True
        
        return config
    
    @classmethod
    def create_fuzzy_match_config(
        cls,
        name_field: str = "stname",
        threshold: float = 0.8,
        method: str = "token_sort_ratio"
    ) -> "MatchConfig":
        """Create configuration for fuzzy matching."""
        
        config = cls()
        config.strategy = MatchStrategy.FUZZY
        config.fallback_keys = [name_field]
        config.fuzzy_threshold = threshold
        config.fuzzy_method = method
        config.require_id_match = False
        
        return config
    
    @classmethod
    def create_composite_match_config(
        cls,
        field_weights: Dict[str, float],
        min_fields: int = 2,
        min_confidence: float = 0.7
    ) -> "MatchConfig":
        """Create configuration for composite matching."""
        
        config = cls()
        config.strategy = MatchStrategy.COMPOSITE
        config.composite_weights = field_weights
        config.composite_min_fields = min_fields
        config.min_match_confidence = min_confidence
        
        # Create matching rules from weights
        for field, weight in field_weights.items():
            config.matching_rules[field] = MatchingRule(
                field_name=field,
                weight=weight,
                threshold=0.8,
                is_required=weight >= 1.0
            )
        
        return config
    
    def add_matching_rule(
        self,
        field_name: str,
        weight: float = 1.0,
        threshold: float = 0.8,
        is_required: bool = False,
        preprocessing: Optional[str] = None
    ) -> None:
        """Add a matching rule for a specific field."""
        
        rule = MatchingRule(
            field_name=field_name,
            weight=weight,
            threshold=threshold,
            is_required=is_required,
            preprocessing=preprocessing
        )
        
        self.matching_rules[field_name] = rule
    
    def set_duplicate_handling(
        self,
        strategy: str,
        threshold: float = 0.95
    ) -> None:
        """
        Configure duplicate handling strategy.
        
        Args:
            strategy: 'keep_first', 'keep_last', 'merge', 'flag'
            threshold: Similarity threshold for duplicate detection
        """
        valid_strategies = ['keep_first', 'keep_last', 'merge', 'flag']
        if strategy not in valid_strategies:
            raise ValueError(f"Invalid strategy. Must be one of: {valid_strategies}")
        
        self.duplicate_strategy = strategy
        self.duplicate_threshold = threshold
    
    def get_primary_key_candidates(self, available_fields: List[str]) -> List[str]:
        """Get available primary key candidates from field list."""
        candidates = []
        
        for key in self.primary_keys:
            if key in available_fields:
                candidates.append(key)
        
        return candidates
    
    def get_matching_fields(self, available_fields: List[str]) -> List[str]:
        """Get fields that can be used for matching."""
        matching_fields = []
        
        # Add primary keys
        matching_fields.extend(self.get_primary_key_candidates(available_fields))
        
        # Add fallback keys
        for key in self.fallback_keys:
            if key in available_fields and key not in matching_fields:
                matching_fields.append(key)
        
        # Add fields from matching rules
        for field in self.matching_rules.keys():
            if field in available_fields and field not in matching_fields:
                matching_fields.append(field)
        
        return matching_fields
    
    def validate_configuration(self, available_fields: List[str]) -> Dict[str, Any]:
        """
        Validate configuration against available fields.
        
        Returns:
            Validation result with warnings and errors
        """
        result = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check if primary keys are available
        primary_candidates = self.get_primary_key_candidates(available_fields)
        if not primary_candidates and self.require_id_match:
            result["errors"].append("No primary key fields available for exact matching")
            result["is_valid"] = False
        
        # Check fallback keys
        fallback_available = [key for key in self.fallback_keys if key in available_fields]
        if not fallback_available and self.strategy == MatchStrategy.FUZZY:
            result["errors"].append("No fallback fields available for fuzzy matching")
            result["is_valid"] = False
        
        # Check matching rules
        missing_rule_fields = [
            field for field in self.matching_rules.keys()
            if field not in available_fields
        ]
        if missing_rule_fields:
            result["warnings"].append(f"Matching rule fields not available: {missing_rule_fields}")
        
        # Check composite matching requirements
        if self.strategy == MatchStrategy.COMPOSITE:
            available_rule_fields = [
                field for field in self.matching_rules.keys()
                if field in available_fields
            ]
            if len(available_rule_fields) < self.composite_min_fields:
                result["errors"].append(
                    f"Composite matching requires at least {self.composite_min_fields} fields, "
                    f"but only {len(available_rule_fields)} are available"
                )
                result["is_valid"] = False
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "strategy": self.strategy.value,
            "primary_keys": self.primary_keys,
            "fallback_keys": self.fallback_keys,
            "fuzzy_threshold": self.fuzzy_threshold,
            "fuzzy_method": self.fuzzy_method,
            "composite_min_fields": self.composite_min_fields,
            "composite_weights": self.composite_weights,
            "duplicate_strategy": self.duplicate_strategy,
            "duplicate_threshold": self.duplicate_threshold,
            "min_match_confidence": self.min_match_confidence,
            "require_id_match": self.require_id_match,
            "matching_rules": {
                field: {
                    "field_name": rule.field_name,
                    "weight": rule.weight,
                    "threshold": rule.threshold,
                    "is_required": rule.is_required,
                    "preprocessing": rule.preprocessing
                }
                for field, rule in self.matching_rules.items()
            }
        }
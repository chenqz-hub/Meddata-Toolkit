"""
Medical Data Integration Platform (MDIP)

A professional platform for medical data integration, matching, and quality control.
"""

__version__ = "1.0.0"
__author__ = "Medical Data Integration Team"
__email__ = "dev@mdip.org"

# Import main classes for easy access
from .core.matcher import DataMatcher
from .core.quality_control import QualityAssessment
from .core.reporter import ReportGenerator
from .config.field_config import FieldConfig
from .config.match_config import MatchConfig

__all__ = [
    "DataMatcher",
    "QualityAssessment",
    "ReportGenerator",
    "FieldConfig",
    "MatchConfig",
]
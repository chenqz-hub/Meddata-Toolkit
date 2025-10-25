"""
MDIP 默认配置文件

设置系统的默认参数和路径配置
"""

import os
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# 默认数据目录配置
DEFAULT_DATA_DIR = PROJECT_ROOT / "docs"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "docs" 
DEFAULT_TEMP_DIR = PROJECT_ROOT / "temp"

# 默认文件配置
DEFAULT_CONFIG = {
    "data_directory": str(DEFAULT_DATA_DIR),
    "output_directory": str(DEFAULT_OUTPUT_DIR),
    "temp_directory": str(DEFAULT_TEMP_DIR),
    "supported_formats": [".xlsx", ".xls", ".csv"],
    "default_encoding": "utf-8",
    "max_file_size_mb": 100,
    "verbose": True,
    "log_level": "INFO"
}

# 医疗数据特定配置
MEDICAL_DATA_CONFIG = {
    "patient_id_fields": ["患者ID", "患者编号", "病人ID", "ID", "编号"],
    "date_fields": ["日期", "时间", "检查日期", "入院日期", "出院日期"],
    "numeric_fields": ["年龄", "身高", "体重", "血压", "血糖", "胆固醇"],
    "category_fields": ["性别", "诊断", "科室", "医生"],
}

# 质量评估阈值
QUALITY_THRESHOLDS = {
    "completeness_excellent": 0.95,
    "completeness_good": 0.85,
    "completeness_fair": 0.70,
    "consistency_excellent": 0.90,
    "consistency_good": 0.75,
    "consistency_fair": 0.60,
    "accuracy_excellent": 0.95,
    "accuracy_good": 0.85,
    "accuracy_fair": 0.70
}

def get_default_data_path():
    """获取默认数据目录路径"""
    return DEFAULT_DATA_DIR

def get_default_output_path():
    """获取默认输出目录路径"""
    return DEFAULT_OUTPUT_DIR

def ensure_directories():
    """确保必要的目录存在"""
    directories = [DEFAULT_DATA_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_TEMP_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
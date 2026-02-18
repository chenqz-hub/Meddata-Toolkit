# Medical Data Integration Platform (MDIP)

A comprehensive, professional-grade platform for integrating, analyzing, and ensuring quality of medical research data from multiple sources. Built with software engineering best practices for clinical research environments.

## 🎯 Features

- **📊 Multi-format Support**: Excel (.xlsx, .xls), CSV file processing
- **🔍 Data Quality Assessment**: Comprehensive quality metrics and reporting (completeness, accuracy, consistency, uniqueness, timeliness)
- **🔗 Flexible Matching**: Exact and fuzzy matching algorithms with configurable thresholds
- **⚙️ Field Configuration**: Customizable field definitions and categories for medical data
- **✅ Validation Framework**: Built-in medical data validation rules and custom rule support
- **📈 Advanced Reporting**: Detailed reports in Excel and JSON formats with visualizations
- **💻 CLI Interface**: Professional command-line tools for automation and batch processing
- **🏥 Medical Data Focus**: Specialized tools for clinical research data integration

## 🚀 Quick Start

### Method 1: Direct CLI Usage (Recommended)

```bash
# Analyze file structure in a directory
mdip analyze ./data --output analysis_report.xlsx --verbose

# Assess data quality with medical validation rules
mdip quality patients.xlsx --medical --critical-fields patient_id,name --output quality_report.xlsx

# Match data from multiple files with fuzzy matching
mdip match cag_data.xlsx pci_data.csv --fields patient_id,name --fuzzy --output integration_report.xlsx

# Validate data against medical standards
mdip validate lab_results.xlsx --medical --show-errors --output validation_report.xlsx
```

### Method 2: Installation and Library Usage

```bash
# Install MDIP as a package
pip install -r requirements.txt
pip install -e .

# Use as Python library
python -c "from mdip.core.matcher import DataMatcher; print('MDIP installed successfully!')"
```

## 📋 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
# Navigate to the project directory
cd "D:\\git\\Meddata-Toolkit"

# Install runtime dependencies
pip install -r requirements-runtime.txt

# Optional: install dev dependencies
pip install -r requirements.txt

# Optional: Install in development mode for library usage
pip install -e .
```

### Verify Installation

```bash
# Test CLI functionality
mdip --help

# Test with sample data (if available)
python examples/basic_file_analysis.py ./
```

## 🛠️ Usage Examples

### 1. File Structure Analysis

```bash
# Analyze all Excel files in a directory
mdip analyze ./medical_data --output structure_analysis.xlsx --show-fields

# Analyze with verbose output to see detailed field information
mdip analyze ./data --verbose --output detailed_analysis.xlsx
```

### 2. Data Quality Assessment

```bash
# Basic quality assessment
mdip quality patient_data.xlsx --output quality_report.xlsx

# Medical data quality assessment with critical fields
mdip quality clinical_data.xlsx --medical \
  --critical-fields patient_id,medical_record_number \
  --important-fields age,gender,diagnosis \
  --key-fields patient_id \
  --output comprehensive_quality_report.xlsx

# Quality assessment with specific Excel sheet
mdip quality workbook.xlsx --sheet "Patient Demographics" --output quality_report.json
```

### 3. Data Matching and Integration

```bash
# Basic exact matching
mdip match file1.xlsx file2.csv --fields patient_id --output match_results.xlsx

# Advanced fuzzy matching for names and IDs
mdip match cag_patients.xlsx pci_patients.xlsx \
  --fields patient_id,patient_name,medical_record_number \
  --fuzzy --output patient_integration.xlsx

# Multi-file integration with custom configuration
mdip match data1.xlsx data2.xlsx data3.csv \
  --fields id,name --fuzzy --config custom_match_config.json \
  --output multi_source_integration.xlsx
```

### 4. Data Validation

```bash
# Medical data validation with built-in rules
mdip validate patient_records.xlsx --medical --output validation_results.xlsx

# General validation with error details
mdip validate lab_data.csv --show-errors --verbose --output detailed_validation.xlsx

# Custom validation rules (when implemented)
mdip validate research_data.xlsx --rules custom_rules.json --output validation_report.xlsx
```

## 🏗️ Project Structure

```
Meddata-Toolkit/
├── 📄 requirements-runtime.txt   # Runtime dependencies
├── 📄 requirements.txt           # Dev/extra dependencies
├── 📄 setup.py                   # Package installation configuration
├── 📄 README.md                  # This documentation
├── 📂 src/mdip/                  # Main MDIP package
│   ├── 📂 core/                  # Core functionality modules
│   │   ├── 📄 matcher.py         # Data matching and integration engine
│   │   ├── 📄 quality_control.py # Comprehensive quality assessment
│   │   ├── 📄 validation.py      # Data validation framework
│   │   └── 📄 reporter.py        # Advanced reporting and export
│   ├── 📂 config/                # Configuration management
│   │   ├── 📄 field_config.py    # Medical field definitions and categories
│   │   └── 📄 match_config.py    # Matching algorithm configuration
│   ├── 📂 utils/                 # Utility functions and helpers
│   │   └── 📄 data_utils.py      # Data processing and transformation
│   └── 📂 cli/                   # Command-line interface
│       └── 📄 main.py            # CLI implementation and commands
├── 📂 tests/                     # Comprehensive test suite
│   ├── 📄 conftest.py            # Test configuration and fixtures
│   ├── 📄 test_matcher.py        # Data matching tests
│   └── 📄 test_quality_control.py # Quality assessment tests
├── 📂 examples/                  # Usage examples and tutorials
│   ├── 📄 README.md              # Examples documentation
│   ├── 📄 basic_file_analysis.py # File analysis example
│   └── 📄 quality_assessment_demo.py # Quality assessment demo
├── 📂 docs/                      # Additional documentation
└── 📂 scripts/                   # Utility and maintenance scripts
```

## 🧩 Core Components

### DataMatcher (`src/mdip/core/matcher.py`)
- **File Discovery**: Automatically discovers and catalogs Excel and CSV files
- **Structure Analysis**: Extracts sheet names, field names, and basic statistics
- **Multi-format Loading**: Handles Excel (multiple sheets) and CSV files
- **Intelligent Matching**: Exact and fuzzy matching with configurable similarity thresholds
- **Integration Engine**: Merges data from multiple sources with quality tracking

### QualityAssessment (`src/mdip/core/quality_control.py`)
- **5-Dimension Analysis**: Completeness, Accuracy, Consistency, Uniqueness, Timeliness
- **Field-Level Metrics**: Individual field quality scores and recommendations
- **Critical Field Support**: Prioritized assessment for essential medical fields
- **Automated Grading**: A-F quality grades with improvement recommendations
- **Historical Tracking**: Quality trend analysis and monitoring

### ValidationFramework (`src/mdip/core/validation.py`)
- **Medical Rule Library**: Built-in validation for medical data (age ranges, lab values, etc.)
- **Custom Rule Engine**: Extensible validation rule framework
- **Batch Validation**: Efficient processing of large datasets
- **Detailed Reporting**: Row-level and field-level error reporting
- **Real-time Checks**: Integration with data loading pipeline

### ReportingSystem (`src/mdip/core/reporter.py`)
- **Multi-format Export**: Excel workbooks with multiple sheets, JSON for APIs
- **Executive Summaries**: High-level quality and integration reports
- **Detailed Analytics**: Field-by-field analysis and recommendations
- **Visual Elements**: Progress bars, quality grades, and trend indicators
- **Automated Insights**: Intelligent recommendations based on data patterns

## ⚙️ Configuration and Customization

### Medical Field Configuration

```python
from mdip.config.field_config import FieldConfig

# Create custom field configuration
config = FieldConfig()

# Add medical field categories
config.add_field_group("patient_identifiers", [
    "patient_id", "medical_record_number", "study_id"
])

config.add_field_group("demographics", [
    "age", "gender", "date_of_birth", "ethnicity"
])

config.add_field_group("clinical_measurements", [
    "blood_pressure_systolic", "blood_pressure_diastolic", 
    "heart_rate", "weight", "height", "bmi"
])

# Set field priorities
config.set_field_priority("patient_id", "critical")
config.set_field_priority("medical_record_number", "critical")
config.set_field_priority("age", "important")
```

### Matching Algorithm Configuration

```python
from mdip.config.match_config import MatchConfig

# Configure matching behavior
config = MatchConfig()

# Exact match fields (must match exactly)
config.exact_match_fields = ["patient_id", "medical_record_number"]

# Fuzzy match fields (allow similarity matching)
config.fuzzy_match_fields = ["patient_name", "doctor_name"]

# Similarity thresholds
config.fuzzy_threshold = 0.85  # 85% similarity required
config.name_similarity_threshold = 0.9  # Higher threshold for names

# Matching weights for confidence calculation
config.field_weights = {
    "patient_id": 0.4,
    "medical_record_number": 0.3,
    "patient_name": 0.2,
    "date_of_birth": 0.1
}
```

## 📊 Report Examples

### Quality Assessment Report Structure

```
📈 QUALITY ASSESSMENT RESULTS
════════════════════════════════════════════════════════════
🎯 Overall Quality Score: 0.847 (Grade: B)

📊 Quality Dimensions:
  Completeness  0.892 [████████████████████] A
  Consistency   0.834 [███████████████████ ] B  
  Uniqueness    0.978 [████████████████████] A
  Accuracy      0.756 [███████████████     ] C
  Timeliness    0.823 [████████████████████] B

🔍 Key Findings:
  ⚠️  Found 23 duplicate rows (2.3%)
  ⚠️  Found 156 data accuracy issues
  
📋 Field Completeness (lowest 5):
  diagnosis            67.4% (326 missing) [C]
  secondary_diagnosis  45.2% (548 missing) [F]
  follow_up_date      89.1% (109 missing) [B]
  lab_result_date     92.3% (77 missing)  [A]
  notes               34.7% (653 missing) [F]

💡 Recommendations:
  1. Improve data completeness through better data collection processes
  2. Implement deduplication procedures to reduce duplicate records
  3. Add validation rules and data entry checks to improve accuracy
```

### Integration Report Structure

```
🔗 DATA INTEGRATION REPORT
════════════════════════════════════════════════════════════
📊 Integration Summary:
  Source Datasets: 3
  Total Records Processed: 2,847
  Successful Matches: 2,234 (78.5%)
  Failed Matches: 613 (21.5%)
  Final Quality Score: 0.823

🎯 Matching Results by Source:
  CAG_patients.xlsx → PCI_patients.xlsx: 1,456 matches (94.2%)
  Lab_results.csv → Patient_data.xlsx: 778 matches (67.8%)

📈 Confidence Distribution:
  High Confidence (≥90%): 1,567 matches (70.1%)
  Medium Confidence (70-89%): 534 matches (23.9%)
  Low Confidence (<70%): 133 matches (6.0%)
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_matcher.py -v
python -m pytest tests/test_quality_control.py -v

# Run with coverage report
python -m pytest tests/ --cov=mdip --cov-report=html

# Run tests for specific functionality
python -m pytest tests/ -k "test_quality" -v
```

### Test Coverage Areas

- **Unit Tests**: Individual component functionality
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Large dataset handling
- **Error Handling**: Edge cases and error conditions
- **Configuration Tests**: Custom configuration scenarios

## 🔧 Development and Extensions

### Adding Custom Validation Rules

```python
from mdip.core.validation import ValidationRule, DataValidator

class CustomLabValueRule(ValidationRule):
    def __init__(self, min_val, max_val, test_name):
        super().__init__(f"{test_name}_range", f"{test_name} must be between {min_val} and {max_val}")
        self.min_val = min_val
        self.max_val = max_val
    
    def validate(self, data):
        if pd.isna(data):
            return True, ""
        
        try:
            value = float(data)
            if self.min_val <= value <= self.max_val:
                return True, ""
            else:
                return False, f"Value {value} is outside normal range ({self.min_val}-{self.max_val})"
        except (ValueError, TypeError):
            return False, f"Invalid numeric value: {data}"

# Use custom rule
validator = DataValidator()
validator.add_rule("hemoglobin", CustomLabValueRule(8.0, 18.0, "Hemoglobin"))
```

### Extending Field Configurations

```python
from mdip.config.field_config import FieldConfig

class CardiacFieldConfig(FieldConfig):
    def __init__(self):
        super().__init__()
        self._setup_cardiac_fields()
    
    def _setup_cardiac_fields(self):
        # Define cardiac-specific field categories
        self.add_field_group("cardiac_procedures", [
            "pci_date", "stent_type", "vessel_treated", "lesion_location"
        ])
        
        self.add_field_group("cardiac_measurements", [
            "ejection_fraction", "troponin", "ck_mb", "nt_probnp"
        ])
        
        # Set validation rules
        self.add_validation_rule("ejection_fraction", "range", min=15, max=80)
        self.add_validation_rule("pci_date", "date_format", format="%Y-%m-%d")
```

## 🆘 Troubleshooting

### Common Issues and Solutions

**Issue**: `ModuleNotFoundError: No module named 'mdip'`
```bash
# Solution: Install dependencies and package
pip install -r requirements.txt
pip install -e .
```

**Issue**: `Permission denied` when writing reports
```bash
# Solution: Check file permissions and close Excel if open
# Use a different output directory with write permissions
mdip quality data.xlsx --output ./reports/quality_report.xlsx
```

**Issue**: `UnicodeDecodeError` when processing files
```bash
# Solution: Ensure files are in UTF-8 encoding
# Or specify encoding in CSV files (feature to be added)
```

**Issue**: Poor matching results
```bash
# Solution: Adjust fuzzy matching threshold or add more matching fields
mdip match file1.xlsx file2.xlsx \
  --fields patient_id,name,dob \
  --fuzzy --verbose
```

## 📞 Support and Contributing

### Getting Help

1. **Check Documentation**: Review this README and examples
2. **Run with `--verbose`**: Get detailed execution information
3. **Check Log Files**: Look for `mdip.log` in the project directory
4. **Open GitHub Issue**: Provide sample data and error details

### Contributing Guidelines

1. **Fork the Repository**: Create your own copy for development
2. **Create Feature Branch**: `git checkout -b feature/new-functionality`
3. **Follow Code Style**: Use consistent formatting and documentation
4. **Add Tests**: Include tests for new functionality
5. **Update Documentation**: Update README and docstrings
6. **Submit Pull Request**: Include detailed description of changes

### Development Setup

```bash
# Clone and setup development environment
git clone <repository-url>
cd Meddata-Toolkit
pip install -r requirements-runtime.txt
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8

# Run development checks
black src/  # Format code
flake8 src/  # Check style
pytest tests/ --cov=mdip  # Run tests with coverage
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for medical research data integration needs
- Designed with clinical research workflows in mind  
- Follows software engineering best practices for reliability
- Supports FAIR (Findable, Accessible, Interoperable, Reusable) data principles
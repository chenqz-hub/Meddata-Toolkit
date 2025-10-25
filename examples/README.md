# 医疗数据整合平台 (MDIP) 示例

本目录包含演示MDIP功能的示例脚本和教程。

## 可用示例

### 基础使用示例

1. **基础文件分析.py** - 简单的文件结构分析
2. **basic_file_analysis.py** - 英文版文件结构分析
3. **quality_assessment_demo.py** - 全面的质量评估演示
4. **data_matching_example.py** - 两个文件间的基础数据匹配
5. **validation_example.py** - 使用自定义规则的数据验证

### 高级示例

1. **multi_file_integration.py** - 高级多文件整合工作流
2. **custom_field_configuration.py** - 创建自定义字段配置
3. **quality_monitoring.py** - 自动化质量监控设置
4. **reporting_workflow.py** - 完整的报告工作流

### 医疗研究示例

1. **clinical_data_integration.py** - 临床数据整合示例
2. **patient_matching.py** - 跨系统患者记录匹配
3. **longitudinal_analysis_prep.py** - 纵向分析数据准备

## 运行示例

```bash
# 基础文件分析
python examples/基础文件分析.py ./数据目录

# 英文版文件分析  
python examples/basic_file_analysis.py /path/to/data

# 数据匹配
python examples/data_matching_example.py 文件1.xlsx 文件2.csv

# 质量评估
python examples/quality_assessment_demo.py 数据.xlsx
```

## 系统要求

所有示例都需要安装MDIP包：

```bash
cd /path/to/mdip
pip install -e .
```

## 测试数据文件

在 `sample_data/` 子目录中提供了匿名化的示例数据文件用于测试。

## 中文使用说明

### 快速测试
```bash
# 测试文件分析功能
python 基础文件分析.py .

# 测试质量评估功能  
python quality_assessment_demo.py 您的数据文件.xlsx
```

### 常见用法
```bash
# 分析当前目录的所有文件
python ../mdip.py analyze . --output 分析报告.xlsx --verbose

# 评估数据质量
python ../mdip.py quality 数据文件.xlsx --medical --output 质量报告.xlsx
```
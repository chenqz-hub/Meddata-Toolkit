# 医疗数据整合平台 (MDIP) 示例

本目录包含演示MDIP功能的示例脚本和教程。

## 可用示例

### 基础使用示例

1. **基础文件分析.py** - 简单的文件结构分析
2. **basic_file_analysis.py** - 英文版文件结构分析
3. **quality_assessment_demo.py** - 质量评估演示
4. **fill_case_data_example.py** - Case 数据填充示例

## 运行示例

```bash
# 基础文件分析
python examples/基础文件分析.py ./数据目录

# 英文版文件分析  
python examples/basic_file_analysis.py /path/to/data

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

示例脚本使用你提供的本地数据文件运行。

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
mdip analyze . --output 分析报告.xlsx --verbose

# 评估数据质量
mdip quality 数据文件.xlsx --medical --output 质量报告.xlsx
```
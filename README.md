# 医疗数据整合平台 (MDIP)

一个专业级的医疗研究数据整合、分析和质量控制平台，专为多源医疗数据处理而设计，遵循软件工程最佳实践。

## ⚡ 快速启动

### 方式1：使用主菜单（推荐）
**双击运行 `run_launcher.bat`**（固定使用项目 `.venv`，更稳定）

兼容旧方式：也可直接运行 `启动工具.py`。

这将显示图形化菜单，提供以下选项：
1. 单文件多Sheet合并工具
2. 跨文件合并工具（经典版）
3. 跨文件合并工具（增强版）
4. 跨文件合并工具（专业版） 🌟 全功能
5. 重复记录去重工具
6. 字段唯一性检查工具
7. 填充 Case 数据工具
8. 快速清理项目
9. 退出

### 方式2：直接启动工具
也可以直接双击运行单个工具：
- `run_tool1.bat` - 单文件多Sheet合并工具
- `run_tool2.bat` - 跨文件合并工具
- `run_tool3.bat` - 重复记录去重工具
- `run_tool4.bat` - 字段唯一性检查工具

### 方式3：命令行（高级用户）
```bash
python launcher.py
```

### 诊断工具
如果遇到问题，可以运行：
- `诊断环境.bat` - 检查环境配置和依赖
- `使用说明.bat` - 查看所有可用的启动方式

## 🚀 项目概述

医疗数据整合平台 (Medical Data Integration Platform, MDIP) 是一个专为医疗研究和临床数据处理设计的综合性数据整合平台。该平台支持多种格式的医疗数据文件的智能发现、匹配、合并和质量控制，为医疗研究人员提供专业级的数据处理工具。

## 🎯 核心功能

- **� 多格式支持**: Excel (.xlsx, .xls)、CSV 文件处理
- **🔍 数据质量评估**: 全面的质量指标和报告（完整性、准确性、一致性、唯一性、时效性）
- **🔗 灵活匹配策略**: 精确匹配和模糊匹配算法，可配置相似度阈值
- **⚙️ 字段配置系统**: 医疗数据字段定义和分类的可定制化配置
- **✅ 验证框架**: 内置医疗数据验证规则和自定义规则支持
- **📈 高级报告功能**: 详细的Excel和JSON格式报告，包含可视化元素
- **� 命令行界面**: 专业的CLI工具，支持自动化和批处理
- **🏥 医疗数据专用**: 专为临床研究数据整合设计的专业工具

## 🚀 快速开始

### 方法一：GUI工具（最简单）

**启动工具集**
```bash
python 启动工具.py
```

**可用工具**：
1. **单文件多Sheet合并工具** - 将一个Excel文件的多个Sheet合并为一张表
2. **跨文件合并工具（经典版）** - 命令行交互式合并
3. **跨文件合并工具（增强版）** - 图形界面，文件选择器和可视化配置
4. **跨文件合并工具（专业版）** ⭐ **推荐** - 完整功能版
   - 📊 数据预览表格 - 合并前预览数据
   - 📦 **批量合并模式** - 一次处理多个文件对
   - 💾 模板保存 - 保存常用配置
   - 📝 导出报告 - 生成详细报告
   - ↩️ 撤销/重做 - 支持操作回退
5. **重复记录去重工具** - 识别和删除重复数据
6. **字段唯一性检查工具** - 检查字段作为主键的可行性
7. **填充 Case 数据工具** - 从原始表填充合并表中现有 case 的缺失字段值

**快速上手**：
```bash
# 1. 启动工具集（主入口）
python 启动工具.py
# 2. 选择功能模块（数据整理/论文准备）
# 3. 选择具体工具

# 或者直接使用快捷脚本：
# - 启动论文格式化工具.bat
# - 启动参考文献验证工具.bat

# 示例：使用专业版合并工具
# 1. 启动工具集 -> 选择"1. 数据整理" -> 选择"4. 跨文件合并工具 (专业版)"
# 2. 使用图形界面选择文件、配置合并参数
# 3. 点击"执行合并"完成操作
```

📖 **详细教程**：
- 基础功能：`工具使用指南.md`
- 批量处理：`docs/批量合并使用指南.md`

### 方法二：直接CLI使用

```bash
# 分析目录中的文件结构
mdip analyze ./data --output 分析报告.xlsx --verbose

# 使用医疗验证规则进行数据质量评估
mdip quality 患者数据.xlsx --medical --critical-fields patient_id,name --output 质量报告.xlsx

# 多文件模糊匹配整合
mdip match 冠脉造影数据.xlsx PCI数据.csv --fields patient_id,name --fuzzy --output 整合报告.xlsx

# 医疗标准数据验证
mdip validate 实验室结果.xlsx --medical --show-errors --output 验证报告.xlsx
```

### 方法二：安装后作为库使用

```bash
# 安装MDIP包
pip install -r requirements.txt
pip install -e .

# 作为Python库使用
python -c "from mdip.core.matcher import DataMatcher; print('MDIP安装成功！')"
```

### 方法三：VSCode集成开发

**调试配置** (`.vscode/launch.json`)：
- F5 快速启动任何工具
- 断点调试支持
- 集成终端执行

**快速任务** (`.vscode/tasks.json`)：
- Ctrl+Shift+P → "运行任务"
- 一键启动工具

## 📋 安装说明

### 系统要求
- Python 3.8 或更高版本
- pip 包管理器

### 安装依赖包

```bash
# 导航到项目目录
cd "D:\\git\\Meddata-Toolkit"

# 安装运行时依赖（推荐）
pip install -r requirements-runtime.txt

# 可选：安装开发依赖（测试/格式化/可视化）
pip install -r requirements.txt

# 可选：以开发模式安装，用于库调用
pip install -e .
```

### 验证安装

```bash
# 测试CLI功能
mdip --help

# 使用示例数据测试（如果有的话）
python examples/basic_file_analysis.py ./
```

开发规范与常用命令见：[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

## 📁 项目结构

```
medical-data-integration-platform/
├── README.md                          # 项目说明文档
├── requirements.txt                    # Python依赖包
├── setup.py                          # 项目安装配置
├── .gitignore                         # Git忽略文件
├── LICENSE                            # 开源许可证
├── docs/                              # 项目文档
│   ├── installation.md               # 安装指南
│   ├── user_guide.md                 # 用户指南
│   ├── api_reference.md              # API参考
│   └── examples/                      # 使用示例
├── src/                               # 源代码
│   └── mdip/                         # 主程序包
│       ├── __init__.py
│       ├── core/                      # 核心功能模块
│       │   ├── __init__.py
│       │   ├── file_manager.py        # 文件管理
│       │   ├── matcher.py             # 数据匹配引擎
│       │   ├── quality_control.py     # 数据质量控制
│       │   └── reporter.py            # 报告生成
│       ├── config/                    # 配置管理
│       │   ├── __init__.py
│       │   ├── field_config.py        # 字段配置
│       │   ├── match_config.py        # 匹配策略配置
│       │   └── settings.py            # 全局设置
│       ├── utils/                     # 工具函数
│       │   ├── __init__.py
│       │   ├── data_utils.py          # 数据处理工具
│       │   ├── file_utils.py          # 文件操作工具
│       │   └── validation.py          # 数据验证工具
│       ├── gui/                       # 图形界面(可选)
│       │   ├── __init__.py
│       │   └── main_window.py
│       └── cli/                       # 命令行界面
│           ├── __init__.py
│           └── main.py
├── tests/                             # 测试代码
│   ├── __init__.py
│   ├── test_core/                     # 核心功能测试
│   ├── test_config/                   # 配置模块测试
│   ├── test_utils/                    # 工具函数测试
│   └── test_data/                     # 测试数据
│       ├── sample_data.xlsx
│       └── expected_results.xlsx
├── scripts/                           # 脚本和工具
│   ├── install.py                     # 安装脚本
│   ├── migrate_legacy.py              # 迁移脚本
│   └── generate_config.py             # 配置生成脚本
├── data/                              # 数据目录
│   ├── input/                         # 输入数据
│   ├── output/                        # 输出结果
│   ├── config/                        # 配置文件
│   └── logs/                          # 日志文件
└── examples/                          # 使用示例
    ├── basic_usage.py
    ├── advanced_matching.py
    └── custom_config.py
```

## 🛠️ 技术栈

### 核心依赖
- **pandas >= 1.5.0**: 数据处理和分析
- **openpyxl >= 3.0.0**: Excel文件读写
- **fuzzywuzzy >= 0.18.0**: 模糊字符串匹配
- **python-Levenshtein >= 0.12.0**: 字符串相似度计算

### 开发依赖
- **pytest >= 7.0.0**: 单元测试框架
- **black >= 22.0.0**: 代码格式化
- **flake8 >= 5.0.0**: 代码静态检查
- **mypy >= 0.980**: 类型检查

### 可选依赖
- **tkinter**: 图形用户界面
- **matplotlib >= 3.5.0**: 数据可视化
- **seaborn >= 0.11.0**: 统计数据可视化

## 🚀 快速开始

### 安装
```bash
# 从源码安装
git clone https://github.com/your-org/medical-data-integration-platform.git
cd medical-data-integration-platform
pip install -e .

# 或使用pip安装(发布后)
pip install medical-data-integration-platform
```

### 基本使用
```python
from mdip import DataMatcher, FieldConfig

# 创建字段配置
config = FieldConfig.from_template("basic_medical_fields")

# 初始化数据匹配器
matcher = DataMatcher(config)

# 添加数据文件
matcher.add_file("cag_data.xlsx", file_type="primary", group="CAG")
matcher.add_file("pci_data.xlsx", file_type="primary", group="PCI")

# 执行匹配
results = matcher.match_and_merge()

# 保存结果
results.to_excel("merged_results.xlsx")
```

## 📖 文档

- [安装指南](docs/installation.md)
- [用户指南](docs/user_guide.md)
- [API参考](docs/api_reference.md)
- [使用示例](examples/)

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行指定测试
pytest tests/test_core/

# 生成测试覆盖率报告
pytest --cov=src/mdip --cov-report=html
```

## 🤝 贡献指南

欢迎贡献代码！请先阅读 [贡献指南](CONTRIBUTING.md)。

### 开发流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范
- 遵循 PEP 8 Python 代码规范
- 使用 black 进行代码格式化
- 添加类型注解
- 编写单元测试
- 更新文档

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## � 工具详细使用说明

### 7. 补充缺失 Case 工具

**使用场景**：
多个数据表合并后，发现某些 case（病例/样本）的数据在合并表中缺失，但这些 case 仍然存在于某张原始表中。此工具可以从原始表中提取这些缺失的 case 并补充到合并表中。

**功能特点**：
- ✅ 自动识别缺失的 case（基于键字段，如 `case_id`、`patient_id`）
- ✅ 从原始表中提取完整的 case 数据行
- ✅ 智能处理字段不一致问题（自动对齐共同字段）
- ✅ 生成补充后的新文件，保留原始文件
- ✅ 支持交互式 GUI 和命令行模式

**启动方式**：
```bash
# 方式1：从主菜单启动
python 启动工具.py
# 选择选项 7

# 方式2：直接运行批处理文件
run_append_missing.bat

# 方式3：命令行模式
python tools/append_missing_cases.py --merged 合并表.xlsx --source 原始表.xlsx --key case_id
```

**使用步骤**：
1. 选择【合并后的表格】（缺少某些 case 的表）
2. 选择【原始表格】（包含缺失 case 的表）
3. 指定【键字段名】（用于识别 case 的字段，如 `case_id`）
4. 工具会自动：
   - 比较两个表中的 case ID
   - 识别缺失的 case
   - 显示缺失 case 的列表
   - 询问是否补充
   - 生成补充后的新文件

**输出**：
- 生成文件：`原合并表文件名_补充.xlsx` 或 `.csv`
- 包含：原合并表的所有数据 + 从原始表补充的缺失 case

**示例**：
```bash
# 场景：
# - merged.xlsx: 合并后的表，有 100 个 case
# - original.xlsx: 原始表，有 110 个 case
# - 发现有 10 个 case 在合并时丢失了

python tools/append_missing_cases.py --merged merged.xlsx --source original.xlsx --key patient_id

# 输出：
# merged_补充.xlsx - 包含完整的 110 个 case
```

**注意事项**：
- 确保两个表中都有相同的键字段（如 `case_id`）
- 如果字段名不完全一致，工具会只保留共同字段，缺失字段填充为空值
- 建议在补充前备份原文件
- 工具不会修改原始文件，而是生成新文件

## �📞 支持

- 📧 邮箱: support@mdip.org
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-org/medical-data-integration-platform/issues)
- 📖 文档: [在线文档](https://mdip.readthedocs.io/)

## 🎯 路线图

### v1.0.0 (当前版本)
- [x] 核心数据匹配功能
- [x] Excel/CSV文件支持
- [x] 基本质量控制
- [x] 配置管理系统

### v1.1.0 (计划中)
- [ ] 图形用户界面
- [ ] 数据可视化
- [ ] 性能优化
- [ ] 更多匹配策略

### v2.0.0 (未来版本)
- [ ] 数据库支持
- [ ] RESTful API
- [ ] 分布式处理
- [ ] 机器学习匹配

## 🏆 致谢

感谢所有贡献者和使用者对本项目的支持！

---

## 📖 附录：填充 Case 数据工具详细说明

### 使用场景
合并表中已有 case 记录，但部分字段为空。原始表中有这些字段的完整数据。需要将原始表的数据填充到合并表的空白字段中。

### 工作原理
1. 基于键字段（如 `patient_id`）在两个表之间匹配 case
2. 对于每个匹配的 case，逐字段检查：
   - 合并表中该字段是否为空
   - 原始表中该字段是否有值
   - 如果两个条件都满足，则填充
3. 已有数据不会被覆盖

### 命令行示例
```bash
# 基本用法
python tools/fill_case_data.py --merged merged.xlsx --source original.xlsx --key patient_id

# 指定输出文件
python tools/fill_case_data.py -m merged.xlsx -s original.xlsx -k patient_id -o result.xlsx
```

### 实际案例
**测试数据显示**：
- 总 case 数：5
- 匹配到的 case 数：5
- 总共填充单元格数：7
- 各字段填充情况：
  - `blood_pressure`: 3 个值
  - `cholesterol`: 2 个值
  - `age`: 1 个值
  - `diagnosis`: 1 个值

---

**注意**: 这是一个医疗数据处理工具，使用时请确保遵守相关的数据保护法规和医疗数据处理规范。
# 工具文件说明

本目录包含所有数据处理核心工具。

## 📂 文件列表

### 1. merge_tool_gui.py
**单文件多Sheet合并工具**

- **功能：** 将一个Excel文件中的多个sheet合并成一个表格
- **输入：** 一个包含多个sheet的Excel文件
- **输出：** 一个合并后的Excel文件
- **运行：** `python merge_tool_gui.py`

---

### 2. cross_merge_gui.py
**跨文件合并工具**

- **功能：** 将两个Excel文件按ID字段合并
- **输入：** 两个Excel文件
- **输出：** 合并后的Excel文件，包含Merged Data和Merge Info两个sheet
- **运行：** `python cross_merge_gui.py`
- **特点：** 
  - 支持不同字段名的ID匹配
  - 自动检查字段唯一性并警告
  - 支持4种join类型

---

### 3. deduplicate_tool.py
**重复记录去重工具**

- **功能：** 对有重复记录的数据进行去重
- **输入：** 包含重复记录的Excel文件
- **输出：** 去重后的Excel文件
- **运行：** `python deduplicate_tool.py`
- **策略：**
  - 保留第一条记录
  - 保留最后一条记录
  - 按日期保留最早记录
  - 按日期保留最新记录

---

### 4. check_join_fields.py
**字段唯一性检查工具**

- **功能：** 检查两个文件的共同字段是否唯一
- **输入：** 两个Excel文件
- **输出：** 控制台输出，显示共同字段及其唯一性
- **运行：** `python check_join_fields.py`
- **用途：** 在合并之前验证字段是否适合作为主键

---

### 5. append_missing_cases.py
**补充缺失 Case 工具**

- **功能：** 从原始表中补充合并后缺失的 case（病例/样本）数据
- **输入：** 
  - 合并后的表格（缺少某些 case）
  - 原始表格（包含缺失的 case）
- **输出：** 补充后的表格文件（`原文件名_补充.xlsx`）
- **运行方式：**
  - GUI模式：`python append_missing_cases.py`
  - CLI模式：`python append_missing_cases.py --merged merged.xlsx --source original.xlsx --key case_id`
  - 批处理：`run_append_missing.bat`
  - 主菜单：`python 启动工具.py` → 选项 7
- **特点：**
  - 自动识别缺失的 case（基于键字段）
  - 智能处理字段不一致问题
  - 完整保留缺失 case 的所有数据
  - 生成新文件，不修改原文件
- **使用场景：**
  - 多表合并后发现部分 case 丢失
  - 需要从备份表中恢复特定 case
  - 合并验证后补充遗漏数据

---

## 🚀 快速启动

所有工具都支持以下启动方式：

1. **主菜单启动**（推荐）：
   ```bash
   python 启动工具.py
   ```

2. **直接运行**：
   ```bash
   python tools/<工具名>.py
   ```

3. **批处理文件**：
   ```bash
   run_<工具名>.bat
   ```

## 📝 使用示例

详细使用示例请参考 `examples/` 目录：
- `basic_file_analysis.py` - 基础文件分析示例
- `append_missing_example.py` - 补充缺失 Case 示例
- `quality_assessment_demo.py` - 质量评估示例
- **输出：** 终端显示各字段的唯一性分析
- **运行：** `python check_join_fields.py`
- **用途：** 合并前确认使用哪个字段作为连接键

---

### 5. Medical_Manuscript_Formatter
**论文格式化工具**

- **功能：** 将Markdown/文本稿件转换为符合医学期刊投稿标准的Word文档
- **输入：** Markdown (.md) 或 文本 (.txt) 文件
- **输出：** 格式化后的 Word (.docx) 文档
- **运行：** 运行根目录下的 `启动论文格式化工具.bat`
- **特点：**
  - **多文档类型支持**：自动识别并格式化 Main Manuscript, Cover Letter, Title Page, Highlights 等
  - **智能排版**：自动处理行号、页码、双倍行距、首行缩进
  - **表格处理**：Markdown表格转Word表格，宽表格自动转横向页面
  - **符合标准**：默认使用 Times New Roman 12pt，1英寸边距

---

## 🔄 常用工作流程

### 流程1：单文件合并
```
merge_tool_gui.py → 完成
```

### 流程2：跨文件合并（标准流程）
```
1. check_join_fields.py （检查字段）
   ↓
2. cross_merge_gui.py （执行合并）
   ↓
3. deduplicate_tool.py （如需去重）
```

### 流程3：跨文件合并（快速流程）
```
cross_merge_gui.py → 完成
（工具内置唯一性检查）
```

---

## 💡 使用建议

1. **首次使用：** 先用少量数据测试
2. **合并前：** 运行 `check_join_fields.py` 确认ID字段
3. **合并时：** 注意工具的警告信息
4. **合并后：** 检查结果文件的"Info"sheet

---

## 📞 技术支持

遇到问题请查看：
- 上级目录的《工具使用指南.md》
- 上级目录的《项目说明.md》

---

**所有工具都支持GUI文件选择，操作简便！** ✨

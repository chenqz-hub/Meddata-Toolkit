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
- **输出：** 终端显示各字段的唯一性分析
- **运行：** `python check_join_fields.py`
- **用途：** 合并前确认使用哪个字段作为连接键

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

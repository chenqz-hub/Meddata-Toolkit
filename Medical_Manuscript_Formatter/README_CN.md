# 医学论文排版工具 (Medical Manuscript Formatter)

本工具旨在将 Markdown (`.md`) 或纯文本 (`.txt`) 格式的论文草稿，一键转换为严格符合学术投稿要求（如 JCCT、Elsevier 期刊标准）的 Microsoft Word (`.docx`) 文档。

## 功能特性

*   **严格排版规范**:
    *   **字体**: Times New Roman, 12号 (12pt)。
    *   **行距**: 正文双倍行距 (Double spacing)。
    *   **页边距**: 四周均为 1 英寸 (2.54 厘米)。
    *   **对齐**: 左对齐 (Left aligned)，正文段落首行缩进 0.5 英寸。
*   **智能表格支持**:
    *   自动将 Markdown 表格转换为学术标准的“三线表”（顶底粗线、表头细线）。
    *   **全宽自适应**: 表格宽度自动设置为页面宽度的 100%，且列宽根据内容自适应 (Autofit)。
    *   **居中对齐**: 单元格文字水平和垂直方向均居中。
    *   **自动横排**: 列数大于6列的宽表格，自动将所在页面设置为横向 (Landscape)。
    *   **智能布局**: 确保表格标题、表格本体和脚注在同一页，不会断开。
    *   **脚注清理**: 智能识别并移除表格脚注后的分割线，保持版面整洁。
    *   表格内容使用单倍行距（为了美观和可读性）。
*   **图注 (Figure Legends) 优化**:
    *   **智能加粗**: 仅自动加粗 "Figure X" 标题和 Panel 标识 (如 "A.", "B.")。
    *   **严格规范**: 自动移除图注正文中的其他加粗格式，严格符合投稿要求。
    *   **无缩进**: 图注段落左对齐，无首行缩进。
    *   **Panel 合并**: 自动将分行的 Panel 描述 (A., B. 等) 合并到主图注段落中。
    *   **间距优化**: 每个图注后增加间距，提升可读性。
*   **摘要 (Abstract) 支持**:
    *   **支持加粗**: 允许在 Abstract 章节内使用加粗格式 (如 **Background:**)。
*   **论文专用功能**:
    *   **自动行号**: 如果文件名包含 "Main" 或 "Manuscript"，会自动开启连续行号（Blind Review 必需）。
    *   **智能分页**: 在主要章节前自动插入分页符，并优化了 Abstract 与 Introduction 之间的分页逻辑，避免空白页。
    *   **页码**: 页脚居中自动添加 "PAGE X" 格式页码。
*   **自动清理**:
    *   自动移除 Markdown 中的分割线 (`---` 或 `***`)。
    *   自动移除正文中的加粗格式（仅保留标题加粗），符合投稿规范。

## 使用方法

### 方式一：使用便携版（推荐，无需安装 Python）
1.  进入 `dist` 文件夹。
2.  双击 **`Medical_Manuscript_Formatter.exe`**。
3.  在弹出的对话框中选择您的文件即可。
    *   此方式可在任何 Windows 电脑上运行，无需任何配置。

### 方式二：使用脚本版（需要 Python 环境）
如果您希望查看源码或修改功能，可以使用此方式。

1.  **安装 Python**:
    *   访问 [Python 官网](https://www.python.org/downloads/) 下载并安装 Python 3.x。
    *   **重要**: 安装时请勾选 "Add Python to PATH" (将 Python 添加到环境变量)。
    *   验证安装: 打开命令行 (Win+R -> cmd)，输入 `python --version`，应显示版本号。

2.  **运行工具**:
    *   双击 **`run_formatter.bat`**。
    *   脚本会自动安装所需的依赖库 (`python-docx`) 并启动工具。

### 方式三：命令行运行
如果您熟悉命令行，也可以通过 Python 直接运行：

```bash
# 处理当前目录下的所有文件
python format_manuscript.py

# 处理指定文件
python format_manuscript.py "D:\MyDocs\Main_Manuscript.md"

# 处理指定文件夹
python format_manuscript.py "D:\MyDocs\Drafts"
```

## 依赖环境

*   Python 3.x
*   `python-docx` 库 (运行 `run_formatter.bat` 会自动安装)

## 输出示例

*   输入: `Main_Manuscript_Blind.md`
*   输出: `Main_Manuscript_Blind.docx` (包含行号、标准排版)

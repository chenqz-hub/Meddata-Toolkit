# 医学文献引用验证工具 (Medical Reference Verifier)

这是一个独立的 Python 工具，旨在通过交叉检查 **PubMed** 和 **Crossref** 数据库来验证医学参考文献的真实性，防止“幻觉”引用。

## 功能特性

*   **双数据库核查**:
    *   优先查询 **PubMed** (医学领域权威数据库)。
    *   如果未找到，自动回退查询 **Crossref** (通用学术数据库)。
*   **真实性验证**:
    *   确认论文是否真实存在。
    *   自动检索并返回论文的 **DOI** 或 **PMID**。
*   **RIS 导出 (EndNote 支持)**:
    *   自动抓取验证通过的文献的详细元数据（作者、期刊、年份、卷期页）。
    *   生成 `.ris` 文件，可直接导入 EndNote/Zotero。
*   **网络适应性**:
    *   内置了 **60秒超时** 设置，适应国内访问国外数据库可能较慢的情况。

    *   自动 **绕过 SSL 证书验证**，解决某些网络环境下无法连接 API 的问题。

## 使用方法

### 1. 准备文件
您可以使用以下任意格式的文件：
*   **Word 文档 (`.docx`)**: 支持直接读取 Word 格式的手稿或参考文献列表。
*   **文本文件 (`.txt`)**: 纯文本格式。
*   **Markdown 文件 (`.md`)**: 常见的标记语言格式。

*   **智能识别模式**: 如果您直接选择一篇完整的论文手稿（包含正文），工具会自动扫描并**只提取**参考文献部分（例如以 `1.` 或 `[1]` 开头的行），忽略正文。
*   **纯列表模式**: 如果您提供一个只包含参考文献的文件，它会逐行处理。

### 2. 运行工具

#### 方式一：使用便携版（推荐，无需安装 Python）
1.  进入 `dist` 文件夹。
2.  双击 **`Medical_Reference_Verifier.exe`**。
3.  在弹出的对话框中选择您的文件即可。
    *   此方式可在任何 Windows 电脑上运行，无需任何配置。

#### 方式二：使用脚本版（需要 Python 环境）
1.  **安装 Python**:
    *   访问 [Python 官网](https://www.python.org/downloads/) 下载并安装 Python 3.x。
    *   **重要**: 安装时请勾选 "Add Python to PATH"。
2.  **运行工具**:
    *   双击 `verify_medical_references.py` 或在命令行运行：
    ```bash
    python verify_medical_references.py
    ```

### 3. 查看结果
*   脚本会在控制台显示验证进度。
*   验证完成后，会在原文件旁边生成两个文件：
    1.  **验证报告** (`..._verification_report.txt`): 标记每一条引用是 `[FOUND]` 还是 `[NOT FOUND]`。
    2.  **EndNote 导入文件** (`..._verified_refs.ris`): 包含所有验证通过的文献详情。

## 环境要求

*   已安装 Python 3.x。
*   **无需安装任何第三方库** (本工具仅使用 Python 标准库 `urllib`, `json`, `re`)，真正的“开箱即用”。

## 常见问题 (Troubleshooting)

*   **超时 (Timeouts)**: 如果提示连接错误，请检查您的网络连接。由于访问的是 PubMed/Crossref 的国外服务器，偶尔可能会慢，脚本已设置为每个请求等待 60 秒。
*   **SSL 错误**: 脚本已默认配置为忽略 SSL 证书错误，通常不需要您做任何设置。

## EndNote 配合使用流程

如果您使用 EndNote 管理参考文献，可以按照以下步骤验证您的文献库：

1.  **导出参考文献**:
    *   在 EndNote 中选中您想要验证的文献（或 Ctrl+A 全选）。
    *   点击菜单 `File` -> `Export...`。
    *   **Save as type**: 选择 `Text File (*.txt)`。
    *   **Output Style**: 建议选择 `Annotated` 或 `Vancouver` 等包含完整标题和作者的格式。
    *   保存文件（例如 `endnote_export.txt`）。

2.  **运行验证**:
    *   运行本工具 (`verify_medical_references.py`)。
    *   在弹出的对话框中选择刚才导出的 `endnote_export.txt`。

3.  **修正文献库**:
    *   查看生成的报告。
    *   对于标记为 `[NOT FOUND]` 的文献，请回到 EndNote 中仔细检查标题、年份或作者拼写是否正确。
    *   对于标记为 `[FOUND]` 的文献，您可以放心地在论文中使用。


# Medical Manuscript Formatter

This tool converts Markdown (`.md`) manuscript drafts into strictly formatted Microsoft Word (`.docx`) documents suitable for academic submission (e.g., JCCT, Elsevier journals).

## Features

*   **Strict Formatting**:
    *   Font: Times New Roman, 12pt.
    *   Spacing: Double spacing for body text.
    *   Margins: 1 inch (2.54 cm) on all sides.
    *   Alignment: Left aligned (ragged right) with 0.5 inch first-line indent.
*   **Table Support**:
    *   Converts Markdown tables to "Three-Line Tables" (APA/Scientific style).
    *   **Full Width & Adaptive**: Tables are set to 100% of the page width with adaptive column widths (autofit).
    *   **Alignment**: Text is centered horizontally and vertically within cells.
    *   **Landscape Mode**: Automatically switches to Landscape orientation for tables with >6 columns.
    *   **Smart Layout**: Keeps table titles and footnotes on the same page as the table.
    *   **Clean Footnotes**: Correctly handles and removes horizontal rules following table footnotes.
    *   Single spacing for table content (for readability).
*   **Figure Legends**:
    *   **Selective Bolding**: Automatically bolds "Figure X" titles and Panel identifiers (e.g., "A.", "B.").
    *   **Strict Formatting**: Removes all other bold formatting within the legend text to adhere to strict submission guidelines.
    *   **No Indentation**: Legends are flush left.
    *   **Merged Panels**: Panel descriptions (A., B., etc.) are merged into the main legend paragraph.
    *   **Spacing**: Added spacing after each legend for readability.
*   **Abstract**:
    *   **Bold Text**: Supports bold text within the Abstract section (e.g., **Background:**).
*   **Manuscript Specifics**:
    *   **Line Numbering**: Automatically added for files named "Main" or "Manuscript".
    *   **Page Breaks**: Smartly managed to avoid blank pages between Abstract and Introduction.
    *   **Page Numbers**: Added to the footer (centered) in "PAGE X" format.
*   **Clean Up**:
    *   Removes Markdown horizontal rules (`---`).
    *   Removes bold formatting from body text (keeps headings bold).

## Usage

### Prerequisites

*   Python 3.x
*   `python-docx` library

```bash
pip install python-docx
```

### Running the Tool

You can run the script on a single file or a directory.

**1. Process all .md files in the current directory:**

```bash
python format_manuscript.py
```

**2. Process a specific directory:**

```bash
python format_manuscript.py "path/to/your/manuscript/folder"
```

**3. Process a single file:**

```bash
python format_manuscript.py "path/to/Main_Manuscript.md"
```

## Output

The tool will generate a `.docx` file next to each processed `.md` file.
*   `Main_Manuscript.md` -> `Main_Manuscript.docx`

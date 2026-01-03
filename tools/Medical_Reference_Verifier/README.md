# Medical Reference Verifier Tool

This is a standalone Python tool designed to verify the authenticity of medical references by cross-checking them against **PubMed** and **Crossref** databases.

## Features
- **Dual Database Check**: Prioritizes PubMed (Medical), falls back to Crossref (General).
- **Authenticity Verification**: Confirms that the paper actually exists and retrieves its DOI or PubMed ID.
- **Network Resilience**: Configured with extended timeouts (60s) and SSL bypass to handle unstable connections to foreign databases.

## How to Use

1.  **Prepare References**:
    - You can use a `.txt` file OR a `.md` (Markdown) file.
    - **Smart Detection**: 
        - If you open a full manuscript (Markdown), the tool will automatically find and extract only the lines that look like references (e.g., starting with `1.` or `[1]`).
        - If you open a raw list, it will process all lines.

2.  **Run the Tool**:
    - Double-click the script or run:
      ```bash
      python verify_medical_references.py
      ```
    - **A file dialog will pop up**. Select your `.txt` or `.md` file.

3.  **Check Results**:
    - The script will verify each reference.
    - A report file (e.g., `my_paper_refs_verification_report.txt`) will be created in the same folder as your input file.

## Requirements
- Python 3.x installed.
- No external libraries required (uses standard `urllib`, `json`, `re`).

## Troubleshooting
- **Timeouts**: If you see errors, check your internet connection. The script is set to wait 60 seconds per request.
- **SSL Errors**: The script is already configured to ignore SSL certificate errors, which are common when accessing these APIs from certain networks.

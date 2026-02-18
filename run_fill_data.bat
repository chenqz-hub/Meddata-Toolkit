@echo off
chcp 65001 > nul
echo ========================================
echo   填充 Case 数据工具
echo ========================================
echo.

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    echo 使用虚拟环境: .venv
    ".venv\Scripts\python.exe" "tools\fill_case_data.py"
) else (
    echo 使用系统 Python
    python "tools\fill_case_data.py"
)

echo.
pause

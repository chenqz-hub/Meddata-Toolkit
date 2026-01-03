@echo off
title Medical Manuscript Formatter
echo ==========================================
echo      Medical Manuscript Formatter
echo ==========================================
echo.
echo Checking dependencies...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo Error installing dependencies. Please check your internet connection.
    pause
    exit /b
)
echo Dependencies checked.
echo.
echo Starting Manuscript Formatter...
echo Please select your Markdown (.md) or Text (.txt) file in the dialog box.
echo.
python format_manuscript.py
echo.
echo Processing complete.
pause

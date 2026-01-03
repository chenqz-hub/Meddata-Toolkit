@echo off
echo Installing/Updating dependencies...
python -m pip install --upgrade pip
echo.
echo Starting Medical Reference Verifier...
python verify_medical_references.py
pause
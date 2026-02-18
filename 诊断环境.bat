@echo off
chcp 65001 >nul 2>&1
cls
echo ================================================
echo   环境诊断工具
echo ================================================
echo.
echo 正在检查环境配置...
echo.
D:/git/Meddata-Toolkit/.venv/Scripts/python.exe diagnose.py
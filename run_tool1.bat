@echo off
chcp 65001 >nul 2>&1
title 医疗数据工具 - 单文件多Sheet合并工具
cls
D:/git/Meddata-Toolkit/.venv/Scripts/python.exe tools\merge_tool_gui.py
echo.
echo ========================================
echo 工具已结束
echo ========================================
pause
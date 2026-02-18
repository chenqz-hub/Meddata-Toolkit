@echo off
chcp 65001 >nul 2>&1
title 医疗数据工具 - 重复记录去重工具
cls
D:/git/Meddata-Toolkit/.venv/Scripts/python.exe tools\deduplicate_tool.py
echo.
echo ========================================
echo 工具已结束
echo ========================================
pause
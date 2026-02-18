@echo off
chcp 65001 >nul 2>&1
title 医疗数据工具 - 字段唯一性检查工具
cls
D:/git/Meddata-Toolkit/.venv/Scripts/python.exe tools\check_join_fields.py
echo.
echo ========================================
echo 工具已结束
echo ========================================
pause
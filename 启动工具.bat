@echo off
chcp 65001 >nul
echo ========================================
echo   早发冠心病数据处理工具集
echo ========================================
echo.
echo 请选择要使用的工具：
echo.
echo   1. 单文件多Sheet合并工具
echo   2. 跨文件合并工具
echo   3. 重复记录去重工具
echo   4. 字段唯一性检查工具
echo   5. 退出
echo.
set /p choice="请输入选项 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 正在启动单文件多Sheet合并工具...
    python tools\merge_tool_gui.py
) else if "%choice%"=="2" (
    echo.
    echo 正在启动跨文件合并工具...
    python tools\cross_merge_gui.py
) else if "%choice%"=="3" (
    echo.
    echo 正在启动重复记录去重工具...
    python tools\deduplicate_tool.py
) else if "%choice%"=="4" (
    echo.
    echo 正在启动字段唯一性检查工具...
    python tools\check_join_fields.py
) else if "%choice%"=="5" (
    echo.
    echo 再见！
    exit
) else (
    echo.
    echo 无效选项，请重新运行脚本。
)

echo.
pause

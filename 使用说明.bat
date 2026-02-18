@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo   早发冠心病数据处理工具集
echo   使用说明
echo ========================================
echo.
echo 【方式1：主菜单（推荐新手）】
echo   双击: 启动工具.bat
echo   然后选择要使用的工具编号
echo.
echo 【方式2：直接启动（推荐熟练用户）】
echo   双击以下文件直接启动对应工具：
echo   • run_tool1.bat  -  单文件多Sheet合并工具
echo   • run_tool2.bat  -  跨文件合并工具
echo   • run_tool3.bat  -  重复记录去重工具
echo   • run_tool4.bat  -  字段唯一性检查工具
echo.
echo 【故障排除】
echo   如遇问题，请运行:
echo   • 诊断环境.bat  -  检查环境配置和依赖模块
echo.
echo 【注意事项】
echo   1. 工具会在新窗口中运行
echo   2. 请在弹出的文件选择对话框中选择文件
echo   3. 按照提示输入相关信息
echo   4. 处理完成后窗口会保持打开，可查看结果
echo.
echo ========================================
pause
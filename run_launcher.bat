@echo off
setlocal

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
set "PY=%ROOT%\.venv\Scripts\python.exe"

if not exist "%PY%" (
    echo [ERROR] 未找到项目虚拟环境解释器:
    echo         %PY%
    echo.
    echo 请先在项目根目录执行:
    echo   py -3 -m venv .venv
    echo   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist "%ROOT%\launcher.py" (
    echo [ERROR] 未找到项目启动脚本:
    echo         %ROOT%\launcher.py
    pause
    exit /b 1
)

echo 使用解释器: %PY%
"%PY%" -c "import os,runpy; runpy.run_path(os.path.join(r'%ROOT%','\u542f\u52a8\u5de5\u5177.py'), run_name='__main__')"
set "EC=%ERRORLEVEL%"

if not "%EC%"=="0" (
    echo.
    echo [ERROR] 启动失败，退出码: %EC%
    pause
)

exit /b %EC%

# VSCode 启动配置说明

## Python脚本替代bat文件

为了方便在VSCode中直接运行，已将bat脚本转换为Python版本：

### 1. 启动工具集 - `启动工具.py`

**原bat**: `启动工具.bat`

**运行方式**:
```bash
python 启动工具.py
```

或在VSCode中右键选择 "Run Python File"

**功能**:
- 单文件多Sheet合并工具
- 跨文件合并工具
- 重复记录去重工具
- 字段唯一性检查工具

### 2. 项目清理工具 - `清理项目.py`

**原bat**: `清理项目.bat`

**运行方式**:
```bash
python 清理项目.py
```

**功能**:
- 删除 `__pycache__` 缓存目录
- 删除 `.log` 日志文件
- 删除 `.pyc` 编译文件
- 移动旧Python脚本到 `archive/`
- 移动Excel输出文件到 `docs/`
- 清理临时文件

## VSCode 快捷方式配置

可以在 `.vscode/launch.json` 中添加快捷启动配置：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "启动工具集",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/启动工具.py",
            "console": "integratedTerminal"
        },
        {
            "name": "项目清理",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/清理项目.py",
            "console": "integratedTerminal"
        }
    ]
}
```

## VSCode 任务配置

也可以在 `.vscode/tasks.json` 中添加任务：

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "启动工具集",
            "type": "shell",
            "command": "python",
            "args": ["启动工具.py"],
            "problemMatcher": []
        },
        {
            "label": "清理项目",
            "type": "shell",
            "command": "python",
            "args": ["清理项目.py"],
            "problemMatcher": []
        }
    ]
}
```

然后使用 `Ctrl+Shift+P` -> `Tasks: Run Task` 来运行

## 优势

✅ **跨平台**: Python脚本可在Windows/Mac/Linux运行  
✅ **VSCode集成**: 可直接在VSCode中运行和调试  
✅ **错误提示**: 更好的错误处理和提示信息  
✅ **易于维护**: Python代码更容易理解和修改  
✅ **无需cmd**: 不需要打开命令提示符窗口

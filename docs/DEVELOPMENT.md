# 开发指南

## 1) 环境准备

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -U pip
pip install -r requirements-runtime.txt
pip install -r requirements.txt
```

- `requirements-runtime.txt`: 运行时最小依赖
- `requirements.txt`: 运行时 + 开发/可视化依赖

## 2) 运行项目

```bash
python 启动工具.py
```

或使用固定虚拟环境启动：

```bash
run_launcher.bat
```

## 3) 运行测试

```bash
pytest
```

## 4) 代码格式与类型检查

```bash
black src tests tools *.py
flake8 src tests tools
mypy src
```

## 5) 打包安装（可选）

```bash
pip install -e .
```

安装后可用命令：

```bash
mdip --help
```

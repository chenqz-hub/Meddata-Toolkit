# 贡献指南

感谢你为 Meddata-Toolkit 做贡献！

## 开发环境

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -U pip
pip install -r requirements-runtime.txt
pip install -r requirements.txt
```

## 提交前检查

```bash
pytest
black src tests tools *.py
flake8 src tests tools
```

## 提交流程建议

1. 从 `main` 拉取最新代码并创建功能分支。
2. 每个提交聚焦单一改动点，保持提交信息清晰。
3. 提交前通过测试与基础格式检查。
4. 在 PR 描述中说明：变更内容、验证方式、潜在影响。

## 代码约定

- 优先修复根因，避免临时性补丁。
- 保持变更最小化，不重构无关模块。
- 新增功能优先补充文档和示例。

# 修复 Streamlit Cloud 部署错误

## 常见错误原因

### 1. 导入路径问题

Streamlit Cloud 的工作目录可能与本地不同，导致导入失败。

**解决方案**：修改 `app/main.py` 中的导入路径。

### 2. 依赖安装失败

某些依赖可能无法安装或版本不兼容。

**解决方案**：检查 `requirements.txt` 并固定版本。

### 3. 文件路径问题

使用相对路径可能导致问题。

**解决方案**：使用绝对路径或 Streamlit 的路径处理。

## 查看错误日志

在 Streamlit Cloud Dashboard：
1. 点击你的应用
2. 查看 "Logs" 或 "Runtime logs"
3. 找到具体的错误信息

常见错误信息：
- `ModuleNotFoundError` - 导入错误
- `FileNotFoundError` - 文件路径错误
- `ImportError` - 模块导入失败

## 快速修复

### 修复导入路径

如果错误是导入相关的，需要修改 `app/main.py`：

```python
# 原来的代码（可能有问题）
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# 改为更健壮的方式
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 或者使用绝对路径
if project_root not in sys.path:
    sys.path.insert(0, str(project_root))
```

## 需要帮助

请提供 Streamlit Cloud 日志中的具体错误信息，我可以帮你精确修复。

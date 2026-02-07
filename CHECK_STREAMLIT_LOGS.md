# 如何查看 Streamlit Cloud 错误日志

## 查看日志步骤

1. **在 Streamlit Cloud Dashboard**：
   - 访问 https://share.streamlit.io/
   - 点击你的应用

2. **查看日志**：
   - 点击 "Manage app" 或应用设置
   - 找到 "Logs" 或 "Runtime logs" 标签
   - 查看错误信息

3. **常见错误位置**：
   - 构建日志（Build logs）- 安装依赖时的错误
   - 运行时日志（Runtime logs）- 应用运行时的错误

## 常见错误及解决方案

### 错误 1: ModuleNotFoundError

**错误信息**：
```
ModuleNotFoundError: No module named 'core'
```

**原因**：导入路径问题

**解决方案**：已修复在 `app/main.py` 中

### 错误 2: 依赖安装失败

**错误信息**：
```
ERROR: Could not find a version that satisfies the requirement...
```

**原因**：依赖版本不兼容

**解决方案**：固定依赖版本

### 错误 3: 文件路径错误

**错误信息**：
```
FileNotFoundError: [Errno 2] No such file or directory
```

**原因**：相对路径在 Streamlit Cloud 上不正确

**解决方案**：使用绝对路径或 Streamlit 的路径处理

## 请提供具体错误信息

如果你能看到日志，请把错误信息发给我，我可以精确修复。

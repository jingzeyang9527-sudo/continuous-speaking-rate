# Streamlit Cloud Python 版本问题修复

## 问题

Streamlit Cloud 默认使用 Python 3.13.12，但 `runtime.txt` 可能不被支持。

## 解决方案

### 方案 1: 升级依赖版本（推荐）

更新 `requirements.txt` 使用支持 Python 3.13 的版本：

```txt
librosa>=0.11.0
numba>=0.63.0
llvmlite>=0.46.0
```

### 方案 2: 使用 Streamlit Cloud 的 Python 版本选择

在 Streamlit Cloud Dashboard：
1. 进入应用设置
2. 查找 "Python version" 选项
3. 选择 Python 3.11 或 3.12

### 方案 3: 修改依赖约束

如果无法选择 Python 版本，可以：
1. 使用更新的 librosa 版本（0.11.0+ 支持 Python 3.13）
2. 或者移除对 numba 的依赖（如果可能）

## 当前状态

从日志看，依赖安装成功了（使用 pip），但应用启动失败。需要查看运行时错误日志。

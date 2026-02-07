# 🚀 Streamlit Cloud 部署指南

## 准备工作

### 1. 确保代码已推送到 GitHub

```bash
cd /data/jingzeyang/dsal_toolkit

# 如果还没有初始化 git
git init
git add .
git commit -m "Initial commit: DSAL toolkit with batch processing and data browser"

# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### 2. 检查必要文件

确保以下文件存在：
- ✅ `requirements.txt` - 依赖列表
- ✅ `app/main.py` - 主应用入口
- ✅ `.streamlit/config.toml` - Streamlit 配置（可选）
- ✅ `.gitignore` - 忽略大文件

### 3. 处理数据文件

**重要**：PPA 数据集太大，不能直接放在 GitHub 仓库中。

**选项 A：让用户上传数据**（推荐）
- 应用已经支持用户上传文件
- 批量处理后的 CSV 可以通过其他方式分享（Google Drive, Dropbox 等）

**选项 B：使用 GitHub Releases**
- 将处理后的 CSV 文件上传到 GitHub Releases
- 应用可以从 URL 加载数据

**选项 C：使用云存储**
- 上传 CSV 到 Google Drive / Dropbox
- 应用支持从公开 URL 加载

---

## 部署步骤

### 1. 访问 Streamlit Cloud

1. 打开 https://share.streamlit.io/
2. 点击 "Sign in" 使用 GitHub 账号登录
3. 授权 Streamlit Cloud 访问你的 GitHub 仓库

### 2. 创建新应用

1. 点击 "New app"
2. 填写信息：
   - **Repository**: 选择你的 GitHub 仓库
   - **Branch**: `main` (或你的主分支)
   - **Main file path**: `app/main.py`
   - **App URL**: 可以自定义（例如：`dsal-toolkit`）
3. 点击 "Deploy"

### 3. 等待部署

- Streamlit Cloud 会自动：
  - 安装依赖（从 `requirements.txt`）
  - 启动应用
  - 生成公网 URL

### 4. 访问应用

部署完成后，你会得到一个 URL，例如：
```
https://dsal-toolkit.streamlit.app
```

这个 URL 可以分享给任何人！

---

## 配置说明

### 应用配置

`.streamlit/config.toml` 已经配置好了，Streamlit Cloud 会自动使用。

### 环境变量（如果需要）

如果应用需要环境变量，在 Streamlit Cloud Dashboard 中：
1. 点击你的应用
2. 进入 "Settings" → "Secrets"
3. 添加环境变量（格式类似 `.streamlit/secrets.toml`）

---

## 更新应用

每次你推送代码到 GitHub，Streamlit Cloud 会自动重新部署：

```bash
git add .
git commit -m "Update app"
git push
```

Streamlit Cloud 会检测到更新并自动重新部署。

---

## 数据浏览器功能

要让数据浏览器工作，你需要：

### 方法 1：让用户上传 CSV

用户可以在数据浏览器页面手动上传处理后的 CSV 文件。

### 方法 2：从 URL 加载（需要修改代码）

我可以帮你修改代码，支持从公开 URL 加载 CSV（例如 Google Drive 分享链接）。

### 方法 3：使用示例数据

在仓库中放一个小样本 CSV 作为示例。

---

## 常见问题

### Q: 部署失败怎么办？

**检查**：
1. `requirements.txt` 是否包含所有依赖
2. `app/main.py` 是否存在
3. 查看 Streamlit Cloud 的日志（在 Dashboard 中）

### Q: 应用运行很慢？

**可能原因**：
- 首次加载需要安装依赖
- 处理大文件需要时间
- 免费版有资源限制

**解决方案**：
- 使用缓存功能（已经实现）
- 处理小样本数据
- 考虑升级到付费版

### Q: 如何分享数据文件？

**推荐方案**：
1. 将 CSV 上传到 Google Drive
2. 设置为"任何人可查看"
3. 获取分享链接
4. 我可以帮你修改代码支持从 URL 加载

---

## 下一步

1. **推送代码到 GitHub**
2. **访问 https://share.streamlit.io/ 部署**
3. **分享应用 URL 给其他人**

如果需要我帮你修改代码支持从 URL 加载数据，告诉我！

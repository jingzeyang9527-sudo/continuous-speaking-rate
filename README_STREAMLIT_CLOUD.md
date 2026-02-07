# 🚀 使用 Streamlit Cloud 部署（最简单）

## 快速开始（3 步）

### 1. 准备代码

```bash
cd /data/jingzeyang/dsal_toolkit

# 运行准备脚本
./prepare_for_streamlit_cloud.sh

# 或者手动检查：
# ✅ requirements.txt 存在
# ✅ app/main.py 存在
# ✅ .streamlit/config.toml 存在（可选）
```

### 2. 推送到 GitHub

```bash
# 如果还没有初始化 git
git init
git add .
git commit -m "DSAL toolkit ready for Streamlit Cloud"

# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 3. 部署到 Streamlit Cloud

1. 访问 https://share.streamlit.io/
2. 用 GitHub 账号登录
3. 点击 "New app"
4. 填写：
   - **Repository**: 选择你的仓库
   - **Branch**: `main`
   - **Main file path**: `app/main.py`
   - **App URL**: 可以自定义（例如：`dsal-toolkit`）
5. 点击 "Deploy"

**完成！** 几分钟后你会得到一个公网 URL，例如：
```
https://dsal-toolkit.streamlit.app
```

---

## 功能说明

### ✅ 已支持的功能

1. **单个文件分析**：用户可以上传音频文件进行分析
2. **数据浏览器**：支持上传 CSV 文件查看批量处理结果
3. **所有特征提取**：pause analysis, speaking rate, prosody 等

### 📊 数据文件处理

由于 PPA 数据集太大，不能放在 GitHub 仓库中。解决方案：

**方案 1：用户上传 CSV**（已实现）
- 在数据浏览器页面，用户可以上传处理后的 CSV 文件
- 支持所有浏览和对比功能

**方案 2：从 URL 加载**（可选）
- 我可以帮你添加从 Google Drive / Dropbox 链接加载数据的功能

**方案 3：示例数据**
- 在仓库中放一个小样本 CSV 作为演示

---

## 更新应用

每次你推送代码到 GitHub，Streamlit Cloud 会自动重新部署：

```bash
git add .
git commit -m "Update features"
git push
```

---

## 常见问题

### Q: 部署失败？

**检查**：
- `requirements.txt` 是否包含所有依赖
- `app/main.py` 路径是否正确
- 查看 Streamlit Cloud Dashboard 中的日志

### Q: 如何分享数据？

**推荐**：
1. 批量处理生成 CSV：`python batch_process_ppa.py ...`
2. 上传 CSV 到 Google Drive，设置为"任何人可查看"
3. 用户可以在数据浏览器中上传 CSV 文件

### Q: 应用运行慢？

- 首次加载需要安装依赖（正常）
- 处理大文件需要时间
- 免费版有资源限制

---

## 详细文档

查看 `STREAMLIT_CLOUD_DEPLOY.md` 了解更多细节。

# 🚀 DSAL 部署方案总览

## 如果你没有服务器

**推荐方案：使用 ngrok（最简单）**

1. **安装 ngrok**：
   ```bash
   # 从 https://ngrok.com/download 下载
   # 或使用 snap
   sudo snap install ngrok
   ```

2. **注册并配置**（免费）：
   - 访问 https://ngrok.com/ 注册账号
   - 获取 authtoken
   - 运行：`ngrok config add-authtoken YOUR_TOKEN`

3. **启动应用**：
   ```bash
   # 终端1：启动 Streamlit
   cd /data/jingzeyang/dsal_toolkit
   source .venv/bin/activate
   streamlit run app/main.py --server.port 8501
   
   # 终端2：启动 ngrok
   ngrok http 8501
   ```

4. **分享 URL**：
   - ngrok 会给你一个公网 URL（例如：`https://abc123.ngrok-free.app`）
   - 把这个 URL 分享给其他人即可访问

**详细说明**：查看 `DEPLOYMENT_NO_SERVER.md`

---

## 其他方案

- **Streamlit Cloud**：官方免费云服务（需要 GitHub）
- **Railway/Render**：其他云平台（有免费额度）
- **局域网访问**：同一网络内分享（最简单但限制最大）

**详细对比和步骤**：查看 `DEPLOYMENT_NO_SERVER.md`

---

## 如果你有服务器

查看 `DEPLOYMENT.md` 了解详细配置步骤。

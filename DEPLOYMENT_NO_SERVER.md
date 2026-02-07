# DSAL 部署方案（无需自有服务器）

如果你没有自己的服务器，可以使用以下几种方式让其他人访问你的应用：

## 方案 1: 使用 ngrok（内网穿透，最简单）⭐ 推荐

ngrok 可以将你的本地应用暴露到公网，免费且简单。

### 安装 ngrok

```bash
# 下载 ngrok（Linux）
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# 或者使用包管理器
# Ubuntu/Debian
sudo snap install ngrok

# 或者从官网下载：https://ngrok.com/download
```

### 注册并获取 token

1. 访问 https://ngrok.com/ 注册免费账号
2. 获取你的 authtoken
3. 配置：

```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

### 启动应用和 ngrok

**终端 1：启动 Streamlit**
```bash
cd /data/jingzeyang/dsal_toolkit
source .venv/bin/activate
streamlit run app/main.py --server.port 8501
```

**终端 2：启动 ngrok**
```bash
ngrok http 8501
```

ngrok 会给你一个公网 URL，例如：`https://abc123.ngrok-free.app`

**其他人就可以通过这个 URL 访问你的应用了！**

### ngrok 免费版限制
- 每次重启 URL 会变化（可以付费固定域名）
- 有连接数限制
- 适合测试和小规模使用

---

## 方案 2: 使用 Streamlit Cloud（官方云服务）⭐ 推荐

Streamlit 提供免费的云托管服务。

### 准备工作

1. **创建 GitHub 仓库**
```bash
cd /data/jingzeyang/dsal_toolkit
git init
git add .
git commit -m "Initial commit"
# 在 GitHub 创建新仓库，然后：
git remote add origin https://github.com/YOUR_USERNAME/dsal_toolkit.git
git push -u origin main
```

2. **创建 requirements.txt**（已经有了）

3. **创建 .streamlit/config.toml**（已经有了）

4. **部署到 Streamlit Cloud**
   - 访问 https://share.streamlit.io/
   - 用 GitHub 账号登录
   - 点击 "New app"
   - 选择你的仓库和 `app/main.py`
   - 点击 "Deploy"

### 注意事项
- 免费版有资源限制
- 应用会在不活跃时休眠
- 需要将代码推送到 GitHub（公开或私有仓库都可以）

---

## 方案 3: 使用 Railway（简单云部署）

Railway 提供简单的云部署，有免费额度。

### 步骤

1. **注册 Railway**：https://railway.app/

2. **创建 railway.json 配置文件**：

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run app/main.py --server.port $PORT --server.address 0.0.0.0",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

3. **在 Railway 中**：
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库
   - Railway 会自动检测并部署

---

## 方案 4: 使用 Render（免费云服务）

Render 提供免费 tier，适合小型应用。

### 步骤

1. **注册 Render**：https://render.com/

2. **创建 render.yaml**：

```yaml
services:
  - type: web
    name: dsal-toolkit
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app/main.py --server.port $PORT --server.address 0.0.0.0
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
```

3. **在 Render Dashboard**：
   - 点击 "New +" → "Web Service"
   - 连接 GitHub 仓库
   - Render 会自动部署

---

## 方案 5: 局域网访问（同一网络内）

如果你只是想在同一局域网内分享（比如办公室、实验室），不需要公网：

### 启动应用

```bash
cd /data/jingzeyang/dsal_toolkit
source .venv/bin/activate
streamlit run app/main.py --server.port 8501 --server.address 0.0.0.0
```

### 获取你的内网 IP

```bash
# Linux
hostname -I
# 或
ip addr show | grep "inet " | grep -v 127.0.0.1
```

### 其他人访问

在同一局域网内的其他人可以通过以下地址访问：
```
http://YOUR_LOCAL_IP:8501
```

例如：`http://192.168.1.100:8501`

---

## 方案对比

| 方案 | 难度 | 成本 | 稳定性 | 适用场景 |
|------|------|------|--------|----------|
| ngrok | ⭐ 简单 | 免费 | ⭐⭐⭐ | 测试、演示 |
| Streamlit Cloud | ⭐⭐ 中等 | 免费 | ⭐⭐⭐⭐ | 公开分享、研究 |
| Railway | ⭐⭐ 中等 | 免费额度 | ⭐⭐⭐⭐ | 生产环境 |
| Render | ⭐⭐ 中等 | 免费额度 | ⭐⭐⭐⭐ | 生产环境 |
| 局域网 | ⭐ 简单 | 免费 | ⭐⭐⭐⭐⭐ | 内部使用 |

---

## 推荐方案

**快速测试/演示**：使用 **ngrok**（5分钟搞定）

**长期使用/分享**：使用 **Streamlit Cloud**（免费且稳定）

**需要更多控制**：使用 **Railway** 或 **Render**

**仅内部使用**：使用 **局域网访问**

---

## 快速开始（ngrok 方案）

```bash
# 1. 安装 ngrok（如果还没安装）
# 从 https://ngrok.com/download 下载

# 2. 配置 authtoken（注册后获取）
ngrok config add-authtoken YOUR_TOKEN

# 3. 启动 Streamlit（终端1）
cd /data/jingzeyang/dsal_toolkit
source .venv/bin/activate
streamlit run app/main.py --server.port 8501

# 4. 启动 ngrok（终端2）
ngrok http 8501

# 5. 复制 ngrok 给你的 URL（例如：https://abc123.ngrok-free.app）
# 分享这个 URL 给其他人！
```

---

## 数据文件处理

**重要**：如果你使用云服务部署，需要处理数据文件：

1. **小数据集**：可以直接包含在仓库中
2. **大数据集**：使用云存储（AWS S3, Google Cloud Storage等）
3. **或者**：让用户上传自己的数据文件

对于 PPA 数据集，建议：
- 批量处理后的 CSV 文件可以上传到云存储
- 或者让应用支持从 URL 加载数据

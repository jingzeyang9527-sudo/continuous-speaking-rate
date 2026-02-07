# DSAL 快速启动指南

## 1. 批量处理 PPA 数据集

### 测试运行（处理 100 个文件）

```bash
cd /data/jingzeyang/dsal_toolkit
source .venv/bin/activate
python batch_process_ppa.py --root /data/jingzeyang/ppa --output ppa_features_test.csv --max-files 100
```

### 完整处理（所有 3634 个文件）

```bash
# 这会运行几个小时，建议在 screen 或 tmux 中运行
screen -S batch_process
python batch_process_ppa.py --root /data/jingzeyang/ppa --output ppa_features.csv
# 按 Ctrl+A 然后 D 来 detach
```

### 按亚型分别处理

```bash
# 只处理 nfvPPA
python batch_process_ppa.py --root /data/jingzeyang/ppa --output ppa_features_nfvppa.csv --subtype nfvppa

# 只处理 lvPPA
python batch_process_ppa.py --root /data/jingzeyang/ppa --output ppa_features_lvppa.csv --subtype lvppa

# 只处理 svPPA
python batch_process_ppa.py --root /data/jingzeyang/ppa --output ppa_features_svppa.csv --subtype svppa

# 只处理 controls
python batch_process_ppa.py --root /data/jingzeyang/ppa --output ppa_features_controls.csv --subtype controls
```

## 2. 启动 Web 应用（本地访问）

```bash
cd /data/jingzeyang/dsal_toolkit
source .venv/bin/activate
streamlit run app/main.py
```

然后在浏览器打开：`http://localhost:8501`

## 3. 启动 Web 应用（公网访问）

### 方案 A: 使用 ngrok（推荐，无需服务器）⭐

ngrok 可以将本地应用暴露到公网，免费且简单。

```bash
# 1. 安装 ngrok（如果还没安装）
# 从 https://ngrok.com/download 下载，或：
sudo snap install ngrok

# 2. 注册并配置（免费）
# 访问 https://ngrok.com/ 注册，获取 authtoken
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

**快速设置脚本**：
```bash
./setup_ngrok.sh
```

### 方案 B: 使用 Streamlit Cloud（官方云服务）⭐

1. 将代码推送到 GitHub
2. 访问 https://share.streamlit.io/
3. 用 GitHub 账号登录并部署

详细步骤见 `DEPLOYMENT_NO_SERVER.md`

### 方案 C: 局域网访问（同一网络内）

```bash
cd /data/jingzeyang/dsal_toolkit
source .venv/bin/activate
streamlit run app/main.py --server.port 8501 --server.address 0.0.0.0
```

获取你的内网 IP：
```bash
hostname -I
```

其他人访问：`http://YOUR_LOCAL_IP:8501`

### 方案 D: 自有服务器（如果有）

```bash
cd /data/jingzeyang/dsal_toolkit
./start_server.sh
```

详细配置见 `DEPLOYMENT.md`

## 4. 使用数据浏览器

1. 启动应用后，在左侧边栏会看到 "📊 Data Browser" 页面
2. 点击进入数据浏览器
3. 在侧边栏输入 CSV 文件路径（默认：`ppa_features.csv`）
4. 使用过滤器查看不同亚型的数据
5. 在 "Comparison" 标签页对比不同 PPA 亚型的特征

## 5. 功能说明

### 主页面（Audio Analysis）
- 上传或选择 PPA 数据集中的音频文件
- 实时分析单个文件
- 查看所有提取的特征（pause, speaking rate, prosody）

### 数据浏览器（Data Browser）
- 浏览已处理的所有文件
- 按亚型、时长等条件过滤
- 对比不同 PPA 亚型的统计特征
- 导出筛选后的数据

## 6. 故障排除

### 导入错误
```bash
# 清除 Python 缓存
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
find . -name "*.pyc" -delete
```

### 端口被占用
```bash
# 查找占用端口的进程
sudo lsof -i :8502
# 杀死进程
sudo kill -9 <PID>
```

### 数据浏览器显示 "No processed data found"
确保已经运行了批量处理脚本并生成了 CSV 文件。

## 7. 性能优化

- 批量处理建议在后台运行（使用 screen/tmux）
- 大数据集处理可能需要几个小时
- 可以先处理一个亚型测试流程
- 使用 `--max-files` 参数进行小规模测试

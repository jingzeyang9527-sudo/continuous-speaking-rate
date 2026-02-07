# 🧪 部署后测试指南

部署到 Streamlit Cloud 后，使用这个指南来验证所有功能是否正常工作。

## 1. 基本访问测试

### ✅ 应用可以访问
- [ ] 打开 Streamlit Cloud 给你的 URL（例如：`https://continuous-speaking-rate.streamlit.app`）
- [ ] 页面正常加载，没有错误
- [ ] 看到 "🎤 Disordered Speech Analysis Library (DSAL)" 标题

### ✅ 页面导航
- [ ] 左侧边栏可以看到页面列表
- [ ] 可以切换到 "📊 Data Browser" 页面
- [ ] 页面切换流畅，没有错误

---

## 2. 主页面功能测试（Audio Analysis）

### ✅ 文件上传功能
- [ ] 点击文件上传器
- [ ] 可以选择 `.wav` 文件
- [ ] 文件上传后显示文件信息

### ✅ 音频播放器
- [ ] 在侧边栏 "Advanced Options" 中启用 "Show Audio Player"
- [ ] 上传文件后可以看到音频播放控件
- [ ] 可以播放音频

### ✅ 分析功能
- [ ] 调整参数（ZCR Threshold, Minimum Pause Duration）
- [ ] 点击 "🔍 Analyze" 按钮
- [ ] 看到进度条和状态提示
- [ ] 分析完成后显示结果

### ✅ 指标显示
- [ ] 看到 4 个主要指标卡片：
  - Pathological Pause Rate
  - Breath Frequency
  - Pathological Duration
  - Breath Count
- [ ] 看到 Speaking Rate & Articulation Rate 部分
- [ ] 看到 Prosody Features 部分（F0, Jitter, Shimmer, Intensity）
- [ ] 所有指标都有合理的数值（不是全部为 0 或 NaN）

### ✅ 可视化
- [ ] 看到波形图
- [ ] 看到包络线（黑色）
- [ ] 如果有停顿，看到绿色（breath）和红色（pathological）区域
- [ ] 图表可以正常显示

### ✅ 详细列表
- [ ] 展开 "View Detailed Segment List"
- [ ] 看到表格显示所有检测到的段落
- [ ] 表格包含：start, end, duration, type, zcr, energy 列

### ✅ 导出功能
- [ ] 点击 "Download Segments (CSV)" 按钮
- [ ] CSV 文件可以下载
- [ ] 下载的文件可以正常打开

---

## 3. 数据浏览器功能测试（Data Browser）

### ✅ 页面加载
- [ ] 切换到 "📊 Data Browser" 页面
- [ ] 页面正常加载

### ✅ CSV 文件上传
- [ ] 在侧边栏看到 "Upload Features CSV" 选项
- [ ] 可以上传 CSV 文件（从 `batch_process_ppa.py` 生成的）
- [ ] 上传后显示记录数量

### ✅ 数据浏览
- [ ] 在 "Overview" 标签页看到：
  - 总文件数
  - 总时长
  - 亚型分布饼图
  - 指标分布直方图
- [ ] 在 "Search" 标签页可以搜索文件
- [ ] 在 "Comparison" 标签页可以看到不同亚型的对比

### ✅ 过滤功能
- [ ] 可以按亚型过滤（如果 CSV 中有 subtype 列）
- [ ] 可以按时长范围过滤
- [ ] 过滤后数据正确更新

### ✅ 导出功能
- [ ] 可以下载过滤后的 CSV
- [ ] 可以按亚型分别下载

---

## 4. 性能测试

### ✅ 响应速度
- [ ] 页面加载时间合理（< 10 秒）
- [ ] 文件上传响应及时
- [ ] 分析功能在合理时间内完成（取决于文件大小）

### ✅ 缓存功能
- [ ] 启用 "Cache Results" 选项
- [ ] 重复分析相同文件时使用缓存（更快）
- [ ] 侧边栏显示 "✅ Using cached results"

---

## 5. 错误处理测试

### ✅ 无效文件处理
- [ ] 上传非 WAV 文件，显示错误提示
- [ ] 上传损坏的文件，显示友好的错误信息

### ✅ 空数据处理
- [ ] 上传没有停顿的音频，指标显示为 0（正常）
- [ ] 上传空的 CSV，显示提示信息

---

## 6. 多用户测试（如果可能）

### ✅ 并发访问
- [ ] 多个用户同时访问应用
- [ ] 每个用户的分析互不干扰
- [ ] 缓存对每个用户独立

---

## 常见问题排查

### ❌ 应用无法访问
- 检查 Streamlit Cloud Dashboard 中的日志
- 确认部署状态是 "Running"
- 检查是否有构建错误

### ❌ 导入错误
- 检查 `requirements.txt` 是否包含所有依赖
- 查看 Streamlit Cloud 的构建日志

### ❌ 功能不工作
- 打开浏览器开发者工具（F12）查看控制台错误
- 检查 Streamlit Cloud 的运行时日志

### ❌ 数据浏览器显示 "No processed data found"
- 这是正常的，需要用户上传 CSV 文件
- 或者修改代码支持从 URL 加载数据

---

## 测试报告模板

```
部署 URL: https://________________.streamlit.app
部署时间: ________________
测试时间: ________________

基本功能: ✅ / ❌
- 页面访问: ✅ / ❌
- 文件上传: ✅ / ❌
- 分析功能: ✅ / ❌
- 数据浏览器: ✅ / ❌

性能: ✅ / ❌
- 加载速度: ✅ / ❌
- 分析速度: ✅ / ❌

问题记录:
1. ________________
2. ________________

总体评估: ✅ 通过 / ❌ 需要修复
```

---

## 下一步

如果所有测试通过：
- ✅ 应用已成功部署
- ✅ 可以分享 URL 给其他人使用
- ✅ 可以开始批量处理 PPA 数据集

如果发现问题：
- 查看 Streamlit Cloud Dashboard 的日志
- 检查代码是否有错误
- 参考 `STREAMLIT_CLOUD_DEPLOY.md` 中的故障排除部分

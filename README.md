# AI简报MVP

追踪科技创业者、研究者与投资人的前沿动态，每日自动化生成个性化简报。

## ✨ 功能特性

- ✅ **资讯聚合**: 从Readhub等来源爬取AI相关资讯
- ✅ **智能整理**: 自动分类整理为4大板块
  - ⚡ 今日速览
  - 🚀 新产品预告与发布
  - 💡 大佬观点
  - 💰 投融资动态
- ✅ **H5展示**: 响应式网页设计，完美适配移动端
- ✅ **播客转换**: 使用edge-tts实现真实的文本转语音
- ✅ **观点提炼**: 强调判断、立场与潜在影响，避免简单转述

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install edge-tts beautifulsoup4
```

### 2. 生成播客音频

```bash
python podcast-service.py
```

这将：
1. 解析HTML文件提取内容
2. 生成优化的播客脚本
3. 使用微软edge-tts合成语音
4. 保存音频文件到 `podcasts/` 目录

输出示例：
```
✅ 音频生成成功!
📁 文件位置: podcasts/ai_brief_20260302_225137.mp3
📊 文件大小: 2.60 MB
```

### 3. 启动本地服务器

```bash
python start-server.py
```

服务器将自动在浏览器中打开：http://localhost:8000

### 4. 收听播客

在H5页面中：
1. 点击 "🎧 收听播客" 按钮
2. 如果音频已生成，会自动显示播放器
3. 可以直接播放或下载音频

## 📁 项目结构

```
AI简报/
├── ai-daily-brief.html       # H5简报页面（含音频播放器）
├── podcast-service.py        # 播客生成服务（已实现真实TTS）
├── start-server.py           # 本地HTTP服务器
├── generate-brief.py         # 自动化生成脚本
├── requirements.txt          # 依赖列表
└── podcasts/                 # 播客音频目录
    ├── ai_brief_20260302_225137.mp3   # 已生成的音频
    └── ai_brief_script_*.txt          # 播客脚本
```

## 🎙️ 播客功能详解

### 技术实现

使用 **edge-tts**（微软Edge浏览器的TTS服务）：

- ✅ 完全免费
- ✅ 支持中文
- ✅ 音质优秀（新闻播报风格）
- ✅ 需要联网

### 备选方案

如果需要离线TTS，可使用 **pyttsx3**：

```bash
pip install pyttsx3
```

修改 `podcast-service.py` 中的调用方式即可。

### 语音选项

代码中预设了3种中文语音：

```python
voice_options = {
    'female': 'zh-CN-XiaoxiaoNeural',  # 女声（温柔）
    'male': 'zh-CN-YunyangNeural',     # 男声
    'news': 'zh-CN-XiaoyiNeural',      # 新闻播报风格（默认）
}
```

可在代码中修改 `default_voice` 切换语音。

## 📱 H5页面功能

### 音频播放器

当检测到 `podcasts/` 目录中有音频文件时：

1. **自动检测**: 页面加载时自动查找可用音频
2. **播放控制**: 标准HTML5音频控制器
3. **下载功能**: 一键下载音频文件
4. **响应式设计**: 完美适配手机端

### 导航功能

底部固定导航栏，快速切换板块：
- ⚡ 速览
- 🚀 产品
- 💡 观点
- 💰 融资
- 📊 报告

## 📊 今日简报内容

### ⚡ 速览

- 英伟达3月15日发布"世界前所未见"的革命性AI芯片
- 苹果3月推出整合Gemini的新一代Siri
- 2026年前7周：17家AI公司融资540亿美元

### 🚀 新产品

- 英伟达GTC 2026：Rubin CPX/Feynman架构，SRAM集成、3D堆叠突破
- 苹果AI生态：Siri + Gemini + 自研搜索

### 💡 大佬观点

- 黄仁勋：AI芯片逼近物理极限，需要架构革命
- 行业共识：2026年是AI商业化落地关键年
- VC判断：AI、具身智能、生物制造将诞生百亿独角兽

### 💰 投融资

- Anthropic：300亿美元G轮，估值3800亿美元
- xAI：200亿美元，后被SpaceX收购
- 2026年1月诞生9家新AI独角兽

## 🔧 技术栈

- **前端**: HTML5, CSS3, JavaScript (原生)
- **后端**: Python 3.8+
- **TTS**: edge-tts (微软免费服务)
- **HTML解析**: BeautifulSoup4
- **HTTP服务器**: Python内置 http.server

## 📝 使用场景

1. **每日通勤**: 生成音频，路上收听
2. **团队分享**: 部署到内网，团队成员订阅
3. **个人知识库**: 归档历史简报，建立知识库
4. **RSS订阅**: 可扩展为RSS播客源

## 🎯 高级功能

### 自动化每日更新（开发中）

```bash
python generate-brief.py
```

这将：
1. 自动从Readhub爬取最新资讯
2. 更新HTML内容
3. 生成新的播客音频
4. 可配合cron定时任务实现每日自动更新

### RSS订阅源（开发中）

可将生成的音频文件打包为RSS播客源，方便在播客客户端中订阅。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可

MIT License

## 🔗 相关链接

- [Readhub](https://readhub.cn)
- [edge-tts GitHub](https://github.com/rany2/edge-tts)
- [项目演示](http://localhost:8000)

---

**生成时间**: 2026年3月2日
**版本**: v1.0.0 MVP
**状态**: ✅ 播客功能已完整实现

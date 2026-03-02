# ☁️ AI简报云端部署方案

24/7自动运行，无需本地电脑开机！

---

## 🎯 推荐方案对比

| 方案 | 难度 | 免费额度 | 推荐度 |
|------|------|----------|--------|
| **GitHub Actions** | ⭐ 简单 | 2000分钟/月 | ⭐⭐⭐⭐⭐ |
| **Railway** | ⭐⭐ 中等 | $5/月 | ⭐⭐⭐⭐ |
| **阿里云函数** | ⭐⭐ 中等 | 100万次调用/月 | ⭐⭐⭐⭐ |
| **Render** | ⭐⭐ 中等 | 750小时/月 | ⭐⭐⭐ |

---

## 方案1：GitHub Actions（推荐，完全免费）

### 优点
- ✅ 完全免费
- ✅ 无需服务器
- ✅ 支持手动触发
- ✅ 自动记录日志

### 配置步骤

#### 1. 创建GitHub仓库

```bash
cd /Users/baoying/Desktop/AI简报
git init
git add .
git commit -m "Initial commit"

# 在GitHub上创建新仓库后
git remote add origin https://github.com/你的用户名/ai-brief.git
git push -u origin main
```

#### 2. 创建GitHub Actions配置文件

在项目根目录创建 `.github/workflows/daily-update.yml`:

```yaml
name: AI简报每日更新

on:
  schedule:
    - cron: '0 23 * * *'  # UTC时间23点 = 北京时间7点
  workflow_dispatch:      # 支持手动触发

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
    - name: 检出代码
      uses: actions/checkout@v3

    - name: 设置Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: 安装依赖
      run: |
        pip install edge-tts

    - name: 运行更新脚本
      run: |
        python cloud-update.py
      env:
        # 如果需要搜索API，在这里添加环境变量
        # SEARCH_API_KEY: ${{ secrets.SEARCH_API_KEY }}

    - name: 提交更改
      run: |
        git config --local user.email "github-actions[bot]@users.noreply.github.com"
        git config --local user.name "github-actions[bot]"
        git add podcasts/
        git add ai-daily-brief.html
        git diff --quiet && git diff --staged --quiet || git commit -m "🤖 自动更新: $(date +'%Y-%m-%d')"
        git push
```

#### 3. 创建云端更新脚本

创建 `cloud-update.py`（见下方）

#### 4. 推送到GitHub

```bash
git add .
git commit -m "Add cloud deployment"
git push
```

#### 5. 启用Actions

在GitHub仓库页面：
- 点击 "Actions" 标签
- 选择 "AI简报每日更新" workflow
- 点击 "Enable workflow"

#### 6. 手动测试

在Actions页面，点击 "Run workflow" 手动触发一次

---

## 方案2：Railway（推荐，功能强大）

### 优点
- ✅ 支持定时任务
- ✅ 持续运行
- ✅ 简单部署
- ✅ 自动重启

### 配置步骤

#### 1. 安装Railway CLI

```bash
npm install -g @railway/cli
```

#### 2. 登录Railway

```bash
railway login
```

#### 3. 创建项目

```bash
cd /Users/baoying/Desktop/AI简报
railway init
```

#### 4. 配置项目

创建 `railway.json`:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python railway-cron.py",
    "healthcheckPath": "/health"
  }
}
```

#### 5. 部署

```bash
railway up
```

#### 6. 设置环境变量

在Railway控制台添加：
- `PYTHON_VERSION`: 3.10
- 其他需要的环境变量

#### 7. 配置定时任务

在Railway控制台设置cron表达式

---

## 方案3：阿里云函数计算（国内）

### 优点
- ✅ 国内访问快
- ✅ 免费额度大
- ✅ 按需付费

### 配置步骤

#### 1. 安装阿里云CLI

```bash
# macOS
brew install aliyun-cli

# 配置
aliyun configure
```

#### 2. 创建函数

使用FunCLI工具：

```bash
npm install -g @alicloud/funcli
fun init
```

#### 3. 配置函数

创建 `template.yml`:

```yaml
ROSTemplateFormatVersion: '2015-09-01'
Transform: 'Aliyun::Serverless-2018-04-03'
Resources:
    ai-brief-service:
        Type: 'Aliyun::Serverless::Service'
        Properties:
            Description: 'AI简报每日更新'
        LogConfig:
            Project: ai-brief-logs
        ai-brief-function:
            Type: 'Aliyun::Serverless::Function'
            Properties:
                Handler: index.handler
                Runtime: python3.10
                CodeUri: ./
                Timeout: 300
                MemorySize: 512
                Events:
                    - Timer:
                        Type: Timer
                        Properties:
                            CronExpression: '0 0 7 * * *'  # 每天早上7点
                            Input: '{}'
```

#### 4. 部署

```bash
fun deploy
```

---

## 📁 需要创建的文件

### cloud-update.py
云端更新脚本（支持GitHub Actions、Railway等）

### railway-cron.py
Railway专用脚本

### .github/workflows/daily-update.yml
GitHub Actions配置

### requirements.txt
Python依赖

---

## 🔧 管理云端任务

### GitHub Actions
- 查看运行：仓库 → Actions
- 查看日志：点击具体的运行记录
- 手动触发：Actions → 选择workflow → Run workflow
- 修改时间：编辑`.yml`文件中的cron表达式

### Railway
- 查看日志：项目 → Deployments → Logs
- 查看监控：项目 → Metrics
- 修改配置：项目 → Settings

### 阿里云函数
- 查看日志：函数计算 → 日志查询
- 监控：函数计算 → 监控
- 修改触发器：函数计算 → 触发器管理

---

## 💡 选择建议

| 需求 | 推荐方案 |
|------|----------|
| 完全免费 | GitHub Actions |
| 需要API密钥 | Railway |
| 国内访问快 | 阿里云函数 |
| 需要数据库 | Railway |
| 简单快速 | GitHub Actions |

---

## ✅ 快速开始（GitHub Actions）

```bash
# 1. 创建GitHub仓库并推送代码
cd /Users/baoying/Desktop/AI简报
git init
git add .
git commit -m "Initial commit"

# 2. 在GitHub创建仓库后，执行：
git remote add origin https://github.com/你的用户名/ai-brief.git
git push -u origin main

# 3. 在GitHub上启用Actions
# 仓库 → Actions → I understand my workflows → Enable

# 4. 手动测试
# Actions → AI简报每日更新 → Run workflow
```

---

## 🎉 完成！

现在你的AI简报可以：
- ☁️ 24/7自动运行
- 🌍 全球可访问
- 📝 自动记录日志
- 🔄 自动提交更新
- 💰 完全免费（GitHub Actions）

详细步骤请查看各方案的具体配置文件！

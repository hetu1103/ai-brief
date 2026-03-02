# 🚀 GitHub Actions 部署指南（最简单，完全免费）

## ✅ 5分钟完成部署

### 步骤1: 创建GitHub仓库

```bash
cd /Users/baoying/Desktop/AI简报

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: AI简报自动化"

# 创建GitHub仓库后，执行：
# 替换 YOUR_USERNAME 为你的GitHub用户名
git remote add origin https://github.com/YOUR_USERNAME/ai-brief.git
git branch -M main
git push -u origin main
```

### 步骤2: 在GitHub上创建仓库

1. 访问 https://github.com/new
2. 仓库名称：`ai-brief`
3. 设置为 **Public**（免费账户需要公开仓库才能用Actions）
4. **不要**勾选 "Add a README file"
5. 点击 "Create repository"

### 步骤3: 推送代码

```bash
# 执行步骤1中的推送命令
git push -u origin main
```

### 步骤4: 启用GitHub Actions

1. 访问你的仓库页面
2. 点击 **Settings** 标签
3. 左侧菜单找到 **Actions** → **General**
4. 滚动到底部
5. 选择 **Allow all actions and reusable workflows**
6. 点击 **Save**

### 步骤5: 验证Actions

1. 点击 **Actions** 标签
2. 应该能看到 "AI简报每日更新" workflow
3. 点击进入，然后点击 **I understand my workflows, go ahead and enable them**
4. 点击 **Enable workflow**

### 步骤6: 手动测试（可选）

1. 在Actions页面
2. 点击 "AI简报每日更新"
3. 点击 **Run workflow** → **Run workflow**
4. 等待执行完成（约2-3分钟）

---

## ⏰ 修改执行时间

编辑 `.github/workflows/daily-update.yml` 文件：

```yaml
schedule:
  # UTC时间，北京时间需要+8小时
  # 示例：
  #  0 23 * * *  = 北京时间07:00
  #  0 0 * * *   = 北京时间08:00
  # 30 1 * * *  = 北京时间09:30
  - cron: '0 23 * * *'
```

修改后需要：
```bash
git add .github/workflows/daily-update.yml
git commit -m "修改执行时间"
git push
```

---

## 📊 查看运行状态

### 查看历史记录
```
仓库页面 → Actions → 选择workflow → 查看历史运行
```

### 查看日志
```
点击具体的运行记录 → 展开各个步骤 → 查看日志
```

### 查看音频文件
```
仓库页面 → Code → podcasts文件夹 → 点击音频文件
```

---

## 🔧 常见问题

### Q: Actions显示失败？
A:
1. 点击失败的运行记录
2. 展开失败的步骤
3. 查看错误日志
4. 检查依赖是否正确安装

### Q: 没有自动触发？
A:
1. 检查cron表达式是否正确
2. 确认workflow已启用
3. 查看Actions设置中的权限

### Q: 音频文件太大？
A: GitHub单个文件限制100MB，如果超过：
1. 使用Git LFS
2. 或发布为Release

---

## 🎉 完成！

现在你的AI简报会：
- ✅ 每天自动更新
- ✅ 自动生成音频
- ✅ 自动提交到仓库
- ✅ 完全免费
- ✅ 24/7运行

---

## 📝 补充说明

### 音频访问地址

```
https://raw.githubusercontent.com/YOUR_USERNAME/ai-brief/main/podcasts/ai_brief_YYYYMMDD.mp3
```

### 页面访问地址

```
https://YOUR_USERNAME.github.io/ai-brief/ai-daily-brief.html
```

（需要启用GitHub Pages）

### 启用GitHub Pages（可选）

1. 仓库Settings → Pages
2. Source选择：Deploy from a branch
3. Branch选择：main
4. 点击Save
5. 等待部署完成
6. 访问：`https://YOUR_USERNAME.github.io/ai-brief/`

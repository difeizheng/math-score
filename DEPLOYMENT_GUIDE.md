# 🚀 部署指南 - 方案 A

**前端**: Vercel（静态托管）  
**后端**: Render（Python API）  
**成本**: ¥0 完全免费

---

## 📋 准备工作

### 1. 注册账号
- [GitHub](https://github.com) - 必须
- [Vercel](https://vercel.com) - 用 GitHub 登录
- [Render](https://render.com) - 用 GitHub 登录

### 2. 安装 Git
下载地址：https://git-scm.com/downloads

### 3. 上传项目到 GitHub
```bash
# 在项目目录执行
cd C:\Users\58452\.openclaw\workspace\study

# 初始化 Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit"

# 创建 GitHub 仓库（在 github.com 上创建）
# 然后关联远程仓库
git remote add origin https://github.com/你的用户名/math-score.git

# 推送
git push -u origin main
```

---

## 🎨 第一步：部署后端到 Render

### 步骤 1: 创建 Web Service
1. 访问 https://render.com
2. 用 GitHub 账号登录
3. 点击 **"New +"** → **"Web Service"**

### 步骤 2: 连接仓库
1. 选择 **"Connect a repository"**
2. 选择你的 `math-score` 仓库
3. Render 会自动检测 `render.yaml` 配置文件

### 步骤 3: 配置服务
```
Name: math-score-backend
Region: Singapore（选择亚洲节点，速度快）
Branch: main
Root Directory: backend
Environment: Python
```

### 步骤 4: 设置构建和启动命令
```
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

### 步骤 5: 添加磁盘（存储数据库）
```
Name: database
Mount Path: /opt/render/project/src
Size: 1 GB（免费额度）
```

### 步骤 6: 选择免费计划
```
Instance Type: Free
```

### 步骤 7: 创建服务
点击 **"Create Web Service"**

### 步骤 8: 等待部署
- 等待 3-5 分钟
- 看到 **"Live"** 状态表示部署成功
- 复制你的后端 URL，例如：`https://math-score-backend.onrender.com`

---

## 🎨 第二步：部署前端到 Vercel

### 步骤 1: 导入项目
1. 访问 https://vercel.com
2. 用 GitHub 账号登录
3. 点击 **"Add New..."** → **"Project"**
4. 选择 `math-score` 仓库 → **"Import"**

### 步骤 2: 配置项目
```
Framework Preset: Other
Root Directory: ./frontend
Build Command: 留空（静态页面无需构建）
Output Directory: 留空
```

### 步骤 3: 设置环境变量
点击 **"Environment Variables"** → **"Add"**
```
Key: API_BASE_URL
Value: https://你的后端 URL.onrender.com/api
```

**重要**: 把 `你的后端 URL` 替换成刚才在 Render 获得的后端地址

### 步骤 4: 部署
点击 **"Deploy"**

### 步骤 5: 等待完成
- 等待 1-2 分钟
- 看到 **"Ready"** 状态
- 复制你的前端 URL，例如：`https://math-score.vercel.app`

---

## ✅ 测试访问

### 访问前端
```
https://你的项目名.vercel.app
```

### 测试 API
```
https://你的后端 URL.onrender.com/api/students
```

### 检查连接
1. 打开前端页面
2. 按 F12 打开控制台
3. 查看是否有 API 请求错误
4. 应该能看到学生列表和图表

---

## 🔧 配置说明

### 前端配置（vercel.json）
```json
{
  "env": {
    "API_BASE_URL": "https://你的后端 URL.onrender.com/api"
  }
}
```

### 后端配置（render.yaml）
```yaml
services:
  - type: web
    name: math-score-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    disk:
      name: database
      mountPath: /opt/render/project/src
      sizeGB: 1
```

---

## 📊 数据迁移

### 从本地迁移到云端
```bash
# 1. 备份本地数据库
cp backend/scores.db backend/scores_backup.db

# 2. 首次部署时，数据库会自动创建
# 3. 通过 API 导入数据（使用数据导入功能）
```

### 或者手动导入
1. 在本地导出数据为 Excel
2. 部署后通过前端页面的"数据导入"功能上传

---

## ⚠️ 注意事项

### 1. 数据库位置
- **本地**: `backend/scores.db`
- **Render**: `/opt/render/project/src/scores.db`
- 代码中已自动处理路径

### 2. 环境变量
- 本地开发：使用 `http://localhost:8808/api`
- 生产环境：使用环境变量 `API_BASE_URL`

### 3. 免费额度
- **Render**: 750 小时/月（约 31 天连续运行）
- **Vercel**: 无限静态页面
- **带宽**: 两者都足够个人使用

### 4. 休眠问题
- Render 免费实例 15 分钟无访问会休眠
- 下次访问需要 30 秒唤醒时间
- 解决方案：使用 UptimeRobot 免费监控（每 5 分钟访问一次）

---

## 🔄 更新部署

### 代码更新后
```bash
# 1. 提交更改
git add .
git commit -m "更新内容"
git push

# 2. Vercel 和 Render 会自动检测并重新部署
# 3. 等待 2-3 分钟即可
```

### 手动触发部署
- **Vercel**: 在 Dashboard 点击 "Redeploy"
- **Render**: 在 Dashboard 点击 "Manual Deploy"

---

## 🐛 故障排查

### 问题 1: 前端无法连接后端
**检查**:
1. 环境变量是否正确设置
2. 后端 URL 是否包含 `/api`
3. 跨域设置（后端已配置）

### 问题 2: 后端启动失败
**检查**:
1. 查看 Render 日志（Logs 标签）
2. 确认 `requirements.txt` 完整
3. 确认 `main.py` 路径正确

### 问题 3: 数据库为空
**解决**:
1. 检查磁盘是否正确挂载
2. 通过 API 重新导入数据
3. 查看日志确认数据库路径

---

## 📱 访问链接

部署完成后，你会获得：

### 前端链接
```
https://你的项目名.vercel.app
或
https://你的项目名.netlify.app
```

### 后端 API
```
https://你的项目名.onrender.com/api
```

### API 文档
```
https://你的项目名.onrender.com/docs
```

---

## 💡 优化建议

### 1. 自定义域名（可选）
- Vercel: 设置 → Domains
- Render: 设置 → Custom Domain

### 2. 防止休眠（可选）
使用 [UptimeRobot](https://uptimerobot.com):
```
1. 注册账号
2. 添加监控
3. 设置每 5 分钟访问一次
4. 保持实例活跃
```

### 3. 数据备份（重要）
```
定期导出数据库：
1. 访问 /api/export/excel
2. 下载备份文件
3. 保存到本地
```

---

## 📞 需要帮助？

### 部署检查清单
- [ ] GitHub 仓库已创建
- [ ] Vercel 账号已注册
- [ ] Render 账号已注册
- [ ] 后端已部署成功
- [ ] 前端已部署成功
- [ ] 环境变量已设置
- [ ] API 连接正常
- [ ] 数据已导入

### 常见问题
查看本指南的"故障排查"部分

### 技术支持
在家庭群联系我～

---

**预计时间**: 30-40 分钟  
**难度**: ⭐⭐⭐（中等）  
**成本**: ¥0

祝部署顺利！🎉

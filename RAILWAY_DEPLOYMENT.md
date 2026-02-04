# Railway.app 部署指南

## 快速部署步骤

### 1. 注册 Railway.app
1. 访问 https://railway.app
2. 点击 "Start a New Project"
3. 用 GitHub 账号登录（推荐）

### 2. 准备 GitHub 仓库

在你的本地 `portrait-app` 目录执行以下命令：

```bash
# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: Portrait generation app"

# 在 GitHub 创建新仓库后，添加远程地址
# 替换下面的 URL 为你的仓库地址
git remote add origin https://github.com/你的用户名/portrait-app.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 3. 在 Railway 部署

1. 登录 Railway.app
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择你的 `portrait-app` 仓库
4. Railway 会自动检测 Python 项目
5. 点击 "Deploy"

### 4. 配置环境变量

在 Railway 项目页面：
1. 点击 "Variables" 标签
2. 添加以下环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `SECRET_KEY` | 点击 "Generate" | Flask 会话密钥 |
| `ADMIN_USERNAME` | admin | 管理员用户名 |
| `ADMIN_PASSWORD` | 设置强密码 | 管理员密码 |

### 5. 获取访问地址

1. 等待部署完成（约2-3分钟）
2. 点击 "Generate Domain"
3. Railway 会给你一个 `.railway.app` 域名

例如：`https://portrait-app-production.up.railway.app`

### 6. 访问管理后台

1. 访问 `https://你的域名/admin`
2. 使用你设置的用户名和密码登录
3. 点击 "生成新验证码"
4. 生成验证码供测试使用

## 费用说明

Railway 免费套餐：
- $5 免费额度/月
- 有限运行时间（会休眠）
- 适合测试

付费套餐（推荐）：
- $5/月 起步
- 无限制运行
- 按使用量计费

## 常见问题

### Q: 如何查看日志？
A: Railway 控制台 → 项目 → "Deployments" → "View Logs"

### Q: 如何更新代码？
A:
```bash
git add .
git commit -m "更新描述"
git push
# Railway 会自动重新部署
```

### Q: 如何重启服务？
A: Railway 控制台 → 项目 → "Restart"

### Q: 国内访问慢怎么办？
A: 可以使用 Cloudflare CDN 加速（需要自己的域名）

## 文件说明

- `Procfile`: 告诉 Railway 如何启动应用
- `runtime.txt`: 指定 Python 版本
- `requirements.txt`: Python 依赖包
- `.gitignore`: 忽略不需要上传的文件

## 生产环境检查清单

- [x] Procfile 已创建
- [x] runtime.txt 已创建
- [x] requirements.txt 包含 gunicorn
- [x] .gitignore 已配置
- [x] 环境变量已设置
- [ ] GitHub 仓库已创建
- [ ] 代码已推送到 GitHub
- [ ] Railway 项目已部署
- [ ] 管理后台可访问
- [ ] 验证码已生成

## 技术支持

如遇问题，请检查：
1. Railway 部署日志
2. 环境变量是否正确设置
3. GitHub 代码是否最新

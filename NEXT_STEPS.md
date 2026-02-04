# Railway.app 部署 - 下一步操作

## 已完成的步骤

- [x] 创建 `Procfile` - Railway 启动配置
- [x] 创建 `runtime.txt` - Python 3.11.0 版本指定
- [x] 创建 `.gitignore` - 忽略敏感文件
- [x] 创建 `RAILWAY_DEPLOYMENT.md` - 详细部署指南
- [x] 初始化 Git 仓库
- [x] 创建初始提交

## 接下来的步骤

### 步骤 1: 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 创建新仓库，命名为 `portrait-app`
3. 不要初始化 README（我们已经有了代码）
4. 点击 "Create repository"

### 步骤 2: 推送代码到 GitHub

在你的命令行中执行（替换 `你的用户名`）：

```bash
cd "C:\Users\Terrt\Desktop\新项目\portrait-app"
git remote add origin https://github.com/你的用户名/portrait-app.git
git branch -M main
git push -u origin main
```

### 步骤 3: 在 Railway 部署

1. 访问 https://railway.app
2. 点击 "Start a New Project"
3. 选择 "Deploy from GitHub repo"
4. 授权 Railway 访问你的 GitHub
5. 选择 `portrait-app` 仓库
6. 点击 "Deploy Now"

### 步骤 4: 配置环境变量

在 Railway 项目设置中添加：

| 变量名 | 值 |
|--------|-----|
| `SECRET_KEY` | 点击 Railway 的 "Generate" 按钮 |
| `ADMIN_USERNAME` | admin |
| `ADMIN_PASSWORD` | 设置一个强密码 |

### 步骤 5: 生成域名并测试

1. 等待部署完成（约 2-3 分钟）
2. 点击 "Generate Domain" 获取你的 `.railway.app` 地址
3. 访问 `https://你的域名/admin` 登录管理后台
4. 生成一些验证码
5. 测试上传图片功能

## 域名示例

部署成功后，你会得到类似这样的地址：
```
https://portrait-app-production.up.railway.app
```
或
```
https://portrait-app-xxxx.up.railway.app
```

## 管理后台访问

```
https://你的域名/admin
```

使用你设置的环境变量登录。

## 费用提醒

Railway 免费套餐包含：
- $5 免费额度/月
- 有限运行时间（会休眠）

如果要 24/7 运行，需要升级到付费套餐（$5/月起）。

## 问题排查

如果部署失败，检查：
1. Railway 的 "Deployments" → "View Logs" 查看错误
2. 确认 `requirements.txt` 包含所有依赖
3. 确认 `Procfile` 格式正确

## 更新代码

```bash
git add .
git commit -m "更新描述"
git push
```

Railway 会自动检测并重新部署。

## 需要帮助？

查看详细部署指南：`RAILWAY_DEPLOYMENT.md`

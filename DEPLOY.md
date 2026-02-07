# 🚀 AI肖像馆 - 部署指南

一站式部署解决方案，支持多种平台和环境。

## 📋 目录

- [快速开始](#快速开始)
- [平台部署](#平台部署)
  - [Railway (推荐)](#railway-推荐)
  - [Vercel](#vercel)
  - [Docker](#docker)
  - [传统服务器](#传统服务器)
- [自动部署](#自动部署)
- [配置说明](#配置说明)
- [故障排查](#故障排查)

---

## 🚀 快速开始

### 使用一键部署脚本

```bash
# 1. 克隆代码
git clone https://github.com/s26233792-lab/haimati.git
cd haimati

# 2. 复制环境变量模板
cp .env.example .env
# 编辑 .env 文件，填入你的配置
nano .env

# 3. 选择部署方式
./deploy.sh railway    # Railway 部署
./deploy.sh vercel     # Vercel 部署
./deploy.sh docker     # Docker 本地部署
```

---

## 🛤️ Railway 部署 (推荐)

Railway 提供免费额度和自动扩缩容，是最简单的部署方案。

### 方式一：GitHub 自动部署

1. **Fork 本仓库** 到你的 GitHub 账号

2. **在 Railway 创建项目**
   - 访问 [railway.app](https://railway.app)
   - 点击 "New Project" → "Deploy from GitHub repo"
   - 选择你的仓库

3. **配置环境变量**
   - 在 Railway Dashboard 点击 "Variables"
   - 添加以下变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `SECRET_KEY` | Flask 密钥 | `openssl rand -hex 32` |
| `ADMIN_USERNAME` | 管理员用户名 | `admin` |
| `ADMIN_PASSWORD` | 管理员密码 | 强密码 |
| `NANOBANANA_API_KEY` | API 密钥 | 从 apicore 获取 |
| `API_PROVIDER` | API 提供商 | `apicore` |
| `MODEL_NAME` | AI 模型 | `gemini-3-pro-image-preview` |

4. **自动部署**
   - 每次推送代码到 main 分支，Railway 会自动重新部署

### 方式二：CLI 部署

```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
railway init

# 部署
railway up
```

### Railway 配置说明

项目已包含 `railway.json` 配置文件：

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app --bind 0.0.0.0:$PORT --workers 2",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

---

## ▲ Vercel 部署

Vercel 适合前端展示，对 Python 支持有限（函数执行时间限制 60s）。

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 部署
vercel --prod
```

### 环境变量设置

```bash
vercel env add SECRET_KEY
vercel env add NANOBANANA_API_KEY
# ... 其他变量
```

> ⚠️ **注意**: Vercel 免费版有 60 秒执行时间限制，长时间生成的请求可能会超时。

---

## 🐳 Docker 部署

### 快速开始

```bash
# 1. 启动服务
docker-compose up -d

# 2. 查看日志
docker-compose logs -f

# 3. 停止服务
docker-compose down
```

### 使用 Nginx 反向代理

```bash
# 启动包含 Nginx 的服务
docker-compose --profile with-nginx up -d
```

### 生产环境优化

```bash
# 使用生产环境配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 构建多平台镜像

```bash
# 构建并推送到 Docker Hub
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t yourname/ai-portrait:latest --push .
```

---

## 🖥️ 传统服务器部署

### 系统要求

- Ubuntu 20.04+ / CentOS 7+
- Python 3.9+
- 2GB+ RAM
- 10GB+ 磁盘空间

### 部署步骤

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装依赖
sudo apt install -y python3 python3-pip python3-venv nginx

# 3. 创建应用目录
sudo mkdir -p /var/www/ai-portrait
cd /var/www/ai-portrait

# 4. 克隆代码
sudo git clone https://github.com/s26233792-lab/haimati.git .

# 5. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 6. 安装依赖
pip install -r requirements.txt

# 7. 配置环境变量
sudo cp .env.example .env
sudo nano .env

# 8. 创建 systemd 服务
sudo nano /etc/systemd/system/ai-portrait.service
```

服务文件内容：

```ini
[Unit]
Description=AI Portrait Studio
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ai-portrait
Environment="PATH=/var/www/ai-portrait/venv/bin"
ExecStart=/var/www/ai-portrait/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# 9. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable ai-portrait
sudo systemctl start ai-portrait

# 10. 配置 Nginx
sudo cp nginx.conf /etc/nginx/sites-available/ai-portrait
sudo ln -s /etc/nginx/sites-available/ai-portrait /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔄 自动部署 (GitHub Actions)

项目已配置 GitHub Actions 工作流，支持：

- ✅ 代码质量检查 (flake8, black)
- ✅ 自动化测试
- ✅ 自动部署到 Railway
- ✅ 自动部署到 Vercel
- ✅ Docker 镜像构建和推送
- ✅ 自动创建 Release

### 配置 Secrets

在 GitHub 仓库设置中添加以下 Secrets：

| Secret Name | 说明 |
|-------------|------|
| `RAILWAY_TOKEN` | Railway API Token |
| `VERCEL_TOKEN` | Vercel Token |
| `VERCEL_ORG_ID` | Vercel Organization ID |
| `VERCEL_PROJECT_ID` | Vercel Project ID |
| `DOCKER_USERNAME` | Docker Hub 用户名 |
| `DOCKER_PASSWORD` | Docker Hub 密码 |

### 获取 Railway Token

```bash
railway login
railway token
```

---

## ⚙️ 配置说明

### 环境变量详解

#### 必需配置

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `SECRET_KEY` | ✅ | Flask 会话密钥，建议 32 位随机字符串 |
| `ADMIN_USERNAME` | ✅ | 管理员用户名 |
| `ADMIN_PASSWORD` | ✅ | 管理员密码 |
| `NANOBANANA_API_KEY` | ✅ | AI 图像生成 API 密钥 |

#### API 配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `API_PROVIDER` | `apicore` | API 提供商: apicore, laozhang, 12ai |
| `MODEL_NAME` | `gemini-3-pro-image-preview` | AI 模型选择 |

#### 可选配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MAX_CONTENT_LENGTH` | `16777216` | 最大上传文件大小 (16MB) |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `RATE_LIMIT_PER_MINUTE` | `30` | API 限流 (请求/分钟) |

---

## 🔧 故障排查

### 常见问题

#### 1. 验证码验证失败

```bash
# 检查数据库
ls -la codes.db

# 重新生成验证码
python generate_codes.py --count 100 --output codes.txt

# 在 Railway 上需要配置 Volume 持久化
```

#### 2. 图片上传失败

```bash
# 检查 uploads 目录权限
chmod 755 uploads
chown -R www-data:www-data uploads

# 检查磁盘空间
df -h
```

#### 3. API 调用超时

- Vercel: 免费版限制 60 秒，建议升级到 Pro
- Railway: 检查 `timeout` 设置
- Docker: 调整 gunicorn 的 `--timeout` 参数

#### 4. 内存不足

```bash
# 查看内存使用
free -h

# 减少 gunicorn worker 数量
# 在 Procfile 中修改: --workers 1
```

### 日志查看

```bash
# Docker
docker-compose logs -f app

# Railway
railway logs

# Systemd
sudo journalctl -u ai-portrait -f

# Nginx
sudo tail -f /var/log/nginx/error.log
```

### 健康检查

```bash
# 检查服务状态
curl http://localhost:5000/health

# 检查环境变量
curl http://localhost:5000/api/status/your-code
```

---

## 📊 性能优化

### Gunicorn 配置建议

| 环境 | Workers | Threads | Timeout |
|------|---------|---------|---------|
| 小型 (1-2GB RAM) | 2 | 4 | 120s |
| 中型 (2-4GB RAM) | 4 | 4 | 120s |
| 大型 (4GB+ RAM) | 4-8 | 8 | 180s |

Worker 数量公式: `workers = (2 × CPU核心数) + 1`

### 数据库优化

- 本地开发: SQLite 足够
- 生产环境: 建议使用 PostgreSQL
- Railway 自动提供 PostgreSQL

### 缓存建议

高并发场景下，配置 Redis 缓存：

```yaml
# docker-compose.yml 中启用 redis
services:
  redis:
    image: redis:7-alpine
    restart: always
```

---

## 💰 成本估算

| 平台 | 月费 | 适用场景 |
|------|------|----------|
| Railway (免费) | $0 | 测试、小流量 |
| Railway (付费) | $5+ | 生产环境 |
| Vercel (免费) | $0 | 前端展示 |
| Vercel Pro | $20+ | 商业项目 |
| 阿里云 ECS | ¥100+ | 国内部署 |
| 腾讯云 CVM | ¥100+ | 国内部署 |

---

## 🆘 需要帮助？

- 📧 查看日志：`railway logs` 或 `docker-compose logs`
- 📖 详细文档：查看 `DEPLOYMENT.md`
- 🐛 提交 Issue：[GitHub Issues](https://github.com/s26233792-lab/haimati/issues)

---

## 📝 更新日志

### v2.0 (2025-02-07)

- ✅ 新增 Docker 多阶段构建
- ✅ 新增 GitHub Actions 自动部署
- ✅ 新增 Nginx 生产配置
- ✅ 优化 Railway 部署配置
- ✅ 新增一键部署脚本

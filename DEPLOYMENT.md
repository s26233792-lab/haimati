# 肖像照生成网站 - 部署指南

## 目录

1. [本地开发](#本地开发)
2. [Vercel 部署](#vercel-部署)
3. [传统服务器部署](#传统服务器部署)
4. [Docker 部署](#docker-部署)
5. [配置 NanoBanana API](#配置-nanobanana-api)

---

## 本地开发

### 前置要求

- Python 3.8+
- pip

### 安装步骤

1. **进入项目目录**

```bash
cd portrait-app
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **配置环境变量**

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
nano .env
```

4. **生成验证码**

```bash
# 生成 100 个验证码，每个可使用 3 次
python generate_codes.py --count 100 --output codes.txt
```

5. **启动服务**

```bash
# 方式1: 直接运行
python app.py

# 方式2: 使用启动脚本
bash start.sh
```

6. **访问应用**

- 用户界面: http://localhost:5000
- 管理后台: http://localhost:5000/admin

---

## Vercel 部署

Vercel 是一个免费的部署平台，非常适合 Python Flask 应用。

### 前置要求

- Vercel 账号
- GitHub 账号（可选，用于自动部署）

### 部署步骤

1. **安装 Vercel CLI**

```bash
npm install -g vercel
```

2. **登录 Vercel**

```bash
vercel login
```

3. **部署项目**

在项目根目录运行：

```bash
vercel
```

按提示完成配置：
- 链接到现有项目或创建新项目
- 选择项目目录
- 确认构建设置

4. **配置环境变量**

在 Vercel 控制台中设置环境变量：

```bash
vercel env add NANOBANANA_API_URL
vercel env add NANOBANANA_API_KEY
vercel env add SECRET_KEY
```

或在 Vercel 网站控制台中添加：
- 进入项目设置
- 选择 "Environment Variables"
- 添加以下变量：
  - `NANOBANANA_API_URL`
  - `NANOBANANA_API_KEY`
  - `SECRET_KEY`

5. **重新部署**

```bash
vercel --prod
```

### Vercel 配置文件

项目已包含 `vercel.json` 配置文件：

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### 注意事项

- Vercel 免费版有函数执行时间限制（10秒）
- 对于长时间运行的 API 调用，可能需要升级到付费版
- SQLite 数据在 Vercel 上是只读的，建议使用外部数据库

---

## 传统服务器部署

### 服务器要求

- Ubuntu 20.04+ / CentOS 7+
- Python 3.8+
- Nginx（可选，用于反向代理）

### 部署步骤

1. **更新系统**

```bash
sudo apt update && sudo apt upgrade -y
```

2. **安装 Python 和 pip**

```bash
sudo apt install python3 python3-pip python3-venv -y
```

3. **创建项目目录**

```bash
mkdir -p /var/www/portrait-app
cd /var/www/portrait-app
```

4. **创建虚拟环境**

```bash
python3 -m venv venv
source venv/bin/activate
```

5. **上传项目文件**

将项目文件上传到服务器（使用 scp、git 或 ftp）

6. **安装依赖**

```bash
pip install -r requirements.txt
```

7. **配置环境变量**

```bash
nano .env
```

添加你的配置

8. **安装 Gunicorn**

```bash
pip install gunicorn
```

9. **创建 Systemd 服务**

```bash
sudo nano /etc/systemd/system/portrait-app.service
```

添加以下内容：

```ini
[Unit]
Description=Portrait App Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/portrait-app
Environment="PATH=/var/www/portrait-app/venv/bin"
ExecStart=/var/www/portrait-app/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

10. **启动服务**

```bash
sudo systemctl daemon-reload
sudo systemctl start portrait-app
sudo systemctl enable portrait-app
```

11. **配置 Nginx（可选）**

```bash
sudo nano /etc/nginx/sites-available/portrait-app
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/portrait-app/static;
    }

    location /uploads {
        alias /var/www/portrait-app/uploads;
    }

    client_max_body_size 16M;
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/portrait-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

12. **配置 SSL（可选，使用 Let's Encrypt）**

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Docker 部署

### 创建 Dockerfile

在项目根目录创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - NANOBANANA_API_URL=${NANOBANANA_API_URL}
      - NANOBANANA_API_KEY=${NANOBANANA_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./uploads:/app/uploads
      - ./codes.db:/app/codes.db
    restart: always
```

### 运行

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

---

## 配置 NanoBanana API

### 获取 API 密钥

1. 访问 NanoBanana 官网注册账号
2. 在控制台获取 API Key
3. 查看文档了解调用方式

### 更新代码中的 API 调用

编辑 `app.py` 中的 `call_nanobanana_api` 函数：

```python
def call_nanobanana_api(image_path, style):
    """
    根据实际 API 文档调整
    """
    import base64

    # 方式1: Base64 编码（推荐）
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()

    payload = {
        'image': image_data,
        'style': style
    }

    headers = {
        'Authorization': f'Bearer {NANOBANANA_API_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.post(
        NANOBANANA_API_URL,
        json=payload,
        headers=headers,
        timeout=60
    )

    if response.status_code == 200:
        result = response.json()
        # 处理返回结果
        return result.get('image_url')

    return None
```

### 测试 API

```bash
# 使用测试脚本
python test_api.py
```

---

## 监控和日志

### 查看日志

```bash
# Systemd 服务
sudo journalctl -u portrait-app -f

# Docker
docker-compose logs -f

# Vercel
vercel logs
```

### 健康检查

添加健康检查端点：

```python
@app.route('/health')
def health():
    return jsonify({'status': 'ok'})
```

---

## 故障排查

### 常见问题

1. **验证码验证失败**
   - 检查数据库文件是否存在
   - 确认验证码已正确生成

2. **图片上传失败**
   - 检查 uploads 目录权限
   - 确认文件大小限制

3. **API 调用失败**
   - 验证 API 密钥是否正确
   - 检查网络连接
   - 查看错误日志

4. **Vercel 部署超时**
   - API 调用时间过长，考虑使用异步任务队列
   - 升级到 Vercel 付费版

---

## 安全建议

1. **更改默认密钥**
   - 修改 `SECRET_KEY`
   - 使用强密码

2. **添加认证**
   - 管理后台添加密码保护
   - 使用环境变量存储敏感信息

3. **HTTPS**
   - 生产环境务必使用 HTTPS
   - 配置 SSL 证书

4. **限流**
   - 添加请求频率限制
   - 防止滥用

5. **备份**
   - 定期备份数据库
   - 备份上传的图片

---

## 成本估算

| 部署方式 | 月费 | 说明 |
|----------|------|------|
| Vercel 免费版 | ¥0 | 适合小流量 |
| Vercel Pro | ¥150/月 | 更高性能 |
| 阿里云轻量服务器 | ¥100/月 | 2核4G |
| 腾讯云服务器 | ¥100/月 | 2核4G |
| Docker 自托管 | ¥0 | 需要已有服务器 |

---

## 支持

如有问题，请联系技术支持。

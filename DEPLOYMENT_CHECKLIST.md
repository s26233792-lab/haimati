# 部署检查清单

## 部署前必做事项

### 1. 安全配置

- [ ] 修改 `.env` 文件，设置强随机 `SECRET_KEY`
  ```bash
  # 生成随机密钥
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

- [ ] 为管理后台添加身份验证（目前无认证！）
  - 建议使用 HTTP Basic Auth
  - 或添加登录系统
  - 或配置防火墙限制 /admin 路径访问

- [ ] 配置 HTTPS（生产环境必须）

### 2. 目录和文件

- [ ] 确保 `uploads/` 目录存在且有写权限
  ```bash
  mkdir -p uploads
  chmod 755 uploads
  ```

- [ ] 确保 `codes.db` 数据库文件有正确权限

### 3. 环境变量 (.env)

```bash
# 基础配置
SECRET_KEY=your-random-secret-key-here
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# API 配置（如需接入真实 API）
NANOBANANA_API_KEY=your-api-key
NANOBANANA_API_URL=https://cdn.12ai.org/v1/images/edits
```

### 4. 依赖安装

```bash
pip install -r requirements.txt
```

### 5. 生成初始验证码

```bash
python generate_codes.py
```

## 启动方式

### 开发环境
```bash
python app.py
```

### 生产环境
```bash
python app_production.py
```

### 使用 Gunicorn（推荐）
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用 Supervisor 守护进程
```ini
[program:portrait-app]
command=gunicorn -w 4 -b 0.0.0.0:5000 app:app
directory=/path/to/portrait-app
user=www-data
autostart=true
autorestart=true
```

## API 接口列表

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/` | 前端首页 |
| POST | `/api/verify` | 验证验证码 |
| POST | `/api/upload` | 上传图片生成 |
| GET | `/result/<filename>` | 获取生成的图片 |
| GET | `/api/status/<code>` | 查询验证码状态 |
| GET | `/admin` | 管理后台（⚠️ 需添加认证） |
| POST | `/admin/generate_codes` | 生成验证码 |
| GET | `/admin/export_codes` | 导出验证码 |
| GET | `/admin/export_security_logs` | 导出安全日志 |
| POST | `/admin/batch_delete` | 批量删除验证码 |
| POST | `/admin/batch_update_status` | 批量更新状态 |
| POST | `/admin/reset_code` | 重置验证码 |

## 安全建议

### 高优先级
1. **立即**为管理后台添加身份验证
2. **立即**配置防火墙限制 /admin 访问
3. **立即**更改默认 SECRET_KEY

### 中优先级
4. 使用 Redis 替代内存存储（频率限制）
5. 添加文件上传病毒扫描
6. 配置 CDN 加速图片访问

### 低优先级
7. 添加日志轮转
8. 配置监控告警
9. 数据库备份策略

## 当前已知限制

1. **管理后台无认证** - 任何人都可以访问
2. **频率限制使用内存** - 重启服务器后丢失
3. **使用 SQLite** - 不适合高并发场景
4. **模拟模式** - 图片处理为本地模拟，未接入真实 API

## 生产环境推荐配置

```bash
# 使用 Nginx 反向代理
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

# 限制管理后台只允许内网访问
location /admin {
    allow 192.168.1.0/24;
    deny all;
    proxy_pass http://127.0.0.1:5000;
}
```

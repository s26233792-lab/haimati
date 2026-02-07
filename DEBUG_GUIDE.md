# 🔧 Railway 生产环境调试指南

## 快速诊断步骤

### 1. 访问健康检查��点

在你的 Railway 项目 URL 后添加 `/debug/health`

```
https://your-project.railway.app/debug/health
```

**返回信息**：
- ✅ 数据库连接状态
- ✅ API Key 配置状态
- ✅ 上传目录状态
- ✅ 数据库表状态
- ✅ 最后一次 API 调用信息

### 2. 访问配置检查端点

```
https://your-project.railway.app/debug/config
```

**检查项**：
- API Key 是否配置
- API URL 是否正确
- 数据库类型和配置

### 3. 查看 API 调用日志

```
https://your-project.railway.app/debug/api
```

**查看**：
- 最后一次 API 调用的详细信息
- 错误原因
- 响应状态码

---

## 常见问题排查

### 问题 1: 图片生成失败

**症状**：
- 上传图片后返回错误
- 生成结果一直是原图

**排查步骤**：

1. **检查 API Key**
   ```
   访问 /debug/config
   查看 api_key_configured 是否为 true
   ```

2. **检查 API URL**
   ```
   查看 api_url 是否正确
   12ai: https://ismaque.org/v1/models/{model}:generateContent
   ```

3. **查看日志**
   ```
   Railway 控制台 → 项目 → Deployments → View Logs
   搜索 "API" 关键词查看错误信息
   ```

**解决方案**：

#### 如果 API Key 未配置

```bash
# 在 Railway 控制台添加环境变量
Settings → Variables → New Variable

Name: NANOBANANA_API_KEY
Value: 你的_12ai_API_Key
```

#### 如果 API 调用失败

```bash
# 检查 API 提供商
Settings → Variables

API_PROVIDER=12ai
MODEL_NAME=gemini-3-pro-image-preview-2k
```

### 问题 2: 数据库错误

**症状**：
- 验证码验证失败
- 提示"数据库连接失败"

**排查步骤**：

1. **检查数据库类型**
   ```
   /debug/health → checks.database
   ```

2. **检查表是否存在**
   ```
   /debug/health → checks.tables
   应该有 3 个表：
   - verification_codes
   - generation_logs
   - verification_attempts
   ```

**解决方案**：

#### 如果表不存在

Railway 会在首次启动时自动创建表。如果没有创建：

```bash
# 方案 1: 重启服务
Railway 控制台 → 项目 → Deployments → Redeploy

# 方案 2: 检查数据库连接
Settings → Variables → DATABASE_URL
```

### 问题 3: 上传目录错误

**症状**：
- 上传图片失败
- 提示"文件不存在"

**排查步骤**：

```bash
/debug/health → checks.upload_folder
```

**解决方案**：

确保配置了 Railway Volume：

```bash
# 在 railway.toml 中配置
[[volumes]]
name = "data"
mount_to = "/data"
```

### 问题 4: 占位符不兼容

**症状**：
- PostgreSQL 环境报错
- 提示 "syntax error at or near"

**已修复**：✅ 代码已更新为自动适配 PostgreSQL 和 SQLite

**验证**：

```bash
/debug/config
查看 db_type 和 postgres_available
```

---

### 问题 5: Application failed to respond

**症状**：
- 上传图片后显示 "⚠️ Application failed to respond"
- 没有收到任何错误消息
- Railway 日志显示 worker 超时

**原因**：
- gunicorn 默认超时时间为 30 秒
- API 调用可能需要 120 秒
- 时间不匹配导致 gunicorn 提前终止工作进程

**解决方案**：

**已修复**：✅ Procfile 已更新，增加超时时间

```bash
# 新的 Procfile 配置
web: gunicorn app:app --timeout 150 --workers 2 --bind 0.0.0.0:$PORT
```

**验证**：

1. Railway 会自动重新部署
2. 等待部署完成后重新测试
3. 查看日志确认没有超时错误

---

### 问题 6: 占位符不兼容

**症状**：
- PostgreSQL 环境报错
- 提示 "syntax error at or near"

**已修复**：✅ 代码已更新为自动适配 PostgreSQL 和 SQLite

**验证**：

```bash
/debug/config
查看 db_type 和 postgres_available
```

---

## 手动测试步骤

### 测试 1: 验证码验证

```bash
# 生成测试验证码
python generate_codes.py --count 1 --max_uses 3

# 使用验证码访问
curl -X POST https://your-project.railway.app/api/verify \
  -H "Content-Type: application/json" \
  -d '{"code": "生成的验证码"}'
```

**预期响应**：
```json
{
  "success": true,
  "remaining": 3,
  "max_uses": 3
}
```

### 测试 2: 图片上传

```bash
curl -X POST https://your-project.railway.app/api/upload \
  -F "code=你的验证码" \
  -F "clothing=business_suit" \
  -F "angle=front" \
  -F "background=textured" \
  -F "bgColor=white" \
  -F "beautify=no" \
  -F "image=@/path/to/your/image.jpg"
```

**预期响应**：
```json
{
  "success": true,
  "result_url": "/result/xxx_result.jpg",
  "remaining": 2
}
```

---

## 日志查看方法

### Railway 控制台日志

1. 登录 [Railway.app](https://railway.app)
2. 进入你的项目
3. 点击 "Deployments"
4. 选择最新的部署
5. 点击 "View Logs"

### 重要日志关键词

搜索这些关键词快速定位问题：

```
✅ 成功标志：
  [API] ✓ 图片生成成功
  [DB] 数据库初始化成功

❌ 错误标志：
  [API] ❌
  [Upload] 异常
  Error
  Traceback
```

---

## 环境变量配置清单

### 必需配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `NANOBANANA_API_KEY` | 12ai API 密钥 | `sk-xxxxx` |
| `SECRET_KEY` | Flask 会话密钥 | 自动生成或手动设置 |
| `DATABASE_URL` | PostgreSQL 连接 | Railway 自动提供 |

### 可选配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `API_PROVIDER` | `12ai` | API 提供商 |
| `MODEL_NAME` | `gemini-3-pro-image-preview-2k` | 模型名称 |
| `ADMIN_USERNAME` | `admin` | 管理员用户名 |
| `ADMIN_PASSWORD` | `admin123` | 管理员密码 |

---

## 联系支持

如果以上步骤都无法解决问题：

### Railway 支持
- Discord: https://discord.gg/railway
- Email: support@railway.app

### 12ai.org 支持
- 查看 API 文档
- 检查 API Key 是否有效
- 确认 API 额度是否用完

---

## 更新日志

### 2026-02-07
- ✅ **修复 gunicorn 超时问题** - 增加 timeout 到 150 秒，解决 "Application failed to respond" 错误
- ✅ 修复 PostgreSQL/SQLite 占位符兼容性问题
- ✅ 添加健康检查端点 `/debug/health`
- ✅ 改进错误日志输出
- ✅ 优化数据库连接管理

---

*最后更新：2026-02-07*

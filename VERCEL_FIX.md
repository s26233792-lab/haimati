# Vercel 部署修复指南

## 问题原因

在 Vercel 的 Serverless 环境中：
1. **文件系统是只读的**（除了 `/tmp`）
2. **每次请求都是独立的环境**
3. **SQLite 数据库无法持久化**，导致验证码生成后丢失

## 解决方案

### 方案一：使用 Vercel Postgres（推荐）

Vercel 提供了托管 PostgreSQL 服务，非常适合这个场���。

#### 步骤 1：在 Vercel 创建 Postgres 数据库

1. 进入你的 Vercel 项目
2. 点击 "Storage" 标签
3. 点击 "Create Database"
4. 选择 "Postgres"
5. 创建数据库

#### 步骤 2：配置环境变量

Vercel 会自动添加以下环境变量：
- `POSTGRES_URL`
- `POSTGRES_PRISMA_URL`
- `POSTGRES_URL_NON_POOLING`

#### 步骤 3：修改 app.py 使用 Vercel Postgres

在 Vercel 环境中，`DATABASE_URL` 环境变量会自动设置为 Vercel Postgres 连接字符串。

确保在 Vercel 控制台设置以下环境变量：

```
SECRET_KEY=your-random-secret-key-here
NANOBANANA_API_KEY=your-api-key
DATABASE_URL=自动由Vercel Postgres提供
```

### 方案二：使用外部云数据库

使用其他云数据库服务（如 Supabase、Neon、Railway）：

#### 使用 Supabase（免费）

1. 访问 [supabase.com](https://supabase.com) 创建项目
2. 获取数据库连接字符串
3. 在 Vercel 环境变量中设置 `DATABASE_URL`

示例连接字符串格式：
```
postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

#### 使用 Neon（免费）

1. 访问 [neon.tech](https://neon.tech) 创建项目
2. 获取连接字符串
3. 在 Vercel 设置 `DATABASE_URL`

### 方案 3：临时方案 - 使用内存存储（仅测试）

如果你只是想测试功能，可以使用内存存储，但**不推荐生产使用**，因为：
- 验证码每次请求后都会丢失
- 管理后台无法正常工作

## 完整部署步骤

### 1. 确保代码已更新

```bash
git add vercel.json index.py
git commit -m "Fix Vercel deployment configuration"
git push
```

### 2. 在 Vercel 控制台配置环境变量

进入 Vercel 项目 → Settings → Environment Variables，添加：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `SECRET_KEY` | 随机生成的密钥 | 必填 |
| `NANOBANANA_API_KEY` | 你的 API 密钥 | 可选 |
| `DATABASE_URL` | PostgreSQL 连接字符串 | 必填（如果使用 Vercel Postgres 会自动添加） |

生成 SECRET_KEY：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. 重新部署

```bash
vercel --prod
```

### 4. 初始化数据库

部署成功后，访问以下 URL 来初始化数据库：

```
https://your-project.vercel.app/debug/test
```

然后在管理后台生成验证码。

## 上传文件问题

对于上传的图片，你有两个选择：

### 选项 A：使用 Vercel Blob（推荐）

1. 在 Vercel 项目中添加 "Blob" 存储
2. 修改代码上传到 Blob 而不是本地文件系统

### 选项 B：使用外部对象存储

使用 Cloudflare R2、AWS S3 等服务存储图片。

### 选项 C：临时方案（仅测试）

继续使用 `/tmp` 目录，但文件会在函数执行完后删除。

## 验证部署

部署完成后，检查：

1. 访问 `https://your-project.vercel.app/` - 主页应该加载
2. 访问 `https://your-project.vercel.app/debug/test` - 查看配置状态
3. 访问 `https://your-project.vercel.app/debug/config` - 检查数据库连接

## 常见错误排查

### 错误: "no such table: verification_codes"

**原因**: 数据库未初始化

**解决**: 访问管理后台生成验证码，数据库会自动初始化

### 错误: "database is locked"

**原因**: SQLite 并发问题

**解决**: 使用 PostgreSQL 替代 SQLite

### 错误: Session 验证失败

**原因**: SECRET_KEY 未设置或不一致

**解决**: 在 Vercel 控制台设置固定的 SECRET_KEY

## 推荐生产配置

```bash
# 在 Vercel 控制台设置
SECRET_KEY=生成的随机密钥
DATABASE_URL=PostgreSQL连接字符串
NANOBANANA_API_KEY=你的API密钥

# 可选
ADMIN_USERNAME=admin
ADMIN_PASSWORD=强密码
```

## 总结

| 问题 | 解决方案 |
|------|----------|
| 验证码丢失 | 使用 Vercel Postgres 或外部 PostgreSQL |
| Session 失效 | 设置 SECRET_KEY 环境变量 |
| 图片丢失 | 使用 Vercel Blob 或外部对象存储 |
| 超时问题 | API 调用可能超时，考虑异步处理 |

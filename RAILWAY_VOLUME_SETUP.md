# Railway Volume 持久化存储配置指南

## 问题说明

Railway每次部署都会创建新的容器，如果没有配置持久化存储，SQLite数据库文件会丢失，导致：
- 验证码失效
- 生成历史丢失
- 上传的图片丢失

## 解决方案：配置Railway Volume

Railway Volume是Railway提供的持久化存储服务，可以保存数据即使重新部署。

### 步骤1：在Railway项目中添加Volume

1. ��录 [Railway.app](https://railway.app)
2. 进入你的项目
3. 点击项目顶部的 **"New"** → **"Volume"**
4. 配置Volume：
   - **Name**: `portrait-data` (或任意名称)
   - **Mount Path**: `/data`
5. 点击 **"Create"**

### 步骤2：验证环境变量

确保项目中有以下环境变量（如果没有会自动设置）：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `RAILWAY_VOLUME_MOUNT_PATH` | `/data` | Volume挂载路径（Railway自动设置） |
| `RAILWAY_VOLUME_PATH` | (自动生成) | Railway自动设置 |

### 步骤3：重新部署

添加Volume后，Railway会自动重新部署。部署完成后：

1. 访问你的应用
2. 进入管理后台 `/admin`
3. 生成新的验证码
4. 测试生成图片功能

### 步骤4：验证持久化

部署后，验证数据是否持久化：

1. 访问 `/debug/config` 确认配置
2. 检查 `upload_folder` 是否为 `/data/uploads`
3. 生成一些验证码和图片
4. 在Railway控制台重新部署
5. 验证验证码和图片仍然存在

## 配置说明

### 代码中的配置（app.py）

```python
# 持久化存储路径（Railway Volume 或本地）
persistent_path = os.getenv('RAILWAY_VOLUME_MOUNT_PATH', '/data')

if is_railway:
    # 使用持久化存储的 SQLite
    db_config = os.path.join(persistent_path, 'codes.db')
    upload_folder = os.path.join(persistent_path, 'uploads')
```

### 目录结构

使用Railway Volume后，目录结构如下：

```
/data/
├── codes.db           # SQLite数据库（验证码、生成历史）
└── uploads/           # 上传的图片
    ├── 20260206_xxx_original.jpg
    ├── 20260206_xxx_result.jpg
    └── ...
```

## 费用说明

Railway Volume费用：
- 免费套餐：包含 1GB 存储空间
- 付费套餐：$0.25/GB/月

对于小型应用，免费套餐的1GB空间足够使用。

## 故障排查

### Q: 验证码仍然失效？

A: 检查以下几点：
1. Volume是否正确创建（挂载路径为 `/data`）
2. 访问 `/debug/config` 确认配置
3. 查看Railway日志确认数据库路径

### Q: 图片无法上传？

A: 检查：
1. `/data/uploads` 目录是否存在
2. 目录权限是否正确
3. 查看Railway日志

### Q: 如何迁移现有数据？

A:
1. 在配置Volume前，导出现有数据
2. 配置Volume后，重新导入数据
3. 或者在管理后台重新生成验证码

## 替代方案：使用PostgreSQL

如果不想使用Railway Volume + SQLite，可以改用PostgreSQL：

1. 在Railway项目中添加PostgreSQL插件
2. Railway会自动设置 `DATABASE_URL` 环境变量
3. 代码会自动检测并使用PostgreSQL

PostgreSQL的优势：
- 自动备份
- 更好的性能
- 无需手动配置Volume

缺点：
- 免费套餐有连接数限制
- 存储空间有限（1GB）

## 推荐配置

| 应用规模 | 推荐方案 | 费用 |
|---------|---------|------|
| 小型/测试 | Railway Volume + SQLite | 免费 |
| 中型/生产 | PostgreSQL | 免费（1GB）|
| 大型/生产 | PostgreSQL + 付费存储 | 按使用量计费 |

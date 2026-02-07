# 海马体肖像生成 - 项目信息

> 最后更新：2026-02-07

---

## 项目概述

**项目名称**: 海马体肖像生成网站
**功能**: 基于 AI 的美式专业职场风格肖像照生成
**部署平台**: Railway.app
**GitHub**: https://github.com/s26233792-lab/haimati.git

---

## 当前配置

### 模型配置

| 配置项 | 当前值 |
|--------|--------|
| **API 提供商** | ismaque.org |
| **模型名称** | `gemini-3-pro-image-preview-2k` |
| **API 格式** | Gemini 原生格式 |
| **输出分辨率** | **2K** (2048x2730 像素) |
| **画面比例** | 3:4 |

### API 端点

```
https://ismaque.org/v1/models/gemini-3-pro-image-preview-2k:generateContent
```

---

## 环境变量配置

### 必需配置（Railway Variables）

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `NANOBANANA_API_KEY` | **你的 12ai API Key** | 图像生成 API 密钥 |
| `SECRET_KEY` | **自动生成或手动设置** | Flask 会话密钥 |

### 可选配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `API_PROVIDER` | `12ai` | API 提供商 (12ai/laozhang) |
| `MODEL_NAME` | `gemini-3-pro-image-preview-2k` | 模型名称 |
| `ADMIN_USERNAME` | `admin` | 管理后台用户名 |
| `ADMIN_PASSWORD` | `admin123` | 管理后台密码 |
| `DATABASE_URL` | - | PostgreSQL 连接字符串（Railway 自动提供） |

---

## Prompt 配置（2K 分辨率）

当前使用的 prompt 结构：

```
你是一个专业的AI换装助手。请执行以下操作：

【任务目标】根据参考图片，为人物更换服装和背景，生成一张全新的肖像照。

【人物要求】
- 保持人物的面部特征和发型完全一致
- 保持人物的性别和年龄特征
- 可以调整肤色光影，使整体更专业
- 轻微美颜效果（可选）

【服装要求】
- 商务西装 / 正装��服 / 休闲衬衫等
- 必须为人物穿上这套服装
- 服装要贴合身形，看起来真实自然

【背景要求】
- 质感影棚背景 / 纯色背景
- 完全替换原背景
- 背景要专业、干净

【风格要求】
- 美式专业职场风格
- 如军人般挺拔
- 超高清，**2K分辨率**，清晰对焦
- 3:4比例，确保输出分辨率为2048x2730像素
- 影棚级布光，构图优雅

【禁止事项】
- 禁止直接返回原图
- 禁止只做简单滤镜处理
- 必须重新生成图片
```

---

## 支持的生成参数

### 服装选项 (clothing)

| 值 | 描述 |
|----|------|
| `business_suit` | 商务西装 |
| `formal_dress` | 正装礼服 |
| `casual_shirt` | 休闲衬衫 |
| `turtleneck` | 高领毛衣 |
| `tshirt` | 简约T恤 |
| `keep_original` | 和原图保持一致 |

### 拍摄角度 (angle)

| 值 | 描述 |
|----|------|
| `front` | 正面照，完全正对镜头 |
| `slight_tilt` | 微微倾斜角度 |

### 背景类型 (background)

| 值 | 描述 |
|----|------|
| `textured` | 质感影棚背景 |
| `solid` | 纯色背景 |

### 背景颜色 (bgColor)

| 值 | 描述 |
|----|------|
| `white` | 白色 |
| `gray` | 灰色 |
| `blue` | 蓝色 |
| `black` | 深灰色 |
| `warm` | 暖米色 |

### 美颜选项 (beautify)

| 值 | 描述 |
|----|------|
| `yes` | 轻微美颜 |
| `no` | 不美颜 |

---

## Railway 部署信息

### 项目地址

- **GitHub**: https://github.com/s26233792-lab/haimati.git
- **Railway**: 登录后查看项目

### 部署状态检查

1. 登录 Railway.app
2. 进入项目 → Deployments
3. 查看最新部署状态

### 常见部署问题

#### 503 Service Unavailable

**原因**: Railway 容器注册表暂时不可用

**解决方案**:
1. 等待 5-10 分钟后点击 "Redeploy"
2. 或推送空提交触发重新部署
3. 更改部署区域（us-west2 → us-east1）

#### 查看日志

```
Railway 控制台 → 项目 → Deployments → View Logs
```

---

## API 端点

### 前端接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页 |
| `/api/verify` | POST | 验证验证码 |
| `/api/upload` | POST | 上传图片生成 |
| `/result/<filename>` | GET | 获取生成图片 |
| `/api/status/<code>` | GET | 获取验证码状态 |
| `/api/showcase` | GET | 获取示例图片 |

### 管理后台接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/admin` | GET | 管理后台首页 |
| `/admin/login` | GET/POST | 管理后台登录 |
| `/admin/logout` | GET | 管理后台登出 |
| `/admin/generate_codes` | POST | 批量生成验证码 |
| `/admin/export_codes` | GET | 导出验证码 |
| `/admin/export_security_logs` | GET | 导出安全日志 |
| `/admin/batch_delete` | POST | 批量删除验证码 |
| `/admin/batch_update_status` | POST | 批量更新状态 |
| `/admin/reset_code` | POST | 重置验证码 |

### 调试接口

| 端点 | 说明 |
|------|------|
| `/debug/test` | 基础测试 |
| `/debug/config` | 配置检查 |
| `/debug/api` | 最后一次 API 调用信息 |

---

## 文件结构

```
haimati/
├── app.py                      # 主应用文件
├── Procfile                    # Railway 启动配置
├── requirements.txt            # Python 依赖
├── runtime.txt                 # Python 版本
├── start.sh                    # 启动脚本
├── templates/                  # HTML 模板
│   ├── index.html             # 首页
│   ├── admin.html             # 管理后台
│   └── admin_login.html       # 登录页
├── static/                     # 静态资源
│   ├── script.js              # 前端 JS
│   └── style.css              # 样式
├── uploads/                    # 上传文件目录
├── API.md                      # API 文档
├── RAILWAY_DEPLOYMENT.md      # 部署指南
└── PROJECT_INFO.md            # 本文件
```

---

## 快速命令

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 生成验证码
python generate_codes.py

# 启动服务
python app.py
```

访问: http://localhost:5000

### Git 操作

```bash
# 查看状态
git status

# 提交更改
git add .
git commit -m "描述"
git push

# Railway 自动重新部署
```

---

## 技术栈

- **后端**: Flask (Python)
- **数据库**: SQLite (本地) / PostgreSQL (Railway)
- **AI 模型**: Gemini 3 Pro Image Preview (12ai.org)
- **部署**: Railway.app
- **版本控制**: Git

---

## 联系支持

- **Railway 支持**: https://discord.gg/railway
- **Railway 邮箱**: support@railway.app
- **12ai.org**: API 服务提供商

---

## 版本历史

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-02-07 | v1.2 | 更新模型为 gemini-3-pro-image-preview-2k，API 地址改为 ismaque.org |
| 2026-02-07 | v1.1 | 更新模型为 gemini-3-pro-image-preview，添加 2K 分辨率要求 |
| 2026-02-07 | v1.0 | 初始版本，Railway 部署 |

---

*此文件由 Claude 自动生成，包含项目的核心配置信息。*

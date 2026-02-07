# 🚀 Railway 配置更新清单

## 📋 必须更新的环境变量

登录 [Railway.app](https://railway.app) → haimati 项目 → Settings → Variables

### ✅ 更新以下变量

| 变量名 | 旧值 | 新值 | 说明 |
|--------|------|------|------|
| `API_PROVIDER` | `12ai` | `apicore` | API 提供商 |
| `MODEL_NAME` | `gemini-3-pro-image-preview-2k` | `gemini-3-pro-image-preview` | 模型���称 |
| `NANOBANANA_API_KEY` | 旧 key | **新的 apicore API Key** | API 密钥 |

---

## 🔧 详细步骤

### 步骤 1: 获取 apicore API Key

联系 apicore.ai 获取 API Key

### 步骤 2: 更新 Railway 环境变量

1. 登录 Railway.app
2. 进入 haimati 项目
3. 点击 Settings → Variables
4. 更新以下变量：

#### 更新 API_PROVIDER
```
Name: API_PROVIDER
Value: apicore
```

#### 更新 MODEL_NAME
```
Name: MODEL_NAME
Value: gemini-3-pro-image-preview
```

#### 更新 NANOBANANA_API_KEY
```
Name: NANOBANANA_API_KEY
Value: sk-xxxxxxxxxxxxxxxx
```

### 步骤 3: 重启服务

Railway 会自动重新部署。如需手动重启：
Deployments → 选择最新部署 → Redeploy

---

## ✅ 验证配置

### 1. 健康检查
```
https://你的项目.railway.app/debug/health
```

### 2. 配置检查
```
https://你的项目.railway.app/debug/config
```

### 3. 测试图片生成

上传图片并测试生成功能

---

## 🎯 完成清单

- [ ] 获取 apicore API Key
- [ ] 更新 API_PROVIDER 为 apicore
- [ ] 更新 MODEL_NAME 为 gemini-3-pro-image-preview
- [ ] 更新 NANOBANANA_API_KEY
- [ ] 等待 Railway 重新部署
- [ ] 测试图片生成功能

---

*最后更新：2026-02-07*

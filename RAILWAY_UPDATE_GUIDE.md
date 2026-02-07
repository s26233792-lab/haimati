# Railway 环境变量更新指南

## 问题诊断

访问调试端点查看当前配置：
```
https://你的项目.railway.app/debug/config
```

**如果看到以下情况，说明需要更新环境变量：**
- API URL 显示 `ismaque.org` 而不是 `api.apicore.ai`
- API 提供商不是 `apicore`

---

## 更新步骤（5分钟完成）

### 步骤 1: 登录 Railway

1. 访问 [railway.app](https://railway.app)
2. 登录你的账户

### 步骤 2: 进入项目

1. 在 Dashboard 找到 **haimati** 项目
2. 点击进入项目

### 步骤 3: 打开环境变量设置

方法 A - 从项目主页：
```
项目主页 → Settings (齿轮图标) → Variables
```

方法 B - 从部署页面：
```
Deployments → 选择最新部署 → Settings → Variables
```

### 步骤 4: 更新 3 个关键环境变量

找到或添加以下 3 个变量：

#### 变量 1: API_PROVIDER
```
Name:  API_PROVIDER
Value: apicore
```
👆 **重要**：必须是 `apicore`（全小写）

#### 变量 2: MODEL_NAME
```
Name:  MODEL_NAME
Value: gemini-3-pro-image-preview
```
👆 **重要**：必须是 `gemini-3-pro-image-preview`（不是 `gemini-3-pro-image-preview-2k`）

#### 变量 3: NANOBANANA_API_KEY
```
Name:  NANOBANANA_API_KEY
Value: 你的_apicore_API_Key
```
👆 **重要**：使用你的 apicore.ai API Key

### 步骤 5: 保存并触发重新部署

更新完 3 个变量后：
1. 点击 **"Save Changes"** 或 **"Create Variable"**
2. Railway 会自动检测到环境变量变化
3. 会自动触发重新部署（通常 1-2 分钟）

### 步骤 6: 验证部署成功

等待部署完成后：

1. 访问健康检查端点：
```
https://你的项目.railway.app/debug/health
```
应该看到：
```json
{
  "status": "healthy",
  "checks": {
    "api_key": {
      "status": "configured"
    }
  }
}
```

2. 访问配置检查端点：
```
https://你的项目.railway.app/debug/config
```
应该看到：
```json
{
  "api_url": "https://api.apicore.ai/v1/chat/completions"
}
```

---

## 常见问题

### Q1: 找不到 Variables 设置？

**A**: 确保你在正确的地方：
- ✅ 项目主页 → Settings → Variables
- ❌ 不是账户设置（Account Settings）

### Q2: 更新后还是不生效？

**A**: 尝试手动重新部署：
```
Deployments → 选择最新部署 → Redeploy
```

### Q3: API Key 在哪里获取？

**A**: 联系 apicore.ai 获取 API Key

### Q4: 变量名称大小写敏感吗？

**A**: 是的！必须完全一致：
- ✅ `API_PROVIDER` (大写)
- ❌ `api_provider` (小写，错误)

---

## 配置对照表

| 项目 | 旧值（错误） | 新值（正确） |
|------|------------|------------|
| API_PROVIDER | `12ai` 或 `laozhang` | `apicore` |
| MODEL_NAME | `gemini-3-pro-image-preview-2k` | `gemini-3-pro-image-preview` |
| API URL | `https://ismaque.org/...` | `https://api.apicore.ai/v1/chat/completions` |

---

## 验证清单

更新完成后，逐一确认：

- [ ] `API_PROVIDER` = `apicore`
- [ ] `MODEL_NAME` = `gemini-3-pro-image-preview`
- [ ] `NANOBANANA_API_KEY` 已配置
- [ ] 部署状态显示 "✅ Success"
- [ ] `/debug/config` 显示正确的 API URL
- [ ] `/debug/health` 显示 `"status": "healthy"`
- [ ] 上传测试图片能正常生成

---

## 下一步

完成以上步骤后：
1. 上传一张测试图片
2. 访问 `/debug/api` 查看最后一次 API 调用
3. 确认 `called: true`（说明 API 已被调用）

---

*最后更新：2026-02-07*

# 肖像照生成服务 - 测试检查清单

## 部署信息
- **GitHub**: https://github.com/s26233792-lab/haimati
- **Railway 项目**: 已部署
- **API**: 12ai.org Gemini 图片生成

---

## Railway Variables 检查

### 必需的环境变量
- [x] `NANOBANANA_API_KEY` - API 密钥
- [ ] `SECRET_KEY` - Flask 会话密钥（点击 Generate）
- [ ] `ADMIN_USERNAME` - 管理员用户名（建议：admin）
- [ ] `ADMIN_PASSWORD` - 管理员密码（设置强密码）

### 不应该设置的变量
- [x] `NANOBANANA_API_URL` - **必须删除**，让代码使用默认值

### 可选的环境变量
- [ ] `NANOBANANA_API_MODEL` - 模型名称（默认：gemini-3-pro-image-preview）

### 数据库
- [ ] **PostgreSQL** - **必须添加**，否则验证码会丢失

---

## 功能测试清单

### 1. 前端页面测试
- [ ] 首页可以正常访问
- [ ] 输入验证码后点击"验证"按钮
- [ ] 验证成功后显示步骤2（上传图片）
- [ ] 显示剩余使用次数

### 2. 图片上传测试
- [ ] 点击上传区域可以选择文件
- [ ] 支持拖拽上传
- [ ] 上传后显示预览图
- [ ] "生成肖像"按钮可以点击

### 3. 图片生成测试
- [ ] 点击"生成肖像"后显示进度
- [ ] 生成完成后显示结果图片
- [ ] 剩余次数正确扣减
- [ ] 可以点击"再生成一张"

### 4. 图片下载测试
- [ ] 点击"下载图片"可以下载
- [ ] 文件名是动态的（带时间戳）
- [ ] **图片文件大小约 2MB**（如果只有几百 KB，说明被压缩了）

### 5. 管理后台测试
- [ ] 访问 `/admin` 跳转到登录页
- [ ] 使用正确的用户名密码可以登录
- [ ] 登录后显示验证码列表
- [ ] 可以生成新的验证码
- [ ] 生成的验证码会显示在列表中
- [ ] 可以导出验证码

### 6. 验证码持久化测试（重要！）
- [ ] 生成一些验证码
- [ ] **刷新页面** - 验证码还在
- [ ] **重启 Railway 服务** - 验证码还在（需要 PostgreSQL）

### 7. API 调用测试
- [ ] 访问 `/debug/config` 检查配置
  ```json
  {
    "api_key_configured": true,
    "api_url": "https://cdn.12ai.org/v1beta/models/gemini-3-pro-image-preview:generateContent"
  }
  ```
- [ ] 上传图片后访问 `/debug/api` 查看 API 调用结果
  ```json
  {
    "called": true,
    "status_code": 200,
    "response_keys": ["candidates", ...]
  }
  ```

---

## 已知问题检查

### 问题 1: 图片被压缩（只有几百 KB）
- [ ] 当前状态：已添加 `generationConfig` 参数
- [ ] 测试结果：图片大小是否接近 2MB？

### 问题 2: 验证码丢失
- [ ] 当前状态：需要添加 PostgreSQL
- [ ] 测试结果：刷新页面后验证码是否保留？

---

## 快速测试步骤

### 步骤 1: 检查配置
访问：`https://你的域名/debug/config`

确认：
- `api_key_configured`: true
- `api_url`: `https://cdn.12ai.org/v1beta/models/gemini-3-pro-image-preview:generateContent`

### 步骤 2: 生成验证码
1. 访问：`https://你的域名/admin`
2. 登录管理后台
3. 点击"生成新验证码"
4. 生成 10 个验证码

### 步骤 3: 测试前端
1. 访问：`https://你的域名/`
2. 输入一个验证码
3. 上传一张图片
4. 选择服装和背景
5. 点击"生成肖像"
6. 等待生成完成
7. 下载图片，检查文件大小

### 步骤 4: 测试持久化
1. 在管理后台查看验证码列表
2. **刷新页面**
3. 确认验证码还在

---

## 当前代码版本

- **最新提交**: `Add generationConfig to improve image quality`
- **API URL**: `https://cdn.12ai.org/v1beta/models/gemini-3-pro-image-preview:generateContent`
- **认证方式**: URL 参数 `?key=`
- **请求格式**: Gemini 原生格式
- **响应解析**: 支持 `inlineData`（驼峰命名）

---

## 需要修复的问题

1. **图片质量问题** - 图片只有几百 KB，应该约 2MB
   - 已添加 `generationConfig`
   - Prompt 中已添加高质量要求

2. **数据持久化** - 需要添加 PostgreSQL

---

测试完成后，请告诉我哪些功能正常，哪些有问题，我来帮你修复。

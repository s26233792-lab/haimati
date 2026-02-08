# 网络问题修复说明

## 修复内容

### 1. 新增功能

#### 代理支持
现在支持通过环境变量配置 HTTP/HTTPS 代理，方便国内用户使用。

```bash
# 在 .env 文件中配置
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

#### 灵活的超时配置
支持分别配置连接超时和读取超时：

```bash
CONNECT_TIMEOUT=10    # 连接超时（秒）
READ_TIMEOUT=120      # 读取超时（秒）
```

#### 断路器机制
当 API 连续失败时，自动打开断路器，避免浪费资源：

- `CIRCUIT_BREAKER_THRESHOLD=5`: 连续失败5次后打开断路器
- `CIRCUIT_BREAKER_TIMEOUT=60`: 60秒后尝试恢���服务

#### 自定义 API 端点
支持自定义 API 提供商：

```bash
API_PROVIDER=custom
CUSTOM_API_URL=https://your-api.com/v1
```

### 2. 改进的错误处理

#### 详细的错误分类
- 连接超时
- 读取超时
- 连接失败
- SSL 错误
- 代理错误
- 断路器保护

#### 前端错误提示
前端现在会显示更具体的错误信息，并用不同颜色区分：
- 橙色 - 超时警告
- 红色 - 连接错误
- 蓝色 - 一般信息

### 3. 新增调试端点

#### `/debug/network`
查看网络配置状态：
```json
{
  "api_provider": "12ai",
  "api_url": "https://ismaque.org/v1",
  "proxy_configured": true,
  "proxies": {"http": "...", "https": "..."},
  "connect_timeout": 10,
  "read_timeout": 120,
  "circuit_breaker": {
    "open": false,
    "failures": 0,
    "threshold": 5,
    "timeout": 60
  }
}
```

## 配置文件更新

### .env.example 新增选项

```bash
# ==================== 网络配置 ====================
# 代理设置（可选，用于国内网络环境）
# HTTP_PROXY=http://127.0.0.1:7890
# HTTPS_PROXY=http://127.0.0.1:7890

# 连接超时（秒）
CONNECT_TIMEOUT=10

# 读取超时（秒）
READ_TIMEOUT=120

# 断路器配置
# 连续失败多少次后打开断路器
CIRCUIT_BREAKER_THRESHOLD=5

# 断路器恢复时间（秒）
CIRCUIT_BREAKER_TIMEOUT=60

# 自定义 API URL（当 API_PROVIDER=custom 时使用）
# CUSTOM_API_URL=https://your-custom-api.com/v1
```

## 使用建议

### 国内用户
1. 优先使用 `laozhang` API 提供商（国内直连）
2. 如需使用其他 API，配置代理：
   ```bash
   API_PROVIDER=12ai
   HTTP_PROXY=http://127.0.0.1:7890
   HTTPS_PROXY=http://127.0.0.1:7890
   ```

### 生产环境
1. 调整超时时间根据实际 API 响应速度
2. 设置合理的断路器阈值
3. 启用日志监控

### 调试网络问题
访问 `/debug/network` 端点查看：
- 当前网络配置
- 断路器状态
- 代理配置状态

## 文件变更

| 文件 | 变更内容 |
|------|---------|
| `app.py` | 添加代理支持、超时配置、断路器机制、详细错误处理 |
| `.env.example` | 新增网络配置选项 |
| `static/script.js` | 改进前端错误提示 |

## 兼容性

- 向后兼容：不配置新的环境变量也能正常运行
- 默认值：所有新配置都有合理的默认值
- 逐步迁移：可以根据需要逐步启用新功能

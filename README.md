# 肖像照生成网站

## 快速开始

### 1. 安装依赖
```bash
cd portrait-app
pip install -r requirements.txt
```

### 2. 生成验证码
```bash
python generate_codes.py --count 100 --output codes.txt
```

### 3. 启动服务
```bash
python app.py
```

访问: http://localhost:5000

## 目录结构
```
portrait-app/
├── app.py              # 后端主文件
├── generate_codes.py   # 验证码生成工具
├── requirements.txt    # 依赖列表
├── vercel.json        # Vercel部署配置
├── codes.db           # SQLite数据库（自动生成）
├── uploads/           # 上传文件目录
├── templates/
│   └── index.html     # 用户界面
└── static/
    ├── style.css      # 样式
    └── script.js      # 前端逻辑
```

## 配置 NanoBanana API

编辑 `app.py` 中的 `call_nanobanana_api` 函数，替换为实际的API调用。

## 部署到 Vercel

1. 安装 Vercel CLI: `npm i -g vercel`
2. 运行: `vercel`
3. 按提示完成部署

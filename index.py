# Vercel WSGI 入口文件
# 用于 Vercel 部署

from app import app

# Vercel Python 需要导出 app 作为 WSGI 应用
# 不需要 wsgi_app 变量，直接使用 app

# Vercel 会自动调用这个 app
if __name__ == '__main__':
    app.run()

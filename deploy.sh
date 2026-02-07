#!/bin/bash
# ============================================
# AI肖像馆 - 一键部署脚本
# 支持: Railway, Vercel, Docker, 传统服务器
# 用法: ./deploy.sh [platform]
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查环境变量文件
check_env_file() {
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_warning ".env 文件不存在，正在从模板创建..."
            cp .env.example .env
            print_warning "请编辑 .env 文件填入实际配置后再运行此脚本"
            exit 1
        else
            print_error ".env.example 模板文件不存在"
            exit 1
        fi
    fi
}

# 检查 Git 仓库
check_git() {
    if ! command_exists git; then
        print_error "Git 未安装，请先安装 Git"
        exit 1
    fi
    
    if [ ! -d ".git" ]; then
        print_warning "未初始化 Git 仓库，正在初始化..."
        git init
        git add .
        git commit -m "Initial commit"
    fi
}

# 部署到 Railway
deploy_railway() {
    print_info "开始部署到 Railway..."
    
    if ! command_exists railway; then
        print_warning "Railway CLI 未安装，正在安装..."
        npm install -g @railway/cli
    fi
    
    check_env_file
    check_git
    
    # 登录 Railway
    print_info "请登录 Railway..."
    railway login
    
    # 链接项目
    if ! railway status >/dev/null 2>&1; then
        print_info "链接到 Railway 项目..."
        railway link
    fi
    
    # 设置环境变量
    print_info "配置环境变量..."
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
        railway variables set SECRET_KEY="${SECRET_KEY}"
        railway variables set ADMIN_USERNAME="${ADMIN_USERNAME}"
        railway variables set ADMIN_PASSWORD="${ADMIN_PASSWORD}"
        railway variables set NANOBANANA_API_KEY="${NANOBANANA_API_KEY}"
        railway variables set API_PROVIDER="${API_PROVIDER:-apicore}"
        railway variables set MODEL_NAME="${MODEL_NAME:-gemini-3-pro-image-preview}"
    fi
    
    # 部署
    print_info "开始部署..."
    railway up --detach
    
    # 获取域名
    DOMAIN=$(railway domain)
    print_success "部署成功！访问地址: https://$DOMAIN"
    print_info "管理后台: https://$DOMAIN/admin"
}

# 部署到 Vercel
deploy_vercel() {
    print_info "开始部署到 Vercel..."
    
    if ! command_exists vercel; then
        print_warning "Vercel CLI 未安装，正在安装..."
        npm install -g vercel
    fi
    
    check_env_file
    check_git
    
    # 登录 Vercel
    print_info "请登录 Vercel..."
    vercel login
    
    # 部署
    print_info "开始部署..."
    vercel --prod
    
    # 设置环境变量
    print_info "配置环境变量..."
    if [ -f ".env" ]; then
        while IFS='=' read -r key value; do
            # 跳过注释和空行
            [[ $key =~ ^[[:space:]]*# ]] && continue
            [[ -z $key ]] && continue
            
            # 去除空格
            key=$(echo $key | xargs)
            value=$(echo $value | xargs)
            
            if [ -n "$key" ] && [ -n "$value" ]; then
                vercel env add "$key" production <<< "$value" 2>/dev/null || true
            fi
        done < ".env"
    fi
    
    print_success "部署成功！"
}

# Docker 部署
deploy_docker() {
    print_info "开始 Docker 部署..."
    
    if ! command_exists docker; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    check_env_file
    
    # 构建并启动
    print_info "构建 Docker 镜像..."
    docker-compose build
    
    print_info "启动服务..."
    docker-compose up -d
    
    print_success "部署成功！"
    print_info "访问地址: http://localhost:5000"
    print_info "查看日志: docker-compose logs -f"
}

# Docker 停止
stop_docker() {
    print_info "停止 Docker 服务..."
    docker-compose down
    print_success "服务已停止"
}

# Docker 重启
restart_docker() {
    print_info "重启 Docker 服务..."
    docker-compose restart
    print_success "服务已重启"
}

# 查看日志
view_logs() {
    print_info "查看日志..."
    docker-compose logs -f app
}

# 更新部署
update_docker() {
    print_info "更新部署..."
    docker-compose pull
    docker-compose up -d --build
    print_success "更新完成"
}

# 显示帮助信息
show_help() {
    echo "AI肖像馆 - 部署脚本"
    echo ""
    echo "用法: ./deploy.sh [命令]"
    echo ""
    echo "命令:"
    echo "  railway     部署到 Railway.app"
    echo "  vercel      部署到 Vercel"
    echo "  docker      使用 Docker 本地部署"
    echo "  stop        停止 Docker 服务"
    echo "  restart     重启 Docker 服务"
    echo "  logs        查看 Docker 日志"
    echo "  update      更新 Docker 部署"
    echo "  help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  ./deploy.sh railway    # 部署到 Railway"
    echo "  ./deploy.sh docker     # 本地 Docker 部署"
}

# 主函数
main() {
    case "${1:-help}" in
        railway)
            deploy_railway
            ;;
        vercel)
            deploy_vercel
            ;;
        docker)
            deploy_docker
            ;;
        stop)
            stop_docker
            ;;
        restart)
            restart_docker
            ;;
        logs)
            view_logs
            ;;
        update)
            update_docker
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"

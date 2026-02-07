#!/bin/bash
# ============================================
# API 提供商快速切换脚本
# 用法: ./switch_api.sh [apicore|12ai]
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 显示帮助
show_help() {
    echo "API 提供商切换脚本"
    echo ""
    echo "用法: ./switch_api.sh [命令]"
    echo ""
    echo "命令:"
    echo "  apicore    切换到 apicore.ai (OpenAI 格式)"
    echo "  12ai       切换到 ismaque.org (Gemini 原生格式)"
    echo "  status     显示当前配置"
    echo "  test       测试当前 API 连接"
    echo "  help       显示帮助"
    echo ""
    echo "示例:"
    echo "  ./switch_api.sh apicore"
    echo "  ./switch_api.sh 12ai"
    echo "  ./switch_api.sh status"
}

# 显示当前状态
show_status() {
    echo "======================================"
    echo "📊 当前 API 配置"
    echo "======================================"
    
    API_PROVIDER=${API_PROVIDER:-"未设置"}
    MODEL_NAME=${MODEL_NAME:-"未设置"}
    
    echo "API 提供商: $API_PROVIDER"
    echo "模型: $MODEL_NAME"
    
    if [ "$API_PROVIDER" = "apicore" ]; then
        echo "API URL: https://api.apicore.ai/v1/chat/completions"
        echo "API 格式: OpenAI 兼容格式"
    elif [ "$API_PROVIDER" = "12ai" ]; then
        echo "API URL: https://ismaque.org/v1/models/$MODEL_NAME:generateContent"
        echo "API 格式: Gemini 原生格式"
    fi
    
    if [ -n "$NANOBANANA_API_KEY" ]; then
        echo "API Key: 已设置 (${#NANOBANANA_API_KEY} 字符)"
    else
        echo "API Key: 未设置"
    fi
    
    echo "======================================"
}

# 切换到 apicore
switch_apicore() {
    print_info "切换到 apicore.ai..."
    
    # 读取现有的 API Key（如果有）
    read -p "请输入 apicore.ai 的 API Key (回车保持现有): " key
    
    # 导出环境变量
    export API_PROVIDER=apicore
    export MODEL_NAME=gemini-3-pro-image-preview
    if [ -n "$key" ]; then
        export NANOBANANA_API_KEY="$key"
    fi
    
    # 更新 .env 文件
    if [ -f ".env" ]; then
        # 删除旧的配置
        sed -i '/^API_PROVIDER=/d' .env
        sed -i '/^MODEL_NAME=/d' .env
        
        # 添加新的配置
        echo "" >> .env
        echo "# API 配置 ($(date))" >> .env
        echo "API_PROVIDER=apicore" >> .env
        echo "MODEL_NAME=gemini-3-pro-image-preview" >> .env
        
        if [ -n "$key" ]; then
            sed -i '/^NANOBANANA_API_KEY=/d' .env
            echo "NANOBANANA_API_KEY=$key" >> .env
        fi
    fi
    
    print_success "已切换到 apicore.ai"
    print_info "API 格式: OpenAI 兼容格式"
    print_info "端点: https://api.apicore.ai/v1/chat/completions"
    
    # 显示当前配置
    show_status
}

# 切换到 12ai
switch_12ai() {
    print_info "切换到 ismaque.org (12ai)..."
    
    # 读取现有的 API Key（如果有）
    read -p "请输入 ismaque.org 的 API Key (回车保持现有): " key
    
    # 选择模型
    echo "请选择模型:"
    echo "1) gemini-3-pro-image-preview (推荐)"
    echo "2) gemini-2.0-flash-exp"
    echo "3) gemini-1.5-pro-latest"
    read -p "选择 (1-3): " model_choice
    
    case $model_choice in
        1) MODEL="gemini-3-pro-image-preview" ;;
        2) MODEL="gemini-2.0-flash-exp" ;;
        3) MODEL="gemini-1.5-pro-latest" ;;
        *) MODEL="gemini-3-pro-image-preview" ;;
    esac
    
    # 导出环境变量
    export API_PROVIDER=12ai
    export MODEL_NAME="$MODEL"
    if [ -n "$key" ]; then
        export NANOBANANA_API_KEY="$key"
    fi
    
    # 更新 .env 文件
    if [ -f ".env" ]; then
        # 删除旧的配置
        sed -i '/^API_PROVIDER=/d' .env
        sed -i '/^MODEL_NAME=/d' .env
        
        # 添加新的配置
        echo "" >> .env
        echo "# API 配置 ($(date))" >> .env
        echo "API_PROVIDER=12ai" >> .env
        echo "MODEL_NAME=$MODEL" >> .env
        
        if [ -n "$key" ]; then
            sed -i '/^NANOBANANA_API_KEY=/d' .env
            echo "NANOBANANA_API_KEY=$key" >> .env
        fi
    fi
    
    print_success "已切换到 ismaque.org (12ai)"
    print_info "API 格式: Gemini 原生格式"
    print_info "端点: https://ismaque.org/v1/models/$MODEL:generateContent"
    
    # 显示当前配置
    show_status
}

# 测试 API 连接
test_api() {
    print_info "测试 API 连接..."
    
    API_PROVIDER=${API_PROVIDER:-""}
    NANOBANANA_API_KEY=${NANOBANANA_API_KEY:-""}
    MODEL_NAME=${MODEL_NAME:-"gemini-3-pro-image-preview"}
    
    if [ -z "$NANOBANANA_API_KEY" ]; then
        print_error "API Key 未设置"
        return 1
    fi
    
    if [ "$API_PROVIDER" = "apicore" ]; then
        URL="https://api.apicore.ai/v1/chat/completions"
        BODY='{"model": "'$MODEL_NAME'", "messages": [{"role": "user", "content": "Hello"}]}'
    elif [ "$API_PROVIDER" = "12ai" ]; then
        URL="https://ismaque.org/v1/models/$MODEL_NAME:generateContent"
        BODY='{"contents": [{"parts": [{"text": "Hello"}]}]}'
    else
        print_error "未知的 API 提供商: $API_PROVIDER"
        return 1
    fi
    
    print_info "发送测试请求到: $URL"
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$URL" \
        -H "Authorization: Bearer $NANOBANANA_API_KEY" \
        -H "Content-Type: application/json" \
        -d "$BODY" 2>/dev/null)
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "API 连接正常 (HTTP 200)"
        print_info "响应: $(echo $BODY | cut -c 1-100)..."
        return 0
    else
        print_error "API 连接失败 (HTTP $HTTP_CODE)"
        print_error "响应: $BODY"
        return 1
    fi
}

# 主函数
main() {
    case "${1:-status}" in
        apicore)
            switch_apicore
            ;;
        12ai)
            switch_12ai
            ;;
        status)
            show_status
            ;;
        test)
            test_api
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

#!/bin/bash
#===============================================================================
# Cron定时任务设置脚本
# Cron Job Setup Script
#
# 功能: 配置每日金融分析报告的定时任务
# 默认执行时间: 每天上午9:00 (Asia/Shanghai)
#===============================================================================

set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CRON_SCRIPT="${SCRIPT_DIR}/daily_report.sh"

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查脚本是否存在
check_script() {
    if [ ! -f "${CRON_SCRIPT}" ]; then
        log_error "找不到定时任务脚本: ${CRON_SCRIPT}"
        exit 1
    fi
    
    # 检查脚本是否可执行
    if [ ! -x "${CRON_SCRIPT}" ]; then
        log_warning "脚本不可执行，正在添加执行权限..."
        chmod +x "${CRON_SCRIPT}"
        log_success "已添加执行权限"
    fi
}

# 获取当前时区时间
get_timezone_time() {
    TZ="Asia/Shanghai" date '+%Y-%m-%d %H:%M:%S %Z'
}

# 设置定时任务
setup_cron() {
    local hour=${1:-9}    # 默认9点
    local minute=${2:-0}   # 默认0分
    
    # 验证时间参数
    if ! [[ "${hour}" =~ ^[0-9]+$ ]] || [ "${hour}" -lt 0 ] || [ "${hour}" -gt 23 ]; then
        log_error "小时参数无效: ${hour} (有效范围: 0-23)"
        exit 1
    fi
    
    if ! [[ "${minute}" =~ ^[0-9]+$ ]] || [ "${minute}" -lt 0 ] || [ "${minute}" -gt 59 ]; then
        log_error "分钟参数无效: ${minute} (有效范围: 0-59)"
        exit 1
    fi
    
    local cron_expression="${minute} ${hour} * * *"
    local cron_command="bash ${CRON_SCRIPT} >> ${REPO_DIR}/logs/cron_output.log 2>&1"
    
    log_info "准备设置定时任务..."
    log_info "执行时间: 每天 ${hour}:${minute} (Asia/Shanghai)"
    log_info "执行命令: ${cron_command}"
    
    # 获取现有crontab内容
    local current_cron
    current_cron=$(crontab -l 2>/dev/null || echo "")
    
    # 检查是否已有相关定时任务
    if echo "${current_cron}" | grep -q "daily_report.sh"; then
        log_warning "已存在定时任务，正在移除旧任务..."
        # 移除旧的daily_report.sh任务
        current_cron=$(echo "${current_cron}" | grep -v "daily_report.sh")
    fi
    
    # 创建新的crontab
    local new_cron
    new_cron=$(cat << EOF
${current_cron}

# 每日金融分析报告 - AI自动生成
# 设置时间: $(date '+%Y-%m-%d %H:%M:%S %Z')
# 执行时间: 每天 ${hour}:${minute} (Asia/Shanghai)
${cron_expression} ${cron_command}
EOF
)
    
    # 应用新的crontab
    echo "${new_cron}" | crontab -
    
    log_success "定时任务设置成功！"
}

# 验证定时任务
verify_cron() {
    echo ""
    echo "📋 当前定时任务配置:"
    echo "========================================"
    crontab -l
    echo "========================================"
    
    # 检查cron服务状态
    echo ""
    log_info "检查cron服务状态..."
    if command -v systemctl &> /dev/null; then
        if systemctl is-active --quiet cron 2>/dev/null || systemctl is-active --quiet crond 2>/dev/null; then
            log_success "Cron服务正在运行"
        else
            log_warning "Cron服务未运行，建议手动启动"
            log_info "启动命令: sudo systemctl start cron"
        fi
    elif command -v service &> /dev/null; then
        if service cron status &>/dev/null || service crond status &>/dev/null; then
            log_success "Cron服务正在运行"
        else
            log_warning "Cron服务未运行，建议手动启动"
        fi
    else
        log_info "无法检测cron服务状态，请确保cron守护进程正在运行"
    fi
}

# 测试运行
test_run() {
    log_info "执行测试运行..."
    echo ""
    echo "========================================"
    bash "${CRON_SCRIPT}"
    echo "========================================"
    echo ""
}

# 移除定时任务
remove_cron() {
    log_info "移除定时任务..."
    
    local current_cron
    current_cron=$(crontab -l 2>/dev/null || echo "")
    
    if echo "${current_cron}" | grep -q "daily_report.sh"; then
        current_cron=$(echo "${current_cron}" | grep -v "daily_report.sh" | grep -v "^# 每日金融分析报告" | grep -v "^# 设置时间:" | sed '/^$/d')
        echo "${current_cron}" | crontab -
        log_success "定时任务已移除"
    else
        log_info "未找到定时任务，无需移除"
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
用法: $(basename "$0") [命令] [参数]

命令:
    setup [hour] [minute]    设置定时任务 (默认: 9:00)
    remove                    移除定时任务
    verify                    验证定时任务配置
    test                      测试运行一次
    help                      显示此帮助信息

示例:
    $(basename "$0") setup 9 0      # 每天9:00执行
    $(basename "$0") setup 14 30    # 每天14:30执行
    $(basename "$0") test          # 立即测试运行
    $(basename "$0") remove        # 移除定时任务

定时任务说明:
    - 默认执行时间: 每天上午9:00 (Asia/Shanghai)
    - 脚本位置: ${CRON_SCRIPT}
    - 日志位置: ${REPO_DIR}/logs/
    - 使用GitHub CLI提交报告到仓库

注意事项:
    - 需要先安装并配置GitHub CLI (gh)
    - 确保mini-agent命令可用
    - 确保cron守护进程正在运行
EOF
}

# 主函数
main() {
    local command=${1:-help}
    local hour=${2:-9}
    local minute=${3:-0}
    
    echo ""
    echo "========================================"
    echo "⚙️  定时任务配置工具"
    echo "   每日金融分析报告系统"
    echo "========================================"
    echo ""
    
    case "${command}" in
        setup)
            check_script
            setup_cron "${hour}" "${minute}"
            verify_cron
            ;;
        remove)
            remove_cron
            ;;
        verify)
            verify_cron
            ;;
        test)
            check_script
            test_run
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: ${command}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"

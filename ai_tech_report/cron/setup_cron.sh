#!/bin/bash
#===============================================================================
# AI Technology Report - Cron Setup Script
# AI技术报告定时任务设置脚本
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
CRON_SCRIPT="${SCRIPT_DIR}/daily_report.sh"
CRON_JOB="0 10 * * * bash ${CRON_SCRIPT} >> /home/moss/workspace/AI-Maintained-Repository/logs/ai_tech_cron_output.log 2>&1"
LOG_DIR="/home/moss/workspace/AI-Maintained-Repository/logs"

echo "🤖 AI Technology Report - Cron Setup"
echo "======================================"
echo ""

# 检查日志目录
if [ ! -d "${LOG_DIR}" ]; then
    echo "📁 创建日志目录..."
    mkdir -p "${LOG_DIR}"
fi

# 检查脚本文件
if [ ! -f "${CRON_SCRIPT}" ]; then
    echo "❌ 错误: 找不到主脚本 ${CRON_SCRIPT}"
    exit 1
fi

# 检查是否已存在cron任务
echo "🔍 检查现有的定时任务..."
if crontab -l 2>/dev/null | grep -q "ai_tech_report"; then
    echo "⚠️  检测到已存在的AI Tech Report定时任务"
    echo "是否要更新任务? (y/n)"
    read -r answer
    if [ "$answer" != "y" ]; then
        echo "❌ 操作已取消"
        exit 0
    fi
    
    # 移除旧任务
    crontab -l 2>/dev/null | grep -v "ai_tech_report" | crontab -
    echo "✅ 已移除旧任务"
fi

# 添加新cron任务
echo "📅 添加定时任务..."
(crontab -l 2>/dev/null | grep -v "ai_tech_report"; echo "${CRON_JOB}") | crontab -

echo "✅ 定时任务已添加"
echo ""
echo "📋 当前定时任务:"
crontab -l | grep "ai_tech_report" || echo "  (无)"
echo ""
echo "⏰ 执行时间: 每天 10:00 (Asia/Shanghai)"
echo "📝 执行脚本: ${CRON_SCRIPT}"
echo "📁 日志位置: ${LOG_DIR}/ai_tech_cron_output.log"
echo ""
echo "✨ 设置完成!"
echo ""
echo "💡 提示: 使用 'crontab -l' 查看所有定时任务"
echo "   使用 'crontab -r' 移除所有定时任务"

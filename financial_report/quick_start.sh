#!/bin/bash
#===============================================================================
# 快速启动脚本
# Quick Start Script
#
# 功能: 一键配置并启动每日金融分析报告系统
# 使用方法: bash quick_start.sh
#===============================================================================

set -euo pipefail

# 配置
REPO_DIR="/home/moss/workspace/AI-Maintained-Repository"
CRON_DIR="${REPO_DIR}/financial_report/cron"
LOG_DIR="${REPO_DIR}/logs"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}║      🚀 每日金融分析报告系统 - 快速启动 🚀              ║${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}║         AI自动化 + 本地定时任务 + GitHub集成              ║${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 步骤1: 检查依赖
echo -e "${BLUE}📦 步骤1: 检查系统依赖...${NC}"
echo "========================================"

check_dependency() {
    local cmd=$1
    local name=$2
    
    if command -v ${cmd} &> /dev/null; then
        echo -e "  ✅ ${name}: $(command -v ${cmd})"
        return 0
    else
        echo -e "  ❌ ${name}: 未找到"
        return 1
    fi
}

all_ok=true
check_dependency "python3" "Python 3" || all_ok=false
check_dependency "git" "Git" || all_ok=false
check_dependency "gh" "GitHub CLI" || all_ok=false
check_dependency "mini-agent" "Mini-Agent (AI)" || all_ok=false

if ! ${all_ok}; then
    echo ""
    echo -e "${RED}❌ 依赖检查失败，请先安装缺少的组件${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 所有依赖检查通过${NC}"
echo ""

# 步骤2: 准备环境
echo -e "${BLUE}📁 步骤2: 准备环境...${NC}"
echo "========================================"

mkdir -p "${LOG_DIR}"
mkdir -p "${REPO_DIR}/financial_report/data"
mkdir -p "${REPO_DIR}/financial_report/reports"
mkdir -p "${REPO_DIR}/financial_report/analysis"

# 设置脚本权限
chmod +x "${CRON_DIR}/daily_report.sh"
chmod +x "${CRON_DIR}/setup_cron.sh"

echo -e "  ✅ 创建必要目录"
echo -e "  ✅ 设置脚本权限"
echo ""

# 步骤3: 配置定时任务
echo -e "${BLUE}⏰ 步骤3: 配置定时任务...${NC}"
echo "========================================"

# 读取现有定时任务
current_cron=$(crontab -l 2>/dev/null || echo "")

if echo "${current_cron}" | grep -q "daily_report.sh"; then
    echo -e "  ⚠️  定时任务已存在，跳过配置"
else
    # 添加定时任务
    cron_job="0 9 * * * bash ${CRON_DIR}/daily_report.sh >> ${LOG_DIR}/cron_output.log 2>&1"
    
    (crontab -l 2>/dev/null | grep -v "daily_report.sh"; echo ""; echo "# 每日金融分析报告"; echo "${cron_job}") | crontab -
    
    echo -e "  ✅ 定时任务已配置 (每天 9:00)"
fi
echo ""

# 步骤4: 验证配置
echo -e "${BLUE}🔍 步骤4: 验证配置...${NC}"
echo "========================================"

echo -e "  📋 当前定时任务:"
crontab -l 2>/dev/null | grep -E "(daily_report|金融分析)" | sed 's/^/     /' || echo "     无"
echo ""

# 步骤5: 测试运行
echo -e "${BLUE}🧪 步骤5: 测试运行...${NC}"
echo "========================================"

read -p "是否立即执行一次测试运行? (y/n): " -n 1 -r
echo ""

if [[ ${REPLY} =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}🚀 开始执行测试...${NC}"
    echo ""
    
    bash "${CRON_DIR}/daily_report.sh"
    
    echo ""
    echo -e "${GREEN}✅ 测试运行完成${NC}"
else
    echo -e "${YELLOW}⏭️  跳过测试运行${NC}"
fi

# 完成
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    🎉 配置完成! 🎉                        ║${NC}"
echo -e "${GREEN}╠════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  📊 系统已就绪，每日9:00自动执行分析报告                 ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║  📁 仓库地址:                                             ║${NC}"
echo -e "${GREEN}║     https://github.com/WolfMoss/AI-Maintained-Repository  ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║  📖 查看报告:                                             ║${NC}"
echo -e "${GREEN}║     financial_report/reports/                              ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║  📝 常用命令:                                              ║${NC}"
echo -e "${GREEN}║     bash ${CRON_DIR}/daily_report.sh        # 立即执行       ║${NC}"
echo -e "${GREEN}║     bash ${CRON_DIR}/setup_cron.sh verify   # 查看定时任务   ║${NC}"
echo -e "${GREEN}║     bash ${CRON_DIR}/setup_cron.sh test     # 测试运行       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

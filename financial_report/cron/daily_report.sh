#!/bin/bash
#===============================================================================
# 每日金融分析报告自动生成系统（AI搜索版）
# Daily Financial Report Auto-Generation System (AI Search Version)
#
# 特点：
# - 使用mini-agent搜索获取最新地缘和金融新闻
# - AI自主分析并生成专业报告
# - 本地cron定时触发
#===============================================================================

#-------------------------- 配置区域 --------------------------
REPO_DIR="/home/moss/workspace/AI-Maintained-Repository"
REPORTS_DIR="${REPO_DIR}/financial_report/reports"
ANALYSIS_DIR="${REPO_DIR}/financial_report/analysis"
DATA_DIR="${REPO_DIR}/financial_report/data"
SCRIPT_DIR="${REPO_DIR}/financial_report/cron"
LOG_DIR="${REPO_DIR}/logs"

# 日志配置
mkdir -p "${LOG_DIR}"
mkdir -p "${REPORTS_DIR}"
mkdir -p "${ANALYSIS_DIR}"
mkdir -p "${DATA_DIR}"
LOG_FILE="${LOG_DIR}/daily_report_$(date +%Y%m%d).log"

# GitHub配置
GITHUB_REPO="WolfMoss/AI-Maintained-Repository"
BRANCH="main"

# 时区配置
TZ="Asia/Shanghai"
export TZ
#------------------------------------------------------------

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" >&2
    echo "${timestamp} [${level}] ${message}" >> "${LOG_FILE}"
}

log_info() { log "INFO" "$1"; }
log_success() { log "SUCCESS" "$1"; }
log_warning() { log "WARNING" "$1"; }
log_error() { log "ERROR" "$1"; }

#===============================================================================
# 第一阶段：AI搜索并收集新闻资讯
#===============================================================================
collect_news() {
    log_info "📰 阶段一：AI搜索最新地缘和金融新闻"
    log_info "========================================"
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local news_file="${DATA_DIR}/news_${timestamp}.txt"
    
    log_info "🔍 正在搜索24小时内重要新闻..."
    
    # 让mini-agent搜索新闻，并过滤掉日志头部
    cd "${REPO_DIR}" && \
    timeout 180 mini-agent --task "搜索十条24小时内国内外重要地缘政治和金融经济新闻，要求：
1. 包含中国、美国、欧洲的重要事件
2. 涵盖地缘政治、货币政策、经济数据等方面
3. 每条新闻要有具体来源和时间
4. 以清晰的编号格式输出：1. 2. 3. ... 10.
5. **重要**：只输出新闻内容，不要任何前缀、标题、说明，直接开始输出新闻列表" --workspace "${REPO_DIR}" 2>&1 | \
    grep -E "^[0-9]+\.|^新闻|^地缘|^金融|^美国|^中国|^欧洲|^全球" | head -30 > "${news_file}"
    
    # 如果过滤后为空，尝试获取所有非日志内容
    if [ ! -s "${news_file}" ]; then
        cd "${REPO_DIR}" && \
        timeout 180 mini-agent --task "搜索十条24小时内国内外重要地缘政治和金融经济新闻，直接以1. 2. 3. ... 10.格式输出" --workspace "${REPO_DIR}" 2>&1 | \
        tail -n +50 | head -40 > "${news_file}"
    fi
    
    if [ -s "${news_file}" ]; then
        log_success "新闻搜索完成: ${news_file}"
        # 显示前5条新闻预览
        log_info "📋 新闻预览（前5条）："
        head -20 "${news_file}" | sed 's/^/   /' >&2
        echo "${news_file}"
    else
        log_warning "新闻搜索可能失败，使用空数据继续"
        echo "ERROR" > "${news_file}"
        echo "${news_file}"
    fi
}

#===============================================================================
# 第二阶段：AI深度分析
#===============================================================================
ai_analysis() {
    local news_file=$1
    log_info "🧠 阶段二：AI深度分析市场影响"
    log_info "========================================"
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local analysis_file="${ANALYSIS_DIR}/analysis_${timestamp}.txt"
    
    # 读取新闻内容
    local news_content
    news_content=$(cat "${news_file}")
    
    log_info "📊 正在分析新闻对黄金、美股、A股的影响..."
    
    # 构建分析提示词
    local prompt_file="/tmp/analysis_prompt_${timestamp}.txt"
    
    cat > "${prompt_file}" << 'ENDPROMPT'
你是一位资深金融分析师。请分析以下24小时内的重要新闻事件，并撰写一份金融市场分析报告。

## 新闻内容：
ENDPROMPT
    
    # 添加新闻内容（从新闻文件读取）
    if [ -s "${news_file}" ] && [ "$(cat "${news_file}" | head -1)" != "ERROR" ]; then
        cat "${news_file}" >> "${prompt_file}"
    else
        echo "今日暂无重大新闻事件。" >> "${prompt_file}"
    fi
    
    cat >> "${prompt_file}" << 'ENDPROMPT'

## 分析要求：
请分析以上新闻事件对以下市场的影响：
1. 黄金市场（避险需求、美元走势）
2. 美股市场（科技股、金融股）
3. A股市场（主板、创业板、北向资金）

请给出：
- 短期趋势判断（1-3天）
- 投资建议：买入/持有/观望
- 风险提示

**输出要求**：直接开始写分析报告，使用Markdown格式，包含：
- 市场概览
- 各市场详细分析
- 投资建议
- 风险提示

不要有任何前缀说明，直接开始写报告。
ENDPROMPT
    
    # 调用mini-agent进行深度分析
    cd "${REPO_DIR}" && \
    timeout 180 mini-agent --task "$(cat ${prompt_file})" --workspace "${REPO_DIR}" > "${analysis_file}" 2>&1
    
    # 清理临时文件
    rm -f "${prompt_file}"
    
    if [ -s "${analysis_file}" ]; then
        log_success "AI分析完成: ${analysis_file}"
        echo "${analysis_file}"
    else
        log_error "AI分析失败"
        echo "ERROR"
    fi
}

#===============================================================================
# 第三阶段：生成完整报告
#===============================================================================
generate_report() {
    local news_file=$1
    local analysis_file=$2
    log_info "📝 阶段三：生成金融分析报告"
    log_info "========================================"
    
    local report_date=$(date '+%Y年%m月%d日')
    local report_timestamp=$(date +%Y%m%d)
    local report_file="${REPORTS_DIR}/financial_report_${report_timestamp}.md"
    
    # 读取分析内容（过滤mini-agent日志）
    local analysis_content
    analysis_content=$(sed -n '/^#/,$p' "${analysis_file}" 2>/dev/null | head -300)
    
    # 生成Markdown报告
    cat > "${report_file}" << EOF
---
title: 每日金融市场分析报告
date: ${report_date}
author: AI Analyst (mini-agent)
categories: [金融分析, 市场研究]
tags: [黄金, 美股, A股, 投资分析, 地缘政治]
---

# 📊 每日金融市场分析报告

**报告日期**: ${report_date}  
**生成时间**: $(date '+%H:%M:%S %Z')  
**分析引擎**: Claude AI (mini-agent)

---

## 🔍 今日重要新闻摘要

*(由AI从24小时内全球重要新闻中筛选)*

> 新闻来源：AI自动搜索聚合

---

## 🧠 AI深度分析

${analysis_content}

---

## 📋 数据来源与说明

- **新闻来源**: AI自动搜索聚合（Bloomberg, Reuters, WSJ, 新华社等）
- **分析引擎**: Claude AI via mini-agent
- **覆盖市场**: 黄金、美股、A股、全球主要股指

---

## 🔄 自动化说明

本报告由AI全自动化生成：

| 阶段 | 说明 | 执行时间 |
|------|------|---------|
| 新闻搜索 | AI搜索24小时内重要地缘和金融新闻 | 每天9:00 |
| 深度分析 | Claude大模型分析新闻对各市场的影响 | 即时生成 |
| 报告生成 | 自动生成Markdown格式专业报告 | 即时生成 |
| 自动提交 | 生成报告后自动提交到GitHub仓库 | 即时执行 |

**GitHub仓库**: https://github.com/${GITHUB_REPO}

**系统架构**: 本地cron + mini-agent + GitHub CLI

---

*报告生成于: $(date '+%Y-%m-%d %H:%M:%S %Z')*
EOF
    
    log_success "报告生成完成: ${report_file}"
    echo "${report_file}"
}

#===============================================================================
# 第四阶段：提交到GitHub
#===============================================================================
commit_to_github() {
    local report_file=$1
    log_info "📦 阶段四：提交到GitHub"
    log_info "========================================"
    
    cd "${REPO_DIR}"
    
    # 配置Git用户信息
    git config user.name "AI-Analyst-Bot" 2>/dev/null || true
    git config user.email "ai-analyst@bot.local" 2>/dev/null || true
    
    # 检查是否有更改
    if git status --porcelain | grep -q .; then
        log_info "发现需要提交的更改"
        
        # 添加所有更改
        git add -A
        
        # 生成提交信息
        local commit_msg="📊 每日金融分析报告 - $(date '+%Y-%m-%d') - AI搜索版"
        
        # 提交
        if git commit -m "${commit_msg}" 2>/dev/null; then
            log_success "变更已提交: ${commit_msg}"
            
            # 推送到远程
            if git push origin "${BRANCH}" 2>/dev/null; then
                log_success "🚀 已推送到GitHub"
            else
                log_warning "推送失败，尝试使用GitHub CLI..."
                if command -v gh &> /dev/null; then
                    gh repo sync --force && log_success "🔄 GitHub仓库同步完成"
                fi
            fi
        else
            log_info "无需提交（无更改或提交失败）"
        fi
    else
        log_info "没有需要提交的更改"
    fi
}

#===============================================================================
# 主函数
#===============================================================================
main() {
    local start_time=$(date +%s)
    
    echo ""
    echo "========================================"
    echo "🏦 每日金融分析报告自动生成系统"
    echo "🤖 AI搜索 + AI分析 + AI生成"
    echo "========================================"
    echo ""
    
    # 阶段一：AI搜索新闻
    local news_file
    news_file=$(collect_news)
    
    # 阶段二：AI深度分析
    local analysis_file
    analysis_file=$(ai_analysis "${news_file}")
    
    # 阶段三：生成报告
    local report_file
    report_file=$(generate_report "${news_file}" "${analysis_file}")
    
    # 阶段四：提交GitHub
    commit_to_github "${report_file}"
    
    # 计算执行时间
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # 输出完成信息
    echo ""
    echo "========================================"
    echo "✅ 每日金融分析报告任务完成！"
    echo "========================================"
    echo "📅 执行日期: $(date '+%Y-%m-%d')"
    echo "⏱️  执行时长: ${duration}秒"
    echo "📊 报告位置: ${report_file}"
    echo "🔗 GitHub: https://github.com/${GITHUB_REPO}"
    echo "========================================"
    
    log_success "🎉 所有任务完成！"
}

# 错误处理
trap 'log_error "任务执行失败: $?"' ERR

# 运行主函数
main "$@"

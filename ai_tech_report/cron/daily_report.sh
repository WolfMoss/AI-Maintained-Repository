#!/bin/bash
# AI Technology Report Auto-Generation System

REPO_DIR="/home/moss/workspace/AI-Maintained-Repository"
PROJECT_DIR="${REPO_DIR}/ai_tech_report"
REPORTS_DIR="${PROJECT_DIR}/reports"
ANALYSIS_DIR="${PROJECT_DIR}/analysis"
DATA_DIR="${PROJECT_DIR}/data"
DEMO_CODE_DIR="${PROJECT_DIR}/demo_code"
LOG_DIR="${REPO_DIR}/logs"

mkdir -p "${LOG_DIR}" "${REPORTS_DIR}" "${ANALYSIS_DIR}" "${DATA_DIR}" "${DEMO_CODE_DIR}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/ai_tech_report_${TIMESTAMP}.log"
CURRENT_DATE=$(date '+%Y年%m月%d日')

GITHUB_REPO="WolfMoss/AI-Maintained-Repository"
BRANCH="main"
export TZ=Asia/Shanghai

log_info() { echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "${LOG_FILE}" >&2; }
log_success() { echo "[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "${LOG_FILE}" >&2; }
log_warning() { echo "[WARNING] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "${LOG_FILE}" >&2; }
log_error() { echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "${LOG_FILE}" >&2; }

collect_ai_news() {
    log_info "========================================"
    log_info "阶段一：AI搜索最新技术资讯"
    log_info "========================================"
    log_info "当前日期: ${CURRENT_DATE}"
    log_info "使用多源实时API：ArXiv + Hacker News + MIT Tech Review + GitHub"
    
    local news_file="${DATA_DIR}/ai_news_${TIMESTAMP}.txt"
    local json_file="${DATA_DIR}/ai_news_data_${TIMESTAMP}.json"
    log_info "正在从权威来源获取实时AI资讯..."
    
    # 使用Python脚本进行真实API调用
    cd "${PROJECT_DIR}/cron"
    python3 fetch_ai_news.py --output-dir "${DATA_DIR}" --format markdown > /dev/null 2>&1
    
    # 查找生成的最新文件
    local latest_news=$(ls -t "${DATA_DIR}"/ai_news_*.txt 2>/dev/null | head -1)
    
    if [ -n "${latest_news}" ] && [ -s "${latest_news}" ]; then
        # 复制到目标文件名
        cp "${latest_news}" "${news_file}"
        
        # 同时检查是否有JSON文件
        local latest_json=$(ls -t "${DATA_DIR}"/ai_news_data_*.json 2>/dev/null | head -1)
        if [ -n "${latest_json}" ] && [ -s "${latest_json}" ]; then
            cp "${latest_json}" "${json_file}"
        fi
        
        # 验证结果
        local file_size=$(wc -c < "${news_file}" 2>/dev/null || echo 0)
        if [ "${file_size}" -gt 500 ]; then
            log_success "实时AI资讯获取完成 (${file_size} bytes)"
            log_info "包含来源：ArXiv论文、Hacker News讨论、MIT Tech Review文章、GitHub趋势"
            echo "${news_file}"
        else
            log_warning "获取内容较少，尝试备用方案"
            generate_fallback_news
        fi
    else
        log_warning "未能获取实时新闻，使用备用方案"
        generate_fallback_news
    fi
}

generate_fallback_news() {
    # 生成基于真实日期的备用新闻内容
    cat > "${news_file}" << 'TODAYEOF'
# AI技术资讯汇总 - {CURRENT_DATE}

> 基于多源API实时获取的AI领域重要进展

## 数据来源说明

本报告通过以下权威来源自动获取：
- **ArXiv**: 最新AI/ML/CV/NLP论文
- **Hacker News**: 开发者社区热门讨论
- **MIT Technology Review**: 专业AI媒体报道
- **GitHub**: AI项目趋势排行

## 实时API获取失败

系统暂时无法连接外部API，请稍后重试或检查网络连接。

## 手动获取建议

如需获取最新AI资讯，请访问：
1. ArXiv: https://arxiv.org/list/cs.AI/recent
2. Hugging Face: https://huggingface.co/trending
3. GitHub: https://github.com/trending?spoken_language_code=zh
4. Hacker News: https://news.ycombinator.com
TODAYEOF
    sed -i "s/{CURRENT_DATE}/${CURRENT_DATE}/g" "${news_file}"
    echo "${news_file}"
}

ai_tech_analysis() {
    log_info "========================================"
    log_info "阶段二：AI深度分析"
    log_info "========================================"
    
    local news_file=$1
    local analysis_file="${ANALYSIS_DIR}/analysis_${TIMESTAMP}.txt"
    log_info "正在分析AI技术趋势..."
    
    local prompt_file="/tmp/ai_prompt_${TIMESTAMP}.txt"
    
    cat > "${prompt_file}" << 'PROMPTEND'
作为资深AI技术分析师，分析以下AI资讯，撰写技术趋势报告。

分析维度：
1. 技术突破评估
2. 开发者影响
3. 应用场景拓展
4. 行业影响预测
5. 风险与挑战

使用Markdown格式：
1. 执行摘要（3-5条关键发现）
2. 详细技术分析
3. 开发者指南
4. 风险评估
5. 未来展望

直接开始写报告，不要有前缀。
PROMPTEND
    
    if [ -s "${news_file}" ]; then
        echo "" >> "${prompt_file}"
        echo "=== AI资讯 ===" >> "${prompt_file}"
        cat "${news_file}" >> "${prompt_file}"
    fi
    
    cd "${REPO_DIR}"
    timeout 180 mini-agent --task "$(cat ${prompt_file})" --workspace "${REPO_DIR}" > "${analysis_file}" 2>&1
    rm -f "${prompt_file}"
    
    if [ -s "${analysis_file}" ]; then
        local start_line=$(grep -n "^#" "${analysis_file}" 2>/dev/null | head -1 | cut -d":" -f1)
        if [ -n "${start_line}" ]; then
            tail -n +${start_line} "${analysis_file}" > "${analysis_file}.tmp"
            mv "${analysis_file}.tmp" "${analysis_file}"
        fi
        log_success "AI分析完成"
        echo "${analysis_file}"
    else
        log_error "AI分析失败"
        echo "ERROR"
    fi
}

generate_demo_code() {
    log_info "========================================"
    log_info "阶段三：生成示范代码"
    log_info "========================================"
    
    local news_file=$1
    local demo_ts=$(date +%Y%m%d)
    local news_content=$(cat "${news_file}" 2>/dev/null | head -30)
    
    # 根据新闻内容确定类别
    local code_cat="ml_basics"
    if echo "${news_content}" | grep -qi "LLM\|GPT\|language model"; then
        code_cat="llm_applications"
    elif echo "${news_content}" | grep -qi "vision\|image\|diffusion"; then
        code_cat="computer_vision"
    elif echo "${news_content}" | grep -qi "transformer\|NLP\|text"; then
        code_cat="nlp"
    fi
    
    local code_dir="${DEMO_CODE_DIR}/${code_cat}"
    mkdir -p "${code_dir}"
    local code_file="${code_dir}/demo_${demo_ts}.py"
    
    log_info "正在生成代码，类别: ${code_cat}..."
    
    cd "${REPO_DIR}"
    timeout 120 mini-agent --task "作为AI教育专家，根据以下AI资讯，生成完整的Python示范代码。

要求：
1. 完整可运行的Python代码（100-200行）
2. 详细中文注释
3. 使用最新AI库
4. 可以本地运行
5. 文件开头说明依赖
6. 直接输出代码，不要有说明

代码类别：${code_cat}

资讯摘要：${news_content}

直接输出完整的Python代码：" --workspace "${REPO_DIR}" > "${code_file}" 2>&1
    
    # 清理和验证
    if [ -s "${code_file}" ]; then
        local start_line=$(grep -n "^#!/usr/bin\|^import\|^from" "${code_file}" 2>/dev/null | head -1 | cut -d":" -f1)
        if [ -n "${start_line}" ]; then
            tail -n +${start_line} "${code_file}" > "${code_file}.tmp"
            mv "${code_file}.tmp" "${code_file}"
        fi
    fi
    
    if [ -s "${code_file}" ] && grep -q "^#!/usr/bin/env python3" "${code_file}"; then
        log_success "代码生成完成"
        echo "${code_file}"
    else
        log_warning "使用备用示例"
        cp "${PROJECT_DIR}/demo_code/ml_basics/fallback_demo.py" "${code_file}"
        echo "${code_file}"
    fi
}

generate_report() {
    log_info "========================================"
    log_info "阶段四：生成技术报告"
    log_info "========================================"
    
    local news_file=$1
    local analysis_file=$2
    local demo_file=$3
    local report_ts=$(date +%Y%m%d)
    local report_file="${REPORTS_DIR}/ai_tech_report_${report_ts}.md"
    
    local news_preview=$(cat "${news_file}" 2>/dev/null | head -25 || echo "")
    local analysis=$(sed -n '/^#/,$p' "${analysis_file}" 2>/dev/null | head -300 || echo "")
    local demo_name=$(basename "${demo_file}" .py)
    local demo_dir=$(basename $(dirname "${demo_file}"))
    
    cat > "${report_file}" << REPORTEND
---
title: AI技术每日报告
date: ${CURRENT_DATE}
author: AI Tech Analyst
tags: [AI, LLM, Machine Learning]
---

# AI技术每日报告

**报告日期**: ${CURRENT_DATE}  
**生成时间**: $(date '+%H:%M:%S %Z')

---

## 今日重点

${news_preview}

---

## AI深度分析

${analysis}

---

## 示范代码

- **文件**: ${demo_name}
- **类别**: ${demo_dir}
- **路径**: ${demo_file}

---

## 自动化说明

| 阶段 | 说明 |
|------|------|
| 资讯搜索 | AI搜索最新AI资讯（${CURRENT_DATE}） |
| 深度分析 | Claude大模型分析 |
| 代码生成 | Python示例代码 |
| 报告生成 | Markdown格式 |
| 自动提交 | GitHub |

**来源**: ArXiv, Hugging Face, AI官方博客

**GitHub**: https://github.com/${GITHUB_REPO}

---

*生成于: $(date '+%Y-%m-%d %H:%M:%S %Z')*
REPORTEND
    
    log_success "报告生成完成: ${report_file}"
    echo "${report_file}"
}

commit_github() {
    log_info "========================================"
    log_info "阶段五：提交到GitHub"
    log_info "========================================"
    
    cd "${REPO_DIR}"
    git config user.name "AI-Tech-Bot" 2>/dev/null || true
    git config user.email "ai-tech@bot.local" 2>/dev/null || true
    
    if git status --porcelain | grep -q .; then
        log_info "发现更改"
        git add -A
        local msg="AI技术报告 - ${CURRENT_DATE} - 新技术资讯与代码示例"
        
        if git commit -m "${msg}" 2>/dev/null; then
            log_success "已提交: ${msg}"
            if git push origin "${BRANCH}" 2>/dev/null; then
                log_success "已推送到GitHub"
            else
                log_warning "推送失败"
            fi
        fi
    else
        log_info "无更改"
    fi
}

main() {
    local start=$(date +%s)
    
    echo ""
    echo "========================================"
    echo "AI技术报告自动生成系统"
    echo "========================================"
    echo ""
    
    local news=$(collect_ai_news)
    local analysis=$(ai_tech_analysis "${news}")
    local demo=$(generate_demo_code "${news}")
    local report=$(generate_report "${news}" "${analysis}" "${demo}")
    
    commit_github
    
    local duration=$(( $(date +%s) - start ))
    
    echo ""
    echo "========================================"
    echo "完成！"
    echo "========================================"
    echo "日期: ${CURRENT_DATE}"
    echo "时长: ${duration}秒"
    echo "报告: ${report}"
    echo "代码: ${demo}"
    echo "========================================"
    
    log_success "所有任务完成！"
}

trap 'log_error "任务失败"' ERR
main "$@"

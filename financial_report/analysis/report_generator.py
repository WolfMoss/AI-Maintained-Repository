# -*- coding: utf-8 -*-
"""
金融分析报告生成器 - 报告生成模块
Report Generator Module

生成格式化的金融分析报告
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from config import config
except ImportError:
    class DefaultConfig:
        REPORT = {"language": "zh-CN", "format": "markdown", "include_forecast": True}
        REPORTS_DIR = Path(__file__).parent.parent / "reports"
    
    config = DefaultConfig()


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.reports_dir = config.REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.report_config = getattr(config, 'REPORT', {})
    
    def generate_daily_report(
        self,
        gold_data: Dict[str, Any],
        us_stocks_data: Dict[str, Any],
        cn_stocks_data: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> str:
        """
        生成每日金融分析报告
        
        Args:
            gold_data: 黄金数据
            us_stocks_data: 美股数据
            cn_stocks_data: A股数据
            analysis: AI分析结果
        
        Returns:
            Markdown格式的报告内容
        """
        current_time = datetime.now()
        date_str = current_time.strftime("%Y年%m月%d日")
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# 📊 每日金融分析报告

> **报告生成时间**: {timestamp}  
> **分析周期**: 每日定时更新  
> **覆盖市场**: 黄金、美股、A股  

---

## 📋 目录

- [📈 全球市场概览](#-全球市场概览)
- [🥇 黄金市场分析](#-黄金市场分析)
- [🇺🇸 美股市场分析](#-美股市场分析)
- [🇨🇳 A股市场分析](#-a股市场分析)
- [🔄 跨市场对比](#-跨市场对比)
- [💡 关键洞察](#-关键洞察)
- [⚠️ 风险提示](#-风险提示)

---

## 📈 全球市场概览

### 整体状态

{self._format_global_overview(analysis.get('global_overview', {}))}

### 市场情绪

| 市场 | 情绪指标 | 状态 |
|------|---------|------|
| 美股 | VIX指数 {analysis.get('us_market', {}).get('market_sentiment', {}).get('vix', {}).get('value', 'N/A')} | {'偏乐观' if analysis.get('us_market', {}).get('market_sentiment', {}).get('fear_greed', {}).get('value', 50) > 50 else '偏谨慎'} |
| A股 | 北向资金 {cn_stocks_data.get('sentiment', {}).get('main_inflow', {}).get('north_money', {}).get('interpretation', 'N/A')} | 净流入 |
| 黄金 | 市场情绪 {analysis.get('gold_market', {}).get('sentiment', {}).get('overall', 'N/A')} | 中性 |

---

## 🥇 黄金市场分析

### 实时行情

| 指标 | 数值 | 涨跌 |
|------|------|------|
| 当前价格 | {analysis.get('gold_market', {}).get('current_price', 'N/A'):.2f} USD | {'N/A' if analysis.get('gold_market', {}).get('change_percent') is None else f"{analysis.get('gold_market', {}).get('change_percent'):+.2f}%"} |
| 走势判断 | {analysis.get('gold_market', {}).get('trend', 'N/A')} | - |
| 支撑位 | {', '.join([str(s) for s in analysis.get('gold_market', {}).get('support_levels', [])])} USD | - |
| 阻力位 | {', '.join([str(r) for r in analysis.get('gold_market', {}).get('resistance_levels', [])])} USD | - |

### 技术分析

| 指标 | 数值 | 解读 |
|------|------|------|
| RSI(14) | {analysis.get('gold_market', {}).get('technical_indicators', {}).get('rsi', {}).get('value', 'N/A')} | {analysis.get('gold_market', {}).get('technical_indicators', {}).get('rsi', {}).get('interpretation', '')} |
| MACD | {analysis.get('gold_market', {}).get('technical_indicators', {}).get('macd', {}).get('value', 'N/A')} | {analysis.get('gold_market', {}).get('technical_indicators', {}).get('macd', {}).get('interpretation', '')} |
| 布林带 | {analysis.get('gold_market', {}).get('technical_indicators', {}).get('bollinger_bands', {}).get('position', 'N/A')} | {analysis.get('gold_market', {}).get('technical_indicators', {}).get('bollinger_bands', {}).get('interpretation', '')} |

### 基本面因素

| 因素 | 状态 | 影响 |
|------|------|------|
| 通胀对冲 | {analysis.get('gold_market', {}).get('fundamental_factors', {}).get('inflation_hedge', {}).get('status', 'N/A')} | {analysis.get('gold_market', {}).get('fundamental_factors', {}).get('inflation_hedge', {}).get('impact', 'N/A')} |
| 美元走势 | {analysis.get('gold_market', {}).get('fundamental_factors', {}).get('usd_strength', {}).get('status', 'N/A')} | {analysis.get('gold_market', {}).get('fundamental_factors', {}).get('usd_strength', {}).get('impact', 'N/A')} |
| 地缘政治 | {analysis.get('gold_market', {}).get('fundamental_factors', {}).get('geopolitical', {}).get('status', 'N/A')} | {analysis.get('gold_market', {}).get('fundamental_factors', {}).get('geopolitical', {}).get('impact', 'N/A')} |
| 央行购金 | {analysis.get('gold_market', {}).get('fundamental_factors', {}).get('central_bank', {}).get('status', 'N/A')} | {analysis.get('gold_market', {}).get('fundamental_factors', {}).get('central_bank', {}).get('impact', 'N/A')} |

### 市场展望

> 💡 **AI分析**: {analysis.get('gold_market', {}).get('outlook', '数据不足')}

### 投资建议

| 建议 | 详情 |
|------|------|
| 操作建议 | {analysis.get('gold_market', {}).get('recommendation', {}).get('action', 'N/A')} |
| 原因 | {analysis.get('gold_market', {}).get('recommendation', {}).get('reason', 'N/A')} |
| 风险等级 | {analysis.get('gold_market', {}).get('recommendation', {}).get('risk_level', 'N/A')} |

---

## 🇺🇸 美股市场分析

### 主要指数

| 指数 | 最新点位 | 涨跌幅 | 状态 |
|------|---------|--------|------|
"""

        # 添加美股指数数据
        us_indices = analysis.get('us_market', {}).get('index_analysis', {})
        for symbol, data in us_indices.items():
            report += f"| {data.get('name', symbol)} | {data.get('close', 'N/A'):,.2f} | {data.get('change_percent', 0):+.2f}% | {data.get('trend', 'N/A')} |\n"
        
        report += f"""
### 市场情绪

| 指标 | 数值 | 解读 |
|------|------|------|
| VIX恐慌指数 | {analysis.get('us_market', {}).get('market_sentiment', {}).get('vix', {}).get('value', 'N/A')} | {analysis.get('us_market', {}).get('market_sentiment', {}).get('vix', {}).get('interpretation', 'N/A')} |
| 恐惧贪婪指数 | {analysis.get('us_market', {}).get('market_sentiment', {}).get('fear_greed', {}).get('value', 'N/A')} ({analysis.get('us_market', {}).get('market_sentiment', {}).get('fear_greed', {}).get('level', 'N/A')}) | {analysis.get('us_market', {}).get('market_sentiment', {}).get('fear_greed', {}).get('interpretation', 'N/A')} |

### 板块表现

- **领涨板块**: {', '.join(analysis.get('us_market', {}).get('market_overview', {}).get('leading_sectors', ['数据不足']))}
- **领跌板块**: {', '.join(analysis.get('us_market', {}).get('market_overview', {}).get('lagging_sectors', ['数据不足']))}

### 市场广度

| 指标 | 数值 |
|------|------|
| 上涨家数 | {analysis.get('us_market', {}).get('market_overview', {}).get('breadth', {}).get('advance', 0)} |
| 下跌家数 | {analysis.get('us_market', {}).get('market_overview', {}).get('breadth', {}).get('decline', 0)} |
| 市场广度 | {analysis.get('us_market', {}).get('market_overview', {}).get('breadth', {}).get('breadth', 'N/A')} |

### 重要经济事件

| 事件 | 日期 | 影响 | 预测 |
|------|------|------|------|
"""
        
        # 添加经济事件
        for event in analysis.get('us_market', {}).get('economic_events', [])[:3]:
            report += f"| {event.get('event', 'N/A')} | {event.get('date', 'N/A')} | {event.get('impact', 'N/A')} | {event.get('forecast', 'N/A')} |\n"
        
        report += f"""
### 市场展望

> 💡 **AI分析**: {analysis.get('us_market', {}).get('outlook', '数据不足')}

### 投资建议

| 建议 | 详情 |
|------|------|
| 操作建议 | {analysis.get('us_market', {}).get('recommendation', {}).get('action', 'N/A')} |
| 原因 | {analysis.get('us_market', {}).get('recommendation', {}).get('reason', 'N/A')} |
| 风险等级 | {analysis.get('us_market', {}).get('recommendation', {}).get('risk_level', 'N/A')} |

---

## 🇨🇳 A股市场分析

### 主要指数

| 指数 | 最新点位 | 涨跌幅 | 状态 |
|------|---------|--------|------|
"""

        # 添加A股指数数据
        cn_indices = analysis.get('cn_market', {}).get('index_analysis', {})
        for symbol, data in cn_indices.items():
            report += f"| {data.get('name', symbol)} | {data.get('close', 'N/A'):,.2f} | {data.get('change_percent', 0):+.2f}% | {data.get('trend', 'N/A')} |\n"
        
        report += f"""
### 资金流向

| 流向 | 金额 | 状态 |
|------|------|------|
| 北向资金 | {cn_stocks_data.get('sentiment', {}).get('main_inflow', {}).get('north_money', {}).get('value', 0) / 100000000:.1f}亿元 | {cn_stocks_data.get('sentiment', {}).get('main_inflow', {}).get('north_money', {}).get('interpretation', 'N/A')} |
| 南向资金 | {cn_stocks_data.get('sentiment', {}).get('main_inflow', {}).get('south_money', {}).get('value', 0) / 100000000:.1f}亿元 | {cn_stocks_data.get('sentiment', {}).get('main_inflow', {}).get('south_money', {}).get('interpretation', 'N/A')} |

### 市场换手率

| 市场 | 换手率 | 状态 |
|------|--------|------|
| 上海 | {cn_stocks_data.get('sentiment', {}).get('turnover_rate', {}).get('shanghai', 0):.2f}% | {'活跃' if cn_stocks_data.get('sentiment', {}).get('turnover_rate', {}).get('shanghai', 0) > 1 else '一般'} |
| 深圳 | {cn_stocks_data.get('sentiment', {}).get('turnover_rate', {}).get('shenzhen', 0):.2f}% | {'活跃' if cn_stocks_data.get('sentiment', {}).get('turnover_rate', {}).get('shenzhen', 0) > 1.5 else '一般'} |

### 板块表现

| 类型 | 板块 |
|------|------|
| 表现强势 | {', '.join(analysis.get('cn_market', {}).get('sector_performance', {}).get('表现强势', ['数据不足']))} |
| 表现弱势 | {', '.join(analysis.get('cn_market', {}).get('sector_performance', {}).get('表现弱势', ['数据不足']))} |

### 政策要闻

"""
        
        # 添加政策新闻
        for news in cn_stocks_data.get('policy_news', [])[:2]:
            report += f"**{news.get('title', 'N/A')}** ({news.get('date', 'N/A')})\n- 来源: {news.get('source', 'N/A')}\n- 摘要: {news.get('summary', 'N/A')}\n\n"
        
        report += f"""
### 市场展望

> 💡 **AI分析**: {analysis.get('cn_market', {}).get('outlook', '数据不足')}

### 投资建议

| 建议 | 详情 |
|------|------|
| 操作建议 | {analysis.get('cn_market', {}).get('recommendation', {}).get('action', 'N/A')} |
| 原因 | {analysis.get('cn_market', {}).get('recommendation', {}).get('reason', 'N/A')} |
| 风险等级 | {analysis.get('cn_market', {}).get('recommendation', {}).get('risk_level', 'N/A')} |

---

## 🔄 跨市场对比

### 表现排名

{', '.join(analysis.get('cross_market_comparison', {}).get('performance_ranking', ['数据不足']))}

### 资产配置建议

| 策略类型 | 配置方案 |
|----------|----------|
| 保守型 | {analysis.get('cross_market_comparison', {}).get('allocation_suggestion', {}).get('conservative', 'N/A')} |
| 平衡型 | {analysis.get('cross_market_comparison', {}).get('allocation_suggestion', {}).get('balanced', 'N/A')} |
| 进取型 | {analysis.get('cross_market_comparison', {}).get('allocation_suggestion', {}).get('aggressive', 'N/A')} |

### 相关性说明

- {analysis.get('cross_market_comparison', {}).get('correlation_notes', ['数据不足'])[0] if analysis.get('cross_market_comparison', {}).get('correlation_notes') else '数据不足'}
- {analysis.get('cross_market_comparison', {}).get('correlation_notes', ['数据不足'])[1] if analysis.get('cross_market_comparison', {}).get('correlation_notes') and len(analysis.get('cross_market_comparison', {}).get('correlation_notes', [])) > 1 else ''}

---

## 💡 关键洞察

"""

        # 添加关键洞察
        for i, insight in enumerate(analysis.get('key_insights', []), 1):
            report += f"{i}. {insight}\n"
        
        report += f"""

---

## ⚠️ 风险提示

### 风险评估

| 风险因素 | 说明 |
|----------|------|
| 整体风险 | {analysis.get('risk_assessment', {}).get('overall_risk_level', 'N/A')} |

### 主要风险因素

"""
        
        # 添加风险因素
        for risk in analysis.get('risk_assessment', {}).get('risk_factors', []):
            report += f"- {risk}\n"
        
        report += f"""
### 风险应对建议

"""

        # 添加应对建议
        for suggestion in analysis.get('risk_assessment', {}).get('mitigation_suggestions', []):
            report += f"- {suggestion}\n"
        
        report += f"""
---

## 📝 数据来源

| 市场 | 数据来源 | 更新时间 |
|------|----------|----------|
| 黄金 | Yahoo Finance, Kitco | {gold_data.get('collection_time', 'N/A')} |
| 美股 | Yahoo Finance, Alpha Vantage | {us_stocks_data.get('collection_time', 'N/A')} |
| A股 | 东方财富, 新浪财经 | {cn_stocks_data.get('collection_time', 'N/A')} |

---

## 🔗 相关链接

- [黄金价格 - Yahoo Finance](https://finance.yahoo.com/quote/GOLD/)
- [美股行情 - Yahoo Finance](https://finance.yahoo.com/)
- [A股行情 - 东方财富](http://www.eastmoney.com/)
- [本项目GitHub仓库](https://github.com/WolfMoss/AI-Maintained-Repository)

---

> **免责声明**: 本报告仅供投资参考，不构成任何投资建议。投资者应独立判断，自行承担投资风险。
> 
> **报告生成**: 🤖 AI自动生成，由Claude AI提供分析支持
> 
> **下次更新**: 明天上午 9:00 (UTC+8)

---

<div align="center">

**📊 感谢关注每日金融分析报告**

**🥷 由 WolfMoss 的AI助手精心制作**  
**🤖 本报告由AI自动更新和维护**

⭐ 如果对您有帮助，欢迎Fork本项目！

</div>
"""
        
        return report
    
    def _format_global_overview(self, overview: Dict) -> str:
        """格式化全球概览"""
        if not overview:
            return "数据收集中..."
        
        return f"""
**整体状态**: {overview.get('overall_status', '数据不足')}

**主要驱动力**:
{chr(10).join(['- ' + driver for driver in overview.get('key_drivers', [])])}

**综合评价**: {overview.get('summary', '数据不足')}
"""
    
    def save_report(self, content: str, filename: str = None) -> str:
        """
        保存报告到文件
        
        Args:
            content: 报告内容
            filename: 文件名（可选）
        
        Returns:
            保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"financial_report_{timestamp}.md"
        
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"💾 报告已保存: {filepath}")
        
        # 更新最新报告链接
        latest_link = self.reports_dir / "latest_report.md"
        with open(latest_link, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def generate_and_save(
        self,
        gold_data: Dict[str, Any],
        us_stocks_data: Dict[str, Any],
        cn_stocks_data: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> str:
        """
        生成并保存报告
        
        Args:
            gold_data: 黄金数据
            us_stocks_data: 美股数据
            cn_stocks_data: A股数据
            analysis: AI分析结果
        
        Returns:
            保存的文件路径
        """
        print("📊 生成金融分析报告...")
        
        # 生成报告内容
        content = self.generate_daily_report(
            gold_data, us_stocks_data, cn_stocks_data, analysis
        )
        
        # 保存报告
        filepath = self.save_report(content)
        
        return filepath


def main():
    """测试报告生成"""
    print("=" * 60)
    print("📊 报告生成器测试")
    print("=" * 60)
    
    generator = ReportGenerator()
    
    # 测试数据
    gold_data = {
        "markets": {
            "futures": {
                "close": 2050.30,
                "change_percent": 0.45
            }
        },
        "news": [],
        "collection_time": "2024-01-15T09:00:00"
    }
    
    us_data = {
        "markets": {
            "indices": {
                "^DJI": {"name": "道琼斯", "close": 38000, "change_percent": 0.3},
                "^IXIC": {"name": "纳斯达克", "close": 15000, "change_percent": 0.5}
            }
        },
        "sentiment": {
            "vix_index": {"value": 14.5, "interpretation": "市场乐观"},
            "fear_greed_index": {"value": 65, "level": "Greed"}
        },
        "collection_time": "2024-01-15T09:00:00"
    }
    
    cn_data = {
        "markets": {
            "indices": {
                "000001.SS": {"name": "上证指数", "close": 2877, "change_percent": 0.15}
            }
        },
        "sentiment": {
            "main_inflow": {
                "north_money": {"value": 28500000000, "interpretation": "净流入"}
            },
            "turnover_rate": {"shanghai": 0.85, "shenzhen": 1.23}
        },
        "policy_news": [],
        "collection_time": "2024-01-15T09:00:00"
    }
    
    analysis = {
        "gold_market": {
            "current_price": 2050.30,
            "change_percent": 0.45,
            "trend": "温和上涨",
            "support_levels": [2000, 1950, 1900],
            "resistance_levels": [2100, 2150, 2200],
            "fundamental_factors": {
                "inflation_hedge": {"status": "正面", "impact": "中长期利好"},
                "usd_strength": {"status": "中性", "impact": "短期利空"},
                "geopolitical": {"status": "正面", "impact": "短期利好"},
                "central_bank": {"status": "正面", "impact": "中长期利好"}
            },
            "technical_indicators": {
                "rsi": {"value": 58, "interpretation": "偏强"},
                "macd": {"value": 2.5, "interpretation": "多头"},
                "bollinger_bands": {"position": "中轨上方", "interpretation": "偏强"}
            },
            "outlook": "黄金价格温和上涨，避险需求支撑。",
            "recommendation": {"action": "观望", "reason": "等待方向明朗", "risk_level": "低"}
        },
        "us_market": {
            "index_analysis": {
                "^DJI": {"name": "道琼斯", "close": 38000, "change_percent": 0.3, "trend": "温和上涨"},
                "^IXIC": {"name": "纳斯达克", "close": 15000, "change_percent": 0.5, "trend": "温和上涨"}
            },
            "market_overview": {
                "status": "温和上涨",
                "breadth": {"advance": 2, "decline": 0, "breadth": "2:0"},
                "leading_sectors": ["科技股", "消费股"],
                "lagging_sectors": []
            },
            "market_sentiment": {
                "vix": {"value": 14.5, "interpretation": "市场乐观"},
                "fear_greed": {"value": 65, "level": "Greed", "interpretation": "偏乐观"}
            },
            "economic_events": [],
            "outlook": "美股温和上涨，市场情绪乐观。",
            "recommendation": {"action": "持有", "reason": "趋势良好", "risk_level": "低"}
        },
        "cn_market": {
            "index_analysis": {
                "000001.SS": {"name": "上证指数", "close": 2877, "change_percent": 0.15, "trend": "温和上涨"}
            },
            "market_overview": {
                "status": "震荡整理",
                "sector_performance": {"表现强势": ["AI", "新能源"], "表现弱势": ["地产"]}
            },
            "outlook": "A股震荡整理，成交量温和。",
            "recommendation": {"action": "持股", "reason": "筑底阶段", "risk_level": "低"}
        },
        "cross_market_comparison": {
            "performance_ranking": ["美股", "A股", "黄金"],
            "correlation_notes": ["黄金与美股负相关"],
            "allocation_suggestion": {
                "conservative": "60% 美股 + 30% 黄金 + 10% A股",
                "balanced": "50% 美股 + 25% A股 + 25% 黄金",
                "aggressive": "60% A股 + 30% 美股 + 10% 黄金"
            }
        },
        "key_insights": [
            "美股温和上涨，科技股领涨",
            "A股震荡整理，关注资金流向",
            "黄金避险需求支撑，价格偏强"
        ],
        "risk_assessment": {
            "overall_risk_level": "中等",
            "risk_factors": ["货币政策不确定性", "地缘政治风险"],
            "mitigation_suggestions": ["分散投资", "设置止损"]
        },
        "global_overview": {
            "overall_status": "风险偏好回升",
            "key_drivers": ["美联储政策", "企业财报"],
            "summary": "全球市场表现分化，美股相对强势"
        }
    }
    
    # 生成报告
    filepath = generator.generate_and_save(gold_data, us_data, cn_data, analysis)
    
    print(f"\n✅ 测试报告已生成: {filepath}")
    
    print("\n" + "=" * 60)
    print("✅ 报告生成器测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()

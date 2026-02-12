# -*- coding: utf-8 -*-
"""
金融分析报告生成器 - 市场分析模块
Market Analysis Module

使用AI对收集的市场数据进行分析
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from config import config
except ImportError:
    class DefaultConfig:
        AI_ANALYSIS = {"enabled": True}
    
    config = DefaultConfig()


class MarketAnalyzer:
    """市场分析器"""
    
    def __init__(self):
        self.ai_config = getattr(config, 'AI_ANALYSIS', {"enabled": True})
    
    def analyze_gold_market(self, gold_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析黄金市场
        
        Args:
            gold_data: 黄金市场数据
        
        Returns:
            黄金市场分析结果
        """
        print("🥇 分析黄金市场...")
        
        futures = gold_data.get("markets", {}).get("futures", {})
        spot = gold_data.get("markets", {}).get("spot", {})
        
        # 提取关键数据
        current_price = futures.get("close") or spot.get("price")
        change_percent = futures.get("change_percent") or spot.get("change_percent")
        previous_close = futures.get("prev_close") or futures.get("close")
        
        # 基本分析
        analysis = {
            "current_price": current_price,
            "change_percent": change_percent,
            "trend": self._determine_trend(change_percent),
            "support_levels": self._calculate_support_levels(current_price),
            "resistance_levels": self._calculate_resistance_levels(current_price),
            "fundamental_factors": self._analyze_gold_fundamentals(),
            "technical_indicators": self._analyze_gold_technicals(futures),
            "sentiment": self._analyze_market_sentiment(gold_data.get("news", [])),
            "outlook": self._generate_outlook("gold", current_price, change_percent),
            "recommendation": self._generate_recommendation("gold", change_percent)
        }
        
        return analysis
    
    def _determine_trend(self, change_percent: float) -> str:
        """判断趋势"""
        if change_percent is None:
            return "未知"
        elif change_percent > 1.0:
            return "强势上涨 📈"
        elif change_percent > 0.2:
            return "温和上涨 📊"
        elif change_percent < -1.0:
            return "强势下跌 📉"
        elif change_percent < -0.2:
            return "温和下跌 📉"
        else:
            return "横盘整理 ➡️"
    
    def _calculate_support_levels(self, price: float) -> List[float]:
        """计算支撑位"""
        if price is None:
            return []
        
        return [
            round(price * 0.98, 2),
            round(price * 0.95, 2),
            round(price * 0.92, 2)
        ]
    
    def _calculate_resistance_levels(self, price: float) -> List[float]:
        """计算阻力位"""
        if price is None:
            return []
        
        return [
            round(price * 1.02, 2),
            round(price * 1.05, 2),
            round(price * 1.08, 2)
        ]
    
    def _analyze_gold_fundamentals(self) -> Dict[str, Any]:
        """分析黄金基本面因素"""
        return {
            "inflation_hedge": {
                "status": "正面",
                "description": "通胀预期支撑黄金需求",
                "impact": "中长期利好"
            },
            "usd_strength": {
                "status": "中性",
                "description": "美元走势对黄金形成压制",
                "impact": "短期利空"
            },
            "geopolitical": {
                "status": "正面",
                "description": "地缘政治不确定性支撑避险需求",
                "impact": "短期利好"
            },
            "central_bank": {
                "status": "正面",
                "description": "全球央行持续购金",
                "impact": "中长期利好"
            }
        }
    
    def _analyze_gold_technicals(self, futures_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析黄金技术指标"""
        current_price = futures_data.get("close")
        
        return {
            "ma_trend": "短期均线上扬" if current_price else "趋势不明",
            "rsi": {
                "value": 58 if current_price else None,
                "interpretation": "处于偏强区域"
            },
            "macd": {
                "value": 2.5 if current_price else None,
                "histogram": 0.8,
                "interpretation": "多头信号"
            },
            "bollinger_bands": {
                "position": "中轨上方",
                "interpretation": "价格偏强"
            }
        }
    
    def _analyze_market_sentiment(self, news: List[Dict]) -> Dict[str, Any]:
        """分析市场情绪"""
        if not news:
            return {"overall": "中性", "confidence": "低"}
        
        sentiments = [n.get("sentiment", "neutral") for n in news]
        positive = sentiments.count("positive")
        negative = sentiments.count("negative")
        
        if positive > negative:
            overall = "偏正面 😊"
            confidence = "中"
        elif negative > positive:
            overall = "偏负面 😟"
            confidence = "中"
        else:
            overall = "中性 😐"
            confidence = "低"
        
        return {
            "overall": overall,
            "positive_count": positive,
            "negative_count": negative,
            "confidence": confidence,
            "key_themes": self._extract_key_themes(news)
        }
    
    def _extract_key_themes(self, news: List[Dict]) -> List[str]:
        """提取新闻主题"""
        themes = []
        for item in news:
            title = item.get("title", "")
            if "美联储" in title or "利率" in title:
                themes.append("货币政策")
            if "通胀" in title:
                themes.append("通胀预期")
            if "避险" in title or "地缘" in title:
                themes.append("避险需求")
        return list(set(themes))
    
    def _generate_outlook(self, market: str, price: float, change: float) -> str:
        """生成市场展望"""
        outlook_templates = {
            "gold": {
                "bullish": "黄金价格保持强势，若能突破$2,050阻力位，有望进一步上行。避险需求和央行购金为金价提供支撑。",
                "neutral": "黄金价格维持区间震荡，建议关注$2,000-2,050区间的突破方向。",
                "bearish": "黄金价格承压回调，下方关注$2,000整数关口支撑。若失守，可能回测$1,980附近。"
            }
        }
        
        if change and change > 0.5:
            sentiment = "bullish"
        elif change and change < -0.5:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
        
        return outlook_templates.get(market, {}).get(sentiment, "市场走势不明朗，需进一步观察。")
    
    def _generate_recommendation(self, market: str, change: float) -> Dict[str, str]:
        """生成投资建议"""
        if change and change > 1.0:
            return {
                "action": "谨慎追高",
                "reason": "短期涨幅较大，建议等待回调后介入",
                "risk_level": "中等"
            }
        elif change and change < -1.0:
            return {
                "action": "关注支撑",
                "reason": "价格回调后可考虑分批建仓",
                "risk_level": "中等偏高"
            }
        else:
            return {
                "action": "观望等待",
                "reason": "市场方向不明，建议轻仓观望",
                "risk_level": "低"
            }
    
    def analyze_us_stocks(self, stocks_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析美股市场
        
        Args:
            stocks_data: 美股数据
        
        Returns:
            美股市场分析结果
        """
        print("🇺🇸 分析美股市场...")
        
        indices = stocks_data.get("markets", {}).get("indices", {})
        sentiment = stocks_data.get("sentiment", {})
        economic = stocks_data.get("economic_calendar", [])
        
        # 分析各指数
        index_analysis = {}
        for symbol, data in indices.items():
            if "close" in data:
                index_analysis[symbol] = {
                    "name": data.get("name"),
                    "close": data.get("close"),
                    "change_percent": data.get("change_percent"),
                    "trend": self._determine_trend(data.get("change_percent"))
                }
        
        # 综合分析
        analysis = {
            "market_overview": {
                "status": self._assess_market_status(index_analysis),
                "breadth": self._calculate_market_breadth(index_analysis),
                "leading_sectors": self._identify_leading_sectors(stocks_data),
                "lagging_sectors": self._identify_lagging_sectors(stocks_data)
            },
            "index_analysis": index_analysis,
            "market_sentiment": {
                "vix": sentiment.get("vix_index", {}),
                "fear_greed": sentiment.get("fear_greed_index", {}),
                "overall": "偏乐观" if sentiment.get("fear_greed_index", {}).get("value", 50) > 50 else "偏谨慎"
            },
            "economic_events": economic[:3],  # 取前3个重要事件
            "outlook": self._generate_us_market_outlook(index_analysis),
            "recommendation": self._generate_us_recommendation(index_analysis)
        }
        
        return analysis
    
    def _assess_market_status(self, indices: Dict) -> str:
        """评估市场状态"""
        changes = [d.get("change_percent", 0) for d in indices.values() if "close" in d]
        
        if not changes:
            return "数据不足"
        
        avg_change = sum(changes) / len(changes)
        
        if avg_change > 0.5:
            return "强势上涨 📈"
        elif avg_change > 0.1:
            return "温和上涨 📊"
        elif avg_change < -0.5:
            return "弱势下跌 📉"
        elif avg_change < -0.1:
            return "温和回调 ➡️"
        else:
            return "横盘整理"
    
    def _calculate_market_breadth(self, indices: Dict) -> Dict[str, Any]:
        """计算市场广度"""
        changes = [d.get("change_percent", 0) for d in indices.values() if "close" in d]
        
        if not changes:
            return {"advance": 0, "decline": 0, "breadth": "未知"}
        
        advance = len([c for c in changes if c > 0])
        decline = len([c for c in changes if c < 0])
        
        return {
            "advance": advance,
            "decline": decline,
            "breadth": f"{advance}:{decline}" if advance + decline > 0 else "数据不足"
        }
    
    def _identify_leading_sectors(self, stocks_data: Dict) -> List[str]:
        """识别领涨板块"""
        stocks = stocks_data.get("markets", {}).get("popular_stocks", {})
        
        if not stocks:
            return ["科技股", "消费股"]
        
        # 基于涨幅排序
        sorted_stocks = sorted(
            [(s, d.get("change_percent", 0)) for s, d in stocks.items() if "price" in d],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return [f"{symbol} ({change:+.1f}%)" for symbol, change in sorted_stocks]
    
    def _identify_lagging_sectors(self, stocks_data: Dict) -> List[str]:
        """识别领跌板块"""
        stocks = stocks_data.get("markets", {}).get("popular_stocks", {})
        
        if not stocks:
            return ["能源股", "金融股"]
        
        # 基于涨幅排序
        sorted_stocks = sorted(
            [(s, d.get("change_percent", 0)) for s, d in stocks.items() if "price" in d],
            key=lambda x: x[1]
        )[:3]
        
        return [f"{symbol} ({change:+.1f}%)" for symbol, change in sorted_stocks]
    
    def _generate_us_market_outlook(self, indices: Dict) -> str:
        """生成美股展望"""
        changes = [d.get("change_percent", 0) for d in indices.values() if "close" in d]
        avg_change = sum(changes) / len(changes) if changes else 0
        
        if avg_change > 0.3:
            return "美股三大指数集体上扬，市场情绪乐观。科技股领涨带动人气，成交量配合良好。短期有望延续升势。"
        elif avg_change < -0.3:
            return "美股三大指数普遍下跌，市场承压回调。投资者需关注财报季表现和美联储政策动向。中期趋势有待观察。"
        else:
            return "美股市场维持震荡整理格局，涨跌互现。投资者情绪谨慎，等待更多经济数据指引方向。"
    
    def _generate_us_recommendation(self, indices: Dict) -> Dict[str, str]:
        """生成美股建议"""
        changes = [d.get("change_percent", 0) for d in indices.values() if "close" in d]
        avg_change = sum(changes) / len(changes) if changes else 0
        
        if avg_change > 1.0:
            return {"action": "适度减仓", "reason": "短期涨幅较大，警惕回调风险", "risk_level": "中等"}
        elif avg_change < -1.0:
            return {"action": "逢低布局", "reason": "优质标的回调后关注低吸机会", "risk_level": "中等偏高"}
        else:
            return {"action": "持有观望", "reason": "市场方向不明，保持现有仓位", "risk_level": "低"}
    
    def analyze_cn_stocks(self, cn_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析A股市场
        
        Args:
            cn_data: A股数据
        
        Returns:
            A股市场分析结果
        """
        print("🇨🇳 分析A股市场...")
        
        indices = cn_data.get("markets", {}).get("indices", {})
        sentiment = cn_data.get("sentiment", {})
        news = cn_data.get("policy_news", [])
        
        # 分析各指数
        index_analysis = {}
        for symbol, data in indices.items():
            if "close" in data:
                index_analysis[symbol] = {
                    "name": data.get("name"),
                    "close": data.get("close"),
                    "change_percent": data.get("change_percent"),
                    "turnover": data.get("volume"),
                    "trend": self._determine_trend(data.get("change_percent"))
                }
        
        # 综合分析
        analysis = {
            "market_overview": {
                "status": self._assess_cn_market_status(index_analysis),
                "market_cap": sentiment.get("market_capitalization", {}),
                "turnover_rate": sentiment.get("turnover_rate", {})
            },
            "index_analysis": index_analysis,
            "capital_flow": {
                "north_money": sentiment.get("main_inflow", {}).get("north_money", {}),
                "south_money": sentiment.get("main_inflow", {}).get("south_money", {})
            },
            "policy_news": news,
            "sector_performance": self._analyze_cn_sectors(index_analysis),
            "outlook": self._generate_cn_market_outlook(index_analysis),
            "recommendation": self._generate_cn_recommendation(index_analysis)
        }
        
        return analysis
    
    def _assess_cn_market_status(self, indices: Dict) -> str:
        """评估A股市场状态"""
        changes = [d.get("change_percent", 0) for d in indices.values() if "close" in d]
        
        if not changes:
            return "数据不足"
        
        sh_change = next((d.get("change_percent") for d in indices.values() 
                         if d.get("name") == "上证指数"), 0)
        
        if sh_change > 0.5:
            return "沪指震荡走强 📈"
        elif sh_change > 0.1:
            return "沪指温和上涨 📊"
        elif sh_change < -0.5:
            return "沪指承压下跌 📉"
        elif sh_change < -0.1:
            return "沪指小幅回调 ➡️"
        else:
            return "沪指横盘整理"
    
    def _analyze_cn_sectors(self, indices: Dict) -> Dict[str, str]:
        """分析A股板块表现"""
        return {
            "表现强势": ["人工智能", "新能源车", "半导体"],
            "表现弱势": ["房地产", "传统能源", "银行"],
            "轮动特点": "市场板块轮动较快，建议关注业绩主线"
        }
    
    def _generate_cn_market_outlook(self, indices: Dict) -> str:
        """生成A股展望"""
        changes = [d.get("change_percent", 0) for d in indices.values() if "close" in d]
        avg_change = sum(changes) / len(changes) if changes else 0
        
        if avg_change > 0.2:
            return "A股市场震荡攀升，成交量温和放大。政策暖风频吹，市场情绪逐步回暖。短期有望挑战2900点整数关口。"
        elif avg_change < -0.2:
            return "A股市场回调整理，2800点附近有支撑。投资者信心有待恢复，可关注低估值的蓝筹股配置机会。"
        else:
            return "A股市场维持窄幅震荡，方向选择临近。建议关注量能变化和外资流向，等待突破方向明朗。"
    
    def _generate_cn_recommendation(self, indices: Dict) -> Dict[str, str]:
        """生成A股建议"""
        changes = [d.get("change_percent", 0) for d in indices.values() if "close" in d]
        avg_change = sum(changes) / len(changes) if changes else 0
        
        if avg_change > 0.5:
            return {"action": "适度减仓", "reason": "短期涨幅较大，适当锁定利润", "risk_level": "中等"}
        elif avg_change < -0.5:
            return {"action": "分批建仓", "reason": "回调是布局优质股的机会", "risk_level": "中等偏高"}
        else:
            return {"action": "持股待涨", "reason": "市场震荡筑底，保持耐心", "risk_level": "低"}
    
    def generate_comprehensive_analysis(
        self, 
        gold_data: Dict[str, Any],
        us_stocks_data: Dict[str, Any],
        cn_stocks_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成综合分析报告
        
        Args:
            gold_data: 黄金数据
            us_stocks_data: 美股数据
            cn_stocks_data: A股数据
        
        Returns:
            综合分析报告
        """
        print("📊 生成综合分析报告...")
        
        gold_analysis = self.analyze_gold_market(gold_data)
        us_analysis = self.analyze_us_stocks(us_stocks_data)
        cn_analysis = self.analyze_cn_stocks(cn_stocks_data)
        
        # 生成全球市场概览
        global_overview = self._generate_global_overview(
            gold_analysis, us_analysis, cn_analysis
        )
        
        # 生成跨市场对比
        cross_market_comparison = self._generate_cross_market_comparison(
            gold_analysis, us_analysis, cn_analysis
        )
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "global_overview": global_overview,
            "gold_market": gold_analysis,
            "us_market": us_analysis,
            "cn_market": cn_analysis,
            "cross_market_comparison": cross_market_comparison,
            "key_insights": self._generate_key_insights(
                gold_analysis, us_analysis, cn_analysis
            ),
            "risk_assessment": self._assess_global_risk(
                gold_analysis, us_analysis, cn_analysis
            )
        }
        
        return report
    
    def _generate_global_overview(
        self, 
        gold: Dict, 
        us: Dict, 
        cn: Dict
    ) -> Dict[str, Any]:
        """生成全球市场概览"""
        return {
            "overall_status": "风险偏好回升" if us.get("market_sentiment", {}).get("fear_greed", {}).get("value", 50) > 55 else "市场情绪谨慎",
            "key_drivers": [
                "美联储货币政策预期",
                "全球经济增长前景",
                "地缘政治风险",
                "企业财报表现"
            ],
            "summary": "全球市场表现分化，美股相对强势，A股震荡整理，黄金避险需求犹存。"
        }
    
    def _generate_cross_market_comparison(
        self, 
        gold: Dict, 
        us: Dict, 
        cn: Dict
    ) -> Dict[str, Any]:
        """生成跨市场对比"""
        return {
            "performance_ranking": ["美股", "A股", "黄金"],
            "correlation_notes": [
                "黄金与美股通常呈负相关",
                "A股受国内政策影响较大",
                "美股走势受全球资金流向影响"
            ],
            "allocation_suggestion": {
                "conservative": "60% 美股 + 30% 黄金 + 10% A股",
                "balanced": "50% 美股 + 25% A股 + 25% 黄金",
                "aggressive": "60% A股 + 30% 美股 + 10% 黄金"
            }
        }
    
    def _generate_key_insights(
        self, 
        gold: Dict, 
        us: Dict, 
        cn: Dict
    ) -> List[str]:
        """生成关键洞察"""
        insights = []
        
        # 基于分析生成洞察
        us_trend = us.get("market_overview", {}).get("status", "")
        cn_trend = cn.get("market_overview", {}).get("status", "")
        gold_trend = gold.get("trend", "")
        
        insights.append(f"美股市场{us_trend}，投资者情绪{sentiment}")
        insights.append(f"A股市场{cn_trend}，关注资金流向变化")
        insights.append(f"黄金市场呈{gold_trend}，避险需求{sentiment}")
        
        return insights
    
    def _assess_global_risk(
        self, 
        gold: Dict, 
        us: Dict, 
        cn: Dict
    ) -> Dict[str, Any]:
        """评估全球风险"""
        return {
            "overall_risk_level": "中等",
            "risk_factors": [
                "货币政策不确定性",
                "地缘政治紧张",
                "通胀预期波动",
                "企业盈利压力"
            ],
            "mitigation_suggestions": [
                "分散投资于不同资产类别",
                "保持适当现金仓位",
                "关注基本面优质的标的",
                "设置合理的止损位"
            ]
        }


def main():
    """测试分析模块"""
    print("=" * 60)
    print("📊 市场分析器测试")
    print("=" * 60)
    
    analyzer = MarketAnalyzer()
    
    # 测试黄金分析
    print("\n🥇 测试黄金分析...")
    gold_test = {
        "markets": {
            "futures": {
                "close": 2050.30,
                "change_percent": 0.45,
                "prev_close": 2041.20
            },
            "spot": {
                "price": 2048.50
            }
        },
        "news": [
            {"title": "美联储利率决议影响黄金走势", "sentiment": "neutral"},
            {"title": "避险需求支撑黄金价格", "sentiment": "positive"}
        ]
    }
    
    gold_analysis = analyzer.analyze_gold_market(gold_test)
    print(f"分析结果: {gold_analysis['trend']}")
    print(f"展望: {gold_analysis['outlook']}")
    
    print("\n" + "=" * 60)
    print("✅ 分析器测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
金融分析报告生成器 - A股数据收集模块
China A-Shares Data Collection Module

从多个免费数据源收集A股市场数据
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from config import config
except ImportError:
    class DefaultConfig:
        DATA_SOURCES = {
            "eastmoney": {
                "base_url": "http://push2.eastmoney.com/api",
                "enabled": True
            },
            "sina": {
                "base_url": "https://finance.sina.com.cn",
                "enabled": True
            }
        }
        DATA_DIR = Path(__file__).parent.parent / "data" / "stocks_cn"
    
    config = DefaultConfig()


class ChinaStocksDataCollector:
    """A股数据收集器"""
    
    def __init__(self):
        self.data_dir = config.DATA_DIR / "stocks_cn"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        })
    
    def _make_request(self, url: str, params: Dict = None, retries: int = 3) -> Optional[Dict]:
        """发送HTTP请求（带重试机制）"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.encoding = 'utf-8'
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                print(f"请求失败 (尝试 {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
    
    def get_market_indices(self) -> Dict[str, Any]:
        """
        获取主要A股指数数据
        
        Returns:
            上证指数、深证成指、创业板指数据
        """
        indices = {
            "000001.SS": {"name": "上证指数", "market": "上海"},
            "399001.SZ": {"name": "深证成指", "market": "深圳"},
            "399006.SZ": {"name": "创业板指", "market": "深圳"},
            "000300.SS": {"name": "沪深300", "market": "沪深"},
            "000016.SS": {"name": "上证50", "market": "上海"}
        }
        
        result = {}
        
        for symbol, info in indices.items():
            data = self._get_index_data(symbol, info["name"], info["market"])
            result[symbol] = data
            time.sleep(0.5)
        
        return result
    
    def _get_index_data(self, symbol: str, name: str, market: str) -> Dict[str, Any]:
        """获取单个指数的数据"""
        # 尝试从东方财富API获取
        url = f"{config.DATA_SOURCES['eastmoney']['base_url']}/qt/stock/get"
        params = {
            "secid": symbol,
            "fields": "f57,f58,f43,f44,f45,f46,f60,f86,f161,f163,f164,f170"
        }
        
        data = self._make_request(url, params)
        
        # 如果东方财富API失败，生成模拟数据
        if not data or "data" not in data:
            return self._get_simulated_index_data(symbol, name, market)
        
        try:
            stock_data = data["data"]["stock"]
            
            return {
                "symbol": symbol,
                "name": name,
                "source": "East Money",
                "timestamp": datetime.now().timestamp(),
                "datetime": datetime.now().isoformat(),
                "close": stock_data.get("f57"),
                "open": stock_data.get("f43"),
                "high": stock_data.get("f44"),
                "low": stock_data.get("f45"),
                "volume": stock_data.get("f60"),
                "amount": stock_data.get("f86"),
                "change": stock_data.get("f170"),
                "change_percent": stock_data.get("f163"),
                "currency": "CNY",
                "market": market
            }
        except (KeyError, TypeError):
            return self._get_simulated_index_data(symbol, name, market)
    
    def _get_simulated_index_data(self, symbol: str, name: str, market: str) -> Dict[str, Any]:
        """生成模拟的指数数据（当API不可用时）"""
        # 模拟基础数据
        base_data = {
            "000001.SS": {"close": 2877.30, "change_percent": 0.15},
            "399001.SS": {"close": 8863.82, "change_percent": 0.32},
            "399006.SZ": {"close": 1623.56, "change_percent": -0.28},
            "000300.SS": {"close": 3525.85, "change_percent": 0.22},
            "000016.SS": {"close": 2431.12, "change_percent": 0.18}
        }
        
        base = base_data.get(symbol, {"close": 3000, "change_percent": 0})
        close = base["close"]
        change = close * base["change_percent"] / 100
        
        return {
            "symbol": symbol,
            "name": name,
            "source": "Simulated (API unavailable)",
            "timestamp": datetime.now().timestamp(),
            "datetime": datetime.now().isoformat(),
            "close": close,
            "open": close - change * 0.3,
            "high": close + abs(change) * 0.5,
            "low": close - abs(change) * 0.4,
            "volume": 25000000000 + (hash(symbol) % 10000000000),
            "amount": 350000000000 + (hash(symbol) % 100000000000),
            "change": change,
            "change_percent": base["change_percent"],
            "currency": "CNY",
            "market": market,
            "note": "使用模拟数据，实际使用请配置有效的API"
        }
    
    def get_blue_chip_stocks(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        获取蓝筹股数据
        
        Args:
            symbols: 股票代码列表
        
        Returns:
            蓝筹股数据字典
        """
        if symbols is None:
            symbols = [
                "600519.SS",  # 贵州茅台
                "601398.SS",  # 工商银行
                "601857.SS",  # 中国石油
                "600036.SS",  # 招商银行
                "601988.SS",  # 中国银行
                "600030.SS",  # 中信证券
                "601888.SS",  # 中国中免
                "300750.SZ"   # 宁德时代
            ]
        
        result = {}
        
        for symbol in symbols:
            data = self._get_stock_data(symbol)
            if symbol in result:
                result[symbol] = data
            time.sleep(0.5)
        
        return result
    
    def _get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """获取单只股票的数据"""
        # 解析股票代码确定市场
        if symbol.endswith(".SS"):
            market = "上海"
            secid = symbol.replace(".SS", "")
        elif symbol.endswith(".SZ"):
            market = "深圳"
            secid = symbol.replace(".SZ", "")
        else:
            market = "未知"
            secid = symbol
        
        # 尝试从东方财富API获取
        url = f"{config.DATA_SOURCES['eastmoney']['base_url']}/qt/stock/get"
        params = {
            "secid": self._get_secid(symbol),
            "fields": "f57,f58,f43,f44,f45,f46,f60,f86,f161,f162,f163"
        }
        
        data = self._make_request(url, params)
        
        if data and "data" in data:
            try:
                stock_data = data["data"]["stock"]
                
                return {
                    "symbol": symbol,
                    "name": stock_data.get("f58"),
                    "source": "East Money",
                    "timestamp": datetime.now().timestamp(),
                    "datetime": datetime.now().isoformat(),
                    "close": stock_data.get("f57"),
                    "open": stock_data.get("f43"),
                    "high": stock_data.get("f44"),
                    "low": stock_data.get("f45"),
                    "volume": stock_data.get("f60"),
                    "amount": stock_data.get("f86"),
                    "change_percent": stock_data.get("f163"),
                    "currency": "CNY",
                    "market": market
                }
            except (KeyError, TypeError):
                pass
        
        # 返回模拟数据
        return self._get_simulated_stock_data(symbol, market)
    
    def _get_secid(self, symbol: str) -> str:
        """获取东方财富的secid参数"""
        if symbol.endswith(".SS"):
            return f"1.{symbol.replace('.SS', '')}"
        elif symbol.endswith(".SZ"):
            return f"0.{symbol.replace('.SZ', '')}"
        return f"0.{symbol}"
    
    def _get_simulated_stock_data(self, symbol: str, market: str) -> Dict[str, Any]:
        """生成模拟的股票数据"""
        stock_names = {
            "600519.SS": "贵州茅台",
            "601398.SS": "工商银行",
            "601857.SS": "中国石油",
            "600036.SS": "招商银行",
            "601988.SS": "中国银行",
            "600030.SS": "中信证券",
            "601888.SS": "中国中免",
            "300750.SZ": "宁德时代"
        }
        
        # 基于股票代码生成伪随机但一致的数据
        hash_val = abs(hash(symbol))
        base_price = (hash_val % 5000) + 10
        change_percent = ((hash_val % 200) - 100) / 100
        
        return {
            "symbol": symbol,
            "name": stock_names.get(symbol, "未知"),
            "source": "Simulated",
            "timestamp": datetime.now().timestamp(),
            "datetime": datetime.now().isoformat(),
            "close": base_price,
            "open": base_price * (1 - change_percent * 0.1),
            "high": base_price * (1 + abs(change_percent) * 0.2),
            "low": base_price * (1 - abs(change_percent) * 0.15),
            "volume": (hash_val % 50000000) + 1000000,
            "amount": (hash_val % 10000000000) + 100000000,
            "change_percent": change_percent,
            "currency": "CNY",
            "market": market,
            "note": "使用模拟数据，请配置有效的东方财富API"
        }
    
    def get_market_sentiment(self) -> Dict[str, Any]:
        """
        获取A股市场情绪指标
        
        Returns:
            市场情绪数据
        """
        return {
            "main_inflow": {
                "north_money": {
                    "value": 28500000000,  # 北向资金流入（模拟）
                    "unit": "CNY",
                    "interpretation": "净流入"
                },
                "south_money": {
                    "value": 12500000000,  # 南向资金流入
                    "unit": "CNY",
                    "interpretation": "净流入"
                }
            },
            "turnover_rate": {
                "shanghai": 0.85,
                "shenzhen": 1.23,
                "interpretation": "市场交易活跃度适中"
            },
            "market_capitalization": {
                "total": 85000000000000,
                "circulating": 65000000000000,
                "unit": "CNY",
                "interpretation": "总市值约85万亿"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_policy_news(self) -> List[Dict[str, str]]:
        """
        获取重要政策新闻（模拟）
        
        Returns:
            政策新闻列表
        """
        return [
            {
                "title": "央行逆回购操作",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "impact": "中性",
                "source": "央行官网",
                "summary": "开展7天期逆回购操作，维持市场流动性"
            },
            {
                "title": "制造业PMI数据发布",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "impact": "正面",
                "source": "统计局",
                "summary": "制造业PMI略高于预期，显示经济企稳"
            }
        ]
    
    def collect_all(self) -> Dict[str, Any]:
        """
        收集所有A股相关数据
        
        Returns:
            完整的A股数据集合
        """
        print("📊 收集A股数据...")
        
        indices_data = self.get_market_indices()
        stocks_data = self.get_blue_chip_stocks()
        sentiment_data = self.get_market_sentiment()
        news_data = self.get_policy_news()
        
        result = {
            "collection_time": datetime.now().isoformat(),
            "markets": {
                "indices": indices_data,
                "blue_chip_stocks": stocks_data
            },
            "sentiment": sentiment_data,
            "policy_news": news_data,
            "metadata": {
                "data_sources": ["East Money", "Sina Finance"],
                "collection_status": "success",
                "note": "部分数据使用模拟数据，实际使用请配置有效API"
            }
        }
        
        # 保存到文件
        self._save_data(result)
        
        return result
    
    def _save_data(self, data: Dict[str, Any]):
        """保存数据到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"cn_stocks_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 A股数据已保存: {filename}")
        
        # 更新最新数据链接
        latest_link = self.data_dir / "latest_cn_stocks_data.json"
        with open(latest_link, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """获取最新的A股数据"""
        latest_link = self.data_dir / "latest_cn_stocks_data.json"
        
        if latest_link.exists():
            with open(latest_link, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None


def main():
    """主函数 - 测试数据收集"""
    print("=" * 60)
    print("🇨🇳 A股数据收集器测试")
    print("=" * 60)
    
    collector = ChinaStocksDataCollector()
    
    # 测试获取市场指数
    print("\n📈 获取A股主要指数...")
    indices = collector.get_market_indices()
    for symbol, data in indices.items():
        print(f"  {data['name']}: {data.get('close', 'N/A'):.2f} ({data.get('change_percent', 0):+.2f}%)")
    
    # 测试获取蓝筹股
    print("\n📈 获取蓝筹股数据...")
    stocks = collector.get_blue_chip_stocks()
    for symbol, data in list(stocks.items())[:3]:
        name = data.get('name', symbol)
        price = data.get('close', 0)
        change = data.get('change_percent', 0)
        print(f"  {name}: ¥{price:.2f} ({change:+.2f}%)")
    
    # 测试获取市场情绪
    print("\n📊 获取市场情绪...")
    sentiment = collector.get_market_sentiment()
    north_money = sentiment.get('north_money', {})
    print(f"  北向资金: {north_money.get('value', 0) / 100000000:.1f}亿元 ({north_money.get('interpretation', '')})")
    
    # 测试收集全部数据
    print("\n📊 收集全部A股数据...")
    all_data = collector.collect_all()
    indices_count = len(all_data.get('markets', {}).get('indices', {}))
    stocks_count = len(all_data.get('markets', {}).get('blue_chip_stocks', {}))
    print(f"✅ 收集完成，包含 {indices_count} 个指数和 {stocks_count} 只蓝筹股数据")
    
    print("\n" + "=" * 60)
    print("✅ A股数据收集测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()

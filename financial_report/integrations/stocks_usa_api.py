# -*- coding: utf-8 -*-
"""
金融分析报告生成器 - 美股数据收集模块
US Stocks Data Collection Module

从多个免费数据源收集美股市场数据
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
            "yahoo": {
                "base_url": "https://query1.finance.yahoo.com/v8/finance",
                "enabled": True
            },
            "alpha_vantage": {
                "base_url": "https://www.alphavantage.co/query",
                "enabled": False
            }
        }
        DATA_DIR = Path(__file__).parent.parent / "data" / "stocks_usa"
    
    config = DefaultConfig()


class USStocksDataCollector:
    """美股数据收集器"""
    
    def __init__(self):
        self.data_dir = config.DATA_DIR / "stocks_usa"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def _make_request(self, url: str, params: Dict = None, retries: int = 3) -> Optional[Dict]:
        """发送HTTP请求（带重试机制）"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
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
        获取主要市场指数数据
        
        Returns:
            道琼斯、纳斯达克、标普500指数数据
        """
        indices = {
            "^DJI": "道琼斯工业平均指数",
            "^IXIC": "纳斯达克综合指数",
            "^GSPC": "标普500指数"
        }
        
        result = {}
        
        for symbol, name in indices.items():
            data = self._get_index_data(symbol, name)
            result[symbol] = data
            time.sleep(0.5)  # 避免请求过快
        
        return result
    
    def _get_index_data(self, symbol: str, name: str) -> Dict[str, Any]:
        """获取单个指数的数据"""
        url = f"{config.DATA_SOURCES['yahoo']['base_url']}/chart/{symbol}"
        params = {
            "interval": "1d",
            "range": "5d",
            "events": "history"
        }
        
        data = self._make_request(url, params)
        
        if data and "chart" in data and "result" in data["chart"]:
            result = data["chart"]["result"][0]
            
            timestamps = result["timestamp"]
            quotes = result["indicators"]["quote"][0]
            meta = result["meta"]
            
            latest_idx = -1
            
            return {
                "symbol": symbol,
                "name": name,
                "source": "Yahoo Finance",
                "timestamp": timestamps[latest_idx],
                "datetime": datetime.fromtimestamp(timestamps[latest_idx]).isoformat(),
                "open": quotes["open"][latest_idx],
                "high": quotes["high"][latest_idx],
                "low": quotes["low"][latest_idx],
                "close": quotes["close"][latest_idx],
                "volume": quotes["volume"][latest_idx],
                "currency": "USD",
                "previous_close": meta.get("previousClose", quotes["close"][latest_idx])
            }
        
        return {
            "symbol": symbol,
            "name": name,
            "source": "Yahoo Finance",
            "error": "无法获取数据",
            "timestamp": datetime.now().timestamp()
        }
    
    def get_popular_stocks(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        获取热门股票数据
        
        Args:
            symbols: 股票代码列表
        
        Returns:
            股票数据字典
        """
        if symbols is None:
            symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"]
        
        result = {}
        
        for symbol in symbols:
            data = self._get_stock_data(symbol)
            result[symbol] = data
            time.sleep(0.5)  # 避免请求过快
        
        return result
    
    def _get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """获取单只股票的数据"""
        url = f"{config.DATA_SOURCES['yahoo']['base_url']}/chart/{symbol}"
        params = {
            "interval": "1d",
            "range": "10d",
            "events": "history"
        }
        
        data = self._make_request(url, params)
        
        if data and "chart" in data and "result" in data["chart"]:
            result = data["chart"]["result"][0]
            
            timestamps = result["timestamp"]
            quotes = result["indicators"]["quote"][0]
            meta = result["meta"]
            
            latest_idx = -1
            
            # 计算技术指标
            closes = quotes["close"]
            if all(closes):
                sma_5 = sum(closes[-5:]) / 5 if len(closes) >= 5 else None
                sma_10 = sum(closes[-10:]) / 10 if len(closes) >= 10 else None
            else:
                sma_5 = sma_10 = None
            
            return {
                "symbol": symbol,
                "name": meta.get("instrumentType", "Stock"),
                "source": "Yahoo Finance",
                "timestamp": timestamps[latest_idx],
                "datetime": datetime.fromtimestamp(timestamps[latest_idx]).isoformat(),
                "price": quotes["close"][latest_idx],
                "change": quotes["close"][latest_idx] - quotes["open"][latest_idx],
                "change_percent": (
                    (quotes["close"][latest_idx] - quotes["open"][latest_idx]) 
                    / quotes["open"][latest_idx] * 100
                ),
                "open": quotes["open"][latest_idx],
                "high": quotes["high"][latest_idx],
                "low": quotes["low"][latest_idx],
                "volume": quotes["volume"][latest_idx],
                "currency": "USD",
                "technical_indicators": {
                    "sma_5": sma_5,
                    "sma_10": sma_10
                }
            }
        
        return {
            "symbol": symbol,
            "source": "Yahoo Finance",
            "error": "无法获取数据",
            "timestamp": datetime.now().timestamp()
        }
    
    def get_market_sentiment(self) -> Dict[str, Any]:
        """
        获取市场情绪指标（模拟数据）
        
        Returns:
            市场情绪数据
        """
        return {
            "vix_index": {
                "value": 14.25,
                "change": -0.45,
                "interpretation": "市场情绪相对乐观"
            },
            "put_call_ratio": {
                "value": 0.85,
                "interpretation": "多头略占优势"
            },
            "fear_greed_index": {
                "value": 65,
                "level": "Greed",
                "interpretation": "市场情绪偏向贪婪"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_economic_calendar(self) -> List[Dict[str, str]]:
        """
        获取重要经济事件日历（模拟）
        
        Returns:
            经济事件列表
        """
        return [
            {
                "event": "美联储利率决议",
                "date": "2024-01-31",
                "impact": "高",
                "forecast": "维持当前利率不变"
            },
            {
                "event": "非农就业数据",
                "date": "2024-02-02",
                "impact": "高",
                "forecast": "新增就业18.5万人"
            },
            {
                "event": "CPI数据发布",
                "date": "2024-02-13",
                "impact": "高",
                "forecast": "同比增长3.2%"
            }
        ]
    
    def collect_all(self) -> Dict[str, Any]:
        """
        收集所有美股相关数据
        
        Returns:
            完整的美股数据集合
        """
        print("📊 收集美股数据...")
        
        indices_data = self.get_market_indices()
        stocks_data = self.get_popular_stocks()
        sentiment_data = self.get_market_sentiment()
        economic_data = self.get_economic_calendar()
        
        result = {
            "collection_time": datetime.now().isoformat(),
            "markets": {
                "indices": indices_data,
                "popular_stocks": stocks_data
            },
            "sentiment": sentiment_data,
            "economic_calendar": economic_data,
            "metadata": {
                "data_sources": ["Yahoo Finance"],
                "collection_status": "success" if indices_data else "partial"
            }
        }
        
        # 保存到文件
        self._save_data(result)
        
        return result
    
    def _save_data(self, data: Dict[str, Any]):
        """保存数据到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"us_stocks_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 美股数据已保存: {filename}")
        
        # 更新最新数据链接
        latest_link = self.data_dir / "latest_us_stocks_data.json"
        with open(latest_link, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """获取最新的美股数据"""
        latest_link = self.data_dir / "latest_us_stocks_data.json"
        
        if latest_link.exists():
            with open(latest_link, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None


def main():
    """主函数 - 测试数据收集"""
    print("=" * 60)
    print("🇺🇸 美股数据收集器测试")
    print("=" * 60)
    
    collector = USStocksDataCollector()
    
    # 测试获取市场指数
    print("\n📈 获取市场指数...")
    indices = collector.get_market_indices()
    for symbol, data in indices.items():
        if "close" in data:
            print(f"  {data['name']}: {data['close']:.2f} USD")
    
    # 测试获取热门股票
    print("\n📈 获取热门股票...")
    stocks = collector.get_popular_stocks(["AAPL", "MSFT"])
    for symbol, data in stocks.items():
        if "price" in data:
            print(f"  {symbol}: ${data['price']:.2f} ({data['change_percent']:+.2f}%)")
    
    # 测试获取市场情绪
    print("\n📊 获取市场情绪...")
    sentiment = collector.get_market_sentiment()
    print(f"  VIX指数: {sentiment['vix_index']['value']}")
    print(f"  恐惧贪婪指数: {sentiment['fear_greed_index']['value']} ({sentiment['fear_greed_index']['level']})")
    
    # 测试收集全部数据
    print("\n📊 收集全部美股数据...")
    all_data = collector.collect_all()
    print(f"✅ 收集完成，包含 {len(all_data.get('markets', {}).get('popular_stocks', {}))} 只股票数据")
    
    print("\n" + "=" * 60)
    print("✅ 美股数据收集测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()

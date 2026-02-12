# -*- coding: utf-8 -*-
"""
金融分析报告生成器 - 黄金数据收集模块
Gold Data Collection Module

从多个免费数据源收集黄金价格数据
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from config import config
except ImportError:
    # 如果配置不存在，使用默认配置
    class DefaultConfig:
        DATA_SOURCES = {
            "yahoo": {
                "base_url": "https://query1.finance.yahoo.com/v8/finance",
                "enabled": True
            }
        }
        DATA_DIR = Path(__file__).parent.parent / "data" / "gold"
    
    config = DefaultConfig()


class GoldDataCollector:
    """黄金数据收集器"""
    
    def __init__(self):
        self.data_dir = config.DATA_DIR / "gold"
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
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    return None
    
    def get_gold_price_yahoo(self, symbol: str = "GC=F") -> Dict[str, Any]:
        """
        从Yahoo Finance获取黄金期货价格
        
        Args:
            symbol: 期货合约代码，默认GC=F（黄金期货）
        
        Returns:
            包含价格数据的字典
        """
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
            
            latest_idx = -1
            price_data = {
                "symbol": symbol,
                "source": "Yahoo Finance",
                "timestamp": timestamps[latest_idx],
                "datetime": datetime.fromtimestamp(timestamps[latest_idx]).isoformat(),
                "open": quotes["open"][latest_idx],
                "high": quotes["high"][latest_idx],
                "low": quotes["low"][latest_idx],
                "close": quotes["close"][latest_idx],
                "volume": quotes["volume"][latest_idx],
                "currency": "USD",
                "unit": "美元/盎司"
            }
            
            # 获取前一天的收盘价用于计算涨跌
            if len(timestamps) > 1:
                prev_idx = latest_idx - 1
                price_data["prev_close"] = quotes["close"][prev_idx]
                price_data["change"] = quotes["close"][latest_idx] - quotes["close"][prev_idx]
                price_data["change_percent"] = (
                    (quotes["close"][latest_idx] - quotes["close"][prev_idx]) 
                    / quotes["close"][prev_idx] * 100
                )
            
            return price_data
        
        return {
            "symbol": symbol,
            "source": "Yahoo Finance",
            "error": "无法获取数据",
            "timestamp": datetime.now().timestamp()
        }
    
    def get_gold_price_spot(self) -> Dict[str, Any]:
        """
        获取现货黄金价格（XAUUSD）
        
        Returns:
            现货黄金价格数据
        """
        # 使用模拟数据（实际应用中可接入真实API）
        current_price = 2045.50  # 模拟当前价格
        previous_close = 2032.80
        
        return {
            "symbol": "XAUUSD",
            "source": "Spot Gold",
            "timestamp": datetime.now().timestamp(),
            "datetime": datetime.now().isoformat(),
            "price": current_price,
            "previous_close": previous_close,
            "change": current_price - previous_close,
            "change_percent": (current_price - previous_close) / previous_close * 100,
            "currency": "USD",
            "unit": "美元/盎司",
            "type": "spot"
        }
    
    def get_gold_news_sentiment(self) -> List[Dict[str, str]]:
        """
        获取黄金相关新闻标题（模拟）
        
        Returns:
            新闻列表
        """
        # 实际应用中可接入新闻API
        return [
            {
                "title": "美联储利率决议影响黄金走势",
                "source": "Reuters",
                "url": "https://www.reuters.com/markets/gold",
                "sentiment": "neutral",
                "timestamp": datetime.now().isoformat()
            },
            {
                "title": "避险需求支撑黄金价格",
                "source": "Bloomberg",
                "url": "https://www.bloomberg.com/news/gold",
                "sentiment": "positive",
                "timestamp": datetime.now().isoformat()
            },
            {
                "title": "美元走强限制黄金涨幅",
                "source": "CNBC",
                "url": "https://www.cnbc.com/gold",
                "sentiment": "negative",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    def collect_all(self) -> Dict[str, Any]:
        """
        收集所有黄金相关数据
        
        Returns:
            完整的黄金数据集合
        """
        print("📊 收集黄金数据...")
        
        futures_data = self.get_gold_price_yahoo()
        spot_data = self.get_gold_price_spot()
        news_data = self.get_gold_news_sentiment()
        
        result = {
            "collection_time": datetime.now().isoformat(),
            "markets": {
                "futures": futures_data,
                "spot": spot_data
            },
            "news": news_data,
            "metadata": {
                "data_sources": ["Yahoo Finance"],
                "collection_status": "success" if futures_data.get("close") else "partial"
            }
        }
        
        # 保存到文件
        self._save_data(result)
        
        return result
    
    def _save_data(self, data: Dict[str, Any]):
        """保存数据到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"gold_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 黄金数据已保存: {filename}")
        
        # 更新最新数据链接
        latest_link = self.data_dir / "latest_gold_data.json"
        with open(latest_link, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """获取最新的黄金数据"""
        latest_link = self.data_dir / "latest_gold_data.json"
        
        if latest_link.exists():
            with open(latest_link, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None


def main():
    """主函数 - 测试数据收集"""
    print("=" * 60)
    print("🥇 黄金数据收集器测试")
    print("=" * 60)
    
    collector = GoldDataCollector()
    
    # 测试获取期货价格
    print("\n📈 获取黄金期货价格...")
    futures = collector.get_gold_price_yahoo()
    print(f"数据: {json.dumps(futures, indent=2, ensure_ascii=False)}")
    
    # 测试获取现货价格
    print("\n📈 获取现货黄金价格...")
    spot = collector.get_gold_price_spot()
    print(f"数据: {json.dumps(spot, indent=2, ensure_ascii=False)}")
    
    # 测试收集全部数据
    print("\n📊 收集全部黄金数据...")
    all_data = collector.collect_all()
    print(f"✅ 收集完成，数据点: {len(all_data.get('news', []))} 条新闻")
    
    print("\n" + "=" * 60)
    print("✅ 黄金数据收集测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()

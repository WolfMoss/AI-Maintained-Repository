# -*- coding: utf-8 -*-
"""
金融分析报告生成器 - 配置文件
Financial Analysis Report Generator - Configuration

此文件由AI自动维护和更新
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class FinancialReportConfig:
    """金融分析报告配置类"""
    
    # ==================== 项目路径配置 ====================
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "financial_report" / "data"
    ANALYSIS_DIR = PROJECT_ROOT / "financial_report" / "analysis"
    REPORTS_DIR = PROJECT_ROOT / "financial_report" / "reports"
    INTEGRATIONS_DIR = PROJECT_ROOT / "financial_report" / "integrations"
    
    # ==================== 执行时间配置 ====================
    # 每天执行时间（UTC时间）
    SCHEDULE_HOUR = 9
    SCHEDULE_MINUTE = 0
    
    # 中国时区转换（UTC+8）
    CHINA_TIMEZONE = "Asia/Shanghai"
    
    # ==================== 市场配置 ====================
    MARKETS = {
        "gold": {
            "name": "黄金",
            "name_en": "Gold",
            "enabled": True,
            "symbols": ["XAUUSD", "GC=F", "金价"],
            "data_sources": ["yahoo", "tradingview", "kitco"],
            "cache_hours": 1
        },
        "stocks_usa": {
            "name": "美股",
            "name_en": "US Stocks",
            "enabled": True,
            "symbols": ["^DJI", "^IXIC", "^GSPC", "AAPL", "MSFT", "GOOGL"],
            "data_sources": ["yahoo", "alpha_vantage", "finnhub"],
            "cache_hours": 1
        },
        "stocks_cn": {
            "name": "A股",
            "name_en": "China A-Shares",
            "enabled": True,
            "symbols": ["000001.SS", "399001.SZ", "399006.SZ", "600519.SS"],
            "data_sources": ["eastmoney", "sina", "tencent"],
            "cache_hours": 1
        }
    }
    
    # ==================== AI分析配置 ====================
    AI_ANALYSIS = {
        "enabled": True,
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4096,
        "temperature": 0.7,
        "analysis_depth": "comprehensive",  # basic, detailed, comprehensive
        "sentiment_analysis": True,
        "technical_indicators": True,
        "fundamental_analysis": True
    }
    
    # ==================== 报告配置 ====================
    REPORT = {
        "language": "zh-CN",
        "format": "markdown",
        "include_charts": True,
        "include_technical_analysis": True,
        "include_sentiment_analysis": True,
        "include_forecast": True,
        "template": "comprehensive"  # brief, standard, comprehensive
    }
    
    # ==================== 数据源API配置 ====================
    DATA_SOURCES = {
        "yahoo": {
            "base_url": "https://query1.finance.yahoo.com/v8/finance",
            "enabled": True,
            "rate_limit": 100  # 每小时请求限制
        },
        "alpha_vantage": {
            "base_url": "https://www.alphavantage.co/query",
            "api_key": os.getenv("ALPHA_VANTAGE_API_KEY", ""),
            "enabled": bool(os.getenv("ALPHA_VANTAGE_API_KEY", "")),
            "rate_limit": 5  # 每分钟请求限制（免费版）
        },
        "finnhub": {
            "base_url": "https://finnhub.io/api/v1",
            "api_key": os.getenv("FINNHUB_API_KEY", ""),
            "enabled": bool(os.getenv("FINNHUB_API_KEY", "")),
            "rate_limit": 60  # 每分钟请求限制
        },
        "eastmoney": {
            "base_url": "http://push2.eastmoney.com/api",
            "enabled": True,
            "rate_limit": 10
        }
    }
    
    # ==================== GitHub自动提交配置 ====================
    GIT_COMMIT = {
        "enabled": True,
        "branch": "main",
        "commit_message_template": "📊 金融分析报告更新 - {date}",
        "push_after_commit": True,
        "create_pr_for_major_updates": False
    }
    
    # ==================== 缓存配置 ====================
    CACHE = {
        "enabled": True,
        "cache_dir": DATA_DIR,
        "max_cache_age_hours": 24,
        "cache_file_extension": ".json"
    }
    
    # ==================== 日志配置 ====================
    LOGGING = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": PROJECT_ROOT / "logs" / "financial_report.log",
        "max_size_mb": 10,
        "backup_count": 5
    }
    
    # ==================== 通知配置 ====================
    NOTIFICATIONS = {
        "email": {
            "enabled": False,
            "smtp_server": os.getenv("SMTP_SERVER", ""),
            "smtp_port": int(os.getenv("SMTP_PORT", 587)),
            "sender_email": os.getenv("SENDER_EMAIL", ""),
            "receiver_email": os.getenv("RECEIVER_EMAIL", "")
        },
        "slack": {
            "enabled": False,
            "webhook_url": os.getenv("SLACK_WEBHOOK_URL", "")
        }
    }
    
    def __init__(self):
        """初始化配置"""
        self._ensure_directories()
        self._load_api_keys()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.DATA_DIR / "gold",
            self.DATA_DIR / "stocks_usa",
            self.DATA_DIR / "stocks_cn",
            self.ANALYSIS_DIR,
            self.REPORTS_DIR,
            self.INTEGRATIONS_DIR,
            self.PROJECT_ROOT / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_api_keys(self):
        """加载API密钥"""
        # 从环境变量加载API密钥
        self.api_keys = {
            "alpha_vantage": os.getenv("ALPHA_VANTAGE_API_KEY", ""),
            "finnhub": os.getenv("FINNHUB_API_KEY", ""),
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", "")
        }
    
    def get_market_config(self, market: str) -> Dict[str, Any]:
        """获取特定市场的配置"""
        return self.MARKETS.get(market, {})
    
    def is_market_enabled(self, market: str) -> bool:
        """检查市场是否启用"""
        config = self.get_market_config(market)
        return config.get("enabled", False)
    
    def get_enabled_markets(self) -> List[str]:
        """获取所有已启用的市场"""
        return [market for market in self.MARKETS if self.is_market_enabled(market)]
    
    def get_report_filename(self) -> str:
        """生成报告文件名"""
        now = datetime.now()
        return f"financial_report_{now.strftime('%Y%m%d_%H%M%S')}.md"
    
    def get_commit_message(self) -> str:
        """生成提交信息"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M")
        return self.GIT_COMMIT["commit_message_template"].format(date=date_str)


# 全局配置实例
config = FinancialReportConfig()

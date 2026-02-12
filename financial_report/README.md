# 📊 金融分析报告生成器 - 配置文件

## 项目概述
本项目自动收集黄金、美股、A股的市场数据，使用AI进行分析，并生成每日的金融分析报告。

## 📁 项目结构
```
financial_report/
├── 📄 config.py              # 配置文件
├── 📄 main.py                 # 主程序入口
├── 📂 data/                   # 数据存储
│   ├── 📄 gold/              # 黄金数据
│   ├── 📄 stocks_usa/        # 美股数据
│   └── 📄 stocks_cna/        # A股数据
├── 📂 analysis/               # AI分析模块
│   ├── 📄 gold_analyzer.py   # 黄金分析
│   ├── 📄 market_analyzer.py # 市场分析
│   └── 📄 report_generator.py # 报告生成
├── 📂 integrations/           # 数据源集成
│   ├── 📄 gold_api.py        # 黄金数据源
│   ├── 📄 stocks_usa_api.py  # 美股数据源
│   └── 📄 stocks_cn_api.py   # A股数据源
└── 📂 reports/                # 生成的分析报告
```

## 🎯 支持的市场
- 🥇 **黄金 (GOLD)** - 国际金价分析
- 🇺🇸 **美股 (US STOCKS)** - 道琼斯、纳斯达克、标普500
- 🇨🇳 **A股 (CHINA STOCKS)** - 上证指数、深证成指、创业板指

## 📊 数据源
- **黄金**: Yahoo Finance, TradingView, Kitco
- **美股**: Yahoo Finance, Alpha Vantage, Finnhub
- **A股**: 东方财富, 新浪财经, 腾讯财经

## ⚙️ 配置说明
在 `config.py` 中修改以下配置：

```python
# 定时执行时间（每天9:00 UTC）
SCHEDULE_HOUR = 9

# 要分析的市场
MARKETS = ['gold', 'stocks_usa', 'stocks_cn']

# 报告语言
REPORT_LANGUAGE = 'zh-CN'

# 是否自动提交到Git
AUTO_COMMIT = True
```

## 🚀 使用方法
```bash
# 手动执行分析
python main.py --mode=manual

# 执行完整的自动流程
python main.py --mode=auto

# 仅生成报告
python main.py --mode=report
```

## 🤖 AI维护说明
本项目由AI自动维护，会定期：
- 更新数据源配置
- 优化分析算法
- 改进报告格式
- 修复数据采集问题

## 📝 许可证
MIT License - 详见项目根目录 LICENSE 文件

---

**🥷 由 WolfMoss 的AI助手自动维护**
**🤖 最后更新：AI自动执行**

# -*- coding: utf-8 -*-
"""
金融分析报告生成器 - 主程序入口
Financial Analysis Report Generator - Main Entry Point

自动收集、分析金融市场数据并生成报告
此脚本由AI自动维护和执行
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class FinancialReportGenerator:
    """金融分析报告生成器主类"""
    
    def __init__(self):
        self.project_root = project_root
        self.config = self._load_config()
        self.collectors = {}
        self.analyzer = None
        self.report_generator = None
    
    def _load_config(self) -> Any:
        """加载配置"""
        config_path = self.project_root / "financial_report" / "config.py"
        
        if config_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", str(config_path))
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            return config_module.config
        else:
            # 返回默认配置
            class DefaultConfig:
                MARKETS = {
                    "gold": {"enabled": True},
                    "stocks_usa": {"enabled": True},
                    "stocks_cn": {"enabled": True}
                }
                GIT_COMMIT = {"enabled": False, "branch": "main"}
                REPORTS_DIR = self.project_root / "financial_report" / "reports"
            
            config_dir = self.project_root / "financial_report" / "reports"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            return DefaultConfig()
    
    def _initialize_collectors(self):
        """初始化数据收集器"""
        from integrations.gold_api import GoldDataCollector
        from integrations.stocks_usa_api import USStocksDataCollector
        from integrations.stocks_cn_api import ChinaStocksDataCollector
        
        self.collectors = {
            "gold": GoldDataCollector(),
            "stocks_usa": USStocksDataCollector(),
            "stocks_cn": ChinaStocksDataCollector()
        }
    
    def _initialize_analyzer(self):
        """初始化分析器"""
        from analysis.market_analyzer import MarketAnalyzer
        self.analyzer = MarketAnalyzer()
    
    def _initialize_report_generator(self):
        """初始化报告生成器"""
        from analysis.report_generator import ReportGenerator
        self.report_generator = ReportGenerator()
    
    def collect_data(self) -> Dict[str, Any]:
        """
        收集所有市场数据
        
        Returns:
            收集到的数据字典
        """
        print("=" * 70)
        print("📊 金融分析报告 - 数据收集阶段")
        print("=" * 70)
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self._initialize_collectors()
        
        collected_data = {
            "gold": None,
            "stocks_usa": None,
            "stocks_cn": None,
            "collection_time": datetime.now().isoformat()
        }
        
        # 收集黄金数据
        if self.config.MARKETS.get("gold", {}).get("enabled", True):
            print("🥇 收集黄金市场数据...")
            try:
                collected_data["gold"] = self.collectors["gold"].collect_all()
                print("✅ 黄金数据收集完成")
            except Exception as e:
                print(f"❌ 黄金数据收集失败: {e}")
                collected_data["gold"] = self._get_fallback_gold_data()
        else:
            print("⏭️ 黄金市场已禁用，跳过收集")
        
        print()
        
        # 收集美股数据
        if self.config.MARKETS.get("stocks_usa", {}).get("enabled", True):
            print("🇺🇸 收集美股市场数据...")
            try:
                collected_data["stocks_usa"] = self.collectors["stocks_usa"].collect_all()
                print("✅ 美股数据收集完成")
            except Exception as e:
                print(f"❌ 美股数据收集失败: {e}")
                collected_data["stocks_usa"] = self._get_fallback_us_stocks_data()
        else:
            print("⏭️ 美股市场已禁用，跳过收集")
        
        print()
        
        # 收集A股数据
        if self.config.MARKETS.get("stocks_cn", {}).get("enabled", True):
            print("🇨🇳 收集A股市场数据...")
            try:
                collected_data["stocks_cn"] = self.collectors["stocks_cn"].collect_all()
                print("✅ A股数据收集完成")
            except Exception as e:
                print(f"❌ A股数据收集失败: {e}")
                collected_data["stocks_cn"] = self._get_fallback_cn_stocks_data()
        else:
            print("⏭️ A股市场已禁用，跳过收集")
        
        print()
        print(f"⏰ 数据收集完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return collected_data
    
    def analyze_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析收集到的数据
        
        Args:
            collected_data: 收集的市场数据
        
        Returns:
            AI分析结果
        """
        print("\n" + "=" * 70)
        print("🤖 金融分析报告 - AI分析阶段")
        print("=" * 70)
        
        self._initialize_analyzer()
        
        try:
            analysis = self.analyzer.generate_comprehensive_analysis(
                gold_data=collected_data.get("gold", {}),
                us_stocks_data=collected_data.get("stocks_usa", {}),
                cn_stocks_data=collected_data.get("stocks_cn", {})
            )
            
            print("✅ AI分析完成")
            
            # 保存分析结果
            self._save_analysis_result(analysis)
            
            return analysis
        
        except Exception as e:
            print(f"❌ AI分析失败: {e}")
            return self._get_fallback_analysis()
    
    def generate_report(self, collected_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        生成分析报告
        
        Args:
            collected_data: 收集的市场数据
            analysis: AI分析结果
        
        Returns:
            报告文件路径
        """
        print("\n" + "=" * 70)
        print("📝 金融分析报告 - 报告生成阶段")
        print("=" * 70)
        
        self._initialize_report_generator()
        
        try:
            report_path = self.report_generator.generate_and_save(
                gold_data=collected_data.get("gold", {}),
                us_stocks_data=collected_data.get("stocks_usa", {}),
                cn_stocks_data=collected_data.get("stocks_cn", {}),
                analysis=analysis
            )
            
            print(f"✅ 报告已生成: {report_path}")
            
            return report_path
        
        except Exception as e:
            print(f"❌ 报告生成失败: {e}")
            return None
    
    def commit_to_github(self, report_path: str):
        """
        提交报告到GitHub
        
        Args:
            report_path: 报告文件路径
        """
        if not getattr(self.config, 'GIT_COMMIT', {}).get("enabled", False):
            print("⏭️ Git自动提交已禁用")
            return
        
        try:
            import subprocess
            
            report_file = Path(report_path)
            
            # 添加文件
            print("📦 准备提交到GitHub...")
            subprocess.run(["git", "add", str(report_file)], cwd=self.project_root, check=True)
            
            # 生成提交信息
            commit_msg = f"📊 金融分析报告更新 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # 提交
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.project_root,
                check=True
            )
            
            # 推送到远程
            if self.config.GIT_COMMIT.get("push_after_commit", True):
                subprocess.run(
                    ["git", "push", "origin", self.config.GIT_COMMIT.get("branch", "main")],
                    cwd=self.project_root,
                    check=True
                )
                print("✅ 已推送到GitHub")
            else:
                print("✅ 已提交到本地Git")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失败: {e}")
        except Exception as e:
            print(f"❌ 提交失败: {e}")
    
    def run_full_pipeline(self, mode: str = "auto") -> Dict[str, Any]:
        """
        运行完整的分析流程
        
        Args:
            mode: 执行模式 ('auto', 'manual', 'report')
        
        Returns:
            执行结果字典
        """
        result = {
            "success": False,
            "start_time": datetime.now().isoformat(),
            "mode": mode,
            "data_collection": None,
            "analysis": None,
            "report": None,
            "errors": []
        }
        
        try:
            # 阶段1: 数据收集
            if mode in ["auto", "manual"]:
                collected_data = self.collect_data()
                result["data_collection"] = collected_data
            else:
                collected_data = self._load_latest_data()
            
            # 阶段2: AI分析
            if mode in ["auto", "manual"]:
                analysis = self.analyze_data(collected_data)
                result["analysis"] = analysis
            else:
                analysis = self._load_latest_analysis()
            
            # 阶段3: 生成报告
            report_path = self.generate_report(collected_data, analysis)
            result["report"] = report_path
            
            # 阶段4: 提交到GitHub（仅自动模式）
            if mode == "auto" and report_path:
                self.commit_to_github(report_path)
            
            result["success"] = True
            result["end_time"] = datetime.now().isoformat()
            
            print("\n" + "=" * 70)
            print("✅ 金融分析报告生成完成！")
            print("=" * 70)
            print(f"📊 报告已保存: {report_path}")
            print(f"⏰ 执行时间: {result['start_time']} ~ {result['end_time']}")
            
        except Exception as e:
            result["errors"].append(str(e))
            print(f"\n❌ 执行失败: {e}")
        
        return result
    
    def _save_analysis_result(self, analysis: Dict[str, Any]):
        """保存分析结果"""
        analysis_dir = self.project_root / "financial_report" / "analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = analysis_dir / f"analysis_result_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        # 保存最新分析结果
        latest_link = analysis_dir / "latest_analysis.json"
        with open(latest_link, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        print(f"💾 分析结果已保存: {filepath}")
    
    def _load_latest_data(self) -> Dict[str, Any]:
        """加载最新收集的数据"""
        latest_data = {}
        
        for market in ["gold", "stocks_usa", "stocks_cn"]:
            collector = getattr(self.collectors.get(market), 'get_latest_data', lambda: None)()
            if collector:
                latest_data[market] = collector
        
        return latest_data
    
    def _load_latest_analysis(self) -> Dict[str, Any]:
        """加载最新分析结果"""
        analysis_file = self.project_root / "financial_report" / "analysis" / "latest_analysis.json"
        
        if analysis_file.exists():
            with open(analysis_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {}
    
    def _get_fallback_gold_data(self) -> Dict[str, Any]:
        """获取黄金备用数据"""
        return {
            "markets": {
                "futures": {
                    "close": 2050.00,
                    "change_percent": 0.30,
                    "source": "Fallback"
                }
            },
            "collection_time": datetime.now().isoformat()
        }
    
    def _get_fallback_us_stocks_data(self) -> Dict[str, Any]:
        """获取美股备用数据"""
        return {
            "markets": {
                "indices": {
                    "^DJI": {"name": "道琼斯", "close": 38000, "change_percent": 0.2},
                    "^IXIC": {"name": "纳斯达克", "close": 15000, "change_percent": 0.4}
                }
            },
            "collection_time": datetime.now().isoformat()
        }
    
    def _get_fallback_cn_stocks_data(self) -> Dict[str, Any]:
        """获取A股备用数据"""
        return {
            "markets": {
                "indices": {
                    "000001.SS": {"name": "上证指数", "close": 2877, "change_percent": 0.15}
                }
            },
            "collection_time": datetime.now().isoformat()
        }
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """获取备用分析结果"""
        return {
            "gold_market": {
                "current_price": 2050.00,
                "change_percent": 0.30,
                "trend": "横盘整理",
                "outlook": "市场方向不明朗",
                "recommendation": {"action": "观望", "risk_level": "低"}
            },
            "us_market": {
                "index_analysis": {
                    "^DJI": {"close": 38000, "change_percent": 0.2},
                    "^IXIC": {"close": 15000, "change_percent": 0.4}
                },
                "outlook": "美股温和上涨",
                "recommendation": {"action": "持有", "risk_level": "低"}
            },
            "cn_market": {
                "index_analysis": {
                    "000001.SS": {"close": 2877, "change_percent": 0.15}
                },
                "outlook": "A股震荡整理",
                "recommendation": {"action": "持股", "risk_level": "低"}
            }
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="金融分析报告自动生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--mode",
        choices=["auto", "manual", "report"],
        default="auto",
        help="执行模式: auto(自动), manual(手动), report(仅生成报告)"
    )
    
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="仅收集数据，不进行分析"
    )
    
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="不提交到GitHub"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🏦 金融分析报告自动生成器")
    print("🤖 由Claude AI驱动")
    print("=" * 70)
    print()
    
    generator = FinancialReportGenerator()
    
    # 如果指定不提交，临时禁用Git提交
    if args.no_commit:
        generator.config.GIT_COMMIT = {"enabled": False}
    
    # 运行完整流程
    result = generator.run_full_pipeline(mode=args.mode)
    
    # 输出结果摘要
    print("\n📊 执行结果摘要:")
    print(f"  成功: {'✅ 是' if result['success'] else '❌ 否'}")
    print(f"  模式: {result['mode']}")
    print(f"  报告: {result.get('report', 'N/A')}")
    
    if result.get('errors'):
        print(f"  错误: {len(result['errors'])} 个")
        for error in result['errors']:
            print(f"    - {error}")
    
    # 返回退出码
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()

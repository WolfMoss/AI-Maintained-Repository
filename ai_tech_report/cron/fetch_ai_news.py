#!/usr/bin/env python3
"""
AI技术资讯实时抓取器
从多个权威来源获取最新AI新闻和论文：
1. ArXiv (AI/ML/NLP/CV论文)
2. Hacker News (AI讨论)
3. MIT Technology Review (RSS)
4. OpenAI Blog
5. Google AI Blog
"""

import json
import ssl
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from xml.etree import ElementTree as ET
import feedparser
import subprocess
import sys

# 尝试导入requests，如果不存在则使用urllib
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class AINewsFetcher:
    """AI新闻获取器"""

    def __init__(self):
        self.current_date = datetime.now()
        self.yesterday = self.current_date - timedelta(days=1)
        self.two_days_ago = self.current_date - timedelta(days=2)
        self.one_week_ago = self.current_date - timedelta(days=7)

        # SSL上下文（处理证书问题）
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def log(self, msg: str):
        """日志输出"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

    def fetch_arxiv_papers(self, max_papers: int = 15) -> List[Dict]:
        """从ArXiv获取最新AI论文"""
        self.log("📚 正在抓取 ArXiv AI/ML 论文...")

        papers = []

        # 查询最新的AI相关论文
        url = (
            "https://export.arxiv.org/api/query?"
            "search_query=cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.NE+OR+cat:cs.CV+OR+cat:cs.RO+OR+cat:cs.IR&"
            f"start=0&max_results={max_papers}&"
            "sortBy=submittedDate&sortOrder=descending"
        )

        try:
            if HAS_REQUESTS:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                content = response.text
            else:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, context=self.ssl_context, timeout=30) as resp:
                    content = resp.read().decode('utf-8')

            # 解析XML
            root = ET.fromstring(content)

            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                paper = {
                    'title': entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', ' '),
                    'url': entry.find('{http://www.w3.org/2005/Atom}id').text.strip(),
                    'published': entry.find('{http://www.w3.org/2005/Atom}published').text.strip(),
                    'summary': entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()[:500],
                    'authors': [a.find('{http://www.w3.org/2005/Atom}name').text
                               for a in entry.findall('{http://www.w3.org/2005/Atom}author')][:5],
                    'categories': [c.get('term') for c in entry.findall('{http://www.w3.org/2005/Atom}category')],
                    'source': 'ArXiv'
                }
                papers.append(paper)

            self.log(f"✅ 获取到 {len(papers)} 篇ArXiv论文")

        except Exception as e:
            self.log(f"❌ ArXiv获取失败: {e}")

        return papers[:max_papers]

    def fetch_hacker_news(self, max_items: int = 20) -> List[Dict]:
        """从Hacker News获取AI相关讨论"""
        self.log("📰 正在抓取 Hacker News AI讨论...")

        items = []

        try:
            # 使用Algolia API获取HN数据
            url = (
                "https://hn.algolia.com/api/v1/search_by_date?"
                "tags=story&"
                f"tags=AI,Machine Learning,LLM,OpenAI,Claude,GPT,Deep Learning,Artificial Intelligence&"
                f"hitsPerPage={max_items}"
            )

            if HAS_REQUESTS:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
            else:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, context=self.ssl_context, timeout=30) as resp:
                    data = json.loads(resp.read().decode('utf-8'))

            for hit in data.get('hits', []):
                item = {
                    'title': hit.get('title', ''),
                    'url': hit.get('url', f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"),
                    'points': hit.get('points', 0),
                    'author': hit.get('author', ''),
                    'created_at': hit.get('created_at', ''),
                    'num_comments': hit.get('num_comments', 0),
                    'source': 'Hacker News',
                    'object_id': hit.get('objectID', '')
                }
                items.append(item)

            self.log(f"✅ 获取到 {len(items)} 条HN讨论")

        except Exception as e:
            self.log(f"❌ Hacker News获取失败: {e}")

        return items[:max_items]

    def fetch_mit_tech_review(self, max_articles: int = 10) -> List[Dict]:
        """从MIT Technology Review获取AI文章"""
        self.log("📖 正在抓取 MIT Technology Review AI文章...")

        articles = []

        try:
            url = "https://www.technologyreview.com/topic/artificial-intelligence/feed"

            # 使用feedparser解析RSS
            feed = feedparser.parse(url)

            count = 0
            for entry in feed.entries:
                if count >= max_articles:
                    break

                # 解析日期
                published = ""
                if hasattr(entry, 'published_parsed'):
                    try:
                        dt = datetime(*entry.published_parsed[:6])
                        published = dt.strftime('%Y-%m-%d')
                    except:
                        pass

                article = {
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'summary': entry.get('summary', '')[:300],
                    'published': published,
                    'source': 'MIT Technology Review'
                }

                # 只保留近期文章
                if article['title']:
                    articles.append(article)
                    count += 1

            self.log(f"✅ 获取到 {len(articles)} 篇MIT Tech Review文章")

        except Exception as e:
            self.log(f"❌ MIT Technology Review获取失败: {e}")

        return articles[:max_articles]

    def fetch_github_trending(self, max_items: int = 10) -> List[Dict]:
        """获取GitHub AI相关趋势项目"""
        self.log("⭐ 正在抓取 GitHub AI趋势项目...")

        repos = []

        try:
            # 使用搜索API获取最新的AI相关Python项目
            url = (
                "https://api.github.com/search/repositories?"
                "q=AI+machine-learning+deep-learning+language:python+created:>=" + 
                (self.one_week_ago.strftime('%Y-%m-%d')) +
                f"&sort=stars&per_page={max_items}"
            )

            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'AI-News-Fetcher'
            }

            if HAS_REQUESTS:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
            else:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, context=self.ssl_context, timeout=30) as resp:
                    data = json.loads(resp.read().decode('utf-8'))

            for repo in data.get('items', []):
                item = {
                    'name': repo.get('full_name', ''),
                    'description': repo.get('description', '')[:300],
                    'stars': repo.get('stargazers_count', 0),
                    'language': repo.get('language', ''),
                    'url': repo.get('html_url', ''),
                    'updated': repo.get('updated_at', '')[:10],
                    'source': 'GitHub Trending'
                }
                repos.append(item)

            self.log(f"✅ 获取到 {len(repos)} 个GitHub项目")

        except Exception as e:
            self.log(f"⚠️ GitHub趋势获取跳过（需认证）: {str(e)[:50]}")
            # 提供手动查看链接
            self.log("💡 手动查看: https://github.com/trending?spoken_language_code=zh")

        return repos[:max_items]

    def aggregate_news(self) -> Dict:
        """整合所有新闻源"""
        self.log("\n" + "="*60)
        self.log("🚀 开始AI新闻聚合")
        self.log("="*60 + "\n")

        # 并行或顺序获取各来源
        arxiv_papers = self.fetch_arxiv_papers(12)
        hn_discussions = self.fetch_hacker_news(15)
        mit_articles = self.fetch_mit_tech_review(8)
        github_repos = self.fetch_github_trending(8)

        result = {
            'fetch_time': self.current_date.strftime('%Y-%m-%d %H:%M:%S'),
            'arxiv_papers': arxiv_papers,
            'hn_discussions': hn_discussions,
            'mit_articles': mit_articles,
            'github_repos': github_repos,
            'total_sources': 4
        }

        return result

    def format_news_report(self, data: Dict) -> str:
        """格式化新闻报告"""
        report = []
        report.append("# AI技术资讯汇总")
        report.append("")
        report.append(f"**获取时间**: {data['fetch_time']}")
        report.append("")
        report.append("---\n")

        # ArXiv论文
        if data['arxiv_papers']:
            report.append("## 📚 ArXiv最新论文")
            report.append("")
            for i, paper in enumerate(data['arxiv_papers'][:8], 1):
                pub_date = paper['published'][:10] if paper['published'] else 'N/A'
                report.append(f"### {i}. {paper['title']}")
                report.append(f"- **发布时间**: {pub_date}")
                report.append(f"- **链接**: {paper['url']}")
                report.append(f"- **作者**: {', '.join(paper['authors'][:3])}")
                report.append(f"- **类别**: {', '.join(paper['categories'][:3])}")
                report.append("")
            report.append("---\n")

        # Hacker News
        if data['hn_discussions']:
            report.append("## 💬 Hacker News热门讨论")
            report.append("")
            for i, item in enumerate(data['hn_discussions'][:8], 1):
                report.append(f"### {i}. {item['title']}")
                report.append(f"- **来源**: [Hacker News](https://news.ycombinator.com/item?id={item.get('object_id', '')})")
                report.append(f"- **点赞**: {item['points']} | **评论**: {item['num_comments']}")
                if item['url'] and item['url'] != f"https://news.ycombinator.com/item?id={item.get('objectID', '')}":
                    report.append(f"- **原文链接**: {item['url']}")
                report.append("")
            report.append("---\n")

        # MIT Technology Review
        if data['mit_articles']:
            report.append("## 📖 MIT Technology Review")
            report.append("")
            for i, article in enumerate(data['mit_articles'][:5], 1):
                report.append(f"### {i}. {article['title']}")
                report.append(f"- **链接**: {article['url']}")
                report.append(f"- **发布时间**: {article['published']}")
                report.append("")
            report.append("---\n")

        # GitHub Trending
        if data['github_repos']:
            report.append("## ⭐ GitHub趋势项目")
            report.append("")
            for i, repo in enumerate(data['github_repos'][:5], 1):
                report.append(f"### {i}. {repo['name']}")
                report.append(f"- **描述**: {repo['description']}")
                report.append(f"- **⭐ Stars**: {repo['stars']}")
                report.append(f"- **🔤 语言**: {repo['language']}")
                report.append(f"- **🔗 链接**: {repo['url']}")
                report.append("")
            report.append("---\n")

        return "\n".join(report)

    def save_to_file(self, data: Dict, output_file: str):
        """保存数据到文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.log(f"📁 JSON数据已保存: {output_file}")

    def save_report(self, report: str, output_file: str):
        """保存Markdown报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        self.log(f"📄 Markdown报告已保存: {output_file}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='AI新闻获取器')
    parser.add_argument('--output-dir', type=str, required=True, help='输出目录')
    parser.add_argument('--format', type=str, default='both',
                        choices=['json', 'markdown', 'both'],
                        help='输出格式')
    args = parser.parse_args()

    fetcher = AINewsFetcher()
    data = fetcher.aggregate_news()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if args.format in ['json', 'both']:
        json_file = f"{args.output_dir}/ai_news_data_{timestamp}.json"
        fetcher.save_to_file(data, json_file)

    if args.format in ['markdown', 'both']:
        report = fetcher.format_news_report(data)
        md_file = f"{args.output_dir}/ai_news_{timestamp}.txt"
        fetcher.save_report(report, md_file)

    print("\n" + "="*60)
    print("✅ 新闻获取完成!")
    print(f"📊 数据来源: ArXiv, Hacker News, MIT Tech Review, GitHub")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

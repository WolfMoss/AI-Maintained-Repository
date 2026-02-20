#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM应用示范代码 - 基于LangChain的AI应用示例
依赖安装: pip install langchain langchain-openai langchain-community python-dotenv

本代码展示如何构建基于大语言模型(LLM)的应用程序
包含：文本摘要、问答系统、文本分类、内容生成等常见应用场景
"""

# 导入必要的库
import os
from datetime import datetime
from typing import List, Dict, Any

# LangChain 核心组件
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import TextLoader

# ============================================================
# 配置部分 - 请根据实际情况修改
# ============================================================

# 设置API密钥 (建议使用环境变量)
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# 使用Ollama本地模型 (免费，无需API密钥)
# 确保本地已安装Ollama并运行: ollama serve
# 模型列表: llama2, mistral, qwen, etc.

class LLMApplicationDemo:
    """
    LLM应用演示类
    展示大语言模型的多种应用场景
    """
    
    def __init__(self, model_provider: str = "ollama", model_name: str = "llama2"):
        """
        初始化LLM应用
        
        参数:
            model_provider: 模型提供商 ("openai" 或 "ollama")
            model_name: 模型名称
        """
        self.model_provider = model_provider
        self.model_name = model_name
        self.llm = self._create_llm()
        print(f"✓ LLM应用初始化完成，使用模型: {model_name}")
        print(f"  提供商: {model_provider}")
        
    def _create_llm(self):
        """创建LLM实例"""
        if self.model_provider == "openai":
            # OpenAI API 调用 (需要API密钥)
            return ChatOpenAI(
                model=self.model_name,
                temperature=0.7,  # 控制生成随机性
                max_tokens=1000
            )
        elif self.model_provider == "ollama":
            # Ollama 本地模型 (免费开源)
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(
                model=self.model_name,
                temperature=0.7
            )
        else:
            raise ValueError(f"不支持的模型提供商: {self.model_provider}")
    
    def text_summarization(self, text: str) -> str:
        """
        文本摘要功能
        将长文本压缩成简洁的摘要
        
        参数:
            text: 待摘要的文本
            
        返回:
            生成的摘要文本
        """
        print("\n" + "="*50)
        print("📝 应用1: 文本摘要")
        print("="*50)
        
        # 使用LangChain的摘要链
        prompt_template = """请将以下文本简明扼要地摘要成中文摘要:

{text}

摘要:"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        summary = chain.run(text=text)
        
        print(f"原文长度: {len(text)} 字符")
        print(f"摘要: {summary}")
        return summary
    
    def question_answering(self, context: str, question: str) -> str:
        """
        问答系统
        基于给定上下文回答问题 (RAG基本原理)
        
        参数:
            context: 背景上下文
            question: 问题
            
        返回:
            问题的答案
        """
        print("\n" + "="*50)
        print("❓ 应用2: 问答系统")
        print("="*50)
        
        prompt_template = """基于以下背景信息回答问题。如果信息不足以回答，请说明"信息不足"。

背景信息:
{context}

问题: {question}

回答:"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        answer = chain.run(context=context, question=question)
        
        print(f"问题: {question}")
        print(f"答案: {answer}")
        return answer
    
    def text_classification(self, text: str, categories: List[str]) -> Dict[str, float]:
        """
        文本分类
        将文本分类到预定义的类别中
        
        参数:
            text: 待分类文本
            categories: 类别列表
            
        返回:
            各类别的概率
        """
        print("\n" + "="*50)
        print("🏷️ 应用3: 文本分类")
        print("="*50)
        
        categories_str = ", ".join(categories)
        
        prompt_template = """请分析以下文本，判断它属于哪个类别。

可选类别: {categories}

文本: {text}

请直接输出最可能的类别名称，不要其他解释。"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["categories", "text"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(categories=categories_str, text=text)
        
        print(f"文本: {text[:50]}...")
        print(f"分类结果: {result.strip()}")
        return {"category": result.strip(), "confidence": 1.0}
    
    def content_generation(self, topic: str, content_type: str = "article") -> str:
        """
        内容生成
        根据主题生成各类内容
        
        参数:
            topic: 主题
            content_type: 内容类型 (article, poem, email, etc.)
            
        生成的内容
        """
        print("\n" + "="*50)
        print("✍️ 应用4: 内容生成")
        print("="*50)
        
        type_descriptions = {
            "article": "一篇结构清晰、论述有力的文章",
            "poem": "一首中文诗歌",
            "email": "一封专业的电子邮件",
            "summary": "简洁的总结",
            "code": "Python代码示例"
        }
        
        description = type_descriptions.get(content_type, "内容")
        
        prompt_template = """请根据以下主题生成{description}:

主题: {topic}

内容:"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["topic", "description"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        content = chain.run(topic=topic, description=description)
        
        print(f"主题: {topic}")
        print(f"类型: {content_type}")
        print(f"生成内容:\n{content}")
        return content
    
    def sentiment_analysis(self, text: str) -> str:
        """
        情感分析
        分析文本的情感倾向
        
        参数:
            text: 待分析文本
            
        返回:
            情感分析结果
        """
        print("\n" + "="*50)
        print("😊 应用5: 情感分析")
        print("="*50)
        
        prompt_template = """请分析以下文本的情感倾向，只需输出"正面"、"负面"或"中性"：

文本: {text}

情感倾向:"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        sentiment = chain.run(text=text)
        
        print(f"文本: {text}")
        print(f"情感倾向: {sentiment.strip()}")
        return sentiment.strip()
    
    def run_all_demos(self):
        """运行所有演示"""
        print("\n" + "🚀"*25)
        print("开始LLM应用演示")
        print("="*50)
        
        # 示例文本 - 关于LLM的新闻
        sample_text = """
        人工智能技术的快速发展正在深刻改变我们的生活方式和工作模式。
        大语言模型(LLM)作为AI领域的重要突破，已经在各个行业得到广泛应用。
        从智能客服到内容创作，从数据分析到代码编写，LLM展现出强大的能力。
        然而，传统的数据泄露防护(DLP)系统在面对LLM时显得力不从心。
        这是因为LLM可以处理海量数据，且其工作方式与传统软件有本质区别。
        企业需要重新思考数据安全策略，以应对新时代的安全挑战。
        """
        
        # 1. 文本摘要
        self.text_summarization(sample_text)
        
        # 2. 问答系统
        context = "LLM(大语言模型)是一种使用深度学习技术训练的人工智能模型，
                  能够理解和生成人类语言。它们通过大规模文本数据进行预训练，
                  然后可以通过微调适应特定任务。"
        question = "什么是LLM？"
        self.question_answering(context, question)
        
        # 3. 文本分类
        news_text = "NASA宣布启动新的艺术合作计划，将艺术家带入太空探索项目"
        categories = ["科技", "艺术", "体育", "财经", "娱乐"]
        self.text_classification(news_text, categories)
        
        # 4. 内容生成
        self.content_generation("人工智能对未来工作的影响", "article")
        
        # 5. 情感分析
        self.sentiment_analysis("这个产品真是太棒了，我非常喜欢！")
        
        print("\n" + "✅"*25)
        print("所有演示完成!")
        print("="*50)


def main():
    """
    主函数 - 演示LLM的多种应用
    """
    print("="*60)
    print("  🧠 LLM应用示范程序")
    print("  基于LangChain构建的大语言模型应用")
    print("="*60)
    
    # 创建LLM应用实例
    # 可选提供商: "openai" (需要API密钥) 或 "ollama" (本地免费)
    demo = LLMApplicationDemo(
        model_provider="ollama",  # 使用本地Ollama模型
        model_name="llama2"        # 可选: mistral, qwen, etc.
    )
    
    # 运行所有演示
    demo.run_all_demos()


if __name__ == "__main__":
    # 运行主程序
    main()
```

**依赖安装命令:**
```bash
pip install langchain langchain-openai langchain-community langchain-ollama python-dotenv
```

**使用说明:**
1. 推荐使用Ollama本地模型(免费): 先安装Ollama，然后运行`ollama pull llama2`
2. 也可使用OpenAI API: 设置`OPENAI_API_KEY`环境变量并改为`model_provider="openai"`

[2m⏱️  Step 1 completed in 62.99s (total: 62.99s)[0m

[1m[96mSession Statistics:[0m
[2m────────────────────────────────────────[0m
  Session Duration: 00:01:03
  Total Messages: 3
    - User Messages: [92m1[0m
    - Assistant Replies: [94m1[0m
    - Tool Calls: [93m0[0m
  Available Tools: 8
  API Tokens Used: [95m6,413[0m
[2m────────────────────────────────────────[0m


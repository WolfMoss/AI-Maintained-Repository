#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI长文本处理与问答系统 - 基于最新LLM技术
============================================
依赖库:
    pip install transformers torch langchain langchain-community
    pip install sentence-transformers faiss-cpu accelerate

功能说明:
    1. 长文本智能分块处理
    2. 基于语义检索的问答系统
    3. 文本嵌入向量生成
    4. 上下文感知的答案生成

作者: AI教育专家
基于AI资讯: Long Context, Less Focus: A Scaling Gap in LLMs Revealed through Privacy and Personalization
"""

import os
import json
import hashlib
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict

# ==================== 依赖库导入 ====================
try:
    import torch
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM,
        pipeline,
        BitsAndBytesConfig
    )
    from sentence_transformers import SentenceTransformer
    import numpy as np
    print(f"✅ PyTorch版本: {torch.__version__}")
    print(f"✅ GPU可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"✅ GPU设备: {torch.cuda.get_device_name(0)}")
except ImportError as e:
    print(f"❌ 依赖库导入失败: {e}")
    print("请安装: pip install transformers torch sentence-transformers numpy")
    exit(1)


# ==================== 配置类 ====================
@dataclass
class LLMConfig:
    """LLM模型配置类"""
    # 嵌入模型配置
    embedding_model: str = "BAAI/bge-large-zh-v1.5"  # 中文优质嵌入模型
    embedding_device: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    # 生成模型配置
    generation_model: str = "Qwen/Qwen2.5-0.5B-Instruct"  # 轻量级可运行模型
    max_length: int = 512              # 最大生成长度
    temperature: float = 0.7            # 采样温度
    top_p: float = 0.9                 # 核采样概率
    context_window: int = 2048          # 上下文窗口大小
    
    # 文本分块配置
    chunk_size: int = 512              # 块大小（字符数）
    chunk_overlap: int = 50             # 块重叠大小
    
    # 检索配置
    top_k: int = 3                      # 检索Top-K结果


@dataclass
class Document:
    """文档数据类"""
    content: str
    metadata: Dict = field(default_factory=dict)
    
    @property
    def doc_id(self) -> str:
        """生成文档唯一ID"""
        return hashlib.md5(self.content.encode()).hexdigest()[:8]


# ==================== 文本处理模块 ====================
class TextChunker:
    """
    智能文本分块器
    功能: 将长文本分割成适合LLM处理的较小块
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    def chunk_text(self, text: str, chunk_size: Optional[int] = None) -> List[str]:
        """
        文本分块主方法
        
        Args:
            text: 输入长文本
            chunk_size: 块大小（可选，默认使用配置）
        
        Returns:
            文本块列表
        """
        chunk_size = chunk_size or self.config.chunk_size
        overlap = self.config.chunk_overlap
        
        # 简单分块：按固定长度分割
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        print(f"📝 文本分块完成: {len(chunks)} 个块")
        return chunks
    
    def chunk_by_sentences(self, text: str) -> List[str]:
        """
        按句子分块（更智能的分块方式）
        保持句子完整性
        """
        # 简单句号分割（实际应用中可使用更复杂的NLP工具）
        sentences = text.replace('。', '。|').replace('！', '！|').replace('？', '？|')
        sentences = [s.strip() for s in sentences.split('|') if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.config.chunk_size:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks


# ==================== 嵌入向量模块 ====================
class EmbeddingGenerator:
    """
    文本嵌入向量生成器
    功能: 将文本转换为高维向量，用于语义检索
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.device = config.embedding_device
        print(f"🔄 正在加载嵌入模型: {config.embedding_model}")
        
        # 加载句子嵌入模型
        self.model = SentenceTransformer(config.embedding_model, device=self.device)
        print(f"✅ 嵌入模型加载完成 (设备: {self.device})")
    
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        批量生成文本嵌入向量
        
        Args:
            texts: 文本列表
            batch_size: 批处理大小
        
        Returns:
            嵌入向量矩阵 (N, D)
        """
        # 归一化嵌入向量
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True
        )
        return embeddings
    
    def compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        计算两个向量的余弦相似度
        """
        return np.dot(vec1, vec2)


# ==================== 向量检索模块 ====================
class VectorRetriever:
    """
    向量语义检索器
    功能: 基于嵌入向量的相似度检索
    """
    
    def __init__(self, embedding_generator: EmbeddingGenerator):
        self.embedding_gen = embedding_generator
        self.documents: List[Document] = []
        self.chunks: List[str] = []
        self.chunk_embeddings: Optional[np.ndarray] = None
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        添加文档到检索系统
        
        Args:
            documents: Document对象列表
        """
        chunker = TextChunker(LLMConfig())
        
        all_chunks = []
        for doc in documents:
            # 按句子智能分块
            chunks = chunker.chunk_by_sentences(doc.content)
            all_chunks.extend(chunks)
        
        self.chunks = all_chunks
        self.documents = documents
        
        # 批量生成嵌入向量
        print(f"🔄 正在生成 {len(all_chunks)} 个文本块的嵌入向量...")
        self.chunk_embeddings = self.embedding_gen.encode(all_chunks)
        print(f"✅ 嵌入向量生成完成，维度: {self.chunk_embeddings.shape}")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        检索与查询最相关的文本块
        
        Args:
            query: 查询文本
            top_k: 返回Top-K结果
        
        Returns:
            (文本块, 相似度分数)列表
        """
        # 生成查询嵌入
        query_embedding = self.embedding_gen.encode([query])
        
        # 计算相似度
        similarities = np.dot(self.chunk_embeddings, query_embedding.T).flatten()
        
        # 获取Top-K索引
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], similarities[idx]))
        
        return results


# ==================== LLM生成模块 ====================
class LLMGenerator:
    """
    LLM答案生成器
    功能: 基于检索上下文生成自然语言答案
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        print(f"🔄 正在加载生成模型: {config.generation_model}")
        
        # 加载分词器
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.generation_model, 
            trust_remote_code=True
        )
        
        # 量化配置（减少显存占用）
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16
        )
        
        # 加载模型（使用量化减少显存）
        self.model = AutoModelForCausalLM.from_pretrained(
            config.generation_model,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        # 创建生成管道
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_length=config.max_length,
            temperature=config.temperature,
            top_p=config.top_p,
            do_sample=True
        )
        print(f"✅ 生成模型加载完成")
    
    def generate_answer(
        self, 
        query: str, 
        context_chunks: List[Tuple[str, float]]
    ) -> str:
        """
        基于上下文生成答案
        
        Args:
            query: 用户问题
            context_chunks: 检索到的相关上下文
        
        Returns:
            生成的答案
        """
        # 构建提示词
        context = "\n\n".join([chunk[0] for chunk in context_chunks])
        
        prompt = f"""请根据以下参考资料回答问题。如果资料中没有相关信息，请说明"资料不足"。

参考资料:
{context}

问题: {query}

回答:"""
        
        # 生成答案
        output = self.generator(prompt, max_new_tokens=256)[0]
        answer = output['generated_text'].replace(prompt, "").strip()
        
        return answer


# ==================== 主系统类 ====================
class LongContextQA:
    """
    长文本问答系统主类
    整合所有模块，提供统一的问答接口
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        
        print("=" * 50)
        print("🚀 初始化长文本问答系统")
        print("=" * 50)
        
        # 初始化各模块
        self.embedding_gen = EmbeddingGenerator(self.config)
        self.retriever = VectorRetriever(self.embedding_gen)
        self.llm_gen = None  # 延迟加载
    
    def load_documents(self, documents: List[Document]) -> None:
        """
        加载文档到系统
        
        Args:
            documents: 文档列表
        """
        print(f"📂 加载 {len(documents)} 个文档...")
        self.retriever.add_documents(documents)
    
    def initialize_llm(self) -> None:
        """初始化LLM生成器（按需加载）"""
        if self.llm_gen is None:
            self.llm_gen = LLMGenerator(self.config)
    
    def query(
        self, 
        question: str, 
        use_llm: bool = True,
        verbose: bool = False
    ) -> Dict:
        """
        查询接口
        
        Args:
            question: 用户问题
            use_llm: 是否使用LLM生成答案
            verbose: 是否显示详细信息
        
        Returns:
            包含答案和相关上下文的字典
        """
        # 1. 检索相关上下文
        context_chunks = self.retriever.retrieve(question, top_k=self.config.top_k)
        
        if verbose:
            print("\n📋 检索到的相关上下文:")
            for i, (chunk, score) in enumerate(context_chunks, 1):
                print(f"  [{i}] 相似度: {score:.4f}")
                print(f"      内容: {chunk[:100]}...")
        
        # 2. 生成答案
        if use_llm:
            self.initialize_llm()
            answer = self.llm_gen.generate_answer(question, context_chunks)
        else:
            # 简单返回最相关的文本块
            answer = context_chunks[0][0] if context_chunks else "未找到相关内容"
        
        return {
            "question": question,
            "answer": answer,
            "sources": context_chunks
        }


# ==================== 示例运行 ====================
def main():
    """主函数：演示系统功能"""
    
    print("\n" + "=" * 60)
    print("📚 AI长文本问答系统 - 示例演示")
    print("=" * 60 + "\n")
    
    # 示例文档（模拟长文本场景）
    sample_docs = [
        Document(
            content="""
            人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，
            它试图理解智能的本质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
            该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
            
            机器学习是人工智能的核心，是使计算机具有智能的根本途径。
            它是一门多领域交叉学科，涉及概率论、统计学、逼近论、凸分析、算法复杂度理论等多门学科。
            机器学习专门研究计算机怎样模拟或实现人类的学习行为，以获取新的知识或技能，
            重新组织已有的知识结构使之不断改善自身的性能。
            
            深度学习是机器学习的分支，是一种以人工神经网络为架构，
            对数据进行表征学习的算法。深度学习在计算机视觉、语音识别、
            自然语言处理等领域取得了突破性进展。
            """,
            metadata={"source": "AI基础介绍", "category": "技术科普"}
        ),
        Document(
            content="""
            大语言模型（Large Language Model，LLM）是一种人工智能模型，
            旨在理解和生成人类语言。它们在大量的文本数据上训练，
            可以执行各种自然语言处理任务，如问答、翻译、摘要、写作等。
            
            最新的研究表明，长上下文能力是LLM的重要特征之一。
            通过扩展上下文窗口，模型可以处理更长的文档，进行更深入的推理。
            然而，Long Context, Less Focus论文指出，长上下文可能带来挑战：
            模型在处理过长上下文时可能"分心"，影响对关键信息的捕捉。
            
            上下文学习（In-Context Learning）是LLM的重要能力，
            允许模型在不进行额外训练的情况下学习新任务。
            这种能力随着模型规模的增大而增强。
            """,
            metadata={"source": "LLM技术介绍", "category": "深度学习"}
        ),
        Document(
            content="""
            Transformer架构是当前大语言模型的主流架构。
            它由Vaswani等人于2017年提出，完全基于注意力机制。
            Transformer架构摒弃了传统的循环和卷积结构，
            通过自注意力机制实现并行计算，大大提高了训练效率。
            
            自注意力（Self-Attention）机制允许模型同时关注输入序列的所有位置，
            捕捉序列中的长距离依赖关系。多头注意力（Multi-Head Attention）
            进一步增强了模型的表达能力，使其能够学习多种类型的关联。
            
            预训练-微调（Pre-training + Fine-tuning）已成为NLP模型的标准范式。
            模型首先在大规模无标注文本上进行预训练，学习通用语言表示，
            然后在特定任务的数据上进行微调，获得任务相关的能力。
            """,
            metadata={"source": "Transformer架构", "category": "深度学习"}
        )
    ]
    
    # 初始化系统
    config = LLMConfig()
    qa_system = LongContextQA(config)
    
    # 加载文档
    qa_system.load_documents(sample_docs)
    
    # 示例问题
    questions = [
        "什么是大语言模型？",
        "Transformer架构的核心是什么？",
        "深度学习和机器学习有什么关系？"
    ]
    
    print("\n" + "-" * 50)
    print("🔍 开始问答演示")
    print("-" * 50)
    
    # 逐个回答问题
    for q in questions:
        print(f"\n❓ 问题: {q}")
        result = qa_system.query(q, use_llm=True, verbose=True)
        
        print(f"\n💡 回答:")
        print(f"   {result['answer']}")
        print("-" * 50)
    
    print("\n✅ 演示完成!")
    print("\n📌 使用说明:")
    print("   1. 修改 sample_docs 加载您自己的文档")
    print("   2. 调整 LLMConfig 参数优化性能")
    print("   3. 设置 use_llm=False 可仅使用检索功能")


if __name__ == "__main__":
    main()
```

[2m⏱️  Step 1 completed in 68.19s (total: 68.19s)[0m

[1m[96mSession Statistics:[0m
[2m────────────────────────────────────────[0m
  Session Duration: 00:01:08
  Total Messages: 3
    - User Messages: [92m1[0m
    - Assistant Replies: [94m1[0m
    - Tool Calls: [93m0[0m
  Available Tools: 8
  API Tokens Used: [95m7,587[0m
[2m────────────────────────────────────────[0m


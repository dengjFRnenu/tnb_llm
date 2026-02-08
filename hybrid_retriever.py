#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合检索引擎 - Hybrid Retrieval Engine
结合向量检索（ChromaDB）和关键词检索（BM25）
"""

import chromadb
from FlagEmbedding import BGEM3FlagModel
from rank_bm25 import BM25Okapi
import jieba
from typing import List, Dict, Tuple
import numpy as np


class VectorRetriever:
    """向量检索器 - 基于 ChromaDB + BGE-M3"""
    
    def __init__(self, chroma_path: str = "./chroma_db", collection_name: str = "diabetes_guidelines_2024"):
        """
        初始化向量检索器
        
        Args:
            chroma_path: ChromaDB 存储路径
            collection_name: 集合名称
        """
        print("🔧 初始化向量检索器...")
        self.model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_collection(name=collection_name)
        print("✅ 向量检索器就绪")
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        向量检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
        
        Returns:
            List of {id, document, metadata, score}
        """
        # 查询向量化
        query_embedding = self.model.encode([query])['dense_vecs'][0]
        
        # 检索
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        # 格式化结果
        retrieved = []
        for i in range(len(results['ids'][0])):
            retrieved.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': 1 - results['distances'][0][i],  # 转换为相似度
                'source': 'vector'
            })
        
        return retrieved


class KeywordRetriever:
    """关键词检索器 - 基于 BM25"""
    
    def __init__(self, chroma_path: str = "./chroma_db", collection_name: str = "diabetes_guidelines_2024"):
        """
        初始化关键词检索器
        
        Args:
            chroma_path: ChromaDB 存储路径（用于加载文档）
            collection_name: 集合名称
        """
        print("🔧 初始化关键词检索器...")
        
        # 从 ChromaDB 加载所有文档
        client = chromadb.PersistentClient(path=chroma_path)
        collection = client.get_collection(name=collection_name)
        
        # 获取所有文档
        all_data = collection.get()
        self.documents = all_data['documents']
        self.ids = all_data['ids']
        self.metadatas = all_data['metadatas']
        
        # 分词并建立BM25索引
        print(f"📄 对 {len(self.documents)} 篇文档分词...")
        tokenized_corpus = [list(jieba.cut(doc)) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        print("✅ 关键词检索器就绪")
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        BM25 关键词检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
        
        Returns:
            List of {id, document, metadata, score}
        """
        # 查询分词
        tokenized_query = list(jieba.cut(query))
        
        # BM25 打分
        scores = self.bm25.get_scores(tokenized_query)
        
        # 获取 Top-K
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        # 格式化结果
        retrieved = []
        for idx in top_indices:
            if scores[idx] > 0:  # 过滤零分结果
                retrieved.append({
                    'id': self.ids[idx],
                    'document': self.documents[idx],
                    'metadata': self.metadatas[idx],
                    'score': float(scores[idx]),
                    'source': 'keyword'
                })
        
        return retrieved


class HybridRetriever:
    """混合检索器 - 融合向量检索和关键词检索"""
    
    def __init__(self, chroma_path: str = "./chroma_db", collection_name: str = "diabetes_guidelines_2024"):
        """
        初始化混合检索器
        
        Args:
            chroma_path: ChromaDB 存储路径
            collection_name: 集合名称
        """
        self.vector_retriever = VectorRetriever(chroma_path, collection_name)
        self.keyword_retriever = KeywordRetriever(chroma_path, collection_name)
    
    def reciprocal_rank_fusion(self, 
                                vector_results: List[Dict], 
                                keyword_results: List[Dict], 
                                k: int = 60) -> List[Dict]:
        """
        Reciprocal Rank Fusion (RRF) 算法融合结果
        
        公式: RRF_score(d) = Σ 1/(k + rank_i(d))
        
        Args:
            vector_results: 向量检索结果
            keyword_results: 关键词检索结果
            k: RRF 参数（默认60）
        
        Returns:
            融合后的结果列表
        """
        # 构建排名字典
        rrf_scores = {}
        
        # 向量检索排名
        for rank, item in enumerate(vector_results, start=1):
            doc_id = item['id']
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {
                    'score': 0,
                    'document': item['document'],
                    'metadata': item['metadata'],
                    'sources': []
                }
            rrf_scores[doc_id]['score'] += 1 / (k + rank)
            rrf_scores[doc_id]['sources'].append('vector')
        
        # 关键词检索排名
        for rank, item in enumerate(keyword_results, start=1):
            doc_id = item['id']
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {
                    'score': 0,
                    'document': item['document'],
                    'metadata': item['metadata'],
                    'sources': []
                }
            rrf_scores[doc_id]['score'] += 1 / (k + rank)
            rrf_scores[doc_id]['sources'].append('keyword')
        
        # 排序
        fused_results = [
            {
                'id': doc_id,
                'document': data['document'],
                'metadata': data['metadata'],
                'rrf_score': data['score'],
                'sources': data['sources']
            }
            for doc_id, data in rrf_scores.items()
        ]
        fused_results.sort(key=lambda x: x['rrf_score'], reverse=True)
        
        return fused_results
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        混合检索
        
        Args:
            query: 查询文本
            top_k: 初筛数量（每个检索器）
        
        Returns:
            融合后的检索结果
        """
        print(f"\n🔍 混合检索: {query}")
        
        # 并行检索
        print("  📊 向量检索中...")
        vector_results = self.vector_retriever.retrieve(query, top_k=top_k)
        
        print("  📝 关键词检索中...")
        keyword_results = self.keyword_retriever.retrieve(query, top_k=top_k)
        
        # RRF 融合
        print("  🔀 融合结果中...")
        fused_results = self.reciprocal_rank_fusion(vector_results, keyword_results)
        
        print(f"  ✅ 返回 {len(fused_results)} 条结果")
        return fused_results


# 测试代码
if __name__ == "__main__":
    # 初始化
    retriever = HybridRetriever()
    
    # 测试查询
    test_queries = [
        "eGFR小于30的患者不能使用哪些药物？",
        "糖尿病患者的运动建议是什么？",
        "SGLT2抑制剂的禁忌症有哪些？"
    ]
    
    for query in test_queries:
        results = retriever.retrieve(query, top_k=5)
        
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print(f"{'='*60}")
        
        for i, result in enumerate(results[:3], 1):
            print(f"\n[{i}] RRF分数: {result['rrf_score']:.4f}")
            print(f"来源: {', '.join(result['sources'])}")
            print(f"章节: {result['metadata'].get('header', 'N/A')}")
            print(f"内容: {result['document'][:150]}...")

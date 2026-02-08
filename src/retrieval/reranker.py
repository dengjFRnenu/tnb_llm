#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BGE Reranker - 精排模块
对初筛结果进行语义相关性精排
"""

from FlagEmbedding import FlagReranker
from typing import List, Dict


class BGEReranker:
    """BGE Reranker 精排器"""
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3", use_fp16: bool = True):
        """
        初始化 Reranker
        
        Args:
            model_name: 模型名称
            use_fp16: 是否使用 FP16 精度
        """
        print(f"🔧 加载 Reranker 模型: {model_name}...")
        self.reranker = FlagReranker(model_name, use_fp16=use_fp16)
        print("✅ Reranker 就绪")
    
    def rerank(self, query: str, documents: List[Dict], top_k: int = 3) -> List[Dict]:
        """
        对检索结果进行精排
        
        Args:
            query: 用户查询
            documents: 初筛文档列表 [{id, document, metadata, ...}]
            top_k: 返回前 K 个结果
        
        Returns:
            精排后的文档列表
        """
        if not documents:
            return []
        
        # 准备 query-document pairs
        pairs = [[query, doc['document']] for doc in documents]
        
        # 计算相关性分数
        scores = self.reranker.compute_score(pairs, normalize=True)
        
        # 处理不同的返回类型（单值、列表、numpy数组）
        import numpy as np
        if isinstance(scores, np.ndarray):
            scores = scores.tolist()
        elif not isinstance(scores, list):
            scores = [scores]
        
        # 确保scores是一维列表
        if isinstance(scores, list) and len(scores) > 0 and isinstance(scores[0], (list, np.ndarray)):
            # 如果是二维数组，取第一列或展平
            scores = [s[0] if hasattr(s, '__getitem__') else float(s) for s in scores]
        
        # 添加分数到文档
        for doc, score in zip(documents, scores):
            # 确保score是Python标量
            if hasattr(score, 'item'):
                doc['rerank_score'] = score.item()
            else:
                doc['rerank_score'] = float(score)
        
        # 排序并返回 Top-K
        reranked = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)
        return reranked[:top_k]
    
    def rerank_batch(self, queries: List[str], documents_list: List[List[Dict]], top_k: int = 3) -> List[List[Dict]]:
        """
        批量精排（性能优化）
        
        Args:
            queries: 查询列表
            documents_list: 每个查询对应的文档列表
            top_k: 每个查询返回前 K 个结果
        
        Returns:
            每个查询的精排结果
        """
        results = []
        for query, documents in zip(queries, documents_list):
            results.append(self.rerank(query, documents, top_k))
        return results


# 测试代码
if __name__ == "__main__":
    # 模拟初筛结果
    test_query = "eGFR小于30的患者不能使用哪些药物？"
    
    test_documents = [
        {
            'id': 'chunk_1',
            'document': '【章节】用药安全\neGFR < 30 mL/min/1.73m² 时应停用二甲双胍，因为可能导致乳酸酸中毒。',
            'metadata': {'header': '用药安全', 'page': 45},
            'rrf_score': 0.85
        },
        {
            'id': 'chunk_2',
            'document': '【章节】运动建议\n糖尿病患者应每周进行150分钟的中等强度有氧运动。',
            'metadata': {'header': '运动建议', 'page': 78},
            'rrf_score': 0.62
        },
        {
            'id': 'chunk_3',
            'document': '【章节】肾功能监测\n肾功能不全患者使用降糖药需谨慎，定期监测 eGFR 指标。',
            'metadata': {'header': '肾功能监测', 'page': 52},
            'rrf_score': 0.75
        },
        {
            'id': 'chunk_4',
            'document': '【章节】药物分类\nSGLT2抑制剂在 eGFR < 45 时需要减量，< 30 时禁用。',
            'metadata': {'header': '药物分类', 'page': 67},
            'rrf_score': 0.80
        }
    ]
    
    # 初始化 Reranker
    reranker = BGEReranker()
    
    # 精排
    print(f"\n{'='*60}")
    print(f"查询: {test_query}")
    print(f"{'='*60}")
    
    print(f"\n【初筛结果】（按 RRF 分数排序）")
    for i, doc in enumerate(test_documents, 1):
        print(f"{i}. [RRF: {doc['rrf_score']:.3f}] {doc['document'][:60]}...")
    
    # Rerank
    reranked_results = reranker.rerank(test_query, test_documents, top_k=3)
    
    print(f"\n【Rerank 精排后 Top-3】")
    for i, doc in enumerate(reranked_results, 1):
        print(f"\n{i}. [Rerank分数: {doc['rerank_score']:.4f}] [原RRF: {doc['rrf_score']:.3f}]")
        print(f"   章节: {doc['metadata']['header']} (P.{doc['metadata']['page']})")
        print(f"   内容: {doc['document'][:100]}...")

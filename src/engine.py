#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GraphRAG Retrieval Engine - 统一检索接口
整合混合检索、Reranker、Text-to-Cypher 和 Context Fusion
"""

import os
from pathlib import Path
from typing import Dict, Optional, Callable
import re

from .retrieval.hybrid import HybridRetriever
from .retrieval.reranker import BGEReranker
from .retrieval.fusion import ContextFusion
from .graph.text_to_cypher import TextToCypherEngine

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


class GraphRAGEngine:
    """GraphRAG 检索引擎 - 核心总控"""
    
    def __init__(self, 
                 chroma_path: str = None,
                 collection_name: str = "diabetes_guidelines_2024",
                 schema_path: str = None,
                 examples_path: str = None,
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j",
                 neo4j_password: str = "password123"):
        """
        初始化 GraphRAG 引擎
        
        Args:
            chroma_path: ChromaDB 路径
            collection_name: 集合名称
            schema_path: Schema 文件路径
            examples_path: Few-shot 示例路径
            neo4j_uri: Neo4j URI
            neo4j_user: Neo4j 用户名
            neo4j_password: Neo4j 密码
        """
        # 使用默认路径（相对于项目根目录）
        if chroma_path is None:
            chroma_path = str(PROJECT_ROOT / "chroma_db")
        if schema_path is None:
            schema_path = str(PROJECT_ROOT / "configs" / "schema.json")
        if examples_path is None:
            examples_path = str(PROJECT_ROOT / "configs" / "few_shot_examples.json")

        print("\n" + "="*60)
        print("🚀 初始化 GraphRAG 检索引擎")
        print("="*60 + "\n")
        
        # 初始化各模块
        self.hybrid_retriever = HybridRetriever(chroma_path, collection_name)
        self.reranker = BGEReranker()
        self.text_to_cypher = TextToCypherEngine(
            schema_path, 
            examples_path, 
            neo4j_uri, 
            neo4j_user, 
            neo4j_password
        )
        self.context_fusion = ContextFusion(kg_priority=True)
        
        print("\n✅ GraphRAG 引擎初始化完成!\n")
    
    def should_use_kg(self, query: str) -> bool:
        """
        判断查询是否需要使用知识图谱
        
        检测关键词如：禁忌、不能、eGFR、肾功能、心力衰竭等
        
        Args:
            query: 用户查询
        
        Returns:
            是否需要查询 KG
        """
        # 知识图谱相关关键词
        kg_keywords = [
            'eGFR', '肾功能', '禁忌', '不能', '禁用', '慎用',
            '心力衰竭', '肝功能', '孕妇', '妊娠',
            '分类', '属于', '类药物',
            '商品名', '通用名',
            '监测', '剂量', '调整'
        ]
        
        return any(keyword in query for keyword in kg_keywords)
    
    def retrieve(self, 
                 query: str, 
                 use_kg: Optional[bool] = None,
                 llm_api_function: Optional[Callable] = None,
                 hybrid_top_k: int = 10,
                 rerank_top_k: int = 3) -> Dict:
        """
        统一检索接口
        
        Args:
            query: 用户查询
            use_kg: 是否使用知识图谱（None=自动判断）
            llm_api_function: LLM API 函数（用于 Text-to-Cypher）
            hybrid_top_k: 混合检索初筛数量
            rerank_top_k: Rerank 精排数量
        
        Returns:
            {
                'query': str,
                'use_kg': bool,
                'rag_results': List[Dict],  # Reranked 文档
                'kg_results': List[Dict],   # Neo4j 查询结果
                'kg_cypher': str,           # 生成的 Cypher（如果有）
                'merged_context': str,      # 融合后的 Context
                'success': bool
            }
        """
        result = {
            'query': query,
            'use_kg': False,
            'rag_results': [],
            'kg_results': [],
            'kg_cypher': None,
            'merged_context': '',
            'success': False
        }
        
        print(f"\n{'='*60}")
        print(f"📝 用户查询: {query}")
        print(f"{'='*60}\n")
        
        # 1. 判断是否需要 KG
        if use_kg is None:
            use_kg = self.should_use_kg(query)
        result['use_kg'] = use_kg
        
        print(f"🎯 检索策略: {'RAG + KG (GraphRAG)' if use_kg else 'RAG Only'}\n")
        
        # 2. RAG 混合检索
        print("【步骤 1/4】混合检索（向量 + 关键词）")
        hybrid_results = self.hybrid_retriever.retrieve(query, top_k=hybrid_top_k)
        
        # 3. Rerank 精排
        print(f"\n【步骤 2/4】Rerank 精排 Top-{rerank_top_k}")
        reranked_results = self.reranker.rerank(query, hybrid_results, top_k=rerank_top_k)
        result['rag_results'] = reranked_results
        
        for i, doc in enumerate(reranked_results, 1):
            print(f"  {i}. [{doc['rerank_score']:.4f}] {doc['metadata'].get('header', 'N/A')} - P.{doc['metadata'].get('page', 'N/A')}")
        
        # 4. KG 查询（如果需要）
        kg_results = []
        if use_kg:
            print(f"\n【步骤 3/4】知识图谱查询 (Text-to-Cypher)")
            kg_response = self.text_to_cypher.query(query, llm_api_function)
            
            if kg_response['success']:
                kg_results = kg_response['results']
                result['kg_cypher'] = kg_response['cypher']
                result['kg_results'] = kg_results
                print(f"  ✅ 查询成功，返回 {len(kg_results)} 条结果")
                print(f"  Cypher: {kg_response['cypher'][:100]}...")
            else:
                print(f"  ⚠️  KG 查询失败: {kg_response.get('error', 'Unknown')}")
        else:
            print(f"\n【步骤 3/4】跳过知识图谱查询")
        
        # 5. Context 融合
        print(f"\n【步骤 4/4】Context 融合")
        merged_context = self.context_fusion.merge(
            rag_results=reranked_results,
            kg_results=kg_results,
            user_question=query
        )
        result['merged_context'] = merged_context
        result['success'] = True
        
        print("  ✅ Context 融合完成\n")
        
        return result
    
    def format_summary(self, result: Dict) -> str:
        """
        格式化检索结果摘要（用于打印或日志）
        
        Args:
            result: retrieve() 返回的结果
        
        Returns:
            格式化的摘要文本
        """
        summary = []
        summary.append(f"{'='*60}")
        summary.append(f"检索摘要")
        summary.append(f"{'='*60}")
        summary.append(f"查询: {result['query']}")
        summary.append(f"策略: {'GraphRAG (RAG + KG)' if result['use_kg'] else 'RAG Only'}")
        summary.append(f"RAG 结果: {len(result['rag_results'])} 篇文档")
        summary.append(f"KG 结果: {len(result['kg_results'])} 条记录")
        
        if result['kg_cypher']:
            summary.append(f"\nCypher 查询:\n{result['kg_cypher']}")
        
        summary.append(f"\n最终 Context:\n{result['merged_context'][:500]}...")
        summary.append(f"{'='*60}")
        
        return '\n'.join(summary)


# 测试代码
if __name__ == "__main__":
    # 初始化引擎
    engine = GraphRAGEngine()
    
    # 测试查询
    test_queries = [
        # 需要 KG 的查询
        ("eGFR小于30的患者不能使用哪些药物？", None),
        ("有哪些SGLT2抑制剂？", None),
        
        # 纯 RAG 查询
        ("糖尿病患者的运动建议是什么？", False),
        ("糖尿病的诊断标准是什么？", False),
    ]
    
    for query, use_kg in test_queries:
        result = engine.retrieve(query, use_kg=use_kg)
        
        # 打印摘要
        print(engine.format_summary(result))
        print("\n" + "="*60 + "\n")
        
        # 在实际应用中，这里会将 merged_context 喂给 LLM
        # llm_response = call_llm(result['merged_context'])

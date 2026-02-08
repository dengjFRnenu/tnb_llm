#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Fusion - 数据融合模块
将 RAG 检索结果和 KG 查询结果融合为统一的 Context
"""

from typing import List, Dict, Optional


class ContextFusion:
    """Context 融合器 - 合并 RAG 和 KG 的检索结果"""
    
    def __init__(self, kg_priority: bool = True):
        """
        初始化融合器
        
        Args:
            kg_priority: 知识图谱是否优先（True 表示 KG > RAG）
        """
        self.kg_priority = kg_priority
    
    def format_rag_context(self, rag_results: List[Dict]) -> str:
        """
        格式化 RAG 检索结果
        
        Args:
            rag_results: Reranked 文档列表
        
        Returns:
            格式化文本
        """
        if not rag_results:
            return "（未检索到相关指南内容）"
        
        formatted = []
        for i, doc in enumerate(rag_results, 1):
            header = doc.get('metadata', {}).get('header', '未知章节')
            page = doc.get('metadata', {}).get('page', 'N/A')
            content = doc.get('document', '').replace('【章节】', '').strip()
            
            # 截断过长内容
            if len(content) > 300:
                content = content[:300] + "..."
            
            formatted.append(f"{i}. 【{header} - P.{page}】\n   {content}")
        
        return '\n\n'.join(formatted)
    
    def format_kg_context(self, kg_results: List[Dict], question: str = "") -> str:
        """
        格式化知识图谱查询结果
        
        Args:
            kg_results: Neo4j 查询结果
            question: 用户问题（用于生成更自然的描述）
        
        Returns:
            格式化文本
        """
        if not kg_results:
            return "（知识图谱中未查询到相关硬性规则）"
        
        formatted = []
        for i, record in enumerate(kg_results, 1):
            items = [f"{key}: {value}" for key, value in record.items()]
            formatted.append(f"{i}. {' | '.join(items)}")
        
        return '\n'.join(formatted)
    
    def merge(self, 
              rag_results: Optional[List[Dict]] = None, 
              kg_results: Optional[List[Dict]] = None,
              user_question: str = "") -> str:
        """
        融合 RAG 和 KG 结果
        
        Args:
            rag_results: RAG 检索结果（Reranked）
            kg_results: 知识图谱查询结果
            user_question: 用户问题
        
        Returns:
            融合后的 Context 文本
        """
        context_parts = []
        
        # 优先级排序
        if self.kg_priority:
            # KG 优先
            if kg_results:
                kg_context = self.format_kg_context(kg_results, user_question)
                context_parts.append(f"【临床硬性规则】（来自知识图谱）\n{kg_context}")
            
            if rag_results:
                rag_context = self.format_rag_context(rag_results)
                context_parts.append(f"【指南参考知识】（来自《中国糖尿病防治指南2024》）\n{rag_context}")
        else:
            # RAG 优先
            if rag_results:
                rag_context = self.format_rag_context(rag_results)
                context_parts.append(f"【指南参考知识】（来自《中国糖尿病防治指南2024》）\n{rag_context}")
            
            if kg_results:
                kg_context = self.format_kg_context(kg_results, user_question)
                context_parts.append(f"【临床硬性规则】（来自知识图谱）\n{kg_context}")
        
        # 拼接
        if not context_parts:
            return "（未检索到相关信息）"
        
        merged_context = '\n\n' + ('\n\n' + '='*60 + '\n\n').join(context_parts)
        
        # 添加用户问题作为开头
        if user_question:
            merged_context = f"【用户问题】\n{user_question}\n{merged_context}"
        
        return merged_context
    
    def detect_conflict(self, rag_results: List[Dict], kg_results: List[Dict]) -> Dict:
        """
        检测 RAG 和 KG 结果是否冲突
        
        Args:
            rag_results: RAG 结果
            kg_results: KG 结果
        
        Returns:
            {
                'has_conflict': bool,
                'description': str
            }
        """
        # 简化实现：实际应用中可以使用 NLP 技术检测语义冲突
        # 这里仅作为接口示例
        return {
            'has_conflict': False,
            'description': '未实现冲突检测逻辑'
        }


# 测试代码
if __name__ == "__main__":
    # 初始化融合器
    fusion = ContextFusion(kg_priority=True)
    
    # 模拟 RAG 结果
    rag_results = [
        {
            'document': '【章节】用药安全\neGFR < 30 mL/min/1.73m² 时应停用二甲双胍，因为可能导致乳酸酸中毒。患者应改用胰岛素治疗。',
            'metadata': {'header': '用药安全', 'page': 45},
            'rerank_score': 0.92
        },
        {
            'document': '【章节】肾功能监测\n使用二甲双胍的患者应每3-6个月监测肾功能，尤其是老年患者和合并慢性肾病者。',
            'metadata': {'header': '肾功能监测', 'page': 52},
            'rerank_score': 0.85
        }
    ]
    
    # 模拟 KG 结果
    kg_results = [
        {'药品名称': '二甲双胍', '严重程度': '绝对禁忌'},
        {'药品名称': '达格列净', '严重程度': '绝对禁忌'}
    ]
    
    # 测试问题
    user_question = "eGFR小于30的患者不能使用哪些药物？"
    
    # 融合
    merged_context = fusion.merge(
        rag_results=rag_results,
        kg_results=kg_results,
        user_question=user_question
    )
    
    print(f"\n{'='*60}")
    print("Context Fusion 测试")
    print(f"{'='*60}")
    print(merged_context)
    print(f"\n{'='*60}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量级 Demo - 仅测试 Text-to-Cypher，无需下载大模型
"""

from text_to_cypher import TextToCypherEngine
from context_fusion import ContextFusion

def main():
    print("\n" + "="*60)
    print("  GraphRAG 核心功能演示（Text-to-Cypher）")
    print("  无需下载模型，直接测试知识图谱查询")
    print("="*60 + "\n")
    
    # 初始化
    print("🔧 初始化 Text-to-Cypher 引擎...")
    t2c = TextToCypherEngine(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password123"
    )
    
    print("🔧 初始化 Context 融合器...")
    fusion = ContextFusion(kg_priority=True)
    
    print("\n✅ 初始化完成!\n")
    
    # 测试查询
    test_cases = [
        {
            "query": "eGFR小于30的患者不能使用哪些药物？",
            "description": "指标禁忌查询"
        },
        {
            "query": "有哪些SGLT2抑制剂？",
            "description": "药物分类查询"
        },
        {
            "query": "心力衰竭患者禁用哪些降糖药？",
            "description": "疾病禁忌查询"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print("\n" + "="*60)
        print(f"测试 {i}: {case['description']}")
        print("="*60)
        print(f"问题: {case['query']}\n")
        
        # Step 1: Text-to-Cypher
        print("【步骤 1】生成 Cypher 查询")
        print("-" * 60)
        
        result = t2c.query(case['query'])
        
        if result['success']:
            print(f"✅ Cypher 生成成功:")
            print(f"```cypher\n{result['cypher']}\n```\n")
            
            # Step 2: 执行查询
            if result['neo4j_results']:
                print("【步骤 2】Neo4j 查询结果")
                print("-" * 60)
                print(f"✅ 找到 {len(result['neo4j_results'])} 条结果:")
                for j, record in enumerate(result['neo4j_results'][:5], 1):
                    print(f"  {j}. {record}")
                if len(result['neo4j_results']) > 5:
                    print(f"  ... 还有 {len(result['neo4j_results']) - 5} 条结果")
                print()
                
                # Step 3: Context 融合
                print("【步骤 3】Context 融合")
                print("-" * 60)
                
                # 模拟 RAG 结果
                mock_rag = [
                    {"document": f"《指南2024》: 关于{case['description']}的说明..."}
                ]
                
                merged_context = fusion.merge(
                    rag_results=mock_rag,
                    kg_results=result['neo4j_results']
                )
                
                print(merged_context)
            else:
                print("⚠️  Neo4j 未返回结果（可能数据库未连接或无匹配数据）")
                print(f"   生成的 Cypher: {result['cypher']}")
        else:
            print(f"❌ Cypher 生成失败: {result.get('error', '未知错误')}")
        
        print()
    
    print("\n" + "="*60)
    print("演示完成！")
    print("="*60)
    print("\n💡 提示:")
    print("  - 这个演示跳过了向量检索和 Reranker（需要下载大模型）")
    print("  - 直接展示了 Text-to-Cypher 的核心能力")
    print("  - 如需完整功能，请等待 demo_retrieval.py 中的模型下载完成")
    print()

if __name__ == "__main__":
    main()

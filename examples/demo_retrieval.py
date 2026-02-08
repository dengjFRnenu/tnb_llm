#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GraphRAG 系统交互式 Demo
演示混合检索、Rerank 和 Text-to-Cypher 的完整流程
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.engine import GraphRAGEngine


def print_header(text):
    """打印标题"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def print_section(title):
    """打印小节标题"""
    print(f"\n{'─'*70}")
    print(f"📌 {title}")
    print(f"{'─'*70}\n")


def display_results(result: dict):
    """
    展示检索结果
    
    Args:
        result: GraphRAGEngine.retrieve() 返回的结果
    """
    # 基本信息
    print_section("检索策略")
    strategy = "GraphRAG (混合检索 + 知识图谱)" if result['use_kg'] else "RAG Only (仅混合检索)"
    print(f"  💡 {strategy}\n")
    
    # RAG 结果
    print_section("RAG 检索结果（Rerank 精排后）")
    if result['rag_results']:
        for i, doc in enumerate(result['rag_results'], 1):
            print(f"  {i}. 【相关度: {doc['rerank_score']:.4f}】")
            print(f"     章节: {doc['metadata'].get('header', 'N/A')}")
            print(f"     页码: P.{doc['metadata'].get('page', 'N/A')}")
            print(f"     来源: {', '.join(doc.get('sources', ['unknown']))}")
            content = doc['document'].replace('【章节】', '').strip()
            print(f"     内容: {content[:120]}...\n")
    else:
        print("  （无）\n")
    
    # KG 结果
    if result['use_kg']:
        print_section("知识图谱查询结果")
        
        if result['kg_cypher']:
            print(f"  【生成的 Cypher 查询】\n")
            for line in result['kg_cypher'].split('\n'):
                print(f"    {line}")
            print()
        
        if result['kg_results']:
            print(f"  【查询结果】（共 {len(result['kg_results'])} 条）\n")
            for i, record in enumerate(result['kg_results'], 1):
                items = [f"{k}: {v}" for k, v in record.items()]
                print(f"    {i}. {' | '.join(items)}")
            print()
        else:
            print("  （未查询到结果）\n")
    
    # 最终融合 Context
    print_section("最终融合 Context（将喂给 LLM）")
    print(result['merged_context'])
    print()


def interactive_mode(engine: GraphRAGEngine):
    """交互式查询模式"""
    print_header("GraphRAG 交互式 Demo")
    print("💬 输入您的问题，系统将展示完整的检索流程")
    print("💡 输入 'exit' 或 'quit' 退出\n")
    
    while True:
        try:
            # 获取用户输入
            query = input("\n👤 您的问题: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', '退出']:
                print("\n👋 再见！")
                break
            
            # 执行检索
            result = engine.retrieve(query)
            
            # 展示结果
            display_results(result)
            
            # 提示下一步
            print(f"{'─'*70}")
            print("💡 在实际应用中，上述 Context 会喂给 LLM 生成最终回答")
            print(f"{'─'*70}")
        
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()


def batch_test_mode(engine: GraphRAGEngine):
    """批量测试模式"""
    print_header("GraphRAG 批量测试 Demo")
    
    test_cases = [
        {
            'query': 'eGFR小于30的患者不能使用哪些药物？',
            'description': '知识图谱查询（指标禁忌）'
        },
        {
            'query': '有哪些SGLT2抑制剂？',
            'description': '知识图谱查询（药物分类）'
        },
        {
            'query': '二甲双胍有哪些禁忌症和注意事项？',
            'description': '知识图谱查询（复杂多跳）'
        },
        {
            'query': '糖尿病患者的运动建议是什么？',
            'description': 'RAG 查询（指南内容）'
        },
        {
            'query': '糖尿病的诊断标准是什么？',
            'description': 'RAG 查询（医学知识）'
        }
    ]
    
    print(f"📋 测试用例: {len(test_cases)} 个\n")
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'#'*70}")
        print(f"# 测试 {i}/{len(test_cases)}: {case['description']}")
        print(f"{'#'*70}")
        
        result = engine.retrieve(case['query'])
        display_results(result)
        
        # 按任意键继续
        if i < len(test_cases):
            input("\n⏎ 按回车键继续下一个测试...")


def main():
    """主函数"""
    try:
        # 初始化引擎
        print("\n🚀 正在初始化 GraphRAG 引擎...")
        engine = GraphRAGEngine()
        
        # 选择模式
        print("\n请选择运行模式:")
        print("  1. 交互式查询（推荐）")
        print("  2. 批量测试")
        
        choice = input("\n请输入选项 [1/2]: ").strip()
        
        if choice == '2':
            batch_test_mode(engine)
        else:
            interactive_mode(engine)
    
    except KeyboardInterrupt:
        print("\n\n👋 程序已终止")
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

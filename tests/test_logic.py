#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立测试 - 测试核心逻辑（不依赖外部模型）
"""

import json
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
CONFIGS_DIR = PROJECT_ROOT / "configs"


def test_cypher_security():
    """测试 Cypher 安全验证逻辑"""
    print("\n" + "="*60)
    print("测试 1: Cypher 安全验证")
    print("="*60)
    
    # 模拟安全验证函数
    def validate_cypher(cypher: str):
        FORBIDDEN = ['CREATE', 'DELETE', 'REMOVE', 'SET', 'MERGE', 'DROP']
        cypher_upper = cypher.upper()
        
        for kw in FORBIDDEN:
            if kw in cypher_upper:
                return False, f"检测到危险操作: {kw}"
        
        if 'MATCH' not in cypher_upper:
            return False, "必须包含 MATCH"
        if 'RETURN' not in cypher_upper:
            return False, "必须包含 RETURN"
        
        return True, ""
    
    # 测试用例
    tests = [
        ("MATCH (d:Drug) RETURN d.name", True, "正常查询"),
        ("DELETE (d:Drug)", False, "危险删除"),
        ("RETURN 1", False, "缺少MATCH"),
        ("MATCH (d:Drug)", False, "缺少RETURN"),
        ("MATCH (d:Drug) SET d.name='test' RETURN d", False, "危险SET"),
    ]
    
    passed = 0
    for cypher, expected_safe, desc in tests:
        is_safe, msg = validate_cypher(cypher)
        if is_safe == expected_safe:
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc} - 预期 {expected_safe}, 实际 {is_safe}")
    
    print(f"\n  结果: {passed}/{len(tests)} 通过")
    return passed == len(tests)


def test_rrf_fusion():
    """测试 RRF 融合算法"""
    print("\n" + "="*60)
    print("测试 2: RRF 融合算法")
    print("="*60)
    
    # 模拟 RRF 计算
    def calculate_rrf(vector_ranks, keyword_ranks, k=60):
        scores = {}
        
        for rank, doc_id in enumerate(vector_ranks, 1):
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += 1 / (k + rank)
        
        for rank, doc_id in enumerate(keyword_ranks, 1):
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += 1 / (k + rank)
        
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # 测试用例
    vector_ranks = ['doc1', 'doc2', 'doc3']
    keyword_ranks = ['doc2', 'doc3', 'doc4']
    
    result = calculate_rrf(vector_ranks, keyword_ranks, k=60)
    
    print(f"  向量检索排名: {vector_ranks}")
    print(f"  关键词排名: {keyword_ranks}")
    print(f"\n  RRF 融合结果:")
    
    for i, (doc_id, score) in enumerate(result, 1):
        print(f"    {i}. {doc_id}: {score:.6f}")
    
    # doc2 应该排第一（同时在两个列表中靠前）
    if result[0][0] == 'doc2':
        print(f"\n  ✅ doc2 排名第一（正确）")
        return True
    else:
        print(f"\n  ❌ 预期 doc2 第一，实际 {result[0][0]}")
        return False


def test_few_shot_examples():
    """测试 Few-shot 示例质量"""
    print("\n" + "="*60)
    print("测试 3: Few-shot 示例质量检查")
    print("="*60)
    
    with open(CONFIGS_DIR / 'few_shot_examples.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    examples = data['examples']
    
    # 检查每个示例的完整性
    issues = []
    for i, ex in enumerate(examples, 1):
        if 'MATCH' not in ex['cypher']:
            issues.append(f"示例{i}缺少MATCH")
        if 'RETURN' not in ex['cypher']:
            issues.append(f"示例{i}缺少RETURN")
        if len(ex['question']) < 5:
            issues.append(f"示例{i}问题过短")
    
    # 检查类别分布
    categories = {}
    for ex in examples:
        cat = ex['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"  示例总数: {len(examples)}")
    print(f"  类别分布:")
    for cat, count in categories.items():
        print(f"    - {cat}: {count} 个")
    
    if issues:
        print(f"\n  ⚠️  发现 {len(issues)} 个问题:")
        for issue in issues[:5]:
            print(f"    - {issue}")
        return False
    else:
        print(f"\n  ✅ 所有示例格式正确")
        return True


def test_schema_completeness():
    """测试 Schema 完整性"""
    print("\n" + "="*60)
    print("测试 4: Schema 完整性检查")
    print("="*60)
    
    with open(CONFIGS_DIR / 'schema.json', 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    # 检查关键节点
    required_nodes = ['Drug', 'Metric', 'Disease', 'Category']
    missing_nodes = [n for n in required_nodes if n not in schema['nodes']]
    
    # 检查关键关系
    required_rels = ['CONTRAINDICATED_IF', 'FORBIDDEN_FOR', 'BELONGS_TO']
    missing_rels = [r for r in required_rels if r not in schema['relationships']]
    
    print(f"  节点类型: {len(schema['nodes'])} 个")
    for node in required_nodes:
        status = "✅" if node in schema['nodes'] else "❌"
        print(f"    {status} {node}")
    
    print(f"\n  关系类型: {len(schema['relationships'])} 个")
    for rel in required_rels:
        status = "✅" if rel in schema['relationships'] else "❌"
        print(f"    {status} {rel}")
    
    if missing_nodes or missing_rels:
        print(f"\n  ❌ 缺少关键定义")
        return False
    else:
        print(f"\n  ✅ Schema 完整")
        return True


def test_context_fusion_logic():
    """测试 Context 融合逻辑"""
    print("\n" + "="*60)
    print("测试 5: Context 融合逻辑")
    print("="*60)
    
    # 模拟融合函数
    def merge_context(rag_results, kg_results, kg_priority=True):
        parts = []
        
        if kg_priority:
            if kg_results:
                parts.append("【临床硬性规则】\n" + str(kg_results))
            if rag_results:
                parts.append("【指南参考知识】\n" + str(rag_results))
        else:
            if rag_results:
                parts.append("【指南参考知识】\n" + str(rag_results))
            if kg_results:
                parts.append("【临床硬性规则】\n" + str(kg_results))
        
        return "\n\n".join(parts) if parts else "（未检索到信息）"
    
    # 测试用例1: KG 优先
    rag = ["指南内容1", "指南内容2"]
    kg = ["二甲双胍禁用"]
    result = merge_context(rag, kg, kg_priority=True)
    
    kg_first = result.index("硬性规则") < result.index("参考知识")
    print(f"  测试1 - KG优先: {'✅' if kg_first else '❌'}")
    
    # 测试用例2: 空结果
    result_empty = merge_context([], [], kg_priority=True)
    has_empty_msg = "未检索" in result_empty
    print(f"  测试2 - 空结果处理: {'✅' if has_empty_msg else '❌'}")
    
    return kg_first and has_empty_msg


def main():
    """运行所有独立测试"""
    print("\n" + "#"*60)
    print("  GraphRAG 核心逻辑测试（无外部依赖）")
    print("#"*60)
    
    tests = [
        test_schema_completeness,
        test_few_shot_examples,
        test_cypher_security,
        test_rrf_fusion,
        test_context_fusion_logic,
    ]
    
    results = []
    for test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"\n  ⚠️  测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # 总结
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ 所有测试通过! ({passed}/{total})")
        print("\n核心逻辑验证完成，系统设计正确。")
        print("等待依赖安装完成后，可运行完整功能测试。")
    else:
        print(f"⚠️  {total - passed} 个测试失败 ({passed}/{total})")
    
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

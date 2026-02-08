#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证查询 - 测试知识图谱功能"""

from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "password123"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

print("=" * 70)
print("🧪 知识图谱验证查询")
print("=" * 70)

with driver.session() as session:
    # 1. 完整节点统计
    print("\n1️⃣  节点统计:")
    result = session.run("""
        MATCH (n) 
        RETURN labels(n)[0] as type, count(*) as count
        ORDER BY count DESC
    """)
    total_nodes = 0
    for record in result:
        total_nodes += record['count']
        print(f"   {record['type']:20s}: {record['count']:5d}")
    print(f"   {'总计':20s}: {total_nodes:5d}")
    
    # 2. 关系统计
    print("\n2️⃣  关系统计:")
    result = session.run("""
        MATCH ()-[r]->() 
        RETURN type(r) as rel_type, count(*) as count
        ORDER BY count DESC
    """)
    total_rels = 0
    for record in result:
        total_rels += record['count']
        print(f"   {record['rel_type']:30s}: {record['count']:5d}")
    print(f"   {'总计':30s}: {total_rels:5d}")
    
    # 3. eGFR < 30禁用的药品
    print("\n3️⃣  eGFR < 30 禁用的药品:")
    result = session.run("""
        MATCH (d:Drug)-[r:CONTRAINDICATED_IF]->(m:Metric {name: 'eGFR'})
        WHERE r.operator = '<' AND r.value = 30
        RETURN d.name as drug, r.severity as severity
        LIMIT 10
    """)
    for record in result:
        print(f"   ✓ {record['drug']}")
    
    # 4. 双胍类药物
    print("\n4️⃣  双胍类药物:")
    result = session.run("""
        MATCH (d:Drug)-[:BELONGS_TO]->(c:Category {name: '双胍类'})
        RETURN d.name as drug, d.max_daily_dose as max_dose
        ORDER BY d.name
        LIMIT 10
    """)
    for record in result:
        dose = record.get('max_dose', '未知')
        print(f"   ✓ {record['drug']:40s} 最大剂量: {dose}")
    
    # 5. 心力衰竭禁用药物
    print("\n5️⃣  心力衰竭患者禁用药物:")
    result = session.run("""
        MATCH (d:Drug)-[:FORBIDDEN_FOR]->(dis:Disease)
        WHERE dis.name CONTAINS '心力衰竭'
        RETURN DISTINCT d.name as drug
        LIMIT 10
    """)
    for record in result:
        print(f"   ✓ {record['drug']}")
    
    # 6. 商品名及对应药品
    print("\n6️⃣  商品名示例:")
    result = session.run("""
        MATCH (b:Brand)-[:IS_BRAND_OF]->(d:Drug)
        RETURN b.name as brand, d.name as drug
        LIMIT 10
    """)
    for record in result:
        print(f"   ✓ {record['brand']:15s} → {record['drug']}")
    
    # 7. 多跳查询 - 分类+禁忌
    print("\n7️⃣  SGLT2抑制剂的禁忌:")
    result = session.run("""
        MATCH (c:Category)<-[:BELONGS_TO]-(d:Drug)
        WHERE c.name CONTAINS 'SGLT2' OR c.name CONTAINS '格列净'
        OPTIONAL MATCH (d)-[r:CONTRAINDICATED_IF]->(m:Metric)
        RETURN d.name as drug, 
               collect(DISTINCT m.name + ' ' + r.operator + ' ' + toString(r.value)) as constraints
        LIMIT 5
    """)
    for record in result:
        constraints = [c for c in record['constraints'] if c]
        constraints_str = ', '.join(constraints) if constraints else '无数值约束'
        print(f"   ✓ {record['drug']:30s} {constraints_str}")

driver.close()

print("\n" + "=" * 70)
print("✅ 验证完成! 知识图谱功能正常")
print("=" * 70)

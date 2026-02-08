#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""智能导入 - 按行处理Cypher语句"""

from neo4j import GraphDatabase
import time
import re

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "password123"

print("=" * 60)
print("🔧 智能导入脚本  (按行处理)")
print("=" * 60)

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# 读取并处理Cypher文件
statements = []
with open("import_graph.cypher", 'r', encoding='utf-8') as f:
    buffer = ""
    for line in f:
        line = line.strip()
        
        # 跳过注释行和空行
        if not line or line.startswith('//'):
            continue
        
        # 跳过约束和索引
        if line.startswith('CREATE CONSTRAINT') or line.startswith('CREATE INDEX'):
            continue
        
        # 累积到buffer
        buffer += " " + line
        
        # 如果行末有分号,说明语句结束
        if line.endswith(';'):
            stmt = buffer.strip().rstrip(';').strip()
            if stmt:
                statements.append(stmt)
            buffer = ""

# 处理最后一个没有分号的语句
if buffer.strip():
    statements.append(buffer.strip())

print(f"📊 总语句数: {len(statements)}")

# 统计Drug MERGE
drug_merges = [s for s in statements if s.startswith('MERGE (d') and ':Drug' in s]
print(f"   其中Drug节点: {len(drug_merges)}")

print("\n🚀 开始导入...\n")

start_time = time.time()
success = 0
errors = []

with driver.session() as session:
    for i, stmt in enumerate(statements):
        try:
            session.run(stmt)
            success += 1
            if (i + 1) % 100 == 0:
                print(f"   ✓ 进度: [{i+1}/{len(statements)}] {(i+1)/len(statements)*100:.1f}%")
        except Exception as e:
            errors.append((i+1, stmt[:100], str(e)[:100]))
            if len(errors) <= 3:
                print(f"   ⚠️  错误 {i+1}: {str(e)[:80]}")

elapsed = time.time() - start_time

print(f"\n✅ 导入完成!")
print(f"   成功: {success}")
print(f"   失败: {len(errors)}")
print(f"   耗时: {elapsed:.2f}秒")

# 统计
print("\n" + "=" * 60)
print("📊 图谱统计")
print("=" * 60)

with driver.session() as session:
    # 节点统计
    result = session.run("MATCH (n) RETURN labels(n)[0] as type, count(*) as count ORDER BY count DESC")
    print("\n节点:")
    total_nodes = 0
    for record in result:
        count = record['count']
        total_nodes += count
        print(f"   {record['type']:20s}: {count:5d}")
    print(f"   {'总计':20s}: {total_nodes:5d}")
    
    # 关系统计
    result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(*) as count ORDER BY count DESC")
    print("\n关系:")
    total_rels = 0
    for record in result:
        count = record['count']
        total_rels += count
        print(f"   {record['type']:30s}: {count:5d}")
    print(f"   {'总计':30s}: {total_rels:5d}")

driver.close()

if errors:
    print("\n⚠️  导入错误 (前5个):")
    for idx, stmt, err in errors[:5]:
        print(f"   {idx}. {stmt}... => {err}")

print("\n" + "=" * 60)
print("🎉 导入成功!")
print("=" * 60)
print("\n💡 访问Neo4j Browser: http://localhost:7474")
print("   用户名: neo4j")
print("   密码: password123")

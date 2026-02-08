#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""容错导入 - 逐条执行,跳过约束,处理错误"""

from neo4j import GraphDatabase
import time

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "password123"

print("=" * 60)
print("🔧 容错导入脚本")
print("=" * 60)

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# 读取Cypher文件
with open("import_graph.cypher", 'r', encoding='utf-8') as f:
    content = f.read()

# 分割语句,跳过约束创建
statements = []
for stmt in content.split(';'):
    stmt = stmt.strip()
    if stmt and not stmt.startswith('//'):
        # 跳过约束创建
        if 'CREATE CONSTRAINT' not in stmt and 'CREATE INDEX' not in stmt:
            statements.append(stmt)

print(f"📊 总语句数: {len(statements)}")
print("\n🚀 开始导入...\n")

start_time = time.time()
success = 0
skipped = 0

with driver.session() as session:
    for i, stmt in enumerate(statements):
        try:
            session.run(stmt)
            success += 1
            if (i + 1) % 100 == 0:
                print(f"   ✓ 进度: [{i+1}/{len(statements)}] {(i+1)/len(statements)*100:.1f}%")
        except Exception as e:
            skipped += 1
            error_msg = str(e)
            # 只显示前3个错误
            if skipped <= 3:
                print(f"   ⚠️  跳过语句 {i+1}: {error_msg[:80]}")

elapsed = time.time() - start_time

print(f"\n✅ 导入完成!")
print(f"   成功: {success}")
print(f"   跳过: {skipped}")
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

print("\n" + "=" * 60)
print("🎉 导入成功!")
print("=" * 60)
print("\n💡 访问Neo4j Browser: http://localhost:7474")
print("   用户名: neo4j")
print("   密码: password123")

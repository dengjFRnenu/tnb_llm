#!/bin/bash
# 完整导入脚本 - 不使用唯一性约束,允许重复

echo "清空数据库..."
cypher-shell -u neo4j -p password123 "MATCH (n) DETACH DELETE n"

echo "删除所有约束..."
cypher-shell -u neo4j -p password123 "SHOW CONSTRAINTS" | grep -v "^#" | grep -v "^name" | awk '{print $1}' | while read constraint; do
    if [ ! -z "$constraint" ]; then
        cypher-shell -u neo4j -p password123 "DROP CONSTRAINT $constraint IF EXISTS" 2>/dev/null
    fi
done

echo "导入数据(跳过约束创建)..."
# 跳过约束创建,直接导入数据
cat import_graph.cypher | grep -v "CREATE CONSTRAINT" | grep -v "CREATE INDEX" | cypher-shell -u neo4j -p password123

echo "检查导入结果..."
echo "节点统计:"
cypher-shell -u neo4j -p password123 "MATCH (n) RETURN labels(n)[0] as type, count(*) as count ORDER BY count DESC"

echo ""
echo "关系统计:"
cypher-shell -u neo4j -p password123 "MATCH ()-[r]->() RETURN type(r) as type, count(*) as count ORDER BY count DESC"

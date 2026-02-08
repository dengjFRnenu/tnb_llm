#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速导入脚本 - 首次使用,自动设置初始密码

功能:
1. 首次连接使用默认密码'neo4j'
2. 自动修改密码为'password123'
3. 导入图谱数据
"""

import sys
import time
from pathlib import Path

try:
    from neo4j import GraphDatabase
except ImportError:
    print("❌ 未安装neo4j驱动")
    print("请运行: pip install neo4j")
    sys.exit(1)


def first_time_setup(uri, initial_password="neo4j", new_password="password123"):
    """首次设置,修改默认密码"""
    print("🔧 首次设置: 修改默认密码...")
    try:
        driver = GraphDatabase.driver(uri, auth=("neo4j", initial_password))
        with driver.session() as session:
            session.run(f"ALTER CURRENT USER SET PASSWORD FROM '{initial_password}' TO '{new_password}'")
        driver.close()
        print(f"✅ 密码已修改为: {new_password}")
        return True
    except Exception as e:
        # 如果失败,可能已经修改过密码
        print(f"⚠️  密码修改失败(可能已经修改过): {e}")
        return False


def import_data(uri, user, password, cypher_file):
    """导入数据"""
    print(f"\n🔌 连接Neo4j: {uri}")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        driver.verify_connectivity()
        print("✅ 连接成功!")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False
    
    # 读取Cypher文件
    print(f"\n📖 读取: {cypher_file}")
    with open(cypher_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    statements = [s.strip() for s in content.split(';') if s.strip() and not s.strip().startswith('//')]
    print(f"📊 语句数: {len(statements)}")
    
    # 执行导入
    print("\n🚀 开始导入...")
    start_time = time.time()
    
    with driver.session() as session:
        success = 0
        error = 0
        
        for i, stmt in enumerate(statements):
            if stmt.startswith('//'):
                continue
            
            try:
                session.run(stmt)
                success += 1
                if (i + 1) % 100 == 0:
                    print(f"   进度: [{i+1}/{len(statements)}] {(i+1)/len(statements)*100:.1f}%")
            except Exception as e:
                error += 1
                if error <= 3:
                    print(f"   ⚠️ 错误: {str(e)[:80]}")
        
        print(f"\n✅ 导入完成!")
        print(f"   成功: {success}, 失败: {error}")
        print(f"   耗时: {time.time() - start_time:.2f}秒")
    
    # 获取统计
    print("\n📊 图谱统计:")
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN labels(n)[0] as type, count(*) as count ORDER BY count DESC")
        for record in result:
            print(f"   {record['type']:20s}: {record['count']:5d}")
    
    driver.close()
    return True


def main():
    URI = "bolt://localhost:7687"
    USER = "neo4j"
    NEW_PASSWORD = "password123"
    CYPHER_FILE = "import_graph.cypher"
    
    print("=" * 60)
    print("🏥 糖尿病药品知识图谱 - 快速导入")
    print("=" * 60)
    
    # 检查文件
    if not Path(CYPHER_FILE).exists():
        print(f"❌ 找不到: {CYPHER_FILE}")
        return
    
    # 尝试首次设置
    first_time_setup(URI, new_password=NEW_PASSWORD)
    
    # 导入数据
    if import_data(URI, USER, NEW_PASSWORD, CYPHER_FILE):
        print("\n" + "=" * 60)
        print("🎉 知识图谱导入成功!")
        print("=" * 60)
        print(f"\n💡 访问Neo4j Browser: http://localhost:7474")
        print(f"   用户名: {USER}")
        print(f"   密码: {NEW_PASSWORD}")


if __name__ == "__main__":
    main()

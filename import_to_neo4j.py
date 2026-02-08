#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j导入工具 - 执行Cypher脚本导入图谱数据

功能:
1. 连接Neo4j数据库
2. 执行import_graph.cypher脚本
3. 验证导入结果
4. 生成统计报告
"""

import sys
import time
from pathlib import Path

try:
    from neo4j import GraphDatabase
except ImportError:
    print("❌ 错误: 未安装neo4j驱动")
    print("请运行: pip install neo4j")
    sys.exit(1)


class Neo4jImporter:
    """Neo4j数据导入器"""
    
    def __init__(self, uri: str, user: str, password: str):
        """
        初始化连接
        
        Args:
            uri: Neo4j连接URI (如: bolt://localhost:7687)
            user: 用户名
            password: 密码
        """
        print(f"🔌 连接到Neo4j: {uri}")
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # 测试连接
            self.driver.verify_connectivity()
            print("✅ 连接成功!")
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            print("\n💡 请确保:")
            print("  1. Neo4j正在运行")
            print("  2. URI正确 (默认: bolt://localhost:7687)")
            print("  3. 用户名密码正确")
            sys.exit(1)
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
    
    def clear_database(self):
        """清空数据库(谨慎使用!)"""
        print("\n⚠️  清空现有数据...")
        with self.driver.session() as session:
            # 删除所有节点和关系
            session.run("MATCH (n) DETACH DELETE n")
            # 删除所有约束和索引
            constraints = session.run("SHOW CONSTRAINTS").data()
            for constraint in constraints:
                session.run(f"DROP CONSTRAINT {constraint['name']} IF EXISTS")
            
            indexes = session.run("SHOW INDEXES").data()
            for index in indexes:
                if index['type'] != 'LOOKUP':  # 不删除LOOKUP索引
                    session.run(f"DROP INDEX {index['name']} IF EXISTS")
        
        print("✅ 数据库已清空")
    
    def execute_cypher_file(self, filepath: str, batch_size: int = 100):
        """
        执行Cypher脚本文件
        
        Args:
            filepath: .cypher文件路径
            batch_size: 批量执行的语句数量
        """
        print(f"\n📖 读取Cypher脚本: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按分号分割语句
        statements = [stmt.strip() for stmt in content.split(';') if stmt.strip() and not stmt.strip().startswith('//')]
        
        print(f"📊 总语句数: {len(statements)}")
        
        # 批量执行
        with self.driver.session() as session:
            success_count = 0
            error_count = 0
            
            for i, stmt in enumerate(statements):
                # 跳过注释
                if stmt.startswith('//'):
                    continue
                
                try:
                    session.run(stmt)
                    success_count += 1
                    
                    # 显示进度
                    if (i + 1) % batch_size == 0 or (i + 1) == len(statements):
                        progress = (i + 1) / len(statements) * 100
                        print(f"   进度: [{i+1}/{len(statements)}] {progress:.1f}%", end='\r')
                
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # 只显示前5个错误
                        print(f"\n⚠️  语句 {i+1} 执行失败: {str(e)[:100]}")
                        print(f"   语句: {stmt[:200]}...")
        
        print(f"\n\n✅ 导入完成!")
        print(f"   成功: {success_count}")
        print(f"   失败: {error_count}")
    
    def get_statistics(self):
        """获取图谱统计信息"""
        print("\n" + "=" * 60)
        print("📊 图谱统计")
        print("=" * 60)
        
        with self.driver.session() as session:
            # 节点统计
            result = session.run("""
                MATCH (n) 
                RETURN labels(n)[0] as type, count(*) as count
                ORDER BY count DESC
            """)
            
            print("\n节点统计:")
            total_nodes = 0
            for record in result:
                count = record['count']
                total_nodes += count
                print(f"  {record['type']:20s}: {count:5d}")
            print(f"  {'总计':20s}: {total_nodes:5d}")
            
            # 关系统计
            result = session.run("""
                MATCH ()-[r]->() 
                RETURN type(r) as type, count(*) as count
                ORDER BY count DESC
            """)
            
            print("\n关系统计:")
            total_rels = 0
            for record in result:
                count = record['count']
                total_rels += count
                print(f"  {record['type']:30s}: {count:5d}")
            print(f"  {'总计':30s}: {total_rels:5d}")
    
    def run_test_queries(self):
        """运行测试查询"""
        print("\n" + "=" * 60)
        print("🧪 验证查询")
        print("=" * 60)
        
        with self.driver.session() as session:
            # 测试1: 查找eGFR<30禁用的药品
            print("\n1. eGFR < 30 禁用的药品:")
            result = session.run("""
                MATCH (d:Drug)-[r:CONTRAINDICATED_IF]->(m:Metric {name: 'eGFR'})
                WHERE r.operator = '<' AND r.value = 30
                RETURN d.name as drug, r.value as threshold
                LIMIT 10
            """)
            
            for record in result:
                print(f"   ✓ {record['drug']}")
            
            # 测试2: 查找双胍类药物
            print("\n2. 双胍类药物:")
            result = session.run("""
                MATCH (d:Drug)-[:BELONGS_TO]->(c:Category {name: '双胍类'})
                RETURN d.name as drug
                LIMIT 10
            """)
            
            for record in result:
                print(f"   ✓ {record['drug']}")
            
            # 测试3: 查找心力衰竭禁用的药品
            print("\n3. 心力衰竭患者禁用的药品:")
            result = session.run("""
                MATCH (d:Drug)-[:FORBIDDEN_FOR]->(dis:Disease)
                WHERE dis.name CONTAINS '心力衰竭'
                RETURN d.name as drug
                LIMIT 10
            """)
            
            for record in result:
                print(f"   ✓ {record['drug']}")


def main():
    """主函数"""
    print("=" * 60)
    print("🏥 糖尿病药品知识图谱 - Neo4j导入工具")
    print("=" * 60)
    
    # 配置(可根据实际情况修改)
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "password123"  # 默认密码,请根据实际修改
    CYPHER_FILE = "import_graph.cypher"
    
    # 检查文件是否存在
    if not Path(CYPHER_FILE).exists():
        print(f"❌ 错误: 找不到文件 {CYPHER_FILE}")
        print("请先运行 generate_cypher.py 生成Cypher脚本")
        return
    
    # 连接Neo4j
    importer = Neo4jImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # 询问是否清空数据库
        print("\n⚠️  是否清空现有数据库? (yes/no)")
        print("   (如果是首次导入,建议选择yes)")
        response = input("   请输入: ").strip().lower()
        
        if response in ['yes', 'y']:
            importer.clear_database()
        
        # 执行导入
        start_time = time.time()
        importer.execute_cypher_file(CYPHER_FILE)
        elapsed_time = time.time() - start_time
        
        print(f"\n⏱️  导入耗时: {elapsed_time:.2f} 秒")
        
        # 获取统计信息
        importer.get_statistics()
        
        # 运行测试查询
        importer.run_test_queries()
        
        print("\n" + "=" * 60)
        print("🎉 知识图谱导入成功!")
        print("=" * 60)
        print(f"\n💡 访问Neo4j Browser: http://localhost:7474")
        print(f"   用户名: {NEO4J_USER}")
        print(f"   密码: {NEO4J_PASSWORD}")
        
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        importer.close()


if __name__ == "__main__":
    main()

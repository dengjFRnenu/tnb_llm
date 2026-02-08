#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境检查和依赖安装脚本
"""

import sys
import subprocess


def check_python_version():
    """检查 Python 版本"""
    print("🔍 检查 Python 版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 版本过低: {version.major}.{version.minor}")
        print("   需要 Python 3.8 或更高版本")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_import(module_name, package_name=None):
    """检查模块是否可导入"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"  ✅ {package_name}")
        return True
    except ImportError:
        print(f"  ❌ {package_name} (未安装)")
        return False


def check_dependencies():
    """检查所有依赖"""
    print("\n🔍 检查依赖包...")
    
    dependencies = [
        ('chromadb', 'chromadb'),
        ('FlagEmbedding', 'FlagEmbedding'),
        ('rank_bm25', 'rank-bm25'),
        ('jieba', 'jieba'),
        ('neo4j', 'neo4j'),
    ]
    
    missing = []
    for module, package in dependencies:
        if not check_import(module, package):
            missing.append(package)
    
    return missing


def install_dependencies(packages):
    """安装缺失的依赖"""
    print(f"\n📦 安装缺失的依赖: {', '.join(packages)}")
    
    try:
        cmd = [sys.executable, "-m", "pip", "install"] + packages
        subprocess.check_call(cmd)
        print("\n✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 依赖安装失败: {e}")
        return False


def check_neo4j_connection():
    """检查 Neo4j 连接"""
    print("\n🔍 检查 Neo4j 连接...")
    
    try:
        from neo4j import GraphDatabase
        
        uri = "bolt://localhost:7687"
        user = "neo4j"
        password = "password123"
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        driver.close()
        
        print("✅ Neo4j 连接成功")
        return True
    except Exception as e:
        print(f"⚠️  Neo4j 连接失败: {e}")
        print("   Text-to-Cypher 功能将受限")
        print("   请参考 NEO4J_SETUP.md 配置 Neo4j")
        return False


def check_chroma_db():
    """检查 ChromaDB 数据"""
    print("\n🔍 检查 ChromaDB 数据...")
    
    try:
        import chromadb
        
        chroma_path = "./chroma_db"
        collection_name = "diabetes_guidelines_2024"
        
        client = chromadb.PersistentClient(path=chroma_path)
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        
        print(f"✅ ChromaDB 数据就绪 ({count} 条文档)")
        return True
    except Exception as e:
        print(f"⚠️  ChromaDB 数据缺失: {e}")
        print("   请先运行 process_guidelines.py 构建向量库")
        return False


def main():
    """主检查流程"""
    print("="*60)
    print("  GraphRAG 环境检查")
    print("="*60)
    
    # 1. Python 版本
    if not check_python_version():
        sys.exit(1)
    
    # 2. 依赖包
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"\n⚠️  发现 {len(missing_packages)} 个缺失的依赖包")
        choice = input("是否自动安装? [y/N]: ").strip().lower()
        
        if choice == 'y':
            if not install_dependencies(missing_packages):
                print("\n❌ 环境检查失败")
                sys.exit(1)
        else:
            print("\n请手动安装:")
            print(f"  pip install {' '.join(missing_packages)}")
            sys.exit(1)
    
    # 3. Neo4j 连接
    check_neo4j_connection()
    
    # 4. ChromaDB 数据
    check_chroma_db()
    
    # 完成
    print("\n" + "="*60)
    print("✅ 环境检查完成!")
    print("="*60)
    print("\n可以运行以下命令测试系统:")
    print("  python demo_retrieval.py")
    print("\n或直接在代码中使用:")
    print("  from retrieval_engine import GraphRAGEngine")
    print("  engine = GraphRAGEngine()")
    print("  result = engine.retrieve('您的问题')")


if __name__ == "__main__":
    main()

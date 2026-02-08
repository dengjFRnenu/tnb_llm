#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dia-Agent 项目统一配置
集中管理所有配置项：路径、数据库连接、模型参数等
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 加载 .env 文件
load_dotenv(PROJECT_ROOT / ".env")


@dataclass
class PathConfig:
    """路径配置"""
    project_root: Path = PROJECT_ROOT
    
    # 数据目录
    data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data")
    raw_data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "raw")
    processed_data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "processed")
    neo4j_data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "neo4j")
    
    # 配置目录
    configs_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "configs")
    schema_file: Path = field(default_factory=lambda: PROJECT_ROOT / "configs" / "schema.json")
    few_shot_file: Path = field(default_factory=lambda: PROJECT_ROOT / "configs" / "few_shot_examples.json")
    
    # ChromaDB
    chroma_db_path: Path = field(default_factory=lambda: PROJECT_ROOT / "chroma_db")
    
    # 日志
    log_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "logs")


@dataclass
class Neo4jConfig:
    """Neo4j 数据库配置"""
    uri: str = field(default_factory=lambda: os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    user: str = field(default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"))
    password: str = field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", "password123"))
    database: str = field(default_factory=lambda: os.getenv("NEO4J_DATABASE", "neo4j"))


@dataclass
class ChromaConfig:
    """ChromaDB 配置"""
    path: str = field(default_factory=lambda: str(PROJECT_ROOT / "chroma_db"))
    collection_name: str = "diabetes_guidelines_2024"


@dataclass
class LLMConfig:
    """大模型配置"""
    # 提供商: qwen, deepseek, openai, claude, ollama
    provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "qwen"))
    
    # 模型名称
    model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", ""))
    
    # API 密钥
    api_key: str = field(default_factory=lambda: (
        os.getenv("DASHSCOPE_API_KEY") or 
        os.getenv("DEEPSEEK_API_KEY") or 
        os.getenv("OPENAI_API_KEY") or 
        os.getenv("ANTHROPIC_API_KEY") or 
        ""
    ))
    
    # API 基础 URL
    base_url: str = field(default_factory=lambda: os.getenv("LLM_BASE_URL", ""))
    
    # 生成参数
    temperature: float = field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.7")))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "2000")))
    
    @property
    def is_configured(self) -> bool:
        """检查 LLM 是否已配置"""
        return bool(self.api_key) or self.provider == "ollama"


@dataclass
class EmbeddingConfig:
    """嵌入模型配置"""
    model_name: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3"))
    use_fp16: bool = True
    device: str = field(default_factory=lambda: os.getenv("EMBEDDING_DEVICE", "cuda"))


@dataclass
class RerankerConfig:
    """重排序模型配置"""
    model_name: str = field(default_factory=lambda: os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3"))
    use_fp16: bool = True
    device: str = field(default_factory=lambda: os.getenv("RERANKER_DEVICE", "cuda"))


@dataclass
class RetrievalConfig:
    """检索配置"""
    # 向量检索
    vector_top_k: int = 10
    
    # 关键词检索
    keyword_top_k: int = 10
    
    # RRF 融合参数
    rrf_k: int = 60
    
    # 最终返回数量
    final_top_k: int = 5


@dataclass
class AgentConfig:
    """Agent 配置"""
    # 是否启用反思提示
    use_reflection: bool = True
    
    # 是否详细日志
    verbose: bool = True
    
    # 风险检测严重程度阈值
    risk_severity_threshold: str = "HIGH"


@dataclass
class APIConfig:
    """API 服务配置"""
    host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    debug: bool = field(default_factory=lambda: os.getenv("API_DEBUG", "false").lower() == "true")
    cors_origins: list = field(default_factory=lambda: ["*"])


@dataclass
class Config:
    """项目总配置"""
    paths: PathConfig = field(default_factory=PathConfig)
    neo4j: Neo4jConfig = field(default_factory=Neo4jConfig)
    chroma: ChromaConfig = field(default_factory=ChromaConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    reranker: RerankerConfig = field(default_factory=RerankerConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    api: APIConfig = field(default_factory=APIConfig)
    
    def print_summary(self):
        """打印配置摘要"""
        print("=" * 60)
        print("📋 Dia-Agent 配置摘要")
        print("=" * 60)
        
        print(f"\n📁 路径配置:")
        print(f"  项目根目录: {self.paths.project_root}")
        print(f"  ChromaDB: {self.chroma.path}")
        print(f"  Neo4j Cypher: {self.paths.neo4j_data_dir}")
        
        print(f"\n🗄️ Neo4j 配置:")
        print(f"  URI: {self.neo4j.uri}")
        print(f"  User: {self.neo4j.user}")
        
        print(f"\n🤖 LLM 配置:")
        print(f"  Provider: {self.llm.provider}")
        print(f"  已配置: {'✅' if self.llm.is_configured else '❌'}")
        
        print(f"\n📊 嵌入模型:")
        print(f"  Model: {self.embedding.model_name}")
        
        print(f"\n🔄 重排序模型:")
        print(f"  Model: {self.reranker.model_name}")
        
        print(f"\n🌐 API 服务:")
        print(f"  Host: {self.api.host}:{self.api.port}")


# 全局配置实例
config = Config()


# ============================================
# 便捷访问函数
# ============================================

def get_config() -> Config:
    """获取配置实例"""
    return config


def get_neo4j_config() -> Neo4jConfig:
    """获取 Neo4j 配置"""
    return config.neo4j


def get_llm_config() -> LLMConfig:
    """获取 LLM 配置"""
    return config.llm


def get_paths() -> PathConfig:
    """获取路径配置"""
    return config.paths


# ============================================
# 测试
# ============================================

if __name__ == "__main__":
    cfg = get_config()
    cfg.print_summary()

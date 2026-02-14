# Dia-Agent: 糖尿病专病智能诊疗系统
"""
Dia-Agent - 糖尿病专病多模态智能诊疗与决策支持系统

基于 GraphRAG 架构，整合知识图谱和检索增强生成技术
"""

__version__ = "0.1.0"
__author__ = "Jin.Deng"

__all__ = [
    "GraphRAGEngine",
    "Config",
    "config",
    "get_config",
    "LLMClient",
    "create_llm_api",
    "create_qwen_api",
    "create_deepseek_api",
    "create_openai_api",
    "create_ollama_api",
]


def __getattr__(name):
    """延迟导入重量级模块，减少基础 import 开销"""
    if name == "GraphRAGEngine":
        from .engine import GraphRAGEngine
        return GraphRAGEngine

    if name in {"Config", "config", "get_config"}:
        from .config import Config, config, get_config
        mapping = {
            "Config": Config,
            "config": config,
            "get_config": get_config,
        }
        return mapping[name]

    if name in {
        "LLMClient",
        "create_llm_api",
        "create_qwen_api",
        "create_deepseek_api",
        "create_openai_api",
        "create_ollama_api",
    }:
        from .llm_client import (
            LLMClient,
            create_llm_api,
            create_qwen_api,
            create_deepseek_api,
            create_openai_api,
            create_ollama_api,
        )
        mapping = {
            "LLMClient": LLMClient,
            "create_llm_api": create_llm_api,
            "create_qwen_api": create_qwen_api,
            "create_deepseek_api": create_deepseek_api,
            "create_openai_api": create_openai_api,
            "create_ollama_api": create_ollama_api,
        }
        return mapping[name]

    raise AttributeError(f"module 'src' has no attribute '{name}'")

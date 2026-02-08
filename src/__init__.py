# Dia-Agent: 糖尿病专病智能诊疗系统
"""
Dia-Agent - 糖尿病专病多模态智能诊疗与决策支持系统

基于 GraphRAG 架构，整合知识图谱和检索增强生成技术
"""

__version__ = "0.1.0"
__author__ = "Jin.Deng"

from .engine import GraphRAGEngine

__all__ = ["GraphRAGEngine"]

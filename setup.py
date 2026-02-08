#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dia-Agent 安装配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dia-agent",
    version="0.1.0",
    author="Jin.Deng",
    author_email="",
    description="糖尿病专病多模态智能诊疗与决策支持系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jin-Deng/tnb_llm",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "chromadb>=0.4.0",
        "FlagEmbedding>=1.2.0",
        "transformers>=4.30.0",
        "rank-bm25>=0.2.2",
        "jieba>=0.42.0",
        "neo4j>=5.0.0",
        "numpy>=1.24.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "llm": [
            "openai>=1.0.0",
            "langchain>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dia-agent=examples.demo_retrieval:main",
        ],
    },
)

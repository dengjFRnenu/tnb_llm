# GraphRAG 混合检索系统 - 依赖说明

## 核心依赖

以下依赖需要安装才能运行阶段二的代码：

```bash
# 向量检索和 Embedding
pip install chromadb FlagEmbedding

# 关键词检索
pip install rank-bm25 jieba

# Neo4j 连接
pip install neo4j

# 测试框架（可选）
pip install pytest pytest-cov
```

## 一键安装

```bash
cd /home/Jin.Deng/tnb_llm
pip install chromadb FlagEmbedding rank-bm25 jieba neo4j
```

## 模型下载

首次运行会自动下载以下模型（需要网络连接）：

1. **BAAI/bge-m3** - 向量化模型（~2.3GB）
2. **BAAI/bge-reranker-v2-m3** - 精排模型（~1.1GB）

模型会缓存到 `~/.cache/huggingface/`

## 环境检查

运行以下命令验证环境：

```bash
python -c "import chromadb; import rank_bm25; import jieba; from FlagEmbedding import BGEM3FlagModel, FlagReranker; from neo4j import GraphDatabase; print('✅ 所有依赖已安装')"
```

## 可选优化

如果有 GPU，可以加速模型推理：

```bash
# 安装 CUDA 版本的 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

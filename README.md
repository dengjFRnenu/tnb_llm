# Dia-Agent 🏥

**糖尿病专病多模态智能诊疗与决策支持系统**

基于 GraphRAG 架构，整合知识图谱和检索增强生成技术，实现精准的糖尿病临床决策支持。

---

## ✨ 系统特性

- **混合检索**: 向量检索 (BGE-M3) + 关键词检索 (BM25) + RRF 融合
- **智能精排**: BGE-Reranker 语义相关性精排
- **知识图谱查询**: Text-to-Cypher 自然语言转 Neo4j 查询
- **数据融合**: 硬规则（KG）+ 软知识（RAG）智能合并

---

## 📂 项目结构

```
tnb_llm/
├── src/                         # 核心源代码
│   ├── engine.py                # 检索总控引擎
│   ├── data/                    # 数据处理模块
│   ├── retrieval/               # 检索模块
│   └── graph/                   # 知识图谱模块
├── configs/                     # 配置文件
│   ├── schema.json              # 图谱Schema
│   └── few_shot_examples.json   # Text-to-Cypher示例
├── data/                        # 数据文件
│   ├── raw/                     # 原始数据
│   ├── processed/               # 处理后数据
│   └── neo4j/                   # Neo4j相关
├── scripts/                     # 工具脚本
├── tests/                       # 测试代码
├── examples/                    # 示例代码
├── docs/                        # 文档
└── chroma_db/                   # ChromaDB向量库
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /home/Jin.Deng/tnb_llm
pip install -r requirements.txt
```

### 2. 验证环境

```bash
python scripts/setup_check.py
```

### 3. 运行 Demo

```bash
python examples/demo_retrieval.py
```

示例问题：
- `eGFR小于30的患者不能使用哪些药物？`
- `有哪些SGLT2抑制剂？`
- `糖尿病患者的运动建议是什么？`

---

## 💻 代码使用

### 基础示例

```python
import sys
sys.path.insert(0, '/home/Jin.Deng/tnb_llm')
from src import GraphRAGEngine

# 初始化引擎
engine = GraphRAGEngine()

# 执行检索
result = engine.retrieve("eGFR小于30的患者不能使用哪些药物？")

# 查看结果
print("策略:", "GraphRAG" if result['use_kg'] else "RAG Only")
print("RAG文档数:", len(result['rag_results']))
print("KG结果数:", len(result['kg_results']))
print("\n最终Context:\n", result['merged_context'])
```

### 与 LLM 集成

```python
def call_llm(context, question):
    """调用你的 LLM（如 Qwen, GPT 等）"""
    prompt = f"{context}\n\n请回答: {question}"
    # 调用 API...
    return response

# 使用 GraphRAG 检索 + LLM 生成
query = "eGFR小于30能用二甲双胍吗？"
result = engine.retrieve(query)
answer = call_llm(result['merged_context'], query)
```

---

## ⚙️ 配置选项

### 禁用知识图谱查询（仅 RAG）

```python
result = engine.retrieve(query, use_kg=False)
```

### 调整检索数量

```python
result = engine.retrieve(
    query,
    hybrid_top_k=15,    # 初筛15篇
    rerank_top_k=5      # 精排前5篇
)
```

### 使用自定义 LLM 生成 Cypher

```python
def my_llm(prompt):
    # 你的 LLM API 调用
    return cypher_code

result = engine.retrieve(query, llm_api_function=my_llm)
```

---

## 🔧 故障排查

| 问题 | 解决方案 |
|------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `ChromaDB collection not found` | `python src/data/guideline_parser.py` |
| `Neo4j connection failed` | 参考 `docs/NEO4J_SETUP.md` |

---

## 📊 性能参考

| 场景 | 耗时 | 说明 |
|------|------|------|
| 纯 RAG 查询 | ~300ms | 不查知识图谱 |
| GraphRAG 查询 | ~1.3s | 包含 Text-to-Cypher |
| GPU 加速后 | ~600ms | Reranker 加速 |

---

## 📚 文档

- [快速入门](docs/QUICKSTART.md)
- [Neo4j 配置](docs/NEO4J_SETUP.md)
- [安装笔记](docs/INSTALL_NOTES.md)
- [服务部署](docs/SERVER_DEPLOY.md)
- [项目规划](docs/project.md)

---

## 📄 License

MIT License

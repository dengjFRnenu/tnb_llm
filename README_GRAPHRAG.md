# GraphRAG 系统使用指南

## 🚀 快速开始（3步上手）

### 1️⃣ 安装依赖

```bash
cd /home/Jin.Deng/tnb_llm
conda activate tnb_llm
pip install chromadb FlagEmbedding rank-bm25 jieba neo4j
```

### 2️⃣ 验证环境

```bash
python test_system.py
```

### 3️⃣ 运行 Demo

```bash
python demo_retrieval.py
```

选择 **交互式模式**，输入问题例如：
- `eGFR小于30的患者不能使用哪些药物？`
- `有哪些SGLT2抑制剂？`
- `糖尿病患者的运动建议是什么？`

---

## 💻 代码使用

### 基础示例

```python
from retrieval_engine import GraphRAGEngine

# 初始化（只需一次）
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
# 假设你有一个 LLM API 函数
def call_llm(context, question):
    """调用你的 LLM（如 Qwen, GPT 等）"""
    prompt = f"{context}\n\n请回答: {question}"
    # 调用 API...
    return response

# 使用 GraphRAG 检索 + LLM 生成
query = "eGFR小于30能用二甲双胍吗？"
result = engine.retrieve(query)
answer = call_llm(result['merged_context'], query)
print(answer)
```

---

## 📂 关键文件说明

| 文件 | 用途 | 何时使用 |
|------|------|----------|
| `retrieval_engine.py` | 主入口 | 直接使用这个 |
| `demo_retrieval.py` | 演示程序 | 测试系统 |
| `test_system.py` | 测试套件 | 验证功能 |
| `QUICKSTART.md` | 详细文档 | 深入学习 |

---

## ⚙️ 常用配置

### 1. 禁用知识图谱查询（仅 RAG）

```python
result = engine.retrieve(query, use_kg=False)
```

### 2. 调整检索数量

```python
result = engine.retrieve(
    query,
    hybrid_top_k=15,    # 初筛15篇
    rerank_top_k=5      # 精排前5篇
)
```

### 3. 使用自定义 LLM 生成 Cypher

```python
def my_llm(prompt):
    # 你的 LLM API 调用
    return cypher_code

result = engine.retrieve(query, llm_api_function=my_llm)
```

---

## 🔧 故障排查

### 问题1: `ModuleNotFoundError`

**解决**: 
```bash
conda activate tnb_llm
pip install chromadb FlagEmbedding rank-bm25 jieba neo4j
```

### 问题2: `ChromaDB collection not found`

**解决**:
```bash
python process_guidelines.py  # 重新构建向量库
```

### 问题3: `Neo4j connection failed`

**解决**: 
- 检查 Neo4j 是否运行：访问 http://localhost:7474
- 密码是否为 `password123`
- 参考 `NEO4J_SETUP.md`

如果 Neo4j 不可用，系统会降级为示例匹配模式，仍可正常工作。

---

## 📊 性能参考

| 场景 | 耗时 | 说明 |
|------|------|------|
| 纯 RAG 查询 | ~300ms | 不查知识图谱 |
| GraphRAG 查询 | ~1.3s | 包含 Text-to-Cypher |
| GPU 加速后 | ~600ms | Reranker 加速 |

---

## 🎯 推荐使用流程

1. **开发阶段**: 用 `demo_retrieval.py` 交互测试
2. **集成阶段**: 导入 `GraphRAGEngine` 到你的代码
3. **生产阶段**: 考虑添加缓存、异步调用等优化

---

**完整文档**: 见 [`QUICKSTART.md`](file:///home/Jin.Deng/tnb_llm/QUICKSTART.md)

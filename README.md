# Dia-Agent 🏥

**糖尿病专病多模态智能诊疗与决策支持系统**

基于 GraphRAG 架构，整合知识图谱和检索增强生成技术，实现精准的糖尿病临床决策支持。

---

## ✨ 系统特性

### 核心能力
- 🔍 **混合检索**: 向量检索 (BGE-M3) + 关键词检索 (BM25) + RRF 融合
- 🎯 **智能精排**: BGE-Reranker 语义相关性精排
- 📊 **知识图谱查询**: Text-to-Cypher 自然语言转 Neo4j 查询
- 🔗 **数据融合**: 硬规则（KG）+ 软知识（RAG）智能合并

### 智能诊疗 (NEW!)
- 📋 **病例分析**: 从病历文本提取结构化患者画像
- ⚠️ **风险检测**: 基于知识图谱检测用药禁忌
- 💊 **决策融合**: 整合图谱规则和指南知识生成诊疗建议
- 📝 **报告生成**: 带引用来源的临床报告

---

## 📂 项目结构

```
tnb_llm/
├── src/                         # 核心源代码
│   ├── engine.py                # 检索总控引擎
│   ├── data/                    # 数据处理模块
│   │   └── guideline_parser.py  # 指南解析器
│   ├── retrieval/               # 检索模块
│   │   ├── hybrid.py            # 混合检索器
│   │   └── reranker.py          # 重排序器
│   ├── graph/                   # 知识图谱模块
│   │   ├── text_to_cypher.py    # Text-to-Cypher 引擎
│   │   └── langchain_cypher.py  # LangChain 增强检索
│   └── agent/                   # 智能诊疗 Agent
│       ├── patient_profile.py   # 患者画像模型
│       ├── case_analyzer.py     # 病例分析器
│       ├── risk_detector.py     # 风险检测器
│       ├── decision_fusion.py   # 决策融合器
│       └── dia_agent.py         # 主协调器
├── configs/                     # 配置文件
│   ├── schema.json              # 图谱Schema
│   └── few_shot_examples.json   # Text-to-Cypher示例
├── data/                        # 数据文件
│   ├── raw/                     # 原始数据
│   ├── processed/               # 处理后数据
│   └── neo4j/                   # Neo4j导入脚本
├── api.py                       # FastAPI 服务接口
├── chroma_db/                   # ChromaDB向量库
└── docs/                        # 文档
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /home/Jin.Deng/tnb_llm
pip install -r requirements.txt
```

### 2. 启动 Neo4j

```bash
docker run -d --name neo4j-diabetes \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:5.15.0
```

### 3. 导入知识图谱

```bash
python scripts/import_to_neo4j.py
```

### 4. 运行测试

```bash
# 测试 GraphRAG 引擎
python -m src.engine

# 测试 Dia-Agent
python -m src.agent.dia_agent
```

---

## 💻 使用方式

### 方式一：Dia-Agent 智能诊疗 (推荐)

```python
from src.agent import DiaAgent

# 初始化 Agent
agent = DiaAgent()

# 完整诊疗咨询
case = """
患者男，55岁，2型糖尿病10年。
当前用药：二甲双胍0.5g tid、恩格列净10mg qd
检查：HbA1c 8.2%，eGFR 28 mL/min
诊断：糖尿病肾病 CKD 4期
"""

report = agent.consult(case)
print(report.to_markdown())

# 关闭
agent.close()
```

### 方式二：快速风险检查

```python
from src.agent import DiaAgent

agent = DiaAgent(verbose=False)

# 只需提供用药和关键指标
risk_report = agent.quick_risk_check(
    medications=["二甲双胍", "恩格列净"],
    egfr=28,
    complications=["糖尿病肾病"]
)

print(risk_report.to_text())
```

### 方式三：GraphRAG 检索引擎

```python
from src.engine import GraphRAGEngine

engine = GraphRAGEngine()

result = engine.retrieve("eGFR小于30的患者不能使用哪些药物？")

print("检索策略:", "GraphRAG" if result['use_kg'] else "RAG Only")
print("RAG结果:", len(result['rag_results']), "篇文档")
print("KG结果:", len(result['kg_results']), "条记录")
print("\n融合Context:\n", result['merged_context'])
```

---

## 🌐 API 服务

### 启动服务

```bash
# 安装 FastAPI
pip install fastapi uvicorn

# 启动服务
python api.py
```

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 健康检查 |
| `/health` | GET | 组件状态 |
| `/consult` | POST | 完整诊疗咨询 |
| `/risk-check` | POST | 快速风险检查 |
| `/drug-info` | POST | 药品禁忌查询 |

访问 `http://localhost:8000/docs` 查看 API 文档。

### 示例请求

```bash
curl -X POST "http://localhost:8000/risk-check" \
  -H "Content-Type: application/json" \
  -d '{"medications": ["二甲双胍"], "egfr": 25}'
```

---

## 📊 数据资源

| 资源 | 数量 | 说明 |
|------|------|------|
| 指南文档 | 136篇 | 《中国糖尿病防治指南2024》分块 |
| 药品节点 | 89个 | 糖尿病相关药品 |
| 知识关系 | 421条 | 禁忌/适应症/分类等 |
| Few-shot示例 | 20条 | Text-to-Cypher 训练数据 |

---

## 🧪 技术栈

- **向量模型**: BGE-M3, BGE-Reranker-v2-M3
- **向量库**: ChromaDB
- **图数据库**: Neo4j 5.x
- **NLP**: jieba, FlagEmbedding
- **框架**: Pydantic, FastAPI
- **LLM集成**: 可选 (OpenAI/Claude/Qwen)

---

## 📖 文档

- [项目需求文档](project_need.md)
- [LangChain Cypher 使用指南](docs/langchain_cypher.md)

---

## 📝 License

MIT License

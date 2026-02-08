# Dia-Agent 快速启动指南

## 📋 目录

1. [环境准备](#环境准备)
2. [启动 Neo4j](#启动-neo4j)
3. [导入知识图谱](#导入知识图谱)
4. [配置大模型](#配置大模型)
5. [验证系统](#验证系统)
6. [使用示例](#使用示例)
7. [启动 API 服务](#启动-api-服务)
8. [常见问题](#常见问题)

---

## 环境准备

### 1. 进入项目目录

```bash
cd /home/Jin.Deng/tnb_llm
```

### 2. 检查 Python 环境

```bash
python --version
# 要求: Python 3.10+
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装额外依赖（如需 API 服务）

```bash
pip install fastapi uvicorn
```

---

## 启动 Neo4j

### 方式一：Docker 启动（推荐）

```bash
# 检查是否已有容器
docker ps -a | grep neo4j

# 如果没有，创建新容器
docker run -d --name neo4j-diabetes \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:5.15.0

# 如果容器已存在但未运行
docker start neo4j-diabetes

# 查看容器状态
docker ps | grep neo4j
```

### 方式二：本地 Neo4j 安装

如果使用本地安装的 Neo4j，请确保：
- Neo4j 版本 5.x
- Bolt 端口：7687
- 用户名：neo4j
- 密码：password123

### 验证 Neo4j 连接

```bash
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password123'))
driver.verify_connectivity()
print('✅ Neo4j 连接成功')
driver.close()
"
```

---

## 导入知识图谱

### 检查是否已导入

```bash
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password123'))
with driver.session() as session:
    result = session.run('MATCH (n) RETURN count(n) as count')
    count = result.single()['count']
    print(f'📊 当前节点数: {count}')
    if count > 0:
        print('✅ 知识图谱已导入')
    else:
        print('⚠️ 需要导入知识图谱')
driver.close()
"
```

### 导入数据（如果需要）

```bash
python -c "
from neo4j import GraphDatabase
from pathlib import Path

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password123'))
cypher_file = Path('/home/Jin.Deng/tnb_llm/data/neo4j/import_graph.cypher')

print('📖 读取 Cypher 文件...')
with open(cypher_file, 'r', encoding='utf-8') as f:
    content = f.read()

statements = [s.strip() for s in content.split(';') if s.strip() and not s.strip().startswith('//')]
print(f'📊 共 {len(statements)} 条语句')

success = 0
with driver.session() as session:
    for i, stmt in enumerate(statements):
        try:
            session.run(stmt)
            success += 1
            if (i + 1) % 100 == 0:
                print(f'  进度: {i + 1}/{len(statements)}')
        except:
            pass

print(f'✅ 导入完成: 成功 {success} 条')
driver.close()
"
```

---

## 配置大模型

系统支持多种大模型 API，配置后可实现更智能的病历分析和诊疗建议生成。

### 支持的大模型

| 提供商 | 环境变量 | 申请地址 |
|--------|----------|----------|
| 通义千问 (推荐) | `DASHSCOPE_API_KEY` | https://dashscope.console.aliyun.com/ |
| DeepSeek | `DEEPSEEK_API_KEY` | https://platform.deepseek.com/ |
| OpenAI | `OPENAI_API_KEY` | https://platform.openai.com/ |
| Ollama (本地) | 无需密钥 | https://ollama.ai/ |

### 配置方式一：环境变量

```bash
# 通义千问
export DASHSCOPE_API_KEY=sk-your-api-key

# 或 DeepSeek
export DEEPSEEK_API_KEY=sk-your-api-key

# 或 OpenAI
export OPENAI_API_KEY=sk-your-api-key
```

### 配置方式二：代码中指定

```python
from src.llm_client import create_qwen_api, create_deepseek_api
from src.agent import DiaAgent

# 方式1: 通义千问
llm_api = create_qwen_api(api_key="your-api-key")

# 方式2: DeepSeek
llm_api = create_deepseek_api(api_key="your-api-key")

# 创建 Agent
agent = DiaAgent(llm_api=llm_api)
```

### 配置方式三：使用 Ollama 本地模型

```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. 下载模型
ollama pull qwen2.5:7b

# 3. 启动服务（默认已自动启动）
ollama serve
```

```python
from src.llm_client import create_ollama_api
from src.agent import DiaAgent

llm_api = create_ollama_api(model="qwen2.5:7b")
agent = DiaAgent(llm_api=llm_api)
```

### 验证 LLM 配置

```bash
python -c "
from src.llm_client import create_llm_api
import os

if os.getenv('DASHSCOPE_API_KEY'):
    llm = create_llm_api('qwen')
    print('✅ 通义千问 API 配置成功')
    response = llm('你好，请用一句话介绍糖尿病')
    print(f'测试响应: {response[:100]}...')
else:
    print('⚠️ 未配置 API 密钥，将使用规则模式')
"
```

---

## 验证系统

### 1. 测试核心模块

```bash
python -c "
print('🧪 测试核心模块导入...')
from src.agent import DiaAgent, PatientProfile, create_patient_profile
from src.retrieval.hybrid import HybridRetriever
from src.graph.langchain_cypher import LangChainCypherRetriever
print('✅ 所有模块导入成功')
"
```

### 2. 运行完整测试套件

```bash
python -m tests.test_dia_agent
```

### 3. 快速功能验证

```bash
python -c "
from src.agent import DiaAgent

print('🏥 初始化 Dia-Agent...')
agent = DiaAgent(verbose=False)

print('✅ 初始化成功')
print()
print('🧪 测试快速风险检查...')
report = agent.quick_risk_check(
    medications=['二甲双胍', '恩格列净'],
    egfr=28
)

print(f'检测到 {len(report.warnings)} 个风险')
print()
print('📋 风险摘要:')
print(report.to_text())

agent.close()
"
```

---

## 使用示例

### 示例 1：完整诊疗咨询

```python
from src.agent import DiaAgent

# 初始化
agent = DiaAgent()

# 病历文本
case = """
患者男，55岁，因"发现血糖升高10年"入院。
诊断：2型糖尿病，糖尿病肾病 CKD 4期
当前用药：二甲双胍 0.5g tid，恩格列净 10mg qd
检查：HbA1c 8.2%，eGFR 28 mL/min/1.73m²
"""

# 执行诊疗
report = agent.consult(case)

# 输出报告
print(report.to_markdown())

# 关闭
agent.close()
```

### 示例 2：快速用药风险检查

```python
from src.agent import DiaAgent

agent = DiaAgent(verbose=False)

# 只需提供用药和关键指标
report = agent.quick_risk_check(
    medications=["二甲双胍", "格列美脲"],
    egfr=25,
    complications=["心力衰竭"]
)

# 查看风险
for warning in report.warnings:
    print(f"[{warning.severity.value}] {warning.drug_name}: {warning.reason}")

agent.close()
```

### 示例 3：直接使用 GraphRAG 引擎

```python
from src.engine import GraphRAGEngine

engine = GraphRAGEngine()

# 执行检索
result = engine.retrieve("eGFR小于30的患者不能使用哪些药物？")

print("检索策略:", "GraphRAG" if result['use_kg'] else "RAG Only")
print("RAG结果:", len(result['rag_results']), "篇")
print("KG结果:", len(result['kg_results']), "条")
print("\n融合Context:\n", result['merged_context'][:500])
```

### 示例 4：查询知识图谱

```python
from src.graph import LangChainCypherRetriever

retriever = LangChainCypherRetriever()

# 查询
result = retriever.query("双胍类药物有哪些？", use_llm=False)

print(f"成功: {result.success}")
print(f"来源: {result.source}")
print(f"结果数: {len(result.results)}")

for r in result.results[:5]:
    print(f"  - {r}")

retriever.close()
```

---

## 启动 API 服务

### 启动服务

```bash
cd /home/Jin.Deng/tnb_llm
python api.py
```

服务启动后访问：
- API 文档：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

### 测试 API

```bash
# 健康检查
curl http://localhost:8000/health

# 快速风险检查
curl -X POST http://localhost:8000/risk-check \
  -H "Content-Type: application/json" \
  -d '{"medications": ["二甲双胍"], "egfr": 25}'

# 完整诊疗
curl -X POST http://localhost:8000/consult \
  -H "Content-Type: application/json" \
  -d '{"case_text": "患者55岁，2型糖尿病，用药二甲双胍，eGFR 28"}'
```

### 后台运行（可选）

```bash
nohup python api.py > api.log 2>&1 &
```

---

## 常见问题

### Q1: Neo4j 连接失败

**错误**: `Couldn't connect to localhost:7687`

**解决**:
```bash
# 检查容器状态
docker ps | grep neo4j

# 如果未运行，启动容器
docker start neo4j-diabetes

# 等待 30 秒后重试
```

### Q2: ChromaDB 集合不存在

**错误**: `Collection diabetes_guidelines_2024 not found`

**解决**:
```bash
# 检查向量库是否存在
ls -la /home/Jin.Deng/tnb_llm/chroma_db/

# 如果不存在，需要重新构建向量库
python -c "
from src.data.guideline_parser import build_chroma_db
build_chroma_db()
"
```

### Q3: 模型下载慢

首次运行时需要下载 BGE 模型，可能较慢。

**解决**: 使用国内镜像
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Q4: 内存不足

**错误**: `CUDA out of memory` 或 进程被 kill

**解决**:
```python
# 使用 CPU 模式
from FlagEmbedding import BGEM3FlagModel
model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=False, device='cpu')
```

### Q5: 知识图谱为空

```bash
# 检查节点数
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password123'))
with driver.session() as session:
    for label in ['Drug', 'Category', 'Disease', 'Metric']:
        result = session.run(f'MATCH (n:{label}) RETURN count(n) as c')
        print(f'{label}: {result.single()[\"c\"]}')
driver.close()
"
```

如果全部为 0，请重新执行[导入知识图谱](#导入知识图谱)步骤。

---

## 📞 技术支持

如有问题，请查看：
- [README.md](README.md) - 项目概述
- [docs/langchain_cypher.md](docs/langchain_cypher.md) - Cypher 检索文档
- [project_need.md](project_need.md) - 项目需求文档

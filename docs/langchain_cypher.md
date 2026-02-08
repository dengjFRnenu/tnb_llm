# LangChain Text-to-Cypher 检索器

## 概述

`LangChainCypherRetriever` 是一个增强版的 Text-to-Cypher 检索器，用于将自然语言问题转换为 Neo4j Cypher 查询。

### 核心特性

1. **Schema 信息注入** - Prompt 中包含完整的知识图谱结构描述
2. **Few-shot 动态选择** - 基于问题相似度自动选择最相关的示例
3. **多层回退机制** - LLM → 示例匹配 → 预定义模板

## 快速开始

```python
from src.graph import LangChainCypherRetriever, create_cypher_retriever

# 方式1: 直接创建
retriever = LangChainCypherRetriever(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password123"
)

# 方式2: 使用便捷函数
retriever = create_cypher_retriever()

# 执行查询
result = retriever.query("eGFR小于30的患者不能使用哪些药物？")

if result.success:
    print(f"找到 {len(result.results)} 条结果")
    for r in result.results:
        print(r)
else:
    print(f"查询失败: {result.error}")

# 关闭连接
retriever.close()
```

## 使用 LLM API

```python
# 定义 LLM 调用函数
def call_llm(prompt: str) -> str:
    # 这里可以接入任何 LLM API
    # 例如 OpenAI, Claude, Qwen 等
    import openai
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 创建检索器并传入 LLM API
retriever = LangChainCypherRetriever(llm_api=call_llm)

# 查询将优先使用 LLM 生成 Cypher
result = retriever.query("查询所有需要监测肾功能的药物")
```

## 回退机制

检索器采用三层回退策略：

| 层级 | 方法 | 说明 |
|------|------|------|
| 1 | LLM 生成 | 使用 LLM 根据 Schema 和 Few-shot 示例生成 Cypher |
| 2 | 示例匹配 | 从预定义示例库中匹配最相似的问题 |
| 3 | 回退模板 | 使用预定义的通用查询模板 |

## 返回结果

`CypherResult` 对象包含以下字段：

```python
@dataclass
class CypherResult:
    success: bool           # 查询是否成功
    cypher: str             # 生成的 Cypher 语句
    results: List[Dict]     # 查询结果
    error: str              # 错误信息（如果失败）
    fallback_used: bool     # 是否使用了回退机制
    source: str             # 来源: "llm", "example_match", "fallback"
```

## 支持的查询类型

| 类别 | 示例问题 |
|------|----------|
| 指标禁忌 | "eGFR小于30的患者不能使用哪些药物？" |
| 药物分类 | "双胍类药物有哪些？" |
| 疾病禁忌 | "心力衰竭患者禁用哪些药物？" |
| 药物详情 | "二甲双胍有哪些禁忌症？" |
| 复杂查询 | "哪些药物既禁用于心衰又禁用于肾功能不全？" |

## 配置文件

- `configs/schema.json` - 知识图谱 Schema 定义
- `configs/few_shot_examples.json` - Few-shot 示例库

## 测试

```bash
cd /home/Jin.Deng/tnb_llm
python -m src.graph.langchain_cypher
```

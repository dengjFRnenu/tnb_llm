Dia-Agent 深度落地详细规划
第一阶段：医学资产的“数字化”与“特征化”
核心目标： 将原始指南和图谱转化为 Agent 能听懂的语言。
指南文本的层级向量化 (Guideline RAG Engineering)：
构建细节： 糖尿病指南中包含大量阶梯式疗法表格。不能直接按字符切分。
实现方法：
使用 Unstructured 或 PyMuPDF 提取文本。
表格逻辑重建： 遇到表格时，引导 LLM 将表格转化为 Markdown 或 JSON 格式再存入向量库。这样在检索时，表头信息（如“HbA1c阈值”、“用药建议”）能与内容紧密关联。
元数据注入： 为每个 Chunk 标注 章节名（如：并发症处理）、证据分级（如：A级推荐）。
技术栈： LangChain / LlamaIndex, BGE-M3 Embedding.
药品图谱的实体对齐 (Entity Linking Prep)：
构建细节： 确保病例里的“二甲”能对齐图谱里的“二甲双胍”。
实现方法： 提取图谱中所有 Drug 节点的 name 和 alias 属性，构建一个 Aho-Corasick (AC) 自动机或简单的哈希表。这用于在解析病例时，秒级定位图谱实体。
技术栈： pyahocorasick, Neo4j Python Driver.
第二阶段：病例书的“全息画像”提取 (Case Analysis Agent)
核心目标： 从医生写的杂乱病历中抽取出结构化的“临床状态”。
多维度实体识别 (Case NER)：
构建细节： 定义一个精确的 Pydantic 模型来约束 LLM 的输出。
提取维度：
基础信息： 年龄、病程、BMI。
关键指标： HbA1c、FPG（空腹血糖）、PPG（餐后血糖）、eGFR（肾功能）、UACR（尿白蛋白）。
并发症： 视网膜病变（DR）、肾病（DKD）、周围神经病变（DPN）。
提示词引导： 使用“反思提示词”。先让 LLM 提取一遍，再问它：“该患者是否有提到的禁忌指标（如肌酐值）被你漏掉了？”
临床逻辑分层：
根据提取到的指标，自动计算并打标（如：{肾功能分期: CKD-3b}, {心血管风险: 极高危}）。这些标签将直接作为后续 Cypher 查询的参数。
第三阶段：GraphRAG 协同搜索逻辑 (The Logic Core)
核心目标： 这一步是让 LLM 知道如何同时操作向量库和图谱。
图谱端的“风险侦测” (Cypher Generation)：
构建细节： 针对病例中的每一个药物，去图谱查禁忌。
代码逻辑逻辑：
code
Cypher
MATCH (d:Drug {name: $drug_name})-[:CONTRAINDICATION]->(c:Condition)
WHERE c.name IN $patient_conditions OR $patient_metrics >= c.threshold
RETURN d.name, c.reason
LLM 引导： 给 LLM 提供图谱的 Schema，告诉它：“如果检测到患者 eGFR < 45，请务必生成查询二甲双胍和 SGLT2i 禁忌症的 Cypher 语句。”
指南端的“方案检索” (Hybrid Retrieval)：
构建细节： 拿着“画像标签”去搜指南。
技术路径： 采用 Multi-Query Retrieval。LLM 根据病例生成 3 个搜索词。例如：1. “糖尿病合并 CKD3b 期用药指南”；2. “二甲双胍肾功能减退剂量调整”；3. “HbA1c > 8.5% 的联合治疗方案”。
第四阶段：冲突检测与决策生成 (Decision Fusion)
核心目标： 当图谱说“不能用”而指南说“可以用”时（或反之），进行逻辑裁决。
证据融合 Prompt 构建：
构建逻辑： 构造一个“临床决策工作台” Context：
[患者事实]: 55岁，eGFR 28。
[图谱硬规则]: 警告！eGFR < 30 禁用二甲双胍。
[指南软知识]: 指南建议 eGFR 30-45 减量，< 30 停用。
逻辑优先级： 在 Prompt 中明确：图谱规则 (Safety) > 指南通用建议 (General Guidance)。
带引用的报告生成：
构建细节： 要求 LLM 在输出每句话时，必须标记来源。
示例输出： “建议停用二甲双胍（源自：药品图谱-禁忌逻辑），考虑换用利格列汀（源自：2024指南-肾功能不全患者用药建议第4章）。”
第五阶段：评估与代码落地指令 (Evaluation & Implementation)
你可以直接发给大模型（如 Claude 3.5 或 GPT-4）的代码构建指令示例：
指令： “我现在要实现 Dia-Agent 的核心逻辑。请按照以下步骤写出 Python 代码：
定义 Schema：使用 Pydantic 定义一个 PatientProfile 类，包含血糖、肾功、并发症字段。
实现图谱查询函数：编写一个函数，接受 PatientProfile，连接 Neo4j 数据库，根据 schema.json 中的关系，查询该患者当前用药是否存在禁忌，返回一个 warnings 列表。
实现向量检索函数：使用 LangChain 的 EnsembleRetriever，结合 BM25 和 ChromaDB，根据患者画像检索指南中最相关的 3 个片段。
实现融合生成：编写一个主函数，将上述 warnings 和检索到的片段喂给 LLM，要求它生成一份包含‘风险提示’和‘调整建议’的诊疗报告，且必须标注证据来源。”

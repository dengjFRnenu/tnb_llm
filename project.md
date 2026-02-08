项目名称：Dia-Agent (糖尿病专病多模态智能诊疗与决策支持系统)
阶段一：数据深度工程（数据资产化）
目标： 将原始语料转化为 LLM 可理解、可检索的高质量数据集。
指南结构化 (RAG Engine)：
高级解析： 使用 marker 或 PyMuPDF 解析指南 PDF，重点处理表格和流程图（转为 Markdown 表格）。
语义切片： 采用 Header-based Chunking（按标题分片），确保每一段话都带有所属章节（如：#诊疗路径、#运动建议）的元数据。
向量化入库： 使用 BGE-M3 模型进行 Embedding，存入 ChromaDB 或 Milvus，开启向量与关键字混合搜索。
图谱 Schema 链接 (KG Engine)：
编写一个描述你 Neo4j 结构的 schema.json（包含点、边、属性描述）。
准备 Few-shot 样本：编写 20 组“自然语言问题 -> Cypher 查询语句”的对话对，用于实现 Text-to-Cypher。
阶段二：构建 GraphRAG 与混合检索（核心竞争力）
目标： 解决医疗问诊的“确定性”和“广度”问题。
混合检索 Pipeline：
实现 Hybrid Search：同时检索向量库（指南背景知识）和关键词库（说明书细节）。
引入 Rerank 机制：使用 BGE-Reranker 对初筛结果进行精排，只保留 Top-3 喂给模型。
GraphRAG 链路：
实现 Text-to-Cypher 模块：LLM 根据用户问题查询 Neo4j 中的硬指标（如：eGFR 阈值、药物禁忌）。
数据融合： 将 Neo4j 查询出的“硬规则”与 RAG 检索出的“软知识”进行 Context 拼接。
阶段三：基于 LangGraph 的 Agent 编排（系统复杂度体现）
目标： 模拟医生真实的临床决策流程。
使用 LangGraph 构建以下工作流节点（Node）：
意图识别 Node (The Planner)： 判断用户是想查指标、咨询生活建议、还是上传了报告。
感知 Node (Multimodal)： 若有图片，调用 OCR/Qwen2-VL 提取化验单数值（如血糖、肌酐、eGFR）。
决策 Node (The Reasoner)： 整合检索到的指南、图谱规则和患者数据，使用 CoT (思维链) 进行诊断推理。
安全审计 Node (The Auditor) —— [核心亮点]：
逻辑： 无论 Reasoner 给什么结论，Auditor 强制去图谱里对一次“红线规则”。
冲突处理： 如果 Reasoner 建议用药，但 Auditor 查到 eGFR 冲突，则触发“Reflexion（反思机制）”，打回重做。
阶段四：领域指令微调 SFT（算法深度体现）
目标： 提升模型在医学对话中的语气对齐和逻辑严谨性。
构造数据集 (5k-10k 条)：
KG-to-Text 数据： 根据 120 个药品的图谱逻辑构造对话。
指南问诊数据： 根据指南生成生活管理、饮食指导问答。
思维链数据： 包含“分析过程”的对话。
执行微调：
使用 LLaMA-Factory 框架。
基座模型：Qwen2.5-7B。
技术路径：QLoRA（省显存）+ DPO（偏好对齐，强化严谨回答，弱化模糊回答）。
阶段五：评测、工程优化与可视化（闭环展示）
目标： 用数据说话，展示系统性能。
自动化评测 (Ragas Framework)：
使用 Ragas 对系统的 Faithfulness（忠实度）、Answer Correctness（回答正确率） 进行评测。
做对比实验： 原始 Qwen2.5 vs RAG 版 vs 你的 Dia-Agent (GraphRAG+Agent 版)。
推理加速：
使用 vLLM 部署模型。
测试并发情况下的 TTFT（首字延迟）并进行量化（4-bit）。
Demo 展示：
使用 Streamlit 搭一个简单的问诊界面，展示 Agent 的思考路径（Thinking Process）。
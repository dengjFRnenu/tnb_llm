#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangChain Text-to-Cypher 检索器
基于 LangChain 实现的增强版 Text-to-Cypher，支持：
1. Schema 信息注入到 Prompt
2. Few-shot 示例动态选择
3. 查询失败回退机制
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from neo4j import GraphDatabase
import re

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent


@dataclass
class CypherResult:
    """Cypher 查询结果"""
    success: bool
    cypher: Optional[str] = None
    results: List[Dict] = None
    error: Optional[str] = None
    fallback_used: bool = False
    source: str = "llm"  # "llm", "example_match", "fallback"
    
    def __post_init__(self):
        if self.results is None:
            self.results = []


class LangChainCypherRetriever:
    """
    LangChain 增强的 Text-to-Cypher 检索器
    
    特点:
    1. Prompt 包含完整 Schema 信息
    2. 动态选择最相关的 Few-shot 示例
    3. 多层回退机制（LLM -> 示例匹配 -> 预定义模板）
    """
    
    # 预定义的回退查询模板
    FALLBACK_TEMPLATES = {
        "drug_search": {
            "keywords": ["药物", "药品", "降糖药"],
            "cypher": "MATCH (d:Drug) RETURN d.name AS 药品名称 LIMIT 20"
        },
        "egfr_contraindication": {
            "keywords": ["eGFR", "egfr", "肾功能", "肾"],
            "cypher": """MATCH (d:Drug)-[r:CONTRAINDICATED_IF]->(m:Metric {name: 'eGFR'})
RETURN d.name AS 药品名称, r.operator AS 运算符, r.value AS 阈值, r.severity AS 严重程度
ORDER BY r.value"""
        },
        "category_search": {
            "keywords": ["分类", "类型", "有哪些", "种类"],
            "cypher": "MATCH (c:Category)<-[:BELONGS_TO]-(d:Drug) RETURN c.name AS 分类, COLLECT(d.name) AS 药品列表"
        },
        "disease_contraindication": {
            "keywords": ["禁忌", "禁用", "不能用", "不能使用"],
            "cypher": """MATCH (d:Drug)-[r:FORBIDDEN_FOR]->(dis:Disease)
RETURN d.name AS 药品名称, dis.name AS 禁忌疾病, r.severity AS 严重程度
LIMIT 50"""
        }
    }
    
    def __init__(
        self,
        schema_path: str = None,
        examples_path: str = None,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password123",
        llm_api: Callable[[str], str] = None
    ):
        """
        初始化检索器
        
        Args:
            schema_path: Schema JSON 文件路径
            examples_path: Few-shot 示例 JSON 文件路径
            neo4j_uri: Neo4j 连接 URI
            neo4j_user: Neo4j 用户名
            neo4j_password: Neo4j 密码
            llm_api: LLM API 调用函数 (接收 prompt, 返回响应文本)
        """
        # 默认路径
        if schema_path is None:
            schema_path = str(PROJECT_ROOT / "configs" / "schema.json")
        if examples_path is None:
            examples_path = str(PROJECT_ROOT / "configs" / "few_shot_examples.json")
        
        # 加载 Schema
        print("📋 加载知识图谱 Schema...")
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
        
        # 加载 Few-shot 示例
        print("📚 加载 Few-shot 示例...")
        with open(examples_path, 'r', encoding='utf-8') as f:
            examples_data = json.load(f)
            self.examples = examples_data['examples']
            self.prompt_template = examples_data['prompt_template']
        
        # 连接 Neo4j
        self.driver = None
        print(f"🔌 连接 Neo4j: {neo4j_uri}")
        try:
            self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            self.driver.verify_connectivity()
            print("✅ Neo4j 连接成功")
        except Exception as e:
            print(f"⚠️  Neo4j 连接失败: {e}")
            print("   查询将使用回退模式")
        
        # LLM API
        self.llm_api = llm_api
        
        # 构建 Schema 描述字符串（用于 Prompt）
        self.schema_description = self._build_schema_description()
        
        print("✅ LangChain Cypher 检索器初始化完成")
    
    def _build_schema_description(self) -> str:
        """构建 Schema 描述字符串，供 LLM 使用"""
        lines = ["### 知识图谱结构\n"]
        
        # 节点描述
        lines.append("#### 节点类型:")
        for node_name, node_info in self.schema.get('nodes', {}).items():
            props = ", ".join([
                f"{p}: {info.get('type', 'string')}" 
                for p, info in node_info.get('properties', {}).items()
            ])
            lines.append(f"- **{node_name}** ({node_info.get('label', '')}): {node_info.get('description', '')}")
            lines.append(f"  属性: {props}")
        
        lines.append("\n#### 关系类型:")
        for rel_name, rel_info in self.schema.get('relationships', {}).items():
            lines.append(f"- **{rel_name}**: {rel_info.get('description', '')}")
            lines.append(f"  ({rel_info.get('source', '')}) -[:{rel_name}]-> ({rel_info.get('target', '')})")
            if rel_info.get('properties'):
                props = ", ".join(rel_info['properties'].keys())
                lines.append(f"  属性: {props}")
            if rel_info.get('example'):
                lines.append(f"  示例: `{rel_info['example']}`")
        
        return "\n".join(lines)
    
    def _select_relevant_examples(self, question: str, top_k: int = 3) -> List[Dict]:
        """
        基于问题相似度选择最相关的 Few-shot 示例
        使用关键词权重匹配
        """
        import jieba
        
        # 关键词权重
        KEYWORD_WEIGHTS = {
            'eGFR': 3, 'egfr': 3, '肾功能': 3,
            '小于': 2, '<': 2, '大于': 2, '>': 2,
            '禁用': 3, '禁忌': 3, '不能': 2,
            '药物': 2, '药品': 2, '哪些': 1,
            '双胍': 3, 'SGLT2': 3, 'GLP-1': 3, 'DPP-4': 3,
            '分类': 2, '类型': 2, '属于': 2,
            '心力衰竭': 3, '肝功能': 3,
            '二甲双胍': 3, '格列': 2,
            '30': 2, '45': 2, '60': 2,
            '监测': 2, '调整': 2, '剂量': 2,
        }
        
        def extract_keywords(text):
            words = set(jieba.cut(text))
            # 添加特殊关键词
            for kw in KEYWORD_WEIGHTS.keys():
                if kw.lower() in text.lower():
                    words.add(kw)
            return words
        
        def calculate_score(q1, q2):
            kw1 = extract_keywords(q1)
            kw2 = extract_keywords(q2)
            intersection = kw1 & kw2
            if not intersection:
                return 0
            return sum(KEYWORD_WEIGHTS.get(w, 1) for w in intersection)
        
        # 计算每个示例的相似度分数
        scored_examples = []
        for example in self.examples:
            score = calculate_score(question, example['question'])
            scored_examples.append((score, example))
        
        # 按分数排序，返回 top_k
        scored_examples.sort(key=lambda x: x[0], reverse=True)
        return [ex for _, ex in scored_examples[:top_k]]
    
    def _build_prompt(self, question: str, num_examples: int = 3) -> str:
        """
        构建完整的 Prompt
        包含: System Prompt + Schema + Few-shot Examples + User Question
        """
        # System Prompt
        system_prompt = self.prompt_template.get('system', '').format(schema=self.schema_description)
        
        # 选择相关示例
        selected_examples = self._select_relevant_examples(question, num_examples)
        
        # 格式化示例
        examples_text = ""
        for i, ex in enumerate(selected_examples, 1):
            examples_text += self.prompt_template.get('few_shot_format', '').format(
                index=i,
                question=ex['question'],
                cypher=ex['cypher'],
                explanation=ex.get('explanation', '')
            )
        
        # User Question
        user_prompt = self.prompt_template.get('user_template', '').format(user_question=question)
        
        # 组合完整 Prompt
        full_prompt = f"{system_prompt}\n\n{examples_text}\n{user_prompt}"
        
        return full_prompt
    
    def _validate_cypher(self, cypher: str) -> Tuple[bool, str]:
        """验证 Cypher 安全性"""
        FORBIDDEN = ['CREATE', 'DELETE', 'REMOVE', 'SET', 'MERGE', 'DROP', 'DETACH', 'ALTER']
        cypher_upper = cypher.upper()
        
        for kw in FORBIDDEN:
            if kw in cypher_upper:
                return False, f"检测到危险操作: {kw}"
        
        if 'MATCH' not in cypher_upper:
            return False, "缺少 MATCH 子句"
        if 'RETURN' not in cypher_upper:
            return False, "缺少 RETURN 子句"
        
        return True, ""
    
    def _extract_cypher(self, text: str) -> str:
        """从 LLM 输出中提取 Cypher 代码"""
        # 尝试提取代码块
        patterns = [
            r'```cypher\s*\n(.*?)\n```',
            r'```\s*\n(.*?)\n```',
            r'```(.*?)```',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # 如果没有代码块，返回原文本
        return text.strip()
    
    def _execute_cypher(self, cypher: str) -> List[Dict]:
        """执行 Cypher 查询"""
        if not self.driver:
            raise RuntimeError("Neo4j 未连接")
        
        with self.driver.session() as session:
            result = session.run(cypher)
            return [record.data() for record in result]
    
    def _find_fallback_template(self, question: str) -> Optional[str]:
        """根据问题找到合适的回退模板"""
        question_lower = question.lower()
        
        best_match = None
        best_count = 0
        
        for template_name, template_info in self.FALLBACK_TEMPLATES.items():
            keywords = template_info['keywords']
            match_count = sum(1 for kw in keywords if kw.lower() in question_lower)
            if match_count > best_count:
                best_count = match_count
                best_match = template_info['cypher']
        
        return best_match if best_count > 0 else None
    
    def query(self, question: str, use_llm: bool = True) -> CypherResult:
        """
        执行 Text-to-Cypher 查询
        
        回退策略:
        1. 尝试使用 LLM 生成 Cypher
        2. 如果 LLM 失败，尝试从示例库匹配
        3. 如果示例匹配失败，使用预定义模板
        
        Args:
            question: 自然语言问题
            use_llm: 是否使用 LLM（如果为 False，跳过步骤1）
        
        Returns:
            CypherResult 对象
        """
        print(f"\n{'='*60}")
        print(f"📝 Text-to-Cypher 查询: {question}")
        print(f"{'='*60}")
        
        cypher = None
        source = "llm"
        
        # 步骤1: 尝试使用 LLM 生成
        if use_llm and self.llm_api:
            print("🤖 [步骤1] 使用 LLM 生成 Cypher...")
            try:
                prompt = self._build_prompt(question)
                response = self.llm_api(prompt)
                cypher = self._extract_cypher(response)
                
                # 验证
                is_valid, error = self._validate_cypher(cypher)
                if not is_valid:
                    print(f"  ❌ LLM 生成的 Cypher 无效: {error}")
                    cypher = None
                else:
                    print(f"  ✅ LLM 生成成功")
                    source = "llm"
            except Exception as e:
                print(f"  ⚠️ LLM 调用失败: {e}")
                cypher = None
        
        # 步骤2: 尝试从示例库匹配
        if cypher is None:
            print("📚 [步骤2] 从示例库匹配...")
            selected = self._select_relevant_examples(question, top_k=1)
            if selected and self._calculate_similarity(question, selected[0]['question']) > 0.2:
                cypher = selected[0]['cypher']
                print(f"  ✅ 匹配到示例: {selected[0]['question'][:40]}...")
                source = "example_match"
            else:
                print("  ⚠️ 未找到足够相似的示例")
        
        # 步骤3: 使用回退模板
        if cypher is None:
            print("🔄 [步骤3] 使用回退模板...")
            cypher = self._find_fallback_template(question)
            if cypher:
                print(f"  ✅ 找到回退模板")
                source = "fallback"
            else:
                print("  ❌ 无可用回退模板")
                return CypherResult(
                    success=False,
                    error="无法生成有效的 Cypher 查询",
                    fallback_used=True
                )
        
        # 执行查询
        print(f"\n📊 执行 Cypher 查询 (来源: {source}):")
        print(f"   {cypher[:100]}..." if len(cypher) > 100 else f"   {cypher}")
        
        if not self.driver:
            return CypherResult(
                success=False,
                cypher=cypher,
                error="Neo4j 未连接",
                source=source
            )
        
        try:
            results = self._execute_cypher(cypher)
            print(f"  ✅ 查询成功，返回 {len(results)} 条结果")
            
            return CypherResult(
                success=True,
                cypher=cypher,
                results=results,
                source=source,
                fallback_used=(source != "llm")
            )
        except Exception as e:
            print(f"  ❌ 查询执行失败: {e}")
            return CypherResult(
                success=False,
                cypher=cypher,
                error=str(e),
                source=source
            )
    
    def _calculate_similarity(self, q1: str, q2: str) -> float:
        """计算两个问题的相似度"""
        import jieba
        
        words1 = set(jieba.cut(q1))
        words2 = set(jieba.cut(q2))
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
    
    def __del__(self):
        self.close()


# ============================================
# 便捷函数
# ============================================

def create_cypher_retriever(
    neo4j_uri: str = "bolt://localhost:7687",
    neo4j_user: str = "neo4j",
    neo4j_password: str = "password123",
    llm_api: Callable[[str], str] = None
) -> LangChainCypherRetriever:
    """
    创建 Cypher 检索器的便捷函数
    
    Args:
        neo4j_uri: Neo4j 连接 URI
        neo4j_user: Neo4j 用户名
        neo4j_password: Neo4j 密码
        llm_api: LLM API 调用函数
    
    Returns:
        LangChainCypherRetriever 实例
    """
    return LangChainCypherRetriever(
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
        llm_api=llm_api
    )


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 LangChain Cypher 检索器测试")
    print("=" * 60)
    
    # 创建检索器（不使用 LLM，测试回退机制）
    retriever = LangChainCypherRetriever()
    
    # 测试查询
    test_questions = [
        "eGFR小于30的患者不能使用哪些药物？",
        "双胍类药物有哪些？",
        "心力衰竭患者禁用哪些药物？",
        "二甲双胍有哪些禁忌症？",
    ]
    
    for question in test_questions:
        result = retriever.query(question, use_llm=False)
        print(f"\n📋 结果摘要:")
        print(f"  成功: {result.success}")
        print(f"  来源: {result.source}")
        print(f"  结果数: {len(result.results)}")
        if result.results:
            print(f"  前3条: {result.results[:3]}")
        print()
    
    retriever.close()
    print("✅ 测试完成")

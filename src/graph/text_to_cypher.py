#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text-to-Cypher 引擎 - 自然语言转 Neo4j 查询
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from neo4j import GraphDatabase
import re


class TextToCypherEngine:
    """Text-to-Cypher 转换引擎"""
    
    def __init__(self, 
                 schema_path: str = "schema.json",
                 examples_path: str = "text_to_cypher_examples.json",
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j",
                 neo4j_password: str = "password123"):
        """
        初始化 Text-to-Cypher 引擎
        
        Args:
            schema_path: Schema 文件路径
            examples_path: Few-shot 示例路径
            neo4j_uri: Neo4j 连接 URI
            neo4j_user: 用户名
            neo4j_password: 密码
        """
        print("🔧 初始化 Text-to-Cypher 引擎...")
        
        # 加载 Schema
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
        
        # 加载 Few-shot 示例
        with open(examples_path, 'r', encoding='utf-8') as f:
            self.examples_data = json.load(f)
            self.examples = self.examples_data['examples']
            self.prompt_template = self.examples_data['prompt_template']
        
        # 连接 Neo4j
        try:
            self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            self.driver.verify_connectivity()
            print("✅ Neo4j 连接成功")
        except Exception as e:
            print(f"⚠️  Neo4j 连接失败: {e}")
            print("   Text-to-Cypher 功能将受限（可生成但无法执行）")
            self.driver = None
        
        print("✅ Text-to-Cypher 引擎就绪")
    
    def __del__(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
    
    def build_few_shot_prompt(self, user_question: str, num_examples: int = 3) -> str:
        """
        构建 Few-shot Prompt
        
        Args:
            user_question: 用户问题
            num_examples: 使用的示例数量
        
        Returns:
            完整的 Prompt
        """
        # 系统 Prompt（包含 Schema）
        schema_str = json.dumps(self.schema, ensure_ascii=False, indent=2)
        system_prompt = self.prompt_template['system'].format(schema=schema_str)
        
        # Few-shot 示例（简化版，实际应用中可用向量检索选择最相关的示例）
        few_shot_examples = ""
        for i, example in enumerate(self.examples[:num_examples], 1):
            few_shot_examples += self.prompt_template['few_shot_format'].format(
                index=i,
                question=example['question'],
                cypher=example['cypher'],
                explanation=example['explanation']
            )
        
        # 用户问题
        user_prompt = self.prompt_template['user_template'].format(user_question=user_question)
        
        # 组合完整 Prompt
        full_prompt = f"{system_prompt}\n\n{few_shot_examples}\n{user_prompt}"
        return full_prompt
    
    @staticmethod
    def validate_cypher(cypher: str) -> Tuple[bool, str]:
        """
        验证 Cypher 安全性（只允许只读查询）
        
        Args:
            cypher: Cypher 查询语句
        
        Returns:
            (是否安全, 错误信息)
        """
        # 危险关键词黑名单
        FORBIDDEN_KEYWORDS = [
            'CREATE', 'DELETE', 'REMOVE', 'SET', 
            'MERGE', 'DROP', 'DETACH', 'ALTER'
        ]
        
        cypher_upper = cypher.upper()
        
        for keyword in FORBIDDEN_KEYWORDS:
            if keyword in cypher_upper:
                return False, f"检测到危险操作: {keyword}（仅允许只读查询）"
        
        # 必须包含 MATCH 和 RETURN
        if 'MATCH' not in cypher_upper:
            return False, "Cypher 必须包含 MATCH 子句"
        
        if 'RETURN' not in cypher_upper:
            return False, "Cypher 必须包含 RETURN 子句"
        
        return True, ""
    
    def generate_cypher(self, user_question: str, llm_api_function=None) -> Optional[str]:
        """
        生成 Cypher 查询
        
        Args:
            user_question: 用户问题
            llm_api_function: LLM API 调用函数（接收 prompt，返回生成的 Cypher）
                             如果为 None，使用规则匹配示例库
        
        Returns:
            生成的 Cypher 查询（已验证），如果失败返回 None
        """
        # 如果没有提供 LLM API，尝试从示例库中精确匹配或模糊匹配
        if llm_api_function is None:
            print("  ℹ️  未提供 LLM API，尝试从示例库匹配...")
            return self._match_from_examples(user_question)
        
        # 构建 Prompt
        prompt = self.build_few_shot_prompt(user_question, num_examples=3)
        
        # 调用 LLM
        print("  🤖 调用 LLM 生成 Cypher...")
        cypher = llm_api_function(prompt)
        
        # 清理和提取 Cypher（去除可能的 Markdown 标记）
        cypher = self._extract_cypher(cypher)
        
        # 安全验证
        is_safe, error_msg = self.validate_cypher(cypher)
        if not is_safe:
            print(f"  ❌ Cypher 验证失败: {error_msg}")
            return None
        
        return cypher
    
    def _match_from_examples(self, user_question: str) -> Optional[str]:
        """从示例库中匹配最相似的问题（使用jieba分词和关键词权重）"""
        import jieba
        
        # 重要关键词及其权重
        KEYWORD_WEIGHTS = {
            'eGFR': 3, 'egfr': 3, 'EGFR': 3,
            '小于': 2, '<': 2, '大于': 2, '>': 2,
            '禁用': 3, '禁忌': 3, '不能': 2, '不可': 2,
            '药物': 2, '药品': 2, '哪些': 1,
            '双胍': 3, 'SGLT2': 3, 'GLP-1': 3, '磺脲': 3,
            '分类': 2, '类型': 2, '属于': 2,
            '心力衰竭': 3, '肾功能': 3, '肝功能': 3,
            '二甲双胍': 3, '格列': 2,
            '30': 2, '45': 2, '60': 2,
            '适应症': 2, '治疗': 2,
        }
        
        def extract_keywords(text):
            """提取关键词"""
            words = list(jieba.cut(text))
            # 添加原文中的特殊关键词
            for kw in KEYWORD_WEIGHTS.keys():
                if kw.lower() in text.lower():
                    words.append(kw)
            return set(words)
        
        def calculate_similarity(q1, q2):
            """计算问题相似度（加权Jaccard）"""
            kw1 = extract_keywords(q1)
            kw2 = extract_keywords(q2)
            
            intersection_score = sum(KEYWORD_WEIGHTS.get(w, 1) for w in kw1 & kw2)
            union_score = sum(KEYWORD_WEIGHTS.get(w, 1) for w in kw1 | kw2)
            
            return intersection_score / union_score if union_score > 0 else 0
        
        best_match = None
        best_score = 0
        
        for example in self.examples:
            score = calculate_similarity(user_question, example['question'])
            if score > best_score:
                best_score = score
                best_match = example
        
        if best_match and best_score >= 0.15:
            print(f"  ✅ 匹配到示例 (相似度: {best_score:.2f}): {best_match['question'][:40]}...")
            return best_match['cypher']
        else:
            print(f"  ⚠️  最佳匹配相似度不足 ({best_score:.2f})")
            return None
    
    @staticmethod
    def _extract_cypher(text: str) -> str:
        """从 LLM 输出中提取 Cypher 代码"""
        # 尝试提取 ```cypher ... ``` 或 ``` ... ``` 块
        pattern = r'```(?:cypher)?\s*\n(.*?)\n```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # 如果没有代码块，返回原文本（去除首尾空白）
        return text.strip()
    
    def execute_cypher(self, cypher: str) -> List[Dict]:
        """
        执行 Cypher 查询
        
        Args:
            cypher: Cypher 查询语句
        
        Returns:
            查询结果列表
        """
        if not self.driver:
            raise RuntimeError("Neo4j 未连接，无法执行查询")
        
        # 安全验证
        is_safe, error_msg = self.validate_cypher(cypher)
        if not is_safe:
            raise ValueError(f"不安全的 Cypher 查询: {error_msg}")
        
        # 执行查询
        with self.driver.session() as session:
            result = session.run(cypher)
            records = [record.data() for record in result]
        
        return records
    
    def query(self, user_question: str, llm_api_function=None) -> Dict:
        """
        端到端查询：问题 -> Cypher -> 结果
        
        Args:
            user_question: 用户问题
            llm_api_function: LLM API 函数
        
        Returns:
            {
                'question': str,
                'cypher': str,
                'results': List[Dict],
                'success': bool,
                'error': str (if failed)
            }
        """
        response = {
            'question': user_question,
            'cypher': None,
            'results': [],
            'success': False,
            'error': None
        }
        
        try:
            # 生成 Cypher
            cypher = self.generate_cypher(user_question, llm_api_function)
            if not cypher:
                response['error'] = "无法生成有效的 Cypher 查询"
                return response
            
            response['cypher'] = cypher
            
            # 执行查询
            if self.driver:
                results = self.execute_cypher(cypher)
                response['results'] = results
                response['success'] = True
            else:
                response['error'] = "Neo4j 未连接，无法执行查询"
        
        except Exception as e:
            response['error'] = str(e)
        
        return response
    
    def format_results(self, results: List[Dict]) -> str:
        """
        格式化查询结果为文本
        
        Args:
            results: Neo4j 查询结果
        
        Returns:
            格式化的文本
        """
        if not results:
            return "（未查询到相关信息）"
        
        formatted = []
        for i, record in enumerate(results, 1):
            items = [f"{key}: {value}" for key, value in record.items()]
            formatted.append(f"{i}. {', '.join(items)}")
        
        return '\n'.join(formatted)


# 测试代码
if __name__ == "__main__":
    # 初始化引擎
    engine = TextToCypherEngine()
    
    # 测试问题
    test_questions = [
        "eGFR小于30的患者不能使用哪些药物？",
        "有哪些SGLT2抑制剂？",
        "二甲双胍有哪些禁忌症？"
    ]
    
    print(f"\n{'='*60}")
    print("Text-to-Cypher 测试")
    print(f"{'='*60}")
    
    for question in test_questions:
        print(f"\n【问题】{question}")
        
        # 查询（使用示例匹配模式）
        response = engine.query(question)
        
        if response['success']:
            print(f"\n【生成的 Cypher】\n{response['cypher']}")
            print(f"\n【查询结果】\n{engine.format_results(response['results'])}")
        else:
            print(f"\n【错误】{response['error']}")
            if response['cypher']:
                print(f"【生成的 Cypher】\n{response['cypher']}")

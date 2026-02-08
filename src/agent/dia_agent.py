#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dia-Agent 糖尿病智能诊疗助手
整合 GraphRAG、病例分析、风险检测、决策融合的完整系统
"""

import sys
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agent.patient_profile import PatientProfile, create_patient_profile
from src.agent.case_analyzer import CaseAnalyzer
from src.agent.risk_detector import RiskDetector, RiskReport
from src.agent.decision_fusion import DecisionFusion, ClinicalReport
from src.retrieval.hybrid import HybridRetriever
from src.retrieval.reranker import BGEReranker
from src.graph.langchain_cypher import LangChainCypherRetriever


class DiaAgent:
    """
    Dia-Agent 糖尿病智能诊疗助手
    
    核心功能:
    1. 病例分析: 从病历文本提取结构化患者画像
    2. 风险检测: 基于知识图谱检测用药禁忌
    3. 指南检索: 使用混合检索获取相关指南内容
    4. 决策融合: 整合多源证据生成诊疗建议
    """
    
    def __init__(
        self,
        chroma_path: str = None,
        collection_name: str = "diabetes_guidelines_2024",
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password123",
        llm_api: Callable[[str], str] = None,
        verbose: bool = True
    ):
        """
        初始化 Dia-Agent
        
        Args:
            chroma_path: ChromaDB 路径
            collection_name: 向量集合名称
            neo4j_uri: Neo4j 连接 URI
            neo4j_user: Neo4j 用户名
            neo4j_password: Neo4j 密码
            llm_api: LLM API 调用函数
            verbose: 是否输出详细日志
        """
        self.verbose = verbose
        self.llm_api = llm_api
        
        if chroma_path is None:
            chroma_path = str(PROJECT_ROOT / "chroma_db")
        
        self._log("=" * 60)
        self._log("🤖 初始化 Dia-Agent 糖尿病智能诊疗助手")
        self._log("=" * 60)
        
        # 初始化各模块
        self._log("\n📦 加载模块...")
        
        # 1. 病例分析器
        self._log("  ├─ CaseAnalyzer")
        self.case_analyzer = CaseAnalyzer(llm_api=llm_api)
        
        # 2. 风险检测器
        self._log("  ├─ RiskDetector")
        self.risk_detector = RiskDetector(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password
        )
        
        # 3. 混合检索器
        self._log("  ├─ HybridRetriever")
        self.hybrid_retriever = HybridRetriever(
            chroma_path=chroma_path,
            collection_name=collection_name
        )
        
        # 4. Reranker
        self._log("  ├─ BGEReranker")
        self.reranker = BGEReranker()
        
        # 5. Text-to-Cypher
        self._log("  ├─ CypherRetriever")
        self.cypher_retriever = LangChainCypherRetriever(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password,
            llm_api=llm_api
        )
        
        # 6. 决策融合器
        self._log("  └─ DecisionFusion")
        self.decision_fusion = DecisionFusion(llm_api=llm_api)
        
        self._log("\n✅ Dia-Agent 初始化完成!")
    
    def _log(self, message: str):
        """日志输出"""
        if self.verbose:
            print(message)
    
    def analyze_case(self, case_text: str) -> PatientProfile:
        """
        分析病历文本
        
        Args:
            case_text: 病历文本
        
        Returns:
            PatientProfile 患者画像
        """
        self._log("\n" + "=" * 60)
        self._log("📋 [步骤 1/4] 病例分析")
        self._log("=" * 60)
        
        profile = self.case_analyzer.analyze(case_text)
        
        self._log(f"\n提取的患者画像:")
        self._log(profile.to_clinical_summary())
        
        return profile
    
    def detect_risks(self, profile: PatientProfile) -> RiskReport:
        """
        检测用药风险
        
        Args:
            profile: 患者画像
        
        Returns:
            RiskReport 风险报告
        """
        self._log("\n" + "=" * 60)
        self._log("⚠️ [步骤 2/4] 风险检测")
        self._log("=" * 60)
        
        report = self.risk_detector.detect_risks(profile)
        
        if report.warnings:
            self._log(f"\n检测到 {len(report.warnings)} 个风险:")
            for w in report.warnings:
                self._log(f"  • [{w.severity.value}] {w.drug_name}: {w.reason}")
        else:
            self._log("\n✅ 未检测到用药风险")
        
        return report
    
    def retrieve_guidelines(self, query: str, profile: PatientProfile = None, top_k: int = 3) -> str:
        """
        检索相关指南内容
        
        Args:
            query: 检索查询
            profile: 患者画像（用于生成额外查询）
            top_k: 返回文档数
        
        Returns:
            合并的指南内容
        """
        self._log("\n" + "=" * 60)
        self._log("📚 [步骤 3/4] 指南检索")
        self._log("=" * 60)
        
        # 生成多个查询
        queries = [query]
        if profile:
            # 基于患者画像生成额外查询
            if profile.has_severe_renal_impairment:
                queries.append("肾功能不全糖尿病患者用药指南")
            if profile.glycemic.hba1c and profile.glycemic.hba1c > 8:
                queries.append("HbA1c控制不佳的强化治疗方案")
            if any('心' in c.name for c in profile.complications):
                queries.append("糖尿病合并心血管疾病用药")
        
        all_results = []
        for q in queries[:2]:  # 最多2个查询（优化：减少查询次数）
            self._log(f"  🔍 查询: {q[:40]}...")
            results = self.hybrid_retriever.retrieve(q, top_k=3)  # 优化：减少候选数
            all_results.extend(results)
        
        # 去重
        seen = set()
        unique_results = []
        for r in all_results:
            doc_id = r.get('id', r.get('document', '')[:50])
            if doc_id not in seen:
                seen.add(doc_id)
                unique_results.append(r)
        
        # Rerank（优化：限制最大候选数为5）
        if unique_results:
            unique_results = unique_results[:5]  # 限制 Rerank 输入数量
            self._log(f"  📊 Rerank {len(unique_results)} 篇文档...")
            reranked = self.reranker.rerank(query, unique_results, top_k=min(top_k, 2))
            
            # 合并内容
            context_parts = []
            for i, doc in enumerate(reranked, 1):
                header = doc.get('metadata', {}).get('header', '未知章节')
                page = doc.get('metadata', {}).get('page', '?')
                content = doc.get('document', '')[:500]
                context_parts.append(f"【{header} - P.{page}】\n{content}")
            
            context = "\n\n".join(context_parts)
            self._log(f"  ✅ 返回 {len(reranked)} 篇相关文档")
            return context
        
        return ""
    
    def generate_report(
        self,
        profile: PatientProfile,
        risk_report: RiskReport,
        guideline_context: str
    ) -> ClinicalReport:
        """
        生成诊疗报告
        
        Args:
            profile: 患者画像
            risk_report: 风险报告
            guideline_context: 指南内容
        
        Returns:
            ClinicalReport 诊疗报告
        """
        self._log("\n" + "=" * 60)
        self._log("📝 [步骤 4/4] 决策融合与报告生成")
        self._log("=" * 60)
        
        report = self.decision_fusion.fuse(
            profile=profile,
            risk_report=risk_report,
            rag_context=guideline_context
        )
        
        self._log(f"\n生成 {len(report.recommendations)} 条诊疗建议")
        
        return report
    
    def consult(self, case_text: str) -> ClinicalReport:
        """
        完整诊疗流程
        
        Args:
            case_text: 病历文本
        
        Returns:
            ClinicalReport 完整诊疗报告
        """
        self._log("\n" + "=" * 60)
        self._log("🏥 Dia-Agent 智能诊疗咨询")
        self._log("=" * 60)
        
        # 1. 病例分析
        profile = self.analyze_case(case_text)
        
        # 2. 风险检测
        risk_report = self.detect_risks(profile)
        
        # 3. 指南检索
        # 构造检索查询
        if profile.current_medications:
            query = f"糖尿病患者使用{', '.join(profile.medication_names)}的注意事项"
        else:
            query = "糖尿病用药治疗指南"
        
        guideline_context = self.retrieve_guidelines(query, profile)
        
        # 4. 生成报告
        report = self.generate_report(profile, risk_report, guideline_context)
        
        self._log("\n" + "=" * 60)
        self._log("✅ 诊疗咨询完成!")
        self._log("=" * 60)
        
        return report
    
    def quick_risk_check(self, medications: List[str], egfr: float = None, complications: List[str] = None) -> RiskReport:
        """
        快速用药风险检查
        
        Args:
            medications: 用药列表
            egfr: eGFR 值
            complications: 并发症列表
        
        Returns:
            RiskReport 风险报告
        """
        profile = create_patient_profile(
            egfr=egfr,
            medications=medications,
            complications=complications or []
        )
        
        return self.risk_detector.detect_risks(profile)
    
    def query_drug_info(self, drug_name: str) -> Dict:
        """
        查询药品信息
        
        Args:
            drug_name: 药品名称
        
        Returns:
            药品信息字典
        """
        # 查询知识图谱
        result = self.cypher_retriever.query(f"{drug_name}有哪些禁忌症？")
        
        return {
            "drug": drug_name,
            "cypher": result.cypher,
            "contraindications": result.results,
            "source": result.source
        }
    
    def close(self):
        """关闭所有连接"""
        self.risk_detector.close()
        self.cypher_retriever.close()
        self._log("🔌 Dia-Agent 已关闭")


# ============================================
# 便捷函数
# ============================================

def create_dia_agent(
    llm_api: Callable[[str], str] = None,
    verbose: bool = True
) -> DiaAgent:
    """
    创建 Dia-Agent 实例
    
    Args:
        llm_api: LLM API 调用函数
        verbose: 是否输出日志
    
    Returns:
        DiaAgent 实例
    """
    return DiaAgent(llm_api=llm_api, verbose=verbose)


# ============================================
# 测试
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧪 Dia-Agent 完整功能测试")
    print("=" * 70)
    
    # 测试病例
    test_case = """
    患者男，55岁，因"发现血糖升高10年，双下肢麻木3月"入院。
    
    现病史：患者10年前体检发现血糖升高，诊断2型糖尿病，长期服用二甲双胍0.5g tid、
    恩格列净10mg qd治疗。近3月出现双下肢麻木、感觉减退。近1周加重。
    
    既往史：高血压5年，服用氨氯地平5mg qd。2年前曾因胸闷就诊，诊断冠心病。
    
    查体：身高172cm，体重76kg，BP 138/85mmHg。双足痛觉减退。
    
    辅助检查：
    - HbA1c: 8.2%
    - FPG: 8.5 mmol/L
    - 肌酐: 168 μmol/L
    - eGFR: 38 mL/min/1.73m²
    - UACR: 210 mg/g
    
    诊断：
    1. 2型糖尿病
       糖尿病肾病 CKD 3b期
       糖尿病周围神经病变
    2. 高血压病2级
    3. 冠心病
    """
    
    # 创建 Agent
    agent = create_dia_agent(verbose=True)
    
    # 完整诊疗流程
    report = agent.consult(test_case)
    
    # 输出报告
    print("\n" + "=" * 70)
    print("📋 生成的诊疗报告:")
    print("=" * 70)
    print(report.to_markdown())
    
    # 关闭
    agent.close()

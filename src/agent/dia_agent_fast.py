#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dia-Agent 快速版 - 优化性能
减少模型加载和重复计算
"""

import sys
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List
import time

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class DiaAgentFast:
    """
    Dia-Agent 快速版
    
    优化点:
    1. 延迟加载模型
    2. 缓存嵌入结果
    3. 减少 Rerank 调用
    4. 简化检索流程
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """单例模式 - 避免重复加载模型"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        llm_api: Callable[[str], str] = None,
        verbose: bool = False,
        skip_reranker: bool = True,  # 跳过 Reranker 加速
        skip_rag: bool = False  # 跳过 RAG 检索
    ):
        # 避免重复初始化
        if DiaAgentFast._initialized and self.llm_api is not None:
            if llm_api:
                self.llm_api = llm_api
            return
        
        self.verbose = verbose
        self.llm_api = llm_api
        self.skip_reranker = skip_reranker
        self.skip_rag = skip_rag
        
        self._log("🚀 初始化 Dia-Agent (快速版)...")
        
        t0 = time.time()
        
        # 1. 核心模块 - 必须加载
        from src.agent.case_analyzer import CaseAnalyzer
        from src.agent.risk_detector import RiskDetector
        from src.agent.decision_fusion import DecisionFusion
        
        self.case_analyzer = CaseAnalyzer(llm_api=llm_api)
        self.risk_detector = RiskDetector()
        self.decision_fusion = DecisionFusion(llm_api=llm_api)
        
        # 2. 检索模块 - 可选
        self.hybrid_retriever = None
        self.reranker = None
        
        if not skip_rag:
            from src.retrieval.hybrid import HybridRetriever
            self.hybrid_retriever = HybridRetriever()
            
            if not skip_reranker:
                from src.retrieval.reranker import BGEReranker
                self.reranker = BGEReranker()
        
        t1 = time.time()
        self._log(f"✅ 初始化完成 ({t1-t0:.1f}s)")
        
        DiaAgentFast._initialized = True
    
    def _log(self, msg: str):
        if self.verbose:
            print(msg)
    
    def consult(self, case_text: str) -> 'ClinicalReport':
        """
        快速诊疗咨询
        
        优化流程:
        1. 病例分析 (规则提取，不调用 LLM)
        2. 风险检测 (知识图谱查询，<1s)
        3. 跳过 RAG 或简化检索
        4. 决策融合 (调用 LLM 生成建议)
        """
        from src.agent.patient_profile import create_patient_profile
        from src.agent.risk_detector import RiskReport
        
        t0 = time.time()
        
        # 1. 病例分析
        self._log("📋 分析病历...")
        profile = self.case_analyzer.analyze(case_text)
        t1 = time.time()
        self._log(f"  ✓ 病例分析完成 ({t1-t0:.1f}s)")
        
        # 2. 风险检测
        self._log("⚠️ 检测风险...")
        risk_report = self.risk_detector.detect_risks(profile)
        t2 = time.time()
        self._log(f"  ✓ 风险检测完成 ({t2-t1:.1f}s)")
        
        # 3. 指南检索 (简化版)
        guideline_context = ""
        if self.hybrid_retriever and not self.skip_rag:
            self._log("📚 检索指南...")
            query = f"糖尿病 {profile.ckd_stage or ''} 用药"
            results = self.hybrid_retriever.retrieve(query, top_k=3)
            
            if self.reranker and not self.skip_reranker:
                results = self.reranker.rerank(query, results, top_k=2)
            
            guideline_context = "\n".join([r.get('document', '')[:300] for r in results[:2]])
            t3 = time.time()
            self._log(f"  ✓ 指南检索完成 ({t3-t2:.1f}s)")
        else:
            t3 = t2
        
        # 4. 决策融合
        self._log("🤖 生成建议...")
        report = self.decision_fusion.fuse(
            profile=profile,
            risk_report=risk_report,
            rag_context=guideline_context
        )
        t4 = time.time()
        self._log(f"  ✓ 建议生成完成 ({t4-t3:.1f}s)")
        
        self._log(f"✅ 总耗时: {t4-t0:.1f}s")
        
        return report
    
    def quick_risk_check(
        self, 
        medications: List[str], 
        egfr: float = None,
        complications: List[str] = None
    ) -> 'RiskReport':
        """
        极速风险检查 - 只查询知识图谱
        """
        from src.agent.patient_profile import create_patient_profile
        
        profile = create_patient_profile(
            egfr=egfr,
            medications=medications,
            complications=complications or []
        )
        
        return self.risk_detector.detect_risks(profile)
    
    def close(self):
        """关闭连接"""
        if hasattr(self, 'risk_detector'):
            self.risk_detector.close()
        DiaAgentFast._initialized = False
        DiaAgentFast._instance = None


# ============================================
# 便捷函数
# ============================================

def get_fast_agent(llm_api: Callable = None, **kwargs) -> DiaAgentFast:
    """获取快速 Agent 单例"""
    return DiaAgentFast(llm_api=llm_api, **kwargs)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    from src.llm_client import create_llm_api
    
    print("=" * 60)
    print("⚡ Dia-Agent 快速版测试")
    print("=" * 60)
    
    llm = create_llm_api('siliconflow')
    
    # 第一次调用 - 包含初始化
    print("\n📋 首次调用...")
    t0 = time.time()
    agent = get_fast_agent(llm_api=llm, verbose=True, skip_rag=True)
    
    report = agent.consult("""
    患者男，55岁，2型糖尿病。
    用药：二甲双胍
    eGFR：28 mL/min
    """)
    t1 = time.time()
    print(f"\n首次调用耗时: {t1-t0:.1f}s")
    
    # 第二次调用 - 模型已加载
    print("\n📋 二次调用...")
    t2 = time.time()
    report = agent.consult("""
    患者女，60岁，2型糖尿病。
    用药：格列美脲
    eGFR：45 mL/min
    """)
    t3 = time.time()
    print(f"\n二次调用耗时: {t3-t2:.1f}s")
    
    agent.close()

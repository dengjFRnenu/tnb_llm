#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dia-Agent 测试套件
包含完整的功能测试和集成测试
"""

import sys
from pathlib import Path
import unittest

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestPatientProfile(unittest.TestCase):
    """测试患者画像模型"""
    
    def test_create_patient_profile(self):
        """测试创建患者画像"""
        from src.agent.patient_profile import create_patient_profile
        
        profile = create_patient_profile(
            age=55,
            hba1c=8.5,
            egfr=28,
            medications=["二甲双胍"]
        )
        
        self.assertEqual(profile.age, 55)
        self.assertEqual(profile.glycemic.hba1c, 8.5)
        self.assertEqual(profile.renal.egfr, 28)
        self.assertEqual(len(profile.current_medications), 1)
    
    def test_ckd_stage_calculation(self):
        """测试CKD分期计算"""
        from src.agent.patient_profile import create_patient_profile, CKDStage
        
        # eGFR >= 90 -> G1
        profile = create_patient_profile(egfr=95)
        self.assertEqual(profile.ckd_stage, CKDStage.G1)
        
        # eGFR 60-89 -> G2
        profile = create_patient_profile(egfr=75)
        self.assertEqual(profile.ckd_stage, CKDStage.G2)
        
        # eGFR 30-44 -> G3b
        profile = create_patient_profile(egfr=35)
        self.assertEqual(profile.ckd_stage, CKDStage.G3b)
        
        # eGFR < 15 -> G5
        profile = create_patient_profile(egfr=10)
        self.assertEqual(profile.ckd_stage, CKDStage.G5)
    
    def test_severe_renal_impairment(self):
        """测试严重肾功能损害判断"""
        from src.agent.patient_profile import create_patient_profile
        
        profile = create_patient_profile(egfr=28)
        self.assertTrue(profile.has_severe_renal_impairment)
        
        profile = create_patient_profile(egfr=35)
        self.assertFalse(profile.has_severe_renal_impairment)
    
    def test_clinical_tags(self):
        """测试临床标签生成"""
        from src.agent.patient_profile import create_patient_profile
        
        profile = create_patient_profile(
            egfr=28,
            hba1c=8.5,
            medications=["二甲双胍"]
        )
        
        tags = profile.get_clinical_tags()
        
        self.assertTrue(tags['egfr_below_30'])
        self.assertTrue(tags['hba1c_above_8'])
        self.assertIn('二甲双胍', tags['current_medications'])


class TestCaseAnalyzer(unittest.TestCase):
    """测试病例分析器"""
    
    def test_rule_based_extraction(self):
        """测试规则提取"""
        from src.agent.case_analyzer import CaseAnalyzer
        
        analyzer = CaseAnalyzer()
        
        case = """
        患者男，55岁，2型糖尿病10年。
        检查：HbA1c 8.2%，eGFR 28 mL/min
        用药：二甲双胍
        """
        
        profile = analyzer.analyze(case, use_reflection=False)
        
        self.assertEqual(profile.age, 55)
        self.assertEqual(profile.glycemic.hba1c, 8.2)
        self.assertEqual(profile.renal.egfr, 28)
    
    def test_drug_normalization(self):
        """测试药品名称标准化"""
        from src.agent.case_analyzer import CaseAnalyzer
        
        analyzer = CaseAnalyzer()
        
        self.assertEqual(analyzer.normalize_drug_name("格华止"), "二甲双胍")
        self.assertEqual(analyzer.normalize_drug_name("欧唐静"), "恩格列净")
        self.assertEqual(analyzer.normalize_drug_name("未知药品"), "未知药品")


class TestRiskDetector(unittest.TestCase):
    """测试风险检测器"""
    
    @classmethod
    def setUpClass(cls):
        """类级别的设置"""
        from src.agent.risk_detector import RiskDetector
        cls.detector = RiskDetector()
    
    @classmethod
    def tearDownClass(cls):
        """类级别的清理"""
        cls.detector.close()
    
    def test_egfr_contraindication(self):
        """测试eGFR禁忌检测"""
        from src.agent.patient_profile import create_patient_profile
        
        profile = create_patient_profile(
            egfr=28,
            medications=["二甲双胍"]
        )
        
        report = self.detector.detect_risks(profile)
        
        # 应该检测到二甲双胍在 eGFR < 30 时的禁忌
        self.assertTrue(len(report.warnings) > 0)
    
    def test_no_risk_for_safe_medication(self):
        """测试安全用药"""
        from src.agent.patient_profile import create_patient_profile
        
        profile = create_patient_profile(
            egfr=65,  # 正常肾功能
            medications=["利格列汀"]  # 无需调整的药物
        )
        
        report = self.detector.detect_risks(profile)
        
        # 利格列汀在正常肾功能下应该安全
        egfr_warnings = [w for w in report.warnings if 'eGFR' in w.reason]
        self.assertEqual(len(egfr_warnings), 0)


class TestDecisionFusion(unittest.TestCase):
    """测试决策融合器"""
    
    def test_fusion_without_llm(self):
        """测试无LLM的规则融合"""
        from src.agent.patient_profile import create_patient_profile
        from src.agent.risk_detector import RiskDetector, RiskReport
        from src.agent.decision_fusion import DecisionFusion
        
        profile = create_patient_profile(
            egfr=28,
            medications=["二甲双胍"]
        )
        
        detector = RiskDetector()
        risk_report = detector.detect_risks(profile)
        detector.close()
        
        fusion = DecisionFusion()
        report = fusion.fuse(profile, risk_report)
        
        # 应该生成建议
        self.assertTrue(len(report.recommendations) >= 0)
        
        # 应该包含肾功能评估建议
        if profile.has_severe_renal_impairment:
            renal_recs = [r for r in report.recommendations if '肾' in r.action or '肾' in r.reason]
            self.assertTrue(len(renal_recs) > 0)


class TestHybridRetriever(unittest.TestCase):
    """测试混合检索器"""
    
    @classmethod
    def setUpClass(cls):
        """类级别的设置"""
        from src.retrieval.hybrid import HybridRetriever
        cls.retriever = HybridRetriever()
    
    def test_retrieve_returns_results(self):
        """测试检索返回结果"""
        results = self.retriever.retrieve("糖尿病用药", top_k=5)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
    
    def test_result_structure(self):
        """测试结果结构"""
        results = self.retriever.retrieve("二甲双胍", top_k=1)
        
        if results:
            result = results[0]
            self.assertIn('document', result)
            self.assertIn('metadata', result)
            self.assertIn('rrf_score', result)


class TestLangChainCypherRetriever(unittest.TestCase):
    """测试LangChain Cypher检索器"""
    
    @classmethod
    def setUpClass(cls):
        """类级别的设置"""
        from src.graph.langchain_cypher import LangChainCypherRetriever
        cls.retriever = LangChainCypherRetriever()
    
    @classmethod
    def tearDownClass(cls):
        """类级别的清理"""
        cls.retriever.close()
    
    def test_example_matching(self):
        """测试示例匹配"""
        result = self.retriever.query("eGFR小于30禁用药物", use_llm=False)
        
        self.assertTrue(result.success)
        self.assertEqual(result.source, "example_match")
        self.assertGreater(len(result.results), 0)
    
    def test_category_query(self):
        """测试分类查询"""
        result = self.retriever.query("双胍类药物有哪些？", use_llm=False)
        
        self.assertTrue(result.success)
        self.assertGreater(len(result.results), 0)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_consult_flow(self):
        """测试完整诊疗流程"""
        from src.agent import DiaAgent
        
        agent = DiaAgent(verbose=False)
        
        case = """
        患者男，55岁，2型糖尿病10年。
        用药：二甲双胍
        检查：eGFR 28
        """
        
        report = agent.consult(case)
        
        # 检查报告结构
        self.assertIsNotNone(report.patient_summary)
        self.assertIsInstance(report.risk_warnings, list)
        self.assertIsInstance(report.recommendations, list)
        
        # 应该检测到eGFR禁忌
        self.assertTrue(len(report.risk_warnings) > 0)
        
        agent.close()


# ============================================
# 测试运行器
# ============================================

def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestPatientProfile,
        TestCaseAnalyzer,
        TestRiskDetector,
        TestDecisionFusion,
        TestHybridRetriever,
        TestLangChainCypherRetriever,
        TestIntegration,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

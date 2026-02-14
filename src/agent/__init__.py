#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dia-Agent 智能诊疗助手模块

核心组件:
- PatientProfile: 患者画像数据模型
- CaseAnalyzer: 病例分析器
- RiskDetector: 风险检测器
- DecisionFusion: 决策融合器
- DiaAgent: 主协调器
"""

from .patient_profile import (
    PatientProfile,
    Medication,
    Complication,
    VitalSigns,
    GlycemicIndicators,
    RenalIndicators,
    HepaticIndicators,
    LipidIndicators,
    CKDStage,
    CVRiskLevel,
    DiabetesType,
    create_patient_profile,
)

from .case_analyzer import CaseAnalyzer

from .risk_detector import (
    RiskDetector,
    RiskWarning,
    RiskReport,
    RiskSeverity,
)

from .decision_fusion import (
    DecisionFusion,
    ClinicalReport,
    Recommendation,
    EvidenceSource,
)

__all__ = [
    # 数据模型
    "PatientProfile",
    "Medication", 
    "Complication",
    "VitalSigns",
    "GlycemicIndicators",
    "RenalIndicators",
    "HepaticIndicators",
    "LipidIndicators",
    "CKDStage",
    "CVRiskLevel",
    "DiabetesType",
    "create_patient_profile",
    
    # 病例分析
    "CaseAnalyzer",
    
    # 风险检测
    "RiskDetector",
    "RiskWarning",
    "RiskReport",
    "RiskSeverity",
    
    # 决策融合
    "DecisionFusion",
    "ClinicalReport",
    "Recommendation",
    "EvidenceSource",
    
    # 主 Agent
    "DiaAgent",
    "create_dia_agent",
    "DiaAgentFast",
    "get_fast_agent",
]


def __getattr__(name):
    """对重量级模块使用延迟导入，减少包初始化耗时"""
    if name in {"DiaAgent", "create_dia_agent"}:
        from .dia_agent import DiaAgent, create_dia_agent
        mapping = {
            "DiaAgent": DiaAgent,
            "create_dia_agent": create_dia_agent,
        }
        return mapping[name]

    if name in {"DiaAgentFast", "get_fast_agent"}:
        from .dia_agent_fast import DiaAgentFast, get_fast_agent
        mapping = {
            "DiaAgentFast": DiaAgentFast,
            "get_fast_agent": get_fast_agent,
        }
        return mapping[name]

    raise AttributeError(f"module 'src.agent' has no attribute '{name}'")

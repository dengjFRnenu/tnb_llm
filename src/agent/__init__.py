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

from .dia_agent import DiaAgent, create_dia_agent


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
]

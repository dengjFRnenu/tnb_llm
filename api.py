#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dia-Agent FastAPI Web 服务接口
提供 RESTful API 访问智能诊疗功能
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path
import os

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agent.dia_agent_fast import DiaAgentFast
from src.llm_client import create_llm_api


# ============================================
# FastAPI 应用
# ============================================

app = FastAPI(
    title="Dia-Agent API",
    description="糖尿病智能诊疗助手 - RESTful API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================
# 请求/响应模型
# ============================================

class CaseAnalysisRequest(BaseModel):
    """病例分析请求"""
    case_text: str = Field(..., description="病历文本")
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_text": "患者男，55岁，2型糖尿病10年。当前用药：二甲双胍0.5g tid。检查：HbA1c 8.2%，eGFR 28 mL/min"
            }
        }


class QuickRiskCheckRequest(BaseModel):
    """快速风险检查请求"""
    medications: List[str] = Field(..., description="用药列表")
    egfr: Optional[float] = Field(None, description="eGFR值")
    complications: Optional[List[str]] = Field(None, description="并发症列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "medications": ["二甲双胍", "恩格列净"],
                "egfr": 28,
                "complications": ["糖尿病肾病"]
            }
        }


class DrugQueryRequest(BaseModel):
    """药品查询请求"""
    drug_name: str = Field(..., description="药品名称")


class RiskWarningResponse(BaseModel):
    """风险警告响应"""
    drug: str
    risk_type: str
    severity: str
    reason: str
    recommendation: str = ""


class RiskReportResponse(BaseModel):
    """风险报告响应"""
    warnings: List[RiskWarningResponse]
    safe_medications: List[str]
    summary: str


class RecommendationResponse(BaseModel):
    """诊疗建议响应"""
    action: str
    drug_name: Optional[str] = None
    reason: str = ""
    sources: List[str] = []
    priority: int = 1


class ClinicalReportResponse(BaseModel):
    """诊疗报告响应"""
    patient_summary: str
    risk_warnings: List[RiskWarningResponse]
    recommendations: List[RecommendationResponse]
    markdown_report: str


# ============================================
# 全局 Agent 实例
# ============================================

_agent = None


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


AGENT_MODE = os.getenv("DIA_AGENT_MODE", "fast").strip().lower()
LLM_PROVIDER = os.getenv("DIA_LLM_PROVIDER", "siliconflow").strip()
USE_FAST_AGENT = AGENT_MODE != "full"
SKIP_RAG = _env_bool("DIA_SKIP_RAG", True)
SKIP_RERANKER = _env_bool("DIA_SKIP_RERANKER", True)
LLM_CASE_EXTRACTION = _env_bool("DIA_LLM_CASE_EXTRACTION", False)
USE_REFLECTION = _env_bool("DIA_USE_REFLECTION", False)


def get_agent():
    """获取或创建 Agent 实例"""
    global _agent
    if _agent is None:
        llm_api = create_llm_api(LLM_PROVIDER)
        if USE_FAST_AGENT:
            _agent = DiaAgentFast(
                llm_api=llm_api,
                verbose=False,
                skip_reranker=SKIP_RERANKER,
                skip_rag=SKIP_RAG,
                llm_case_extraction=LLM_CASE_EXTRACTION,
                use_reflection=USE_REFLECTION
            )
        else:
            from src.agent import DiaAgent
            _agent = DiaAgent(llm_api=llm_api, verbose=False)
    return _agent


# ============================================
# API 端点
# ============================================

@app.get("/", tags=["健康检查"])
async def root():
    """API 根路径"""
    return {
        "service": "Dia-Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查"""
    agent = get_agent()
    return {
        "status": "healthy",
        "neo4j_connected": agent.risk_detector.driver is not None,
        "agent_mode": "fast" if USE_FAST_AGENT else "full",
        "components": {
            "case_analyzer": "ready",
            "risk_detector": "ready",
            "hybrid_retriever": "ready" if getattr(agent, "hybrid_retriever", None) else "disabled",
            "reranker": "ready" if getattr(agent, "reranker", None) else "disabled",
            "cypher_retriever": "ready" if hasattr(agent, "cypher_retriever") else "disabled",
            "decision_fusion": "ready"
        }
    }


@app.post("/consult", response_model=ClinicalReportResponse, tags=["诊疗"])
async def consult(request: CaseAnalysisRequest):
    """
    完整诊疗咨询
    
    根据病历文本提供完整的诊疗建议，包括：
    - 病例分析
    - 风险检测
    - 指南检索
    - 决策融合
    """
    try:
        agent = get_agent()
        report = agent.consult(request.case_text)
        
        return ClinicalReportResponse(
            patient_summary=report.patient_summary,
            risk_warnings=[
                RiskWarningResponse(
                    drug=w.drug_name,
                    risk_type=w.risk_type,
                    severity=w.severity.value,
                    reason=w.reason,
                    recommendation=w.recommendation
                )
                for w in report.risk_warnings
            ],
            recommendations=[
                RecommendationResponse(
                    action=r.action,
                    drug_name=r.drug_name,
                    reason=r.reason,
                    sources=[e.source_type for e in r.evidence],
                    priority=r.priority
                )
                for r in report.recommendations
            ],
            markdown_report=report.to_markdown()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/risk-check", response_model=RiskReportResponse, tags=["风险检测"])
async def quick_risk_check(request: QuickRiskCheckRequest):
    """
    快速用药风险检查
    
    无需提供完整病历，只需提供用药列表和关键指标，
    即可快速检测用药风险。
    """
    try:
        agent = get_agent()
        report = agent.quick_risk_check(
            medications=request.medications,
            egfr=request.egfr,
            complications=request.complications
        )
        
        return RiskReportResponse(
            warnings=[
                RiskWarningResponse(
                    drug=w.drug_name,
                    risk_type=w.risk_type,
                    severity=w.severity.value,
                    reason=w.reason,
                    recommendation=w.recommendation
                )
                for w in report.warnings
            ],
            safe_medications=report.safe_medications,
            summary=report.summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/drug-info", tags=["药品查询"])
async def query_drug_info(request: DrugQueryRequest):
    """
    查询药品禁忌信息
    
    从知识图谱中查询指定药品的禁忌信息。
    """
    try:
        agent = get_agent()
        result = agent.query_drug_info(request.drug_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理资源"""
    global _agent
    if _agent:
        _agent.close()
        _agent = None


# ============================================
# 运行服务
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

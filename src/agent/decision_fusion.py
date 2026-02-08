#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
决策融合器 (Decision Fusion)
整合图谱规则和指南知识，生成带引用的诊疗建议
"""

from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path

from .patient_profile import PatientProfile
from .risk_detector import RiskReport, RiskWarning, RiskSeverity


@dataclass
class EvidenceSource:
    """证据来源"""
    source_type: str  # "knowledge_graph", "guideline", "llm"
    content: str
    reference: str = ""
    confidence: float = 1.0


@dataclass 
class Recommendation:
    """诊疗建议"""
    action: str                                      # 建议动作
    drug_name: Optional[str] = None                  # 涉及药品
    reason: str = ""                                 # 原因
    evidence: List[EvidenceSource] = field(default_factory=list)
    priority: int = 1                                # 优先级 (1最高)
    
    def to_text(self, include_evidence: bool = True) -> str:
        text = f"• {self.action}"
        if self.reason:
            text += f"\n  原因: {self.reason}"
        if include_evidence and self.evidence:
            refs = [f"[{e.source_type}: {e.reference}]" for e in self.evidence if e.reference]
            if refs:
                text += f"\n  来源: {', '.join(refs)}"
        return text


@dataclass
class ClinicalReport:
    """临床诊疗报告"""
    patient_summary: str = ""
    risk_warnings: List[RiskWarning] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    rag_context: str = ""
    kg_context: str = ""
    llm_response: str = ""
    
    def to_markdown(self) -> str:
        """生成 Markdown 格式报告"""
        lines = ["# 📋 Dia-Agent 智能诊疗报告\n"]
        
        # 患者摘要
        if self.patient_summary:
            lines.append("## 患者信息")
            lines.append(self.patient_summary)
            lines.append("")
        
        # 风险提示
        if self.risk_warnings:
            lines.append("## ⚠️ 用药风险提示")
            critical = [w for w in self.risk_warnings if w.severity == RiskSeverity.CRITICAL]
            others = [w for w in self.risk_warnings if w.severity != RiskSeverity.CRITICAL]
            
            if critical:
                lines.append("\n### 🚨 严重风险")
                for w in critical:
                    lines.append(f"- **{w.drug_name}**: {w.reason}")
            
            if others:
                lines.append("\n### ⚡ 其他风险")
                for w in others:
                    lines.append(f"- {w.drug_name}: {w.reason}")
            lines.append("")
        
        # 诊疗建议
        if self.recommendations:
            lines.append("## 💊 诊疗建议")
            
            # 按优先级排序
            sorted_recs = sorted(self.recommendations, key=lambda x: x.priority)
            
            for i, rec in enumerate(sorted_recs, 1):
                lines.append(f"\n### {i}. {rec.action}")
                if rec.reason:
                    lines.append(f"**原因**: {rec.reason}")
                if rec.evidence:
                    refs = []
                    for e in rec.evidence:
                        ref = f"*{e.source_type}*"
                        if e.reference:
                            ref += f": {e.reference}"
                        refs.append(ref)
                    lines.append(f"\n**证据来源**: {'; '.join(refs)}")
            lines.append("")
        
        # LLM 综合分析
        if self.llm_response:
            lines.append("## 🤖 AI 综合分析")
            lines.append(self.llm_response)
        
        return "\n".join(lines)


class DecisionFusion:
    """
    决策融合器
    整合知识图谱规则和指南知识，生成诊疗建议
    
    优先级规则:
    1. 图谱硬规则 (Safety) > 指南通用建议 (General Guidance)
    2. 绝对禁忌 > 相对禁忌 > 谨慎使用
    """
    
    # 决策融合 Prompt
    FUSION_PROMPT = """你是一位资深内分泌科临床药师，请根据以下信息为糖尿病患者提供用药调整建议。

## 患者信息
{patient_summary}

## 用药风险警告（来自药品知识图谱，优先级最高）
{risk_warnings}

## 相关指南知识（来自《中国糖尿病防治指南2024》）
{guideline_context}

## 决策规则
1. 对于"严重风险"的药物，必须建议停药或换药，不可忽视
2. 参考指南知识给出替代治疗方案
3. 考虑患者的整体情况（年龄、肾功能、并发症等）
4. 每条建议必须标注来源：[图谱规则] 或 [指南建议]

## 输出格式
请生成以下格式的建议：

### 停药/换药建议
1. [具体建议] —— 来源: [图谱规则/指南建议]
   原因: [具体原因]

### 剂量调整建议  
1. [具体建议] —— 来源: [图谱规则/指南建议]

### 用药监测建议
1. [具体建议]

### 总结
[一段话总结诊疗方案]

请开始分析："""

    def __init__(self, llm_api: Callable[[str], str] = None):
        """
        初始化决策融合器
        
        Args:
            llm_api: LLM API 调用函数
        """
        self.llm_api = llm_api
    
    def fuse(
        self,
        profile: PatientProfile,
        risk_report: RiskReport,
        rag_context: str = "",
        kg_context: str = ""
    ) -> ClinicalReport:
        """
        融合多源证据，生成诊疗报告
        
        Args:
            profile: 患者画像
            risk_report: 风险检测报告
            rag_context: RAG 检索的指南内容
            kg_context: KG 查询的结构化结果
        
        Returns:
            ClinicalReport 临床报告
        """
        report = ClinicalReport(
            patient_summary=profile.to_clinical_summary(),
            risk_warnings=risk_report.warnings,
            rag_context=rag_context,
            kg_context=kg_context
        )
        
        print("\n🔄 开始决策融合...")
        
        # 1. 基于规则生成基础建议
        rule_recommendations = self._generate_rule_based_recommendations(
            profile, risk_report
        )
        report.recommendations.extend(rule_recommendations)
        
        # 2. 如果有 LLM，生成综合分析
        if self.llm_api and (risk_report.warnings or rag_context):
            print("  🤖 调用 LLM 生成综合分析...")
            
            # 构建 Prompt
            risk_text = self._format_risks_for_prompt(risk_report)
            prompt = self.FUSION_PROMPT.format(
                patient_summary=profile.to_clinical_summary(),
                risk_warnings=risk_text or "无明显风险",
                guideline_context=rag_context or "无相关指南检索结果"
            )
            
            try:
                llm_response = self.llm_api(prompt)
                report.llm_response = llm_response
                
                # 解析 LLM 建议并添加
                llm_recommendations = self._parse_llm_recommendations(llm_response)
                report.recommendations.extend(llm_recommendations)
                
                print("  ✅ LLM 分析完成")
            except Exception as e:
                print(f"  ⚠️ LLM 调用失败: {e}")
        
        # 3. 去重和排序
        report.recommendations = self._deduplicate_recommendations(report.recommendations)
        
        print(f"  ✅ 决策融合完成，生成 {len(report.recommendations)} 条建议")
        
        return report
    
    def _generate_rule_based_recommendations(
        self,
        profile: PatientProfile,
        risk_report: RiskReport
    ) -> List[Recommendation]:
        """基于规则生成建议"""
        recommendations = []
        
        # 处理严重风险
        for warning in risk_report.critical_warnings:
            rec = Recommendation(
                action=f"立即停用 {warning.drug_name}",
                drug_name=warning.drug_name,
                reason=warning.reason,
                evidence=[EvidenceSource(
                    source_type="knowledge_graph",
                    content=warning.reason,
                    reference="药品禁忌规则"
                )],
                priority=1
            )
            recommendations.append(rec)
        
        # 处理高风险
        for warning in risk_report.high_warnings:
            rec = Recommendation(
                action=f"评估是否需要调整 {warning.drug_name}",
                drug_name=warning.drug_name,
                reason=warning.reason,
                evidence=[EvidenceSource(
                    source_type="knowledge_graph",
                    content=warning.reason,
                    reference="药品禁忌规则"
                )],
                priority=2
            )
            recommendations.append(rec)
        
        # 基于患者状态的通用建议
        if profile.has_severe_renal_impairment:
            recommendations.append(Recommendation(
                action="肾功能严重受损，所有用药需评估肾脏安全性",
                reason=f"eGFR: {profile.renal.egfr}，属于 {profile.ckd_stage.value} 期",
                evidence=[EvidenceSource(
                    source_type="clinical_rule",
                    content="CKD分期规则",
                    reference="临床实践指南"
                )],
                priority=1
            ))
        
        return recommendations
    
    def _format_risks_for_prompt(self, risk_report: RiskReport) -> str:
        """格式化风险信息供 Prompt 使用"""
        if not risk_report.warnings:
            return ""
        
        lines = []
        for i, w in enumerate(risk_report.warnings, 1):
            lines.append(f"{i}. [{w.severity.value}] {w.drug_name}: {w.reason}")
        
        return "\n".join(lines)
    
    def _parse_llm_recommendations(self, llm_response: str) -> List[Recommendation]:
        """从 LLM 响应中解析建议"""
        # 简单解析，实际应用中可以更精细
        recommendations = []
        
        # 查找带编号的建议
        import re
        pattern = r'\d+\.\s*\[?(.+?)\]?\s*[—-]+\s*来源:\s*\[?(.+?)\]?(?:\n|$)'
        
        for match in re.finditer(pattern, llm_response):
            action = match.group(1).strip()
            source = match.group(2).strip()
            
            source_type = "guideline" if "指南" in source else "knowledge_graph"
            
            recommendations.append(Recommendation(
                action=action,
                evidence=[EvidenceSource(
                    source_type=source_type,
                    content=action,
                    reference=source
                )],
                priority=3  # LLM 建议优先级较低
            ))
        
        return recommendations
    
    def _deduplicate_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """去重和排序"""
        seen = set()
        unique = []
        
        # 按优先级排序
        sorted_recs = sorted(recommendations, key=lambda x: x.priority)
        
        for rec in sorted_recs:
            # 简单去重：基于药品名称
            key = (rec.drug_name, rec.action[:20]) if rec.drug_name else rec.action[:30]
            if key not in seen:
                seen.add(key)
                unique.append(rec)
        
        return unique


# ============================================
# 测试
# ============================================

if __name__ == "__main__":
    from .patient_profile import create_patient_profile
    from .risk_detector import RiskDetector
    
    print("=" * 60)
    print("🧪 决策融合器测试")
    print("=" * 60)
    
    # 创建测试患者
    patient = create_patient_profile(
        age=55,
        diabetes_type="2型糖尿病",
        hba1c=8.5,
        egfr=28,
        complications=["糖尿病肾病", "心力衰竭"],
        medications=["二甲双胍", "恩格列净"]
    )
    
    # 检测风险
    detector = RiskDetector()
    risk_report = detector.detect_risks(patient)
    detector.close()
    
    # 模拟 RAG 检索结果
    rag_context = """
    根据《中国糖尿病防治指南2024》：
    - eGFR < 30 mL/min/1.73m² 时，应停用二甲双胍
    - eGFR 30-45 时，二甲双胍应减量至最大 1000mg/日
    - 对于 CKD 3b-5 期患者，推荐使用利格列汀（无需调整剂量）
    - SGLT2 抑制剂在 eGFR < 30 时应停用
    """
    
    # 决策融合
    fusion = DecisionFusion()
    report = fusion.fuse(patient, risk_report, rag_context=rag_context)
    
    # 输出报告
    print("\n" + report.to_markdown())

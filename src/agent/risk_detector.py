#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险检测器 (Risk Detector)
基于患者画像查询知识图谱，检测用药风险和禁忌
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from neo4j import GraphDatabase

from .patient_profile import PatientProfile


class RiskSeverity(str, Enum):
    """风险严重程度"""
    CRITICAL = "严重"  # 绝对禁忌
    HIGH = "高"        # 相对禁忌
    MODERATE = "中等"  # 需要谨慎
    LOW = "低"         # 需要监测
    INFO = "提示"      # 信息提示


@dataclass
class RiskWarning:
    """风险警告"""
    drug_name: str                          # 药品名称
    risk_type: str                          # 风险类型
    severity: RiskSeverity                  # 严重程度
    reason: str                             # 原因
    recommendation: str = ""                # 建议
    source: str = "knowledge_graph"         # 来源
    patient_value: Optional[float] = None   # 患者实际值
    threshold: Optional[float] = None       # 阈值
    
    def to_dict(self) -> Dict:
        return {
            "drug": self.drug_name,
            "type": self.risk_type,
            "severity": self.severity.value,
            "reason": self.reason,
            "recommendation": self.recommendation,
            "source": self.source,
        }
    
    def to_text(self) -> str:
        """转换为文本描述"""
        text = f"⚠️ [{self.severity.value}] {self.drug_name}: {self.reason}"
        if self.recommendation:
            text += f"\n   建议: {self.recommendation}"
        return text


@dataclass
class RiskReport:
    """风险检测报告"""
    patient_id: Optional[str] = None
    warnings: List[RiskWarning] = field(default_factory=list)
    safe_medications: List[str] = field(default_factory=list)
    summary: str = ""
    
    @property
    def has_critical_risks(self) -> bool:
        return any(w.severity == RiskSeverity.CRITICAL for w in self.warnings)
    
    @property
    def critical_warnings(self) -> List[RiskWarning]:
        return [w for w in self.warnings if w.severity == RiskSeverity.CRITICAL]
    
    @property
    def high_warnings(self) -> List[RiskWarning]:
        return [w for w in self.warnings if w.severity == RiskSeverity.HIGH]
    
    def to_text(self) -> str:
        """生成文本报告"""
        lines = ["=" * 50, "📋 用药风险检测报告", "=" * 50]
        
        if not self.warnings:
            lines.append("✅ 未检测到用药风险")
        else:
            # 按严重程度分组
            critical = self.critical_warnings
            high = self.high_warnings
            others = [w for w in self.warnings if w.severity not in [RiskSeverity.CRITICAL, RiskSeverity.HIGH]]
            
            if critical:
                lines.append("\n🚨 严重风险 (需立即处理):")
                for w in critical:
                    lines.append(f"  • {w.drug_name}: {w.reason}")
                    if w.recommendation:
                        lines.append(f"    → {w.recommendation}")
            
            if high:
                lines.append("\n⚠️ 高风险 (需密切关注):")
                for w in high:
                    lines.append(f"  • {w.drug_name}: {w.reason}")
            
            if others:
                lines.append("\nℹ️ 其他提示:")
                for w in others:
                    lines.append(f"  • {w.drug_name}: {w.reason}")
        
        if self.safe_medications:
            lines.append(f"\n✅ 安全用药: {', '.join(self.safe_medications)}")
        
        if self.summary:
            lines.append(f"\n📝 总结: {self.summary}")
        
        return "\n".join(lines)


class RiskDetector:
    """
    风险检测器
    基于患者画像和知识图谱检测用药风险
    """
    
    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password123"
    ):
        """
        初始化风险检测器
        
        Args:
            neo4j_uri: Neo4j 连接 URI
            neo4j_user: Neo4j 用户名
            neo4j_password: Neo4j 密码
        """
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            self.driver.verify_connectivity()
            print("✅ RiskDetector: Neo4j 连接成功")
        except Exception as e:
            print(f"⚠️ RiskDetector: Neo4j 连接失败: {e}")
    
    def detect_risks(self, profile: PatientProfile) -> RiskReport:
        """
        检测患者用药风险
        
        Args:
            profile: 患者画像
        
        Returns:
            RiskReport 风险报告
        """
        report = RiskReport(patient_id=profile.patient_id)
        
        if not self.driver:
            report.summary = "无法连接知识图谱，风险检测受限"
            return report
        
        print("\n🔍 开始风险检测...")
        
        # 1. 检测每个用药的禁忌
        for medication in profile.current_medications:
            drug_name = medication.name
            print(f"  检查药品: {drug_name}")
            
            # 1.1 检测指标禁忌 (eGFR, ALT 等)
            indicator_warnings = self._check_indicator_contraindications(drug_name, profile)
            report.warnings.extend(indicator_warnings)
            
            # 1.2 检测疾病禁忌
            disease_warnings = self._check_disease_contraindications(drug_name, profile)
            report.warnings.extend(disease_warnings)
            
            # 如果没有警告，加入安全用药列表
            if not any(w.drug_name == drug_name for w in report.warnings):
                report.safe_medications.append(drug_name)
        
        # 2. 生成总结
        report.summary = self._generate_summary(report, profile)
        
        print(f"  ✅ 检测完成: {len(report.warnings)} 个风险")
        
        return report
    
    def _check_indicator_contraindications(
        self, 
        drug_name: str, 
        profile: PatientProfile
    ) -> List[RiskWarning]:
        """检测指标相关的禁忌"""
        warnings = []
        
        # 构建查询
        cypher = """
        MATCH (d:Drug)-[r:CONTRAINDICATED_IF]->(m:Metric)
        WHERE d.name CONTAINS $drug_name OR $drug_name CONTAINS d.name
        RETURN d.name AS drug, m.name AS metric, 
               r.operator AS operator, r.value AS threshold, 
               r.severity AS severity
        """
        
        try:
            with self.driver.session() as session:
                results = session.run(cypher, drug_name=drug_name)
                
                for record in results:
                    metric_name = record['metric']
                    operator = record['operator']
                    threshold = record['threshold']
                    severity = record['severity'] or 'CRITICAL'
                    
                    # 获取患者对应指标值
                    patient_value = self._get_patient_metric(profile, metric_name)
                    
                    if patient_value is None:
                        continue
                    
                    # 检查是否违反禁忌
                    is_violated = self._check_threshold(patient_value, operator, threshold)
                    
                    if is_violated:
                        warnings.append(RiskWarning(
                            drug_name=record['drug'],
                            risk_type="指标禁忌",
                            severity=self._parse_severity(severity),
                            reason=f"{metric_name} {operator} {threshold}（患者: {patient_value}）",
                            recommendation=f"请考虑停用或减量",
                            patient_value=patient_value,
                            threshold=threshold
                        ))
        except Exception as e:
            print(f"    ⚠️ 指标禁忌查询失败: {e}")
        
        return warnings
    
    def _check_disease_contraindications(
        self, 
        drug_name: str, 
        profile: PatientProfile
    ) -> List[RiskWarning]:
        """检测疾病相关的禁忌"""
        warnings = []
        
        # 获取患者疾病/并发症列表
        patient_conditions = profile.complication_names + profile.medical_history
        
        if not patient_conditions:
            return warnings
        
        # 构建查询
        cypher = """
        MATCH (d:Drug)-[r:FORBIDDEN_FOR]->(dis:Disease)
        WHERE (d.name CONTAINS $drug_name OR $drug_name CONTAINS d.name)
        RETURN d.name AS drug, dis.name AS disease, 
               r.severity AS severity, r.reason AS reason
        """
        
        try:
            with self.driver.session() as session:
                results = session.run(cypher, drug_name=drug_name)
                
                for record in results:
                    disease = record['disease']
                    
                    # 检查患者是否有该疾病
                    has_disease = any(
                        disease.lower() in cond.lower() or cond.lower() in disease.lower()
                        for cond in patient_conditions
                    )
                    
                    if has_disease:
                        warnings.append(RiskWarning(
                            drug_name=record['drug'],
                            risk_type="疾病禁忌",
                            severity=self._parse_severity(record['severity'] or '禁忌'),
                            reason=f"患者存在 {disease}",
                            recommendation=record['reason'] or "请评估是否需要换药"
                        ))
        except Exception as e:
            print(f"    ⚠️ 疾病禁忌查询失败: {e}")
        
        return warnings
    
    def _get_patient_metric(self, profile: PatientProfile, metric_name: str) -> Optional[float]:
        """获取患者的指标值"""
        metric_map = {
            'eGFR': profile.renal.egfr,
            'egfr': profile.renal.egfr,
            'creatinine': profile.renal.creatinine,
            'UACR': profile.renal.uacr,
            'ALT': profile.hepatic.alt,
            'AST': profile.hepatic.ast,
            'HbA1c': profile.glycemic.hba1c,
            'BMI': profile.vital_signs.bmi,
            'CrCl': profile.renal.egfr,  # 近似使用 eGFR
        }
        
        # 不区分大小写匹配
        for key, value in metric_map.items():
            if key.lower() == metric_name.lower():
                return value
        
        return None
    
    def _check_threshold(self, value: float, operator: str, threshold: float) -> bool:
        """检查值是否违反阈值"""
        if operator == '<':
            return value < threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '>':
            return value > threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '=':
            return value == threshold
        return False
    
    def _parse_severity(self, severity_str: str) -> RiskSeverity:
        """解析严重程度"""
        severity_str = severity_str.upper() if severity_str else ''
        
        if 'CRITICAL' in severity_str or '绝对' in severity_str or '严重' in severity_str:
            return RiskSeverity.CRITICAL
        elif 'HIGH' in severity_str or '禁忌' in severity_str:
            return RiskSeverity.HIGH
        elif 'MODERATE' in severity_str or '谨慎' in severity_str:
            return RiskSeverity.MODERATE
        elif 'LOW' in severity_str or '监测' in severity_str:
            return RiskSeverity.LOW
        else:
            return RiskSeverity.HIGH  # 默认为高风险
    
    def _generate_summary(self, report: RiskReport, profile: PatientProfile) -> str:
        """生成风险总结"""
        if not report.warnings:
            return "当前用药方案未检测到明显风险"
        
        critical_count = len(report.critical_warnings)
        total_count = len(report.warnings)
        
        if critical_count > 0:
            drugs = ', '.join(set(w.drug_name for w in report.critical_warnings))
            return f"检测到 {critical_count} 个严重风险，涉及药品: {drugs}，建议立即评估"
        else:
            return f"检测到 {total_count} 个用药风险，请结合临床情况综合评估"
    
    def query_drug_contraindications(self, drug_name: str) -> List[Dict]:
        """查询药品的所有禁忌信息"""
        if not self.driver:
            return []
        
        cypher = """
        MATCH (d:Drug)-[r]->(target)
        WHERE (d.name CONTAINS $drug_name OR $drug_name CONTAINS d.name)
          AND type(r) IN ['CONTRAINDICATED_IF', 'FORBIDDEN_FOR', 'DOSAGE_ADJUST_IF']
        RETURN d.name AS drug, type(r) AS relation_type, 
               target.name AS target, properties(r) AS properties
        """
        
        results = []
        try:
            with self.driver.session() as session:
                records = session.run(cypher, drug_name=drug_name)
                for record in records:
                    results.append(record.data())
        except Exception as e:
            print(f"查询失败: {e}")
        
        return results
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()


# ============================================
# 测试
# ============================================

if __name__ == "__main__":
    from .patient_profile import create_patient_profile
    
    print("=" * 60)
    print("🧪 风险检测器测试")
    print("=" * 60)
    
    # 创建测试患者
    patient = create_patient_profile(
        age=55,
        diabetes_type="2型糖尿病",
        diabetes_duration=10,
        hba1c=8.5,
        egfr=28,  # 严重肾功能损害
        complications=["糖尿病肾病", "心力衰竭"],
        medications=["二甲双胍", "恩格列净", "格列美脲"]
    )
    
    print("\n📋 患者画像:")
    print(patient.to_clinical_summary())
    
    # 创建检测器
    detector = RiskDetector()
    
    # 检测风险
    report = detector.detect_risks(patient)
    
    print("\n" + report.to_text())
    
    detector.close()

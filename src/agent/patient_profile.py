#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
患者画像数据模型 (Patient Profile Schema)
使用 Pydantic 定义结构化的患者临床信息
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import date


class CKDStage(str, Enum):
    """慢性肾病分期"""
    G1 = "G1"  # eGFR ≥ 90
    G2 = "G2"  # eGFR 60-89
    G3a = "G3a"  # eGFR 45-59
    G3b = "G3b"  # eGFR 30-44
    G4 = "G4"  # eGFR 15-29
    G5 = "G5"  # eGFR < 15
    UNKNOWN = "未知"


class CVRiskLevel(str, Enum):
    """心血管风险等级"""
    LOW = "低危"
    MODERATE = "中危"
    HIGH = "高危"
    VERY_HIGH = "极高危"
    UNKNOWN = "未知"


class DiabetesType(str, Enum):
    """糖尿病类型"""
    TYPE1 = "1型糖尿病"
    TYPE2 = "2型糖尿病"
    GESTATIONAL = "妊娠期糖尿病"
    OTHER = "其他类型"
    UNKNOWN = "未明确"


class Complication(BaseModel):
    """并发症信息"""
    name: str = Field(..., description="并发症名称")
    severity: Optional[str] = Field(None, description="严重程度")
    diagnosed_date: Optional[str] = Field(None, description="诊断时间")
    notes: Optional[str] = Field(None, description="备注")


class Medication(BaseModel):
    """用药信息"""
    name: str = Field(..., description="药品名称")
    dose: Optional[str] = Field(None, description="剂量")
    frequency: Optional[str] = Field(None, description="用药频率")
    route: Optional[str] = Field(None, description="给药途径")
    start_date: Optional[str] = Field(None, description="开始用药时间")
    notes: Optional[str] = Field(None, description="备注")


class LabResult(BaseModel):
    """实验室检查结果"""
    name: str = Field(..., description="检查项目名称")
    value: float = Field(..., description="检查值")
    unit: Optional[str] = Field(None, description="单位")
    reference_range: Optional[str] = Field(None, description="参考范围")
    is_abnormal: Optional[bool] = Field(None, description="是否异常")
    test_date: Optional[str] = Field(None, description="检查日期")


class VitalSigns(BaseModel):
    """生命体征"""
    height_cm: Optional[float] = Field(None, description="身高(cm)")
    weight_kg: Optional[float] = Field(None, description="体重(kg)")
    bmi: Optional[float] = Field(None, description="体重指数")
    systolic_bp: Optional[int] = Field(None, description="收缩压(mmHg)")
    diastolic_bp: Optional[int] = Field(None, description="舒张压(mmHg)")
    heart_rate: Optional[int] = Field(None, description="心率(次/分)")
    
    @validator('bmi', pre=True, always=True)
    def calculate_bmi(cls, v, values):
        """自动计算BMI"""
        if v is not None:
            return v
        height = values.get('height_cm')
        weight = values.get('weight_kg')
        if height and weight and height > 0:
            return round(weight / ((height / 100) ** 2), 1)
        return None


class GlycemicIndicators(BaseModel):
    """血糖相关指标"""
    hba1c: Optional[float] = Field(None, description="糖化血红蛋白(%)")
    fpg: Optional[float] = Field(None, description="空腹血糖(mmol/L)")
    ppg_2h: Optional[float] = Field(None, description="餐后2小时血糖(mmol/L)")
    random_glucose: Optional[float] = Field(None, description="随机血糖(mmol/L)")
    tir: Optional[float] = Field(None, description="葡萄糖目标范围内时间(%)")


class RenalIndicators(BaseModel):
    """肾功能指标"""
    egfr: Optional[float] = Field(None, description="估算肾小球滤过率(mL/min/1.73m²)")
    creatinine: Optional[float] = Field(None, description="血肌酐(μmol/L)")
    uacr: Optional[float] = Field(None, description="尿白蛋白/肌酐(mg/g)")
    urea: Optional[float] = Field(None, description="血尿素氮(mmol/L)")
    
    @property
    def ckd_stage(self) -> CKDStage:
        """根据eGFR计算CKD分期"""
        if self.egfr is None:
            return CKDStage.UNKNOWN
        if self.egfr >= 90:
            return CKDStage.G1
        elif self.egfr >= 60:
            return CKDStage.G2
        elif self.egfr >= 45:
            return CKDStage.G3a
        elif self.egfr >= 30:
            return CKDStage.G3b
        elif self.egfr >= 15:
            return CKDStage.G4
        else:
            return CKDStage.G5


class HepaticIndicators(BaseModel):
    """肝功能指标"""
    alt: Optional[float] = Field(None, description="丙氨酸氨基转移酶(U/L)")
    ast: Optional[float] = Field(None, description="天冬氨酸氨基转移酶(U/L)")
    tbil: Optional[float] = Field(None, description="总胆红素(μmol/L)")
    albumin: Optional[float] = Field(None, description="白蛋白(g/L)")


class LipidIndicators(BaseModel):
    """血脂指标"""
    tc: Optional[float] = Field(None, description="总胆固醇(mmol/L)")
    tg: Optional[float] = Field(None, description="甘油三酯(mmol/L)")
    ldl: Optional[float] = Field(None, description="低密度脂蛋白(mmol/L)")
    hdl: Optional[float] = Field(None, description="高密度脂蛋白(mmol/L)")


class PatientProfile(BaseModel):
    """
    患者完整画像
    包含从病历中提取的所有结构化临床信息
    """
    
    # 基本信息
    patient_id: Optional[str] = Field(None, description="患者ID")
    age: Optional[int] = Field(None, description="年龄")
    gender: Optional[str] = Field(None, description="性别")
    diabetes_type: DiabetesType = Field(DiabetesType.UNKNOWN, description="糖尿病类型")
    diabetes_duration_years: Optional[float] = Field(None, description="糖尿病病程(年)")
    
    # 生命体征
    vital_signs: VitalSigns = Field(default_factory=VitalSigns)
    
    # 血糖指标
    glycemic: GlycemicIndicators = Field(default_factory=GlycemicIndicators)
    
    # 肾功能
    renal: RenalIndicators = Field(default_factory=RenalIndicators)
    
    # 肝功能
    hepatic: HepaticIndicators = Field(default_factory=HepaticIndicators)
    
    # 血脂
    lipid: LipidIndicators = Field(default_factory=LipidIndicators)
    
    # 并发症
    complications: List[Complication] = Field(default_factory=list, description="并发症列表")
    
    # 当前用药
    current_medications: List[Medication] = Field(default_factory=list, description="当前用药列表")
    
    # 既往病史
    medical_history: List[str] = Field(default_factory=list, description="既往病史")
    
    # 过敏史
    allergies: List[str] = Field(default_factory=list, description="过敏史")
    
    # 计算属性
    @property
    def ckd_stage(self) -> CKDStage:
        """CKD分期"""
        return self.renal.ckd_stage
    
    @property
    def cv_risk_level(self) -> CVRiskLevel:
        """心血管风险评估"""
        # 简化的风险评估逻辑
        risk_factors = 0
        
        # 年龄因素
        if self.age and self.age >= 65:
            risk_factors += 1
        
        # 血糖控制
        if self.glycemic.hba1c and self.glycemic.hba1c >= 8.0:
            risk_factors += 1
        
        # 肾功能
        if self.renal.egfr and self.renal.egfr < 60:
            risk_factors += 1
        
        # 血脂
        if self.lipid.ldl and self.lipid.ldl >= 2.6:
            risk_factors += 1
        
        # 并发症
        cv_complications = ['心力衰竭', '冠心病', '心肌梗死', '脑卒中', 'ASCVD']
        for comp in self.complications:
            if any(cv in comp.name for cv in cv_complications):
                risk_factors += 2
        
        # 判断风险等级
        if risk_factors >= 4:
            return CVRiskLevel.VERY_HIGH
        elif risk_factors >= 3:
            return CVRiskLevel.HIGH
        elif risk_factors >= 2:
            return CVRiskLevel.MODERATE
        elif risk_factors >= 1:
            return CVRiskLevel.LOW
        else:
            return CVRiskLevel.UNKNOWN
    
    @property
    def has_ckd(self) -> bool:
        """是否存在CKD"""
        return self.ckd_stage not in [CKDStage.G1, CKDStage.G2, CKDStage.UNKNOWN]
    
    @property
    def has_severe_renal_impairment(self) -> bool:
        """是否存在严重肾功能损害 (eGFR < 30)"""
        return self.renal.egfr is not None and self.renal.egfr < 30
    
    @property
    def medication_names(self) -> List[str]:
        """获取当前用药名称列表"""
        return [med.name for med in self.current_medications]
    
    @property
    def complication_names(self) -> List[str]:
        """获取并发症名称列表"""
        return [comp.name for comp in self.complications]
    
    def get_clinical_tags(self) -> Dict[str, Any]:
        """生成临床标签，用于后续查询"""
        tags = {
            "ckd_stage": self.ckd_stage.value,
            "cv_risk": self.cv_risk_level.value,
            "has_ckd": self.has_ckd,
            "has_severe_renal_impairment": self.has_severe_renal_impairment,
        }
        
        # eGFR 阈值标签
        if self.renal.egfr is not None:
            tags["egfr_below_30"] = self.renal.egfr < 30
            tags["egfr_below_45"] = self.renal.egfr < 45
            tags["egfr_below_60"] = self.renal.egfr < 60
        
        # HbA1c 标签
        if self.glycemic.hba1c is not None:
            tags["hba1c_above_7"] = self.glycemic.hba1c > 7.0
            tags["hba1c_above_8"] = self.glycemic.hba1c > 8.0
            tags["hba1c_above_9"] = self.glycemic.hba1c > 9.0
        
        # 并发症标签
        tags["complications"] = self.complication_names
        tags["current_medications"] = self.medication_names
        
        return tags
    
    def to_clinical_summary(self) -> str:
        """生成临床摘要文本"""
        lines = []
        
        # 基本信息
        if self.age:
            lines.append(f"患者 {self.age}岁")
        if self.diabetes_type != DiabetesType.UNKNOWN:
            lines.append(f"诊断: {self.diabetes_type.value}")
        if self.diabetes_duration_years:
            lines.append(f"病程: {self.diabetes_duration_years}年")
        
        # BMI
        if self.vital_signs.bmi:
            lines.append(f"BMI: {self.vital_signs.bmi}")
        
        # 血糖指标
        glycemic_parts = []
        if self.glycemic.hba1c:
            glycemic_parts.append(f"HbA1c {self.glycemic.hba1c}%")
        if self.glycemic.fpg:
            glycemic_parts.append(f"FPG {self.glycemic.fpg} mmol/L")
        if glycemic_parts:
            lines.append("血糖: " + ", ".join(glycemic_parts))
        
        # 肾功能
        if self.renal.egfr:
            lines.append(f"肾功能: eGFR {self.renal.egfr} mL/min ({self.ckd_stage.value})")
        
        # 并发症
        if self.complications:
            lines.append(f"并发症: {', '.join(self.complication_names)}")
        
        # 当前用药
        if self.current_medications:
            lines.append(f"当前用药: {', '.join(self.medication_names)}")
        
        return "\n".join(lines)
    
    class Config:
        use_enum_values = True


# ============================================
# 便捷创建函数
# ============================================

def create_patient_profile(
    age: int = None,
    diabetes_type: str = None,
    diabetes_duration: float = None,
    hba1c: float = None,
    fpg: float = None,
    egfr: float = None,
    bmi: float = None,
    complications: List[str] = None,
    medications: List[str] = None,
    **kwargs
) -> PatientProfile:
    """
    便捷函数：快速创建患者画像
    
    Args:
        age: 年龄
        diabetes_type: 糖尿病类型
        diabetes_duration: 病程(年)
        hba1c: 糖化血红蛋白(%)
        fpg: 空腹血糖(mmol/L)
        egfr: eGFR
        bmi: BMI
        complications: 并发症列表
        medications: 用药列表
    
    Returns:
        PatientProfile 对象
    """
    profile = PatientProfile(
        age=age,
        diabetes_duration_years=diabetes_duration,
    )
    
    # 设置糖尿病类型
    if diabetes_type:
        type_map = {
            "1型": DiabetesType.TYPE1,
            "2型": DiabetesType.TYPE2,
            "妊娠": DiabetesType.GESTATIONAL,
        }
        for key, val in type_map.items():
            if key in diabetes_type:
                profile.diabetes_type = val
                break
    
    # 设置血糖指标
    if hba1c:
        profile.glycemic.hba1c = hba1c
    if fpg:
        profile.glycemic.fpg = fpg
    
    # 设置肾功能
    if egfr:
        profile.renal.egfr = egfr
    
    # 设置BMI
    if bmi:
        profile.vital_signs.bmi = bmi
    
    # 设置并发症
    if complications:
        profile.complications = [Complication(name=c) for c in complications]
    
    # 设置用药
    if medications:
        profile.current_medications = [Medication(name=m) for m in medications]
    
    return profile


# ============================================
# 测试
# ============================================

if __name__ == "__main__":
    # 创建示例患者
    patient = create_patient_profile(
        age=55,
        diabetes_type="2型糖尿病",
        diabetes_duration=10,
        hba1c=8.5,
        fpg=9.2,
        egfr=28,
        bmi=26.5,
        complications=["糖尿病肾病", "周围神经病变"],
        medications=["二甲双胍", "恩格列净"]
    )
    
    print("=" * 60)
    print("📋 患者画像示例")
    print("=" * 60)
    print(patient.to_clinical_summary())
    print("\n📊 临床标签:")
    for k, v in patient.get_clinical_tags().items():
        print(f"  {k}: {v}")

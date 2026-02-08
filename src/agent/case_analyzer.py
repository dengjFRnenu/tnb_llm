#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
病例分析器 (Case Analyzer)
从病历文本中提取结构化的患者画像
使用 LLM 进行实体抽取，支持反思提示词二次校验
"""

import json
import re
from typing import Optional, Callable, Dict, List, Any
from pathlib import Path

from .patient_profile import (
    PatientProfile, 
    Complication, 
    Medication,
    DiabetesType,
    create_patient_profile
)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent


class CaseAnalyzer:
    """
    病例分析器
    从医生书写的病历中提取结构化患者画像
    """
    
    # 提取 Prompt 模板
    EXTRACTION_PROMPT = """你是一个专业的医学信息提取助手。请从以下糖尿病患者的病历中提取关键临床信息。

## 病历内容
{case_text}

## 提取要求
请提取以下信息并以 JSON 格式返回：

```json
{{
    "age": 数字或null,
    "gender": "男"/"女"/null,
    "diabetes_type": "1型糖尿病"/"2型糖尿病"/"妊娠期糖尿病"/null,
    "diabetes_duration_years": 数字或null,
    "height_cm": 数字或null,
    "weight_kg": 数字或null,
    "bmi": 数字或null,
    "hba1c": 数字(%)或null,
    "fpg": 数字(mmol/L)或null,
    "ppg_2h": 数字(mmol/L)或null,
    "egfr": 数字(mL/min/1.73m²)或null,
    "creatinine": 数字(μmol/L)或null,
    "uacr": 数字(mg/g)或null,
    "alt": 数字(U/L)或null,
    "ast": 数字(U/L)或null,
    "tc": 数字(mmol/L)或null,
    "tg": 数字(mmol/L)或null,
    "ldl": 数字(mmol/L)或null,
    "hdl": 数字(mmol/L)或null,
    "systolic_bp": 数字(mmHg)或null,
    "diastolic_bp": 数字(mmHg)或null,
    "complications": ["并发症1", "并发症2", ...],
    "current_medications": [
        {{"name": "药品名", "dose": "剂量", "frequency": "频率"}},
        ...
    ],
    "medical_history": ["既往病史1", "既往病史2", ...],
    "allergies": ["过敏药物1", ...]
}}
```

## 注意事项
1. 如果信息不明确，填写 null
2. 数值请转换为标准单位
3. 药品名称尽量使用通用名
4. 注意提取所有并发症，包括糖尿病视网膜病变(DR)、糖尿病肾病(DKD)、糖尿病周围神经病变(DPN)等

请直接返回 JSON，不要包含其他解释："""

    # 反思 Prompt 模板
    REFLECTION_PROMPT = """请检查之前的提取结果，看是否有遗漏或错误。

## 原始病历
{case_text}

## 已提取的信息
{extracted_json}

## 检查要点
1. 是否遗漏了任何肾功能指标（如肌酐、eGFR）？
2. 是否遗漏了禁忌相关的信息（如心力衰竭、酮症酸中毒）？
3. 药品剂量和用法是否完整？
4. 是否有计算错误（如BMI）？

如果发现任何遗漏或错误，请返回修正后的完整 JSON。如果没有问题，直接返回原 JSON。
只返回 JSON，不要解释："""

    def __init__(self, llm_api: Callable[[str], str] = None):
        """
        初始化病例分析器
        
        Args:
            llm_api: LLM API 调用函数 (接收 prompt, 返回响应文本)
        """
        self.llm_api = llm_api
        
        # 加载药品别名映射
        self.drug_aliases = self._load_drug_aliases()
    
    def _load_drug_aliases(self) -> Dict[str, str]:
        """加载药品别名映射表"""
        # 常见别名 -> 标准名
        return {
            "二甲": "二甲双胍",
            "格华止": "二甲双胍",
            "甲福明": "二甲双胍",
            "阿卡波糖": "阿卡波糖",
            "拜糖苹": "阿卡波糖",
            "卡博平": "阿卡波糖",
            "格列美脲": "格列美脲",
            "亚莫利": "格列美脲",
            "格列齐特": "格列齐特",
            "达美康": "格列齐特",
            "恩格列净": "恩格列净",
            "欧唐静": "恩格列净",
            "达格列净": "达格列净",
            "安达唐": "达格列净",
            "西格列汀": "西格列汀",
            "捷诺维": "西格列汀",
            "利格列汀": "利格列汀",
            "欧唐宁": "利格列汀",
            "司美格鲁肽": "司美格鲁肽",
            "诺和泰": "司美格鲁肽",
            "利拉鲁肽": "利拉鲁肽",
            "诺和力": "利拉鲁肽",
        }
    
    def normalize_drug_name(self, name: str) -> str:
        """标准化药品名称"""
        # 去除空格和特殊字符
        name = name.strip()
        
        # 查找别名映射
        for alias, standard in self.drug_aliases.items():
            if alias in name:
                return standard
        
        return name
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """从 LLM 输出中提取 JSON"""
        # 尝试提取 JSON 代码块
        patterns = [
            r'```json\s*\n(.*?)\n```',
            r'```\s*\n(.*?)\n```',
            r'\{.*\}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1) if '```' in pattern else match.group(0)
                    return json.loads(json_str)
                except:
                    continue
        
        # 尝试直接解析
        try:
            return json.loads(text)
        except:
            return None
    
    def analyze(self, case_text: str, use_reflection: bool = True) -> PatientProfile:
        """
        分析病历文本，提取患者画像
        
        Args:
            case_text: 病历文本
            use_reflection: 是否使用反思提示词进行二次校验
        
        Returns:
            PatientProfile 对象
        """
        if not self.llm_api:
            print("⚠️ 未配置 LLM API，使用规则提取")
            return self._rule_based_extraction(case_text)
        
        print("🔍 [步骤1] LLM 提取病历信息...")
        
        # 第一次提取
        prompt1 = self.EXTRACTION_PROMPT.format(case_text=case_text)
        response1 = self.llm_api(prompt1)
        extracted = self._extract_json(response1)
        
        if not extracted:
            print("  ❌ 提取失败，使用规则提取")
            return self._rule_based_extraction(case_text)
        
        print(f"  ✅ 初步提取完成")
        
        # 反思校验
        if use_reflection:
            print("🔍 [步骤2] 反思校验...")
            prompt2 = self.REFLECTION_PROMPT.format(
                case_text=case_text,
                extracted_json=json.dumps(extracted, ensure_ascii=False, indent=2)
            )
            response2 = self.llm_api(prompt2)
            refined = self._extract_json(response2)
            
            if refined:
                extracted = refined
                print("  ✅ 反思校验完成")
        
        # 转换为 PatientProfile
        return self._dict_to_profile(extracted)
    
    def _rule_based_extraction(self, case_text: str) -> PatientProfile:
        """基于规则的简单提取（当无 LLM 时使用）"""
        profile = PatientProfile()
        
        # 年龄
        age_match = re.search(r'(\d{1,3})\s*岁', case_text)
        if age_match:
            profile.age = int(age_match.group(1))
        
        # 性别
        if '男' in case_text:
            profile.gender = '男'
        elif '女' in case_text:
            profile.gender = '女'
        
        # 糖尿病类型
        if '2型' in case_text or '二型' in case_text:
            profile.diabetes_type = DiabetesType.TYPE2
        elif '1型' in case_text or '一型' in case_text:
            profile.diabetes_type = DiabetesType.TYPE1
        
        # 病程
        duration_match = re.search(r'病程\s*(\d+(?:\.\d+)?)\s*年', case_text)
        if duration_match:
            profile.diabetes_duration_years = float(duration_match.group(1))
        
        # HbA1c
        hba1c_match = re.search(r'HbA1c[：:\s]*(\d+(?:\.\d+)?)\s*%?', case_text, re.I)
        if hba1c_match:
            profile.glycemic.hba1c = float(hba1c_match.group(1))
        
        # eGFR
        egfr_match = re.search(r'eGFR[：:\s]*(\d+(?:\.\d+)?)', case_text, re.I)
        if egfr_match:
            profile.renal.egfr = float(egfr_match.group(1))
        
        # 空腹血糖
        fpg_match = re.search(r'空腹血糖[：:\s]*(\d+(?:\.\d+)?)', case_text)
        if fpg_match:
            profile.glycemic.fpg = float(fpg_match.group(1))
        
        # BMI
        bmi_match = re.search(r'BMI[：:\s]*(\d+(?:\.\d+)?)', case_text, re.I)
        if bmi_match:
            profile.vital_signs.bmi = float(bmi_match.group(1))
        
        # 常见并发症
        complication_keywords = [
            '糖尿病肾病', '糖尿病视网膜病变', '糖尿病周围神经病变',
            '心力衰竭', '冠心病', '高血压', '脑卒中',
            'DKD', 'DR', 'DPN', 'CKD'
        ]
        for kw in complication_keywords:
            if kw in case_text:
                profile.complications.append(Complication(name=kw))
        
        # 常见药物
        drug_keywords = list(self.drug_aliases.keys()) + [
            '二甲双胍', '格列美脲', '阿卡波糖', '恩格列净', '达格列净',
            '西格列汀', '利格列汀', '司美格鲁肽', '利拉鲁肽',
            '胰岛素', '甘精胰岛素', '门冬胰岛素'
        ]
        for kw in drug_keywords:
            if kw in case_text:
                normalized = self.normalize_drug_name(kw)
                if not any(m.name == normalized for m in profile.current_medications):
                    profile.current_medications.append(Medication(name=normalized))
        
        return profile
    
    def _dict_to_profile(self, data: Dict) -> PatientProfile:
        """将提取的字典转换为 PatientProfile"""
        profile = PatientProfile()
        
        # 基本信息
        profile.age = data.get('age')
        profile.gender = data.get('gender')
        profile.diabetes_duration_years = data.get('diabetes_duration_years')
        
        # 糖尿病类型
        dtype = data.get('diabetes_type', '')
        if dtype:
            if '1型' in dtype:
                profile.diabetes_type = DiabetesType.TYPE1
            elif '2型' in dtype:
                profile.diabetes_type = DiabetesType.TYPE2
            elif '妊娠' in dtype:
                profile.diabetes_type = DiabetesType.GESTATIONAL
        
        # 生命体征
        profile.vital_signs.height_cm = data.get('height_cm')
        profile.vital_signs.weight_kg = data.get('weight_kg')
        profile.vital_signs.bmi = data.get('bmi')
        profile.vital_signs.systolic_bp = data.get('systolic_bp')
        profile.vital_signs.diastolic_bp = data.get('diastolic_bp')
        
        # 血糖指标
        profile.glycemic.hba1c = data.get('hba1c')
        profile.glycemic.fpg = data.get('fpg')
        profile.glycemic.ppg_2h = data.get('ppg_2h')
        
        # 肾功能
        profile.renal.egfr = data.get('egfr')
        profile.renal.creatinine = data.get('creatinine')
        profile.renal.uacr = data.get('uacr')
        
        # 肝功能
        profile.hepatic.alt = data.get('alt')
        profile.hepatic.ast = data.get('ast')
        
        # 血脂
        profile.lipid.tc = data.get('tc')
        profile.lipid.tg = data.get('tg')
        profile.lipid.ldl = data.get('ldl')
        profile.lipid.hdl = data.get('hdl')
        
        # 并发症
        complications = data.get('complications', [])
        for comp in complications:
            if isinstance(comp, str):
                profile.complications.append(Complication(name=comp))
            elif isinstance(comp, dict):
                profile.complications.append(Complication(**comp))
        
        # 用药
        medications = data.get('current_medications', [])
        for med in medications:
            if isinstance(med, str):
                normalized = self.normalize_drug_name(med)
                profile.current_medications.append(Medication(name=normalized))
            elif isinstance(med, dict):
                med['name'] = self.normalize_drug_name(med.get('name', ''))
                profile.current_medications.append(Medication(**med))
        
        # 病史和过敏
        profile.medical_history = data.get('medical_history', [])
        profile.allergies = data.get('allergies', [])
        
        return profile


# ============================================
# 测试
# ============================================

if __name__ == "__main__":
    # 测试病例
    test_case = """
    患者张某，男，55岁，因"发现血糖升高10年，口渴多饮1月"入院。
    
    现病史：患者10年前体检发现血糖升高，诊断为2型糖尿病，长期口服二甲双胍0.5g tid、
    格列美脲2mg qd治疗，血糖控制欠佳。近1月出现口渴多饮、多尿，体重下降约3kg。
    
    既往史：高血压病史5年，服用氨氯地平5mg qd，血压控制可。
    
    查体：身高170cm，体重78kg，BMI 27.0，血压145/90mmHg。
    
    辅助检查：
    - 空腹血糖：9.8 mmol/L
    - 餐后2h血糖：15.2 mmol/L
    - HbA1c：8.9%
    - 肌酐：156 μmol/L
    - eGFR：42 mL/min/1.73m²
    - UACR：180 mg/g
    - ALT 35 U/L, AST 28 U/L
    - TC 5.8 mmol/L, TG 2.1 mmol/L, LDL 3.2 mmol/L, HDL 1.1 mmol/L
    
    诊断：
    1. 2型糖尿病
    2. 糖尿病肾病 CKD 3b期
    3. 高血压病2级
    """
    
    print("=" * 60)
    print("🧪 病例分析器测试（规则提取模式）")
    print("=" * 60)
    
    analyzer = CaseAnalyzer()
    profile = analyzer.analyze(test_case, use_reflection=False)
    
    print("\n📋 提取的患者画像:")
    print(profile.to_clinical_summary())
    
    print("\n📊 临床标签:")
    for k, v in profile.get_clinical_tags().items():
        print(f"  {k}: {v}")

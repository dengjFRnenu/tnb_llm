#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实体提取器 - 从结构化药品数据中提取图谱实体和关系

功能:
1. 推断药物分类(Category)
2. 提取疾病实体(Disease)从适应症和禁忌
3. 提取Metric约束(eGFR < 30等)
4. 构建关系数据
5. 输出为Neo4j友好的JSON格式
"""

import re
import json
from typing import List, Dict, Set, Tuple
from collections import defaultdict


class EntityExtractor:
    """实体和关系提取器"""
    
    def __init__(self):
        # 药物分类规则
        self.category_rules = {
            '双胍类': [r'二甲双胍', r'苯乙双胍'],
            '磺脲类': [r'格列\w+', r'优降糖'],
            'DPP-4抑制剂': [r'(西|沙|利|维|阿)格列汀', r'DPP-4'],
            'SGLT2抑制剂': [r'(达|恩|卡|埃|恒)格列净', r'SGLT'],
            'TZD类': [r'吡格列酮', r'罗格列酮', r'噻唑烷二酮'],
            'GLP-1激动剂': [r'(利拉|司美|度拉|洛塞那|利司那|艾塞那|贝那|阿必)肽', r'GLP-1'],
            'α-糖苷酶抑制剂': [r'阿卡波糖', r'伏格列波糖', r'米格列醇'],
            '格列奈类': [r'(瑞|那|米)格列奈', r'格列奈'],
            '胰岛素': [r'胰岛素', r'insulin'],
            '胆汁酸螯合剂': [r'考来\w+'],
            '其他': [r'溴隐亭', r'普兰林肽', r'氯化铬', r'吡啶甲酸铬'],
        }
        
        # 疾病实体模式
        self.disease_patterns = [
            # 糖尿病相关
            r'[12]\s*型糖尿病',
            r'糖尿病',
            r'高血糖',
            r'酮症酸中毒',
            r'糖尿病\w*并发症',
            
            # 心血管疾病
            r'心力衰竭', r'心衰', r'充血性心力衰竭',
            r'心肌梗死', r'心肌梗塞',
            r'心血管疾病',
            r'心绞痛',
            r'冠心病',
            
            # 肾脏疾病
            r'肾功能不全', r'肾功能损害', r'肾功能受损',
            r'慢性肾\w*病', r'CKD',
            r'肾衰竭', r'终末期肾病',
            r'肾病综合征',
            
            # 肝脏疾病
            r'肝功能不全', r'肝功能损害',
            r'肝衰竭',
            r'爆发性肝炎',
            r'黄疸',
            
            # 其他代谢疾病
            r'低血糖',
            r'乳酸酸中毒',
            r'代谢性酸中毒',
            
            # 癌症
            r'膀胱癌',
            r'甲状腺髓样癌', r'MTC',
            r'胰腺癌',
            
            # 其他
            r'胰腺炎',
            r'酒精中毒', r'酗酒',
            r'休克',
            r'感染',
            r'呼吸衰竭',
        ]
        
        # Metric模式
        self.metric_patterns = {
            'eGFR': [
                r'eGFR\s*([<>≥≤])\s*(\d+)\s*(mL/min)?',
                r'eGFR\s*(\d+)-(\d+)',  # 范围
            ],
            'CrCl': [
                r'(肌酐清除率|CrCl)\s*([<>≥≤])\s*(\d+)',
            ],
            'ALT': [
                r'(ALT|转氨酶|丙氨酸氨基转移酶)\s*>\s*(\d+)\s*倍',
                r'(ALT|AST)\s*>\s*正常上限\s*(\d+)\s*倍',
            ],
            'BMI': [
                r'BMI\s*([<>≥≤])\s*(\d+)',
            ],
            '甘油三酯': [
                r'甘油三酯\s*>\s*(\d+)\s*mg/dL',
            ],
        }
    
    def infer_category(self, drug: Dict) -> str:
        """推断药物分类"""
        text = f"{drug['name']} {drug.get('ingredients', '')} {drug.get('pharmacology', '')}"
        
        for category, patterns in self.category_rules.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return category
        
        return '未分类'
    
    def extract_diseases(self, text: str, source_type: str) -> List[Dict]:
        """
        从文本中提取疾病实体
        
        Args:
            text: 要提取的文本
            source_type: 来源类型('适应症'或'禁忌')
        
        Returns:
            疾病实体列表
        """
        diseases = []
        seen = set()
        
        for pattern in self.disease_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                disease_name = match.group(0)
                # 规范化名称
                disease_name = disease_name.replace(' ', '')
                
                if disease_name not in seen:
                    diseases.append({
                        'name': disease_name,
                        'type': source_type,
                        'context': text[max(0, match.start()-20):match.end()+20]
                    })
                    seen.add(disease_name)
        
        return diseases
    
    def extract_metric_constraints(self, text: str) -> List[Dict]:
        """
        提取Metric约束
        
        Returns:
            约束列表,每个包含: metric, operator, value, unit等
        """
        constraints = []
        
        # eGFR提取
        # 1. 简单比较: eGFR < 30
        for match in re.finditer(r'eGFR\s*([<>≥≤＜＞])\s*(\d+)\s*(mL/min)?', text):
            operator = match.group(1).replace('＜', '<').replace('＞', '>')
            value = float(match.group(2))
            
            constraints.append({
                'metric': 'eGFR',
                'operator': operator,
                'value': value,
                'unit': 'mL/min',
                'severity': 'CRITICAL' if operator in ['<', '≤'] and value == 30 else 'WARNING',
                'context': match.group(0)
            })
        
        # 2. 范围: eGFR 30-45
        for match in re.finditer(r'eGFR\s*(\d+)-(\d+)', text):
            constraints.append({
                'metric': 'eGFR',
                'operator': 'BETWEEN',
                'value_min': float(match.group(1)),
                'value_max': float(match.group(2)),
                'unit': 'mL/min',
                'severity': 'WARNING',
                'context': match.group(0)
            })
        
        # CrCl提取
        for match in re.finditer(r'(CrCl|肌酐清除率)\s*([<>≥≤＜＞])\s*(\d+)', text):
            operator = match.group(2).replace('＜', '<').replace('＞', '>')
            value = float(match.group(3))
            
            constraints.append({
                'metric': 'CrCl',
                'operator': operator,
                'value': value,
                'unit': 'mL/min',
                'severity': 'CRITICAL' if operator == '<' and value <= 30 else 'WARNING',
                'context': match.group(0)
            })
        
        # ALT/AST提取
        for match in re.finditer(r'(ALT|AST|转氨酶)\s*>\s*(\d+)\s*倍', text):
            metric_name = 'ALT' if 'ALT' in match.group(1) else 'AST' if 'AST' in match.group(1) else '转氨酶'
            constraints.append({
                'metric': metric_name,
                'operator': '>',
                'value': float(match.group(2)),
                'unit': '倍正常值',
                'severity': 'WARNING',
                'context': match.group(0)
            })
        
        return constraints
    
    def extract_dosage_info(self, text: str) -> Dict:
        """提取剂量信息"""
        dosage_info = {}
        
        # 最大剂量
        max_dose_match = re.search(r'最大剂量[为：:]*\s*(\d+[.\d]*)\s*(mg|g|μg|单位)', text)
        if max_dose_match:
            dosage_info['max_daily_dose'] = f"{max_dose_match.group(1)}{max_dose_match.group(2)}"
        
        # 起始剂量
        start_dose_match = re.search(r'起始剂量[为：:]*\s*(\d+[.\d]*)\s*(mg|g|μg)', text)
        if start_dose_match:
            dosage_info['starting_dose'] = f"{start_dose_match.group(1)}{start_dose_match.group(2)}"
        
        # 服药时间
        timing_patterns = [
            r'(餐前|餐后|随餐|空腹|睡前|晨起)',
            r'(早[餐晨午]|晚[餐饭]|中午)\s*(前|后|时)',
        ]
        for pattern in timing_patterns:
            timing_match = re.search(pattern, text)
            if timing_match:
                dosage_info['timing'] = timing_match.group(0)
                break
        
        # 给药途径
        if '注射' in text:
            dosage_info['route'] = '注射'
        elif '口服' in text:
            dosage_info['route'] = '口服'
        elif '皮下' in text:
            dosage_info['route'] = '皮下注射'
        
        return dosage_info
    
    def process_drug(self, drug: Dict) -> Dict:
        """处理单个药品,提取所有实体和关系"""
        drug_data = {
            'drug': {
                'id': drug['id'],
                'name': drug['name'],
                'en_name': drug.get('en_name', ''),
                'dosage_info': self.extract_dosage_info(drug.get('dosage', '')),
            },
            'category': self.infer_category(drug),
            'brands': drug.get('brand_names', []),
            'treats': [],  # 适应症
            'forbidden_diseases': [],  # 禁忌疾病
            'metric_constraints': [],  # Metric约束
        }
        
        # 提取适应症疾病
        if drug.get('indications'):
            drug_data['treats'] = self.extract_diseases(drug['indications'], '适应症')
        
        # 提取禁忌疾病和Metric约束
        if drug.get('contraindications'):
            drug_data['forbidden_diseases'] = self.extract_diseases(drug['contraindications'], '禁忌')
            drug_data['metric_constraints'] = self.extract_metric_constraints(drug['contraindications'])
        
        # 从用法用量中也提取Metric约束
        if drug.get('dosage'):
            dosage_constraints = self.extract_metric_constraints(drug['dosage'])
            drug_data['metric_constraints'].extend(dosage_constraints)
        
        # 去重约束
        seen_constraints = set()
        unique_constraints = []
        for c in drug_data['metric_constraints']:
            key = f"{c['metric']}_{c['operator']}_{c.get('value', '')}_{c.get('value_min', '')}"
            if key not in seen_constraints:
                unique_constraints.append(c)
                seen_constraints.add(key)
        drug_data['metric_constraints'] = unique_constraints
        
        return drug_data


def process_all_drugs(input_file: str, output_file: str):
    """处理所有药品"""
    print("=" * 60)
    print("🧬 实体和关系提取器")
    print("=" * 60)
    
    # 读取结构化数据
    print(f"📖 正在读取: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        drugs = json.load(f)
    
    print(f"📊 加载了 {len(drugs)} 个药品")
    
    # 初始化提取器
    extractor = EntityExtractor()
    
    # 处理每个药品
    graph_data = []
    stats = {
        'categories': defaultdict(int),
        'total_treats': 0,
        'total_forbidden': 0,
        'total_constraints': 0,
        'drugs_with_constraints': 0,
    }
    
    print("\n🔍 开始提取实体和关系...")
    for i, drug in enumerate(drugs):
        try:
            drug_graph = extractor.process_drug(drug)
            graph_data.append(drug_graph)
            
            # 统计
            stats['categories'][drug_graph['category']] += 1
            stats['total_treats'] += len(drug_graph['treats'])
            stats['total_forbidden'] += len(drug_graph['forbidden_diseases'])
            stats['total_constraints'] += len(drug_graph['metric_constraints'])
            if drug_graph['metric_constraints']:
                stats['drugs_with_constraints'] += 1
            
            print(f"✅ [{i+1}/{len(drugs)}] {drug['name']}: {drug_graph['category']}, "
                  f"{len(drug_graph['metric_constraints'])} 约束")
        except Exception as e:
            print(f"❌ [{i+1}/{len(drugs)}] {drug.get('name', '未知')}: {e}")
    
    # 保存结果
    print(f"\n💾 保存到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)
    
    # 打印统计
    print("\n" + "=" * 60)
    print("📈 提取统计")
    print("=" * 60)
    print(f"总药品数: {len(graph_data)}")
    print(f"含Metric约束的药品: {stats['drugs_with_constraints']}")
    print(f"总Metric约束数: {stats['total_constraints']}")
    print(f"总适应症关系: {stats['total_treats']}")
    print(f"总禁忌关系: {stats['total_forbidden']}")
    
    print("\n📊 药物分类统计:")
    for category, count in sorted(stats['categories'].items(), key=lambda x: -x[1]):
        print(f"  {category}: {count}")
    
    # 显示示例
    print("\n" + "=" * 60)
    print("📋 实体提取示例(前2个药品)")
    print("=" * 60)
    for drug_graph in graph_data[:2]:
        print(f"\n💊 {drug_graph['drug']['name']}")
        print(f"   分类: {drug_graph['category']}")
        print(f"   商品名: {', '.join(drug_graph['brands']) if drug_graph['brands'] else '无'}")
        print(f"   适应症: {len(drug_graph['treats'])} 个")
        print(f"   禁忌: {len(drug_graph['forbidden_diseases'])} 个")
        print(f"   Metric约束: {len(drug_graph['metric_constraints'])} 个")
        
        if drug_graph['metric_constraints']:
            print("   约束详情:")
            for c in drug_graph['metric_constraints'][:3]:  # 只显示前3个
                if 'value' in c:
                    print(f"     - {c['metric']} {c['operator']} {c['value']} {c.get('unit', '')}")
                else:
                    print(f"     - {c['metric']} BETWEEN {c['value_min']}-{c['value_max']} {c.get('unit', '')}")


if __name__ == "__main__":
    process_all_drugs(
        input_file="drugs_structured.json",
        output_file="graph_data.json"
    )

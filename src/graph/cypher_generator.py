#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cypher生成器 - 将图谱数据转换为Neo4j导入脚本

功能:
1. 读取graph_data.json
2. 生成节点创建语句(Drug, Brand, Category, Disease, Metric)
3. 生成关系创建语句
4. 生成索引和约束
5. 输出为.cypher文件
"""

import json
from collections import defaultdict
from typing import List, Dict, Set


class CypherGenerator:
    """Neo4j Cypher语句生成器"""
    
    def __init__(self):
        self.categories = set()
        self.diseases = set()
        self.metrics = set()
        self.brands = set()
        
    def escape_string(self, text: str) -> str:
        """转义Cypher字符串中的特殊字符"""
        if not text:
            return ""
        return text.replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
    
    def generate_constraints_and_indexes(self) -> List[str]:
        """生成约束和索引"""
        statements = [
            "// ========================================",
            "// 1. 创建约束和索引",
            "// ========================================",
            "",
            "// 唯一性约束",
            "CREATE CONSTRAINT drug_name_unique IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE;",
            "CREATE CONSTRAINT brand_name_unique IF NOT EXISTS FOR (b:Brand) REQUIRE b.name IS UNIQUE;",
            "CREATE CONSTRAINT category_name_unique IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE;",
            "",
            "// 索引",
            "CREATE INDEX drug_id_idx IF NOT EXISTS FOR (d:Drug) ON (d.id);",
            "CREATE INDEX disease_name_idx IF NOT EXISTS FOR (dis:Disease) ON (dis.name);",
            "CREATE INDEX metric_name_idx IF NOT EXISTS FOR (m:Metric) ON (m.name);",
            "",
        ]
        return statements
    
    def generate_category_nodes(self) -> List[str]:
        """生成Category节点"""
        statements = [
            "// ========================================",
            "// 2. 创建药物分类节点",
            "// ========================================",
            "",
        ]
        
        for category in sorted(self.categories):
            stmt = f"MERGE (c:Category {{name: '{self.escape_string(category)}'}})"
            statements.append(stmt + ";")
        
        statements.append("")
        return statements
    
    def generate_metric_nodes(self) -> List[str]:
        """生成Metric节点"""
        statements = [
            "// ========================================",
            "// 3. 创建临床指标节点",
            "// ========================================",
            "",
        ]
        
        metric_definitions = {
            'eGFR': '肾小球滤过率',
            'CrCl': '肌酐清除率',
            'ALT': '丙氨酸氨基转移酶',
            'AST': '天冬氨酸氨基转移酶',
            'BMI': '体重指数',
        }
        
        for metric, full_name in metric_definitions.items():
            unit = 'mL/min' if metric in ['eGFR', 'CrCl'] else ''
            stmt = f"MERGE (m:Metric {{name: '{metric}', full_name: '{full_name}', unit: '{unit}'}})"
            statements.append(stmt + ";")
        
        statements.append("")
        return statements
    
    def generate_drug_node(self, drug_data: Dict) -> List[str]:
        """生成单个药品节点及其关系"""
        statements = []
        drug = drug_data['drug']
        drug_name = self.escape_string(drug['name'])
        drug_id = drug['id']
        
        # 1. 创建Drug节点
        properties = [
            f"id: '{drug_id}'",
            f"name: '{drug_name}'",
            f"en_name: '{self.escape_string(drug.get('en_name', ''))}'"
        ]
        
        # 添加剂量信息
        dosage_info = drug.get('dosage_info', {})
        if dosage_info.get('max_daily_dose'):
            properties.append(f"max_daily_dose: '{self.escape_string(dosage_info['max_daily_dose'])}'")
        if dosage_info.get('starting_dose'):
            properties.append(f"starting_dose: '{self.escape_string(dosage_info['starting_dose'])}'")
        if dosage_info.get('timing'):
            properties.append(f"timing: '{self.escape_string(dosage_info['timing'])}'")
        if dosage_info.get('route'):
            properties.append(f"route: '{self.escape_string(dosage_info['route'])}'")
        
        drug_props = ", ".join(properties)
        statements.append(f"MERGE (d{drug_id}:Drug {{{drug_props}}});")
        
        # 2. 创建Brand节点并关联
        for brand in drug_data.get('brands', []):
            if brand:
                brand_escaped = self.escape_string(brand)
                self.brands.add(brand)
                statements.append(f"MERGE (b{drug_id}_{hash(brand) % 10000}:Brand {{name: '{brand_escaped}'}});")
                statements.append(f"MATCH (d:Drug {{id: '{drug_id}'}}), (b:Brand {{name: '{brand_escaped}'}}) MERGE (b)-[:IS_BRAND_OF]->(d);")
        
        # 3. 关联Category
        category = drug_data.get('category', '未分类')
        self.categories.add(category)
        statements.append(f"MATCH (d:Drug {{id: '{drug_id}'}}), (c:Category {{name: '{self.escape_string(category)}'}}) MERGE (d)-[:BELONGS_TO]->(c);")
        
        # 4. 创建适应症关系
        for disease in drug_data.get('treats', []):
            disease_name = self.escape_string(disease['name'])
            self.diseases.add(disease_name)
            statements.append(f"MERGE (dis:Disease {{name: '{disease_name}', type: '适应症'}});")
            statements.append(f"MATCH (d:Drug {{id: '{drug_id}'}}), (dis:Disease {{name: '{disease_name}'}}) MERGE (d)-[:TREATS]->(dis);")
        
        # 5. 创建禁忌疾病关系
        for disease in drug_data.get('forbidden_diseases', []):
            disease_name = self.escape_string(disease['name'])
            self.diseases.add(disease_name)
            statements.append(f"MERGE (dis:Disease {{name: '{disease_name}', type: '禁忌'}});")
            statements.append(f"MATCH (d:Drug {{id: '{drug_id}'}}), (dis:Disease {{name: '{disease_name}'}}) MERGE (d)-[:FORBIDDEN_FOR {{severity: '禁忌'}}]->(dis);")
        
        # 6. 创建Metric约束关系
        for constraint in drug_data.get('metric_constraints', []):
            metric = constraint['metric']
            self.metrics.add(metric)
            
            # 创建关系属性
            rel_props = [
                f"operator: '{constraint['operator']}'",
                f"severity: '{constraint.get('severity', 'WARNING')}'",
            ]
            
            if 'value' in constraint:
                rel_props.append(f"value: {constraint['value']}")
            if 'value_min' in constraint:
                rel_props.append(f"value_min: {constraint['value_min']}")
                rel_props.append(f"value_max: {constraint['value_max']}")
            if constraint.get('unit'):
                rel_props.append(f"unit: '{constraint['unit']}'")
            
            rel_props_str = ", ".join(rel_props)
            
            statements.append(f"MATCH (d:Drug {{id: '{drug_id}'}}), (m:Metric {{name: '{metric}'}}) MERGE (d)-[:CONTRAINDICATED_IF {{{rel_props_str}}}]->(m);")
        
        statements.append("")  # 空行分隔
        return statements

    
    def generate_all_cypher(self, graph_data_file: str, output_file: str):
        """生成完整的Cypher脚本"""
        print("=" * 60)
        print("🔧 Cypher脚本生成器")
        print("=" * 60)
        
        # 读取图谱数据
        print(f"📖 读取: {graph_data_file}")
        with open(graph_data_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        
        print(f"📊 药品数量: {len(graph_data)}")
        
        # 第一遍:收集所有节点类型
        print("🔍 分析节点和关系...")
        for drug_data in graph_data:
            self.categories.add(drug_data.get('category', '未分类'))
            for disease in drug_data.get('treats', []):
                self.diseases.add(disease['name'])
            for disease in drug_data.get('forbidden_diseases', []):
                self.diseases.add(disease['name'])
            for constraint in drug_data.get('metric_constraints', []):
                self.metrics.add(constraint['metric'])
        
        print(f"   Category节点: {len(self.categories)}")
        print(f"   Disease节点: {len(self.diseases)}")
        print(f"   Metric节点: {len(self.metrics)}")
        
        # 生成Cypher语句
        print("\n🏗️  生成Cypher语句...")
        statements = []
        
        # 添加头部注释
        statements.extend([
            "// ========================================",
            "// 糖尿病药品知识图谱 - Neo4j导入脚本",
            "// ========================================",
            "// 自动生成时间: 2026-02-06",
            f"// 药品数量: {len(graph_data)}",
            f"// Category: {len(self.categories)}",
            f"// Disease: {len(self.diseases)}",
            f"// Metric: {len(self.metrics)}",
            "// ========================================",
            "",
        ])
        
        # 1. 约束和索引
        statements.extend(self.generate_constraints_and_indexes())
        
        # 2. Category节点
        statements.extend(self.generate_category_nodes())
        
        # 3. Metric节点
        statements.extend(self.generate_metric_nodes())
        
        # 4. 药品节点和关系
        statements.append("// ========================================")
        statements.append("// 4. 创建药品节点及其关系")
        statements.append("// ========================================")
        statements.append("")
        
        for i, drug_data in enumerate(graph_data):
            statements.append(f"// ------ 药品 {i+1}/{len(graph_data)}: {drug_data['drug']['name']} ------")
            statements.extend(self.generate_drug_node(drug_data))
        
        # 写入文件
        print(f"\n💾 保存到: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(statements))
        
        # 统计
        print("\n" + "=" * 60)
        print("📈 生成统计")
        print("=" * 60)
        print(f"总语句数: {len(statements)}")
        print(f"Category节点: {len(self.categories)}")
        print(f"Metric节点: {len(self.metrics)}")
        print(f"Disease节点: {len(self.diseases)}")
        print(f"Brand节点: {len(self.brands)}")
        print(f"Drug节点: {len(graph_data)}")
        
        print("\n✅ Cypher脚本生成完成!")
        print(f"📄 文件大小: {len('\n'.join(statements)) // 1024} KB")


def main():
    generator = CypherGenerator()
    generator.generate_all_cypher(
        graph_data_file="graph_data.json",
        output_file="import_graph.cypher"
    )


if __name__ == "__main__":
    main()

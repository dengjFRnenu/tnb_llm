// ========================================
// 糖尿病药品知识图谱 - Neo4j导入脚本
// ========================================
// 自动生成时间: 2026-02-06
// 药品数量: 108
// Category: 8
// Disease: 29
// Metric: 2
// ========================================

// ========================================
// 1. 创建约束和索引
// ========================================

// 唯一性约束
CREATE CONSTRAINT drug_name_unique IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT brand_name_unique IF NOT EXISTS FOR (b:Brand) REQUIRE b.name IS UNIQUE;
CREATE CONSTRAINT category_name_unique IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE;

// 索引
CREATE INDEX drug_id_idx IF NOT EXISTS FOR (d:Drug) ON (d.id);
CREATE INDEX disease_name_idx IF NOT EXISTS FOR (dis:Disease) ON (dis.name);
CREATE INDEX metric_name_idx IF NOT EXISTS FOR (m:Metric) ON (m.name);

// ========================================
// 2. 创建药物分类节点
// ========================================

MERGE (c:Category {name: 'GLP-1激动剂'});
MERGE (c:Category {name: 'α-糖苷酶抑制剂'});
MERGE (c:Category {name: '其他'});
MERGE (c:Category {name: '双胍类'});
MERGE (c:Category {name: '未分类'});
MERGE (c:Category {name: '磺脲类'});
MERGE (c:Category {name: '胆汁酸螯合剂'});
MERGE (c:Category {name: '胰岛素'});

// ========================================
// 3. 创建临床指标节点
// ========================================

MERGE (m:Metric {name: 'eGFR', full_name: '肾小球滤过率', unit: 'mL/min'});
MERGE (m:Metric {name: 'CrCl', full_name: '肌酐清除率', unit: 'mL/min'});
MERGE (m:Metric {name: 'ALT', full_name: '丙氨酸氨基转移酶', unit: ''});
MERGE (m:Metric {name: 'AST', full_name: '天冬氨酸氨基转移酶', unit: ''});
MERGE (m:Metric {name: 'BMI', full_name: '体重指数', unit: ''});

// ========================================
// 4. 创建药品节点及其关系
// ========================================

// ------ 药品 1/108: 盐酸二甲双胍片 ------
MERGE (d1:Drug {id: '1', name: '盐酸二甲双胍片', en_name: 'Metformin Hydrochloride Tablets', max_daily_dose: '2550mg', starting_dose: '500mg', timing: '随餐'});
MERGE (b1_8817:Brand {name: '格华止'});
MATCH (d:Drug {id: '1'}), (b:Brand {name: '格华止'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '1'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '心力衰竭', type: '禁忌'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '心力衰竭'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '心肌梗死', type: '禁忌'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '心肌梗死'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能不全', type: '禁忌'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '肾功能不全'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肝功能不全', type: '禁忌'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '肝功能不全'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '代谢性酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '代谢性酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酒精中毒', type: '禁忌'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '酒精中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酗酒', type: '禁忌'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '酗酒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '休克', type: '禁忌'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '休克'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '感染', type: '禁忌'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '感染'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '呼吸衰竭', type: '禁忌'});
MATCH (d:Drug {id: '1'}), (dis:Disease {name: '呼吸衰竭'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '1'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);

// ------ 药品 2/108: 阿卡波糖片 ------
MERGE (d2:Drug {id: '2', name: '阿卡波糖片', en_name: 'Acarbose Tablets', starting_dose: '50mg', timing: '餐前'});
MERGE (b2_519:Brand {name: '拜糖苹'});
MATCH (d:Drug {id: '2'}), (b:Brand {name: '拜糖苹'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '2'}), (c:Category {name: 'α-糖苷酶抑制剂'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '2'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '2'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '肾功能损害', type: '禁忌'});
MATCH (d:Drug {id: '2'}), (dis:Disease {name: '肾功能损害'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '2'}), (m:Metric {name: 'CrCl'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 25.0, unit: 'mL/min'}]->(m);

// ------ 药品 3/108: 格列美脲片 ------
MERGE (d3:Drug {id: '3', name: '格列美脲片', en_name: 'Glimepiride Tablets', max_daily_dose: '6mg', starting_dose: '1mg', timing: '餐前'});
MERGE (b3_5837:Brand {name: '亚莫利'});
MATCH (d:Drug {id: '3'}), (b:Brand {name: '亚莫利'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '3'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '3'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '3'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '1型糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '3'}), (dis:Disease {name: '1型糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '3'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '3'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能损害', type: '禁忌'});
MATCH (d:Drug {id: '3'}), (dis:Disease {name: '肾功能损害'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 4/108: 瑞格列奈片 ------
MERGE (d4:Drug {id: '4', name: '瑞格列奈片', en_name: 'Repaglinide Tablets', starting_dose: '0.5mg', timing: '餐前'});
MERGE (b4_9671:Brand {name: '诺和龙'});
MATCH (d:Drug {id: '4'}), (b:Brand {name: '诺和龙'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '4'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '4'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '4'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '高血糖', type: '适应症'});
MATCH (d:Drug {id: '4'}), (dis:Disease {name: '高血糖'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '1型糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '4'}), (dis:Disease {name: '1型糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '4'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '4'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能不全', type: '禁忌'});
MATCH (d:Drug {id: '4'}), (dis:Disease {name: '肾功能不全'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 5/108: 盐酸吡格列酮片 ------
MERGE (d6:Drug {id: '6', name: '盐酸吡格列酮片', en_name: 'Pioglitazone Hydrochloride Tablets', starting_dose: '15mg', timing: '餐前'});
MERGE (b6_9310:Brand {name: '艾汀'});
MATCH (d:Drug {id: '6'}), (b:Brand {name: '艾汀'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MERGE (b6_1481:Brand {name: '卡司平'});
MATCH (d:Drug {id: '6'}), (b:Brand {name: '卡司平'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '6'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '6'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '6'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '6'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '6'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '心力衰竭', type: '禁忌'});
MATCH (d:Drug {id: '6'}), (dis:Disease {name: '心力衰竭'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肝功能损害', type: '禁忌'});
MATCH (d:Drug {id: '6'}), (dis:Disease {name: '肝功能损害'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '膀胱癌', type: '禁忌'});
MATCH (d:Drug {id: '6'}), (dis:Disease {name: '膀胱癌'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 6/108: 达格列净片 ------
MERGE (d7:Drug {id: '7', name: '达格列净片', en_name: 'Dapagliflozin Tablets', starting_dose: '5mg'});
MERGE (b7_6173:Brand {name: '安达唐'});
MATCH (d:Drug {id: '7'}), (b:Brand {name: '安达唐'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '7'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '7'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '7'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '心力衰竭', type: '适应症'});
MATCH (d:Drug {id: '7'}), (dis:Disease {name: '心力衰竭'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '心衰', type: '适应症'});
MATCH (d:Drug {id: '7'}), (dis:Disease {name: '心衰'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '慢性肾脏病', type: '适应症'});
MATCH (d:Drug {id: '7'}), (dis:Disease {name: '慢性肾脏病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: 'CKD', type: '适应症'});
MATCH (d:Drug {id: '7'}), (dis:Disease {name: 'CKD'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '终末期肾病', type: '适应症'});
MATCH (d:Drug {id: '7'}), (dis:Disease {name: '终末期肾病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '肾功能损害', type: '禁忌'});
MATCH (d:Drug {id: '7'}), (dis:Disease {name: '肾功能损害'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '7'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);
MATCH (d:Drug {id: '7'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'WARNING', value: 25.0, unit: 'mL/min'}]->(m);
MATCH (d:Drug {id: '7'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'WARNING', value: 45.0, unit: 'mL/min'}]->(m);

// ------ 药品 7/108: 恩格列净片 ------
MERGE (d8:Drug {id: '8', name: '恩格列净片', en_name: 'Empagliflozin Tablets', timing: '空腹'});
MERGE (b8_2938:Brand {name: '欧唐静'});
MATCH (d:Drug {id: '8'}), (b:Brand {name: '欧唐静'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '8'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '8'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '8'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '心力衰竭', type: '适应症'});
MATCH (d:Drug {id: '8'}), (dis:Disease {name: '心力衰竭'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '心衰', type: '适应症'});
MATCH (d:Drug {id: '8'}), (dis:Disease {name: '心衰'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '心血管疾病', type: '适应症'});
MATCH (d:Drug {id: '8'}), (dis:Disease {name: '心血管疾病'}) MERGE (d)-[:TREATS]->(dis);
MATCH (d:Drug {id: '8'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);

// ------ 药品 8/108: 维格列汀片 ------
MERGE (d9:Drug {id: '9', name: '维格列汀片', en_name: 'Vildagliptin Tablets', timing: '餐前'});
MERGE (b9_7184:Brand {name: '佳维'});
MATCH (d:Drug {id: '9'}), (b:Brand {name: '佳维'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '9'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '9'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '9'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '1型糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '9'}), (dis:Disease {name: '1型糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '9'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '9'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肝功能损害', type: '禁忌'});
MATCH (d:Drug {id: '9'}), (dis:Disease {name: '肝功能损害'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 9/108: 利格列汀片 ------
MERGE (d10:Drug {id: '10', name: '利格列汀片', en_name: 'Linagliptin Tablets', timing: '餐前'});
MERGE (b10_7500:Brand {name: '欧唐宁'});
MATCH (d:Drug {id: '10'}), (b:Brand {name: '欧唐宁'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '10'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '10'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '10'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);

// ------ 药品 10/108: 利拉鲁肽注射液 ------
MERGE (d11:Drug {id: '11', name: '利拉鲁肽注射液', en_name: 'Liraglutide Injection'});
MATCH (d:Drug {id: '11'}), (c:Category {name: '未分类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 11/108: 司美格鲁肽注射液 ------
MERGE (d12:Drug {id: '12', name: '司美格鲁肽注射液', en_name: 'Semaglutide Injection'});
MATCH (d:Drug {id: '12'}), (c:Category {name: '未分类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 12/108: 伏格列波糖片 ------
MERGE (d13:Drug {id: '13', name: '伏格列波糖片', en_name: 'Voglibose Tablets'});
MATCH (d:Drug {id: '13'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 13/108: 那格列奈片 ------
MERGE (d14:Drug {id: '14', name: '那格列奈片', en_name: 'Nateglinide Tablets'});
MATCH (d:Drug {id: '14'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 14/108: 格列齐特缓释片 ------
MERGE (d15:Drug {id: '15', name: '格列齐特缓释片', en_name: 'Gliclazide Sustained-release Tablets'});
MATCH (d:Drug {id: '15'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 15/108: 沙格列汀片 ------
MERGE (d16:Drug {id: '16', name: '沙格列汀片', en_name: 'Saxagliptin Tablets'});
MATCH (d:Drug {id: '16'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 16/108: 卡格列净片 ------
MERGE (d17:Drug {id: '17', name: '卡格列净片', en_name: 'Canagliflozin Tablets'});
MATCH (d:Drug {id: '17'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 17/108: 罗格列酮片 ------
MERGE (d18:Drug {id: '18', name: '罗格列酮片', en_name: 'Rosiglitazone Tablets'});
MATCH (d:Drug {id: '18'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 18/108: 格列喹酮片 ------
MERGE (d19:Drug {id: '19', name: '格列喹酮片', en_name: 'Gliquidone Tablets'});
MATCH (d:Drug {id: '19'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 19/108: 艾塞那肽注射液 ------
MERGE (d20:Drug {id: '20', name: '艾塞那肽注射液', en_name: 'Exenatide Injection'});
MATCH (d:Drug {id: '20'}), (c:Category {name: 'GLP-1激动剂'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 20/108: 门冬胰岛素注射液 ------
MERGE (d21:Drug {id: '21', name: '门冬胰岛素注射液', en_name: 'Insulin Aspart'});
MATCH (d:Drug {id: '21'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 21/108: 门冬胰岛素 30 注射液 ------
MERGE (d22:Drug {id: '22', name: '门冬胰岛素 30 注射液', en_name: 'Insulin Aspart 30'});
MATCH (d:Drug {id: '22'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 22/108: 德谷胰岛素注射液 ------
MERGE (d23:Drug {id: '23', name: '德谷胰岛素注射液', en_name: 'Insulin Degludec'});
MATCH (d:Drug {id: '23'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 23/108: 甘精胰岛素 U300 ------
MERGE (d24:Drug {id: '24', name: '甘精胰岛素 U300', en_name: 'Insulin Glargine 300 U/mL'});
MATCH (d:Drug {id: '24'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 24/108: 度拉糖肽注射液 ------
MERGE (d25:Drug {id: '25', name: '度拉糖肽注射液', en_name: 'Dulaglutide'});
MATCH (d:Drug {id: '25'}), (c:Category {name: '未分类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 25/108: 聚乙二醇洛塞那肽注射液 ------
MERGE (d26:Drug {id: '26', name: '聚乙二醇洛塞那肽注射液', en_name: 'Polyethylene Glycol Loxenatide'});
MATCH (d:Drug {id: '26'}), (c:Category {name: 'GLP-1激动剂'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 26/108: 阿格列汀片 ------
MERGE (d27:Drug {id: '27', name: '阿格列汀片', en_name: 'Alogliptin Tablets'});
MATCH (d:Drug {id: '27'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 27/108: 德谷门冬双胰岛素注射液 ------
MERGE (d28:Drug {id: '28', name: '德谷门冬双胰岛素注射液', en_name: 'Insulin Degludec/Insulin Aspart'});
MATCH (d:Drug {id: '28'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 28/108: 米格列奈钙片 ------
MERGE (d29:Drug {id: '29', name: '米格列奈钙片', en_name: 'Mitiglinide Calcium Tablets'});
MATCH (d:Drug {id: '29'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 29/108: 利司那肽注射液 ------
MERGE (d30:Drug {id: '30', name: '利司那肽注射液', en_name: 'Lixisenatide Injection'});
MATCH (d:Drug {id: '30'}), (c:Category {name: 'GLP-1激动剂'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 30/108: 伏格列波糖散 ------
MERGE (d31:Drug {id: '31', name: '伏格列波糖散', en_name: 'Voglibose Dispersible Tablets'});
MATCH (d:Drug {id: '31'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 31/108: 米格列醇片 ------
MERGE (d32:Drug {id: '32', name: '米格列醇片', en_name: 'Miglitol Tablets'});
MATCH (d:Drug {id: '32'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 32/108: 格列喹酮片 ------
MERGE (d33:Drug {id: '33', name: '格列喹酮片', en_name: 'Gliquidone'});
MATCH (d:Drug {id: '33'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 33/108: 格列本脲 ------
MERGE (d34:Drug {id: '34', name: '格列本脲', en_name: 'Glibenclamide'});
MATCH (d:Drug {id: '34'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 34/108: 精蛋白锌重组人胰岛素注射液 ------
MERGE (d35:Drug {id: '35', name: '精蛋白锌重组人胰岛素注射液', en_name: 'NPH'});
MATCH (d:Drug {id: '35'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 35/108: 精蛋白锌重组人胰岛素混合注射液 ------
MERGE (d36:Drug {id: '36', name: '精蛋白锌重组人胰岛素混合注射液', en_name: '70/30'});
MATCH (d:Drug {id: '36'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 36/108: 地特胰岛素 ------
MERGE (d37:Drug {id: '37', name: '地特胰岛素', en_name: 'Insulin Detemir'});
MATCH (d:Drug {id: '37'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 37/108: 艾塞那肽周制剂 ------
MERGE (d38:Drug {id: '38', name: '艾塞那肽周制剂', en_name: 'Exenatide Extended-Release'});
MATCH (d:Drug {id: '38'}), (c:Category {name: 'GLP-1激动剂'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 38/108: 考来维仑 ------
MERGE (d39:Drug {id: '39', name: '考来维仑', en_name: 'Colesevelam'});
MATCH (d:Drug {id: '39'}), (c:Category {name: '胆汁酸螯合剂'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 39/108: 普兰林肽 ------
MERGE (d40:Drug {id: '40', name: '普兰林肽', en_name: 'Pramlintide'});
MATCH (d:Drug {id: '40'}), (c:Category {name: '其他'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 40/108: 盐酸二甲双胍片 ------
MERGE (d51:Drug {id: '51', name: '盐酸二甲双胍片', en_name: 'Metformin Hydrochloride Tablets', max_daily_dose: '2.55g', starting_dose: '0.5g', timing: '随餐'});
MERGE (b51_6357:Brand {name: '格华止 (Glucophage)'});
MATCH (d:Drug {id: '51'}), (b:Brand {name: '格华止 (Glucophage)'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '51'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '51'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '51'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '51'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '心力衰竭', type: '禁忌'});
MATCH (d:Drug {id: '51'}), (dis:Disease {name: '心力衰竭'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '心肌梗死', type: '禁忌'});
MATCH (d:Drug {id: '51'}), (dis:Disease {name: '心肌梗死'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能不全', type: '禁忌'});
MATCH (d:Drug {id: '51'}), (dis:Disease {name: '肾功能不全'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肝功能不全', type: '禁忌'});
MATCH (d:Drug {id: '51'}), (dis:Disease {name: '肝功能不全'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '代谢性酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '51'}), (dis:Disease {name: '代谢性酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酒精中毒', type: '禁忌'});
MATCH (d:Drug {id: '51'}), (dis:Disease {name: '酒精中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酗酒', type: '禁忌'});
MATCH (d:Drug {id: '51'}), (dis:Disease {name: '酗酒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '休克', type: '禁忌'});
MATCH (d:Drug {id: '51'}), (dis:Disease {name: '休克'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '感染', type: '禁忌'});
MATCH (d:Drug {id: '51'}), (dis:Disease {name: '感染'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '51'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);
MATCH (d:Drug {id: '51'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'WARNING', value: 45.0, unit: 'mL/min'}]->(m);
MATCH (d:Drug {id: '51'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: 'BETWEEN', severity: 'WARNING', value_min: 45.0, value_max: 59.0, unit: 'mL/min'}]->(m);

// ------ 药品 41/108: 盐酸二甲双胍缓释片 ------
MERGE (d52:Drug {id: '52', name: '盐酸二甲双胍缓释片', en_name: '格华止 XR 0.5g 规格', max_daily_dose: '2000mg', starting_dose: '500mg', timing: '随餐'});
MERGE (b52_3899:Brand {name: '格华止 XR (Glucophage XR)'});
MATCH (d:Drug {id: '52'}), (b:Brand {name: '格华止 XR (Glucophage XR)'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '52'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '52'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '52'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);

// ------ 药品 42/108: 二甲双胍格列本脲片 (I) ------
MERGE (d54:Drug {id: '54', name: '二甲双胍格列本脲片 (I)', en_name: 'I', timing: '随餐'});
MATCH (d:Drug {id: '54'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '54'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '54'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '1型糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '54'}), (dis:Disease {name: '1型糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '54'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '54'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '心衰', type: '禁忌'});
MATCH (d:Drug {id: '54'}), (dis:Disease {name: '心衰'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能不全', type: '禁忌'});
MATCH (d:Drug {id: '54'}), (dis:Disease {name: '肾功能不全'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 43/108: 西格列汀二甲双胍片 (II) ------
MERGE (d55:Drug {id: '55', name: '西格列汀二甲双胍片 (II)', en_name: 'II', timing: '随餐'});
MATCH (d:Drug {id: '55'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '55'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '55'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '代谢性酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '55'}), (dis:Disease {name: '代谢性酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '55'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);

// ------ 药品 44/108: 维格列汀二甲双胍片 ------
MERGE (d56:Drug {id: '56', name: '维格列汀二甲双胍片', en_name: 'Vildagliptin and Metformin Hydrochloride Tablets', timing: '随餐'});
MATCH (d:Drug {id: '56'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '56'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '56'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '56'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '56'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '心力衰竭', type: '禁忌'});
MATCH (d:Drug {id: '56'}), (dis:Disease {name: '心力衰竭'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '心肌梗死', type: '禁忌'});
MATCH (d:Drug {id: '56'}), (dis:Disease {name: '心肌梗死'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能不全', type: '禁忌'});
MATCH (d:Drug {id: '56'}), (dis:Disease {name: '肾功能不全'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '代谢性酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '56'}), (dis:Disease {name: '代谢性酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酒精中毒', type: '禁忌'});
MATCH (d:Drug {id: '56'}), (dis:Disease {name: '酒精中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '休克', type: '禁忌'});
MATCH (d:Drug {id: '56'}), (dis:Disease {name: '休克'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '感染', type: '禁忌'});
MATCH (d:Drug {id: '56'}), (dis:Disease {name: '感染'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '56'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);
MATCH (d:Drug {id: '56'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: 'BETWEEN', severity: 'WARNING', value_min: 30.0, value_max: 44.0, unit: 'mL/min'}]->(m);

// ------ 药品 45/108: 恩格列净二甲双胍片 ------
MERGE (d57:Drug {id: '57', name: '恩格列净二甲双胍片', en_name: 'Empagliflozin and Metformin Hydrochloride Tablets', timing: '随餐'});
MATCH (d:Drug {id: '57'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '57'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '57'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '57'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '57'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肝功能不全', type: '禁忌'});
MATCH (d:Drug {id: '57'}), (dis:Disease {name: '肝功能不全'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '代谢性酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '57'}), (dis:Disease {name: '代谢性酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '57'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);
MATCH (d:Drug {id: '57'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'WARNING', value: 45.0, unit: 'mL/min'}]->(m);

// ------ 药品 46/108: 利格列汀二甲双胍片 ------
MERGE (d58:Drug {id: '58', name: '利格列汀二甲双胍片', en_name: 'Linagliptin and Metformin Hydrochloride Tablets', timing: '随餐'});
MATCH (d:Drug {id: '58'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '58'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '58'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '肾功能受损', type: '禁忌'});
MATCH (d:Drug {id: '58'}), (dis:Disease {name: '肾功能受损'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '代谢性酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '58'}), (dis:Disease {name: '代谢性酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '58'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);

// ------ 药品 47/108: 沙格列汀二甲双胍缓释片 ------
MERGE (d59:Drug {id: '59', name: '沙格列汀二甲双胍缓释片', en_name: 'Saxagliptin and Metformin Hydrochloride Extended-Release Tablets', timing: '晚餐时'});
MATCH (d:Drug {id: '59'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '59'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '59'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '59'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '59'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能不全', type: '禁忌'});
MATCH (d:Drug {id: '59'}), (dis:Disease {name: '肾功能不全'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '59'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);
MATCH (d:Drug {id: '59'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: 'BETWEEN', severity: 'WARNING', value_min: 30.0, value_max: 45.0, unit: 'mL/min'}]->(m);

// ------ 药品 48/108: 吡格列酮二甲双胍片 ------
MERGE (d60:Drug {id: '60', name: '吡格列酮二甲双胍片', en_name: 'Pioglitazone Hydrochloride and Metformin Hydrochloride Tablets', timing: '随餐'});
MATCH (d:Drug {id: '60'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '60'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '60'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '60'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '60'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '心力衰竭', type: '禁忌'});
MATCH (d:Drug {id: '60'}), (dis:Disease {name: '心力衰竭'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '代谢性酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '60'}), (dis:Disease {name: '代谢性酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '膀胱癌', type: '禁忌'});
MATCH (d:Drug {id: '60'}), (dis:Disease {name: '膀胱癌'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '60'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);

// ------ 药品 49/108: 苯甲酸阿格列汀二甲双胍片 ------
MERGE (d61:Drug {id: '61', name: '苯甲酸阿格列汀二甲双胍片', en_name: 'Alogliptin Benzoate and Metformin Hydrochloride Tablets', timing: '随餐'});
MATCH (d:Drug {id: '61'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '61'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '61'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '61'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '61'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能损害', type: '禁忌'});
MATCH (d:Drug {id: '61'}), (dis:Disease {name: '肾功能损害'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '代谢性酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '61'}), (dis:Disease {name: '代谢性酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '61'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);
MATCH (d:Drug {id: '61'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: 'BETWEEN', severity: 'WARNING', value_min: 45.0, value_max: 59.0, unit: 'mL/min'}]->(m);

// ------ 药品 50/108: 苯甲酸阿格列汀吡格列酮片 ------
MERGE (d62:Drug {id: '62', name: '苯甲酸阿格列汀吡格列酮片', en_name: 'Alogliptin Benzoate and Pioglitazone Hydrochloride Tablets'});
MATCH (d:Drug {id: '62'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '62'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '62'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '心力衰竭', type: '禁忌'});
MATCH (d:Drug {id: '62'}), (dis:Disease {name: '心力衰竭'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肝功能损害', type: '禁忌'});
MATCH (d:Drug {id: '62'}), (dis:Disease {name: '肝功能损害'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '膀胱癌', type: '禁忌'});
MATCH (d:Drug {id: '62'}), (dis:Disease {name: '膀胱癌'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 51/108: 达格列净沙格列汀片 ------
MERGE (d63:Drug {id: '63', name: '达格列净沙格列汀片', en_name: 'Dapagliflozin and Saxagliptin Tablets'});
MATCH (d:Drug {id: '63'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '63'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '63'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '肾功能损害', type: '禁忌'});
MATCH (d:Drug {id: '63'}), (dis:Disease {name: '肾功能损害'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '63'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);
MATCH (d:Drug {id: '63'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'WARNING', value: 45.0, unit: 'mL/min'}]->(m);

// ------ 药品 52/108: 恩格列净利格列汀片 ------
MERGE (d64:Drug {id: '64', name: '恩格列净利格列汀片', en_name: 'Empagliflozin and Linagliptin Tablets'});
MATCH (d:Drug {id: '64'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '64'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '64'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '终末期肾病', type: '禁忌'});
MATCH (d:Drug {id: '64'}), (dis:Disease {name: '终末期肾病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '64'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);

// ------ 药品 53/108: 埃格列净片 ------
MERGE (d65:Drug {id: '65', name: '埃格列净片', en_name: 'Ertugliflozin Tablets', starting_dose: '5mg'});
MATCH (d:Drug {id: '65'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '65'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '65'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '肾功能损害', type: '禁忌'});
MATCH (d:Drug {id: '65'}), (dis:Disease {name: '肾功能损害'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '65'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);
MATCH (d:Drug {id: '65'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'WARNING', value: 45.0, unit: 'mL/min'}]->(m);

// ------ 药品 54/108: 埃格列净二甲双胍片 ------
MERGE (d66:Drug {id: '66', name: '埃格列净二甲双胍片', en_name: 'Ertugliflozin and Metformin Hydrochloride Tablets', timing: '随餐'});
MATCH (d:Drug {id: '66'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '66'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '66'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '66'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '66'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能损害', type: '禁忌'});
MATCH (d:Drug {id: '66'}), (dis:Disease {name: '肾功能损害'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '终末期肾病', type: '禁忌'});
MATCH (d:Drug {id: '66'}), (dis:Disease {name: '终末期肾病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '代谢性酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '66'}), (dis:Disease {name: '代谢性酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '66'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);
MATCH (d:Drug {id: '66'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'WARNING', value: 45.0, unit: 'mL/min'}]->(m);

// ------ 药品 55/108: 阿必鲁肽 ------
MERGE (d67:Drug {id: '67', name: '阿必鲁肽', en_name: 'Albiglutide', route: '注射'});
MERGE (b67_1216:Brand {name: 'Tanzeum（注：部分地区已停产，但临床数据库仍包含）'});
MATCH (d:Drug {id: '67'}), (b:Brand {name: 'Tanzeum（注：部分地区已停产，但临床数据库仍包含）'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '67'}), (c:Category {name: '未分类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '67'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '67'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '甲状腺髓样癌', type: '禁忌'});
MATCH (d:Drug {id: '67'}), (dis:Disease {name: '甲状腺髓样癌'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: 'MTC', type: '禁忌'});
MATCH (d:Drug {id: '67'}), (dis:Disease {name: 'MTC'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 56/108: 米格列奈钙伏格列波糖片 ------
MERGE (d68:Drug {id: '68', name: '米格列奈钙伏格列波糖片', en_name: 'Mitiglinide Calcium and Voglibose Tablets', timing: '餐前', route: '口服'});
MATCH (d:Drug {id: '68'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '68'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '68'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '高血糖', type: '适应症'});
MATCH (d:Drug {id: '68'}), (dis:Disease {name: '高血糖'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '68'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '感染', type: '禁忌'});
MATCH (d:Drug {id: '68'}), (dis:Disease {name: '感染'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 57/108: 格列齐特片 ------
MERGE (d69:Drug {id: '69', name: '格列齐特片', en_name: 'Gliclazide Tablets'});
MATCH (d:Drug {id: '69'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '69'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '69'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '1型糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '69'}), (dis:Disease {name: '1型糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '69'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能不全', type: '禁忌'});
MATCH (d:Drug {id: '69'}), (dis:Disease {name: '肾功能不全'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 58/108: 格列吡嗪控释片 ------
MERGE (d70:Drug {id: '70', name: '格列吡嗪控释片', en_name: 'Glipizide Gastrointestinal Therapeutic System', starting_dose: '5mg'});
MATCH (d:Drug {id: '70'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '70'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '70'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '1型糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '70'}), (dis:Disease {name: '1型糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '70'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '70'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 59/108: 格列吡嗪片 ------
MERGE (d71:Drug {id: '71', name: '格列吡嗪片', en_name: 'Glipizide Tablets', timing: '餐前', route: '口服'});
MERGE (b71_6548:Brand {name: '美吡达'});
MATCH (d:Drug {id: '71'}), (b:Brand {name: '美吡达'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '71'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '71'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '71'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '1型糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '71'}), (dis:Disease {name: '1型糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '71'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '71'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能不全', type: '禁忌'});
MATCH (d:Drug {id: '71'}), (dis:Disease {name: '肾功能不全'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 60/108: 格列喹酮片 ------
MERGE (d72:Drug {id: '72', name: '格列喹酮片', en_name: 'Gliquidone Tablets', timing: '餐前'});
MERGE (b72_6820:Brand {name: '糖适平'});
MATCH (d:Drug {id: '72'}), (b:Brand {name: '糖适平'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '72'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '72'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '72'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '1型糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '72'}), (dis:Disease {name: '1型糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '72'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '酮症酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '72'}), (dis:Disease {name: '酮症酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能不全', type: '禁忌'});
MATCH (d:Drug {id: '72'}), (dis:Disease {name: '肾功能不全'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 61/108: 马来酸罗格列酮片 ------
MERGE (d73:Drug {id: '73', name: '马来酸罗格列酮片', en_name: '文迪雅 / Rosiglitazone Maleate Tablets', starting_dose: '4mg'});
MERGE (b73_1180:Brand {name: '文迪雅 (Avandia)'});
MATCH (d:Drug {id: '73'}), (b:Brand {name: '文迪雅 (Avandia)'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '73'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '73'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '73'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '肝功能损害', type: '禁忌'});
MATCH (d:Drug {id: '73'}), (dis:Disease {name: '肝功能损害'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 62/108: 罗格列酮钠片 ------
MERGE (d74:Drug {id: '74', name: '罗格列酮钠片', en_name: '太罗 / Rosiglitazone Sodium Tablets', timing: '餐前'});
MATCH (d:Drug {id: '74'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 63/108: 罗格列酮二甲双胍片 ------
MERGE (d75:Drug {id: '75', name: '罗格列酮二甲双胍片', en_name: 'Rosiglitazone Maleate and Metformin Hydrochloride Tablets', timing: '随餐'});
MATCH (d:Drug {id: '75'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '75'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '75'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '心力衰竭', type: '禁忌'});
MATCH (d:Drug {id: '75'}), (dis:Disease {name: '心力衰竭'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '充血性心力衰竭', type: '禁忌'});
MATCH (d:Drug {id: '75'}), (dis:Disease {name: '充血性心力衰竭'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能损害', type: '禁忌'});
MATCH (d:Drug {id: '75'}), (dis:Disease {name: '肾功能损害'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '代谢性酸中毒', type: '禁忌'});
MATCH (d:Drug {id: '75'}), (dis:Disease {name: '代谢性酸中毒'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 64/108: 瑞格列奈二甲双胍片 ------
MERGE (d76:Drug {id: '76', name: '瑞格列奈二甲双胍片', en_name: 'Repaglinide and Metformin Hydrochloride Tablets', timing: '餐前'});
MATCH (d:Drug {id: '76'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '76'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '76'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '1型糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '76'}), (dis:Disease {name: '1型糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '禁忌'});
MATCH (d:Drug {id: '76'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '肾功能不全', type: '禁忌'});
MATCH (d:Drug {id: '76'}), (dis:Disease {name: '肾功能不全'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 65/108: 中性重组人胰岛素注射液 ------
MERGE (d77:Drug {id: '77', name: '中性重组人胰岛素注射液', en_name: '诺和灵 R / Novolin R', timing: '餐前', route: '注射'});
MERGE (b77_4426:Brand {name: '诺和灵 R'});
MATCH (d:Drug {id: '77'}), (b:Brand {name: '诺和灵 R'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '77'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '77'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '低血糖', type: '禁忌'});
MATCH (d:Drug {id: '77'}), (dis:Disease {name: '低血糖'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 66/108: 低精蛋白重组人胰岛素注射液 ------
MERGE (d78:Drug {id: '78', name: '低精蛋白重组人胰岛素注射液', en_name: '诺和灵 N / Novolin N', route: '注射'});
MERGE (b78_9235:Brand {name: '诺和灵 N'});
MATCH (d:Drug {id: '78'}), (b:Brand {name: '诺和灵 N'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '78'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '78'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);

// ------ 药品 67/108: 精蛋白重组人胰岛素混合注射液 ------
MERGE (d79:Drug {id: '79', name: '精蛋白重组人胰岛素混合注射液', en_name: '30R', timing: '餐前', route: '注射'});
MATCH (d:Drug {id: '79'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 68/108: 精蛋白重组人胰岛素混合注射液 ------
MERGE (d80:Drug {id: '80', name: '精蛋白重组人胰岛素混合注射液', en_name: '50R', timing: '餐前', route: '注射'});
MATCH (d:Drug {id: '80'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 69/108: 重组人胰岛素注射液 ------
MERGE (d81:Drug {id: '81', name: '重组人胰岛素注射液', en_name: 'Recombinant Human Insulin Injection', timing: '餐前', route: '注射'});
MERGE (b81_2015:Brand {name: '优泌林 R'});
MATCH (d:Drug {id: '81'}), (b:Brand {name: '优泌林 R'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '81'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '81'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '低血糖', type: '禁忌'});
MATCH (d:Drug {id: '81'}), (dis:Disease {name: '低血糖'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 70/108: 精蛋白锌重组人胰岛素注射液 ------
MERGE (d82:Drug {id: '82', name: '精蛋白锌重组人胰岛素注射液', en_name: 'Isophane Protamine Recombinant Human Insulin Injection', route: '注射'});
MERGE (b82_5963:Brand {name: '优泌林 N'});
MATCH (d:Drug {id: '82'}), (b:Brand {name: '优泌林 N'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '82'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '82'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '低血糖', type: '禁忌'});
MATCH (d:Drug {id: '82'}), (dis:Disease {name: '低血糖'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 71/108: 精蛋白锌重组人胰岛素混合注射液 ------
MERGE (d83:Drug {id: '83', name: '精蛋白锌重组人胰岛素混合注射液', en_name: '70/30', timing: '餐前', route: '注射'});
MATCH (d:Drug {id: '83'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '低血糖', type: '禁忌'});
MATCH (d:Drug {id: '83'}), (dis:Disease {name: '低血糖'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 72/108: 赖脯胰岛素注射液 ------
MERGE (d84:Drug {id: '84', name: '赖脯胰岛素注射液', en_name: 'Insulin Lispro Injection', timing: '餐前', route: '注射'});
MERGE (b84_205:Brand {name: '优泌乐'});
MATCH (d:Drug {id: '84'}), (b:Brand {name: '优泌乐'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '84'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '84'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '低血糖', type: '禁忌'});
MATCH (d:Drug {id: '84'}), (dis:Disease {name: '低血糖'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 73/108: 精蛋白锌赖脯胰岛素混合注射液 (25R) ------
MERGE (d85:Drug {id: '85', name: '精蛋白锌赖脯胰岛素混合注射液 (25R)', en_name: '25R', timing: '餐前', route: '注射'});
MERGE (b85_2639:Brand {name: '优泌乐 25'});
MATCH (d:Drug {id: '85'}), (b:Brand {name: '优泌乐 25'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '85'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 74/108: 精蛋白锌赖脯胰岛素混合注射液 ------
MERGE (d86:Drug {id: '86', name: '精蛋白锌赖脯胰岛素混合注射液', en_name: '50R', timing: '餐前', route: '注射'});
MATCH (d:Drug {id: '86'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 75/108: 谷赖胰岛素注射液 ------
MERGE (d87:Drug {id: '87', name: '谷赖胰岛素注射液', en_name: 'Insulin Glulisine Injection', timing: '餐前', route: '注射'});
MATCH (d:Drug {id: '87'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '低血糖', type: '禁忌'});
MATCH (d:Drug {id: '87'}), (dis:Disease {name: '低血糖'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 76/108: 甘精胰岛素注射液 ------
MERGE (d88:Drug {id: '88', name: '甘精胰岛素注射液', en_name: 'Insulin Glargine Injection', route: '注射'});
MERGE (b88_5354:Brand {name: '来得时'});
MATCH (d:Drug {id: '88'}), (b:Brand {name: '来得时'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '88'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '88'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);

// ------ 药品 77/108: 地特胰岛素注射液 ------
MERGE (d89:Drug {id: '89', name: '地特胰岛素注射液', en_name: 'Insulin Detemir Injection', timing: '睡前', route: '注射'});
MATCH (d:Drug {id: '89'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 78/108: 德谷胰岛素注射液 ------
MERGE (d90:Drug {id: '90', name: '德谷胰岛素注射液', en_name: 'Insulin Degludec Injection', route: '注射'});
MATCH (d:Drug {id: '90'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 79/108: 门冬胰岛素 50 注射液 ------
MERGE (d91:Drug {id: '91', name: '门冬胰岛素 50 注射液', en_name: 'Biphasic Insulin Aspart 50 Injection', timing: '餐前', route: '注射'});
MERGE (b91_1246:Brand {name: '诺和锐 50'});
MATCH (d:Drug {id: '91'}), (b:Brand {name: '诺和锐 50'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '91'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '91'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '低血糖', type: '禁忌'});
MATCH (d:Drug {id: '91'}), (dis:Disease {name: '低血糖'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 80/108: 德谷门冬双胰岛素注射液 ------
MERGE (d92:Drug {id: '92', name: '德谷门冬双胰岛素注射液', en_name: 'Insulin Degludec and Insulin Aspart Injection', route: '注射'});
MERGE (b92_6906:Brand {name: '诺和益'});
MATCH (d:Drug {id: '92'}), (b:Brand {name: '诺和益'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '92'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '92'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '92'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '低血糖', type: '禁忌'});
MATCH (d:Drug {id: '92'}), (dis:Disease {name: '低血糖'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 81/108: 甘精胰岛素 U300 ------
MERGE (d93:Drug {id: '93', name: '甘精胰岛素 U300', en_name: 'Insulin Glargine 300 U/mL Injection', route: '注射'});
MERGE (b93_1501:Brand {name: '来优时'});
MATCH (d:Drug {id: '93'}), (b:Brand {name: '来优时'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '93'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 82/108: 注射用艾塞那肽微球 ------
MERGE (d94:Drug {id: '94', name: '注射用艾塞那肽微球', en_name: 'Exenatide Extended-Release for Injectable Suspension', route: '注射'});
MATCH (d:Drug {id: '94'}), (c:Category {name: 'GLP-1激动剂'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '94'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '94'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '肾功能受损', type: '禁忌'});
MATCH (d:Drug {id: '94'}), (dis:Disease {name: '肾功能受损'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '甲状腺髓样癌', type: '禁忌'});
MATCH (d:Drug {id: '94'}), (dis:Disease {name: '甲状腺髓样癌'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: 'MTC', type: '禁忌'});
MATCH (d:Drug {id: '94'}), (dis:Disease {name: 'MTC'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '94'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);

// ------ 药品 83/108: 贝那鲁肽注射液 ------
MERGE (d95:Drug {id: '95', name: '贝那鲁肽注射液', en_name: '谊生泰 / Beinaglutide', starting_dose: '0.05mg', timing: '餐前', route: '注射'});
MERGE (b95_5591:Brand {name: '谊生泰'});
MATCH (d:Drug {id: '95'}), (b:Brand {name: '谊生泰'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '95'}), (c:Category {name: 'GLP-1激动剂'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '95'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '95'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);

// ------ 药品 84/108: 聚乙二醇洛塞那肽注射液 ------
MERGE (d96:Drug {id: '96', name: '聚乙二醇洛塞那肽注射液', en_name: '孚来美 / Loxenatide', route: '注射'});
MERGE (b96_9446:Brand {name: '孚来美'});
MATCH (d:Drug {id: '96'}), (b:Brand {name: '孚来美'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '96'}), (c:Category {name: 'GLP-1激动剂'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 85/108: 德谷胰岛素利拉鲁肽注射液 ------
MERGE (d97:Drug {id: '97', name: '德谷胰岛素利拉鲁肽注射液', en_name: 'Insulin Degludec and Liraglutide Injection', route: '注射'});
MERGE (b97_6493:Brand {name: '诺和佳'});
MATCH (d:Drug {id: '97'}), (b:Brand {name: '诺和佳'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '97'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 86/108: 甘精胰岛素利司那肽注射液 ------
MERGE (d98:Drug {id: '98', name: '甘精胰岛素利司那肽注射液', en_name: 'Insulin Glargine and Lixisenatide Injection', timing: '餐前'});
MERGE (b98_212:Brand {name: '赛益宁'});
MATCH (d:Drug {id: '98'}), (b:Brand {name: '赛益宁'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '98'}), (c:Category {name: 'GLP-1激动剂'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 87/108: 醋酸普兰林肽注射液 ------
MERGE (d99:Drug {id: '99', name: '醋酸普兰林肽注射液', en_name: 'Pramlintide Acetate Injection', timing: '餐前', route: '注射'});
MATCH (d:Drug {id: '99'}), (c:Category {name: '其他'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '99'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '99'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);

// ------ 药品 88/108: 考来维仑片 ------
MERGE (d100:Drug {id: '100', name: '考来维仑片', en_name: 'Colesevelam Tablets', timing: '随餐'});
MATCH (d:Drug {id: '100'}), (c:Category {name: '胆汁酸螯合剂'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '100'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '100'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '胰腺炎', type: '禁忌'});
MATCH (d:Drug {id: '100'}), (dis:Disease {name: '胰腺炎'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 89/108: 度拉糖肽注射液 ------
MERGE (d101:Drug {id: '101', name: '度拉糖肽注射液', en_name: 'Dulaglutide Injection', route: '注射'});
MERGE (b101_7222:Brand {name: '度易达 (Trulicity)'});
MATCH (d:Drug {id: '101'}), (b:Brand {name: '度易达 (Trulicity)'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '101'}), (c:Category {name: '未分类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '101'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '101'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '心血管疾病', type: '适应症'});
MATCH (d:Drug {id: '101'}), (dis:Disease {name: '心血管疾病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '甲状腺髓样癌', type: '禁忌'});
MATCH (d:Drug {id: '101'}), (dis:Disease {name: '甲状腺髓样癌'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: 'MTC', type: '禁忌'});
MATCH (d:Drug {id: '101'}), (dis:Disease {name: 'MTC'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);

// ------ 药品 90/108: 恒格列净片 ------
MERGE (d102:Drug {id: '102', name: '恒格列净片', en_name: 'Henagliflozin Tablets'});
MERGE (b102_3969:Brand {name: '瑞沁'});
MATCH (d:Drug {id: '102'}), (b:Brand {name: '瑞沁'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '102'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '102'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '102'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '肾功能损害', type: '禁忌'});
MATCH (d:Drug {id: '102'}), (dis:Disease {name: '肾功能损害'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '终末期肾病', type: '禁忌'});
MATCH (d:Drug {id: '102'}), (dis:Disease {name: '终末期肾病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '102'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);
MATCH (d:Drug {id: '102'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'WARNING', value: 45.0, unit: 'mL/min'}]->(m);

// ------ 药品 91/108: 司美格鲁肽片 ------
MERGE (d103:Drug {id: '103', name: '司美格鲁肽片', en_name: 'Semaglutide Tablets', starting_dose: '3mg', timing: '空腹', route: '口服'});
MERGE (b103_4917:Brand {name: 'Rybelsus（口服版诺和泰）'});
MATCH (d:Drug {id: '103'}), (b:Brand {name: 'Rybelsus（口服版诺和泰）'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '103'}), (c:Category {name: '未分类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '103'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '103'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);

// ------ 药品 92/108: 艾塞那肽注射液 ------
MERGE (d104:Drug {id: '104', name: '艾塞那肽注射液', en_name: '百泌达 / Byetta - 每日版', starting_dose: '5μg', timing: '餐前', route: '注射'});
MERGE (b104_6935:Brand {name: '百泌达 (Byetta)'});
MATCH (d:Drug {id: '104'}), (b:Brand {name: '百泌达 (Byetta)'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '104'}), (c:Category {name: 'GLP-1激动剂'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '肾功能受损', type: '禁忌'});
MATCH (d:Drug {id: '104'}), (dis:Disease {name: '肾功能受损'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '104'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'CRITICAL', value: 30.0, unit: 'mL/min'}]->(m);

// ------ 药品 93/108: 马来酸罗格列酮二甲双胍片 ------
MERGE (d105:Drug {id: '105', name: '马来酸罗格列酮二甲双胍片', en_name: 'Avandamet', timing: '随餐'});
MATCH (d:Drug {id: '105'}), (c:Category {name: '双胍类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 94/108: 考来替泊颗粒 ------
MERGE (d106:Drug {id: '106', name: '考来替泊颗粒', en_name: 'Colestipol Hydrochloride Granules'});
MATCH (d:Drug {id: '106'}), (c:Category {name: '胆汁酸螯合剂'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '106'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '106'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);

// ------ 药品 95/108: 氯化铬口服液 / 吡啶甲酸铬 ------
MERGE (d107:Drug {id: '107', name: '氯化铬口服液 / 吡啶甲酸铬', en_name: 'Chromium Chloride'});
MATCH (d:Drug {id: '107'}), (c:Category {name: '其他'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '107'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);

// ------ 药品 96/108: 醋酸普兰林肽 ------
MERGE (d108:Drug {id: '108', name: '醋酸普兰林肽', en_name: 'Pramlintide Acetate - 详情版'});
MATCH (d:Drug {id: '108'}), (c:Category {name: '其他'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 97/108: 盐酸溴隐亭速释片 ------
MERGE (d109:Drug {id: '109', name: '盐酸溴隐亭速释片', en_name: 'Cycloset', max_daily_dose: '4.8mg', starting_dose: '0.8mg', timing: '随餐'});
MERGE (b109_8641:Brand {name: 'Cycloset（糖尿病专用规格）'});
MATCH (d:Drug {id: '109'}), (b:Brand {name: 'Cycloset（糖尿病专用规格）'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '109'}), (c:Category {name: '其他'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '109'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '109'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);

// ------ 药品 98/108: 阿必鲁肽 ------
MERGE (d110:Drug {id: '110', name: '阿必鲁肽', en_name: 'Albiglutide'});
MATCH (d:Drug {id: '110'}), (c:Category {name: '未分类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 99/108: 利司那肽注射液 ------
MERGE (d111:Drug {id: '111', name: '利司那肽注射液', en_name: 'Lixisenatide Injection', starting_dose: '10μg', timing: '餐前', route: '注射'});
MERGE (b111_2526:Brand {name: '利必扬'});
MATCH (d:Drug {id: '111'}), (b:Brand {name: '利必扬'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '111'}), (c:Category {name: 'GLP-1激动剂'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '111'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '111'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '肾功能受损', type: '禁忌'});
MATCH (d:Drug {id: '111'}), (dis:Disease {name: '肾功能受损'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MERGE (dis:Disease {name: '终末期肾病', type: '禁忌'});
MATCH (d:Drug {id: '111'}), (dis:Disease {name: '终末期肾病'}) MERGE (d)-[:FORBIDDEN_FOR {severity: '禁忌'}]->(dis);
MATCH (d:Drug {id: '111'}), (m:Metric {name: 'eGFR'}) MERGE (d)-[:CONTRAINDICATED_IF {operator: '<', severity: 'WARNING', value: 15.0, unit: 'mL/min'}]->(m);

// ------ 药品 100/108: 司美格鲁肽注射液 ------
MERGE (d112:Drug {id: '112', name: '司美格鲁肽注射液', en_name: 'Wegovy - 减重规格', route: '注射'});
MERGE (b112_8556:Brand {name: 'Wegovy'});
MATCH (d:Drug {id: '112'}), (b:Brand {name: 'Wegovy'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '112'}), (c:Category {name: '未分类'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '2型糖尿病', type: '适应症'});
MATCH (d:Drug {id: '112'}), (dis:Disease {name: '2型糖尿病'}) MERGE (d)-[:TREATS]->(dis);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '112'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);

// ------ 药品 101/108: 精蛋白锌赖脯胰岛素混悬液 ------
MERGE (d113:Drug {id: '113', name: '精蛋白锌赖脯胰岛素混悬液', en_name: 'Insulin Lispro Protamine Suspension', route: '注射'});
MATCH (d:Drug {id: '113'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);
MERGE (dis:Disease {name: '糖尿病', type: '适应症'});
MATCH (d:Drug {id: '113'}), (dis:Disease {name: '糖尿病'}) MERGE (d)-[:TREATS]->(dis);

// ------ 药品 102/108: 德谷胰岛素注射液 ------
MERGE (d114:Drug {id: '114', name: '德谷胰岛素注射液', en_name: '200 U/mL 规格', route: '注射'});
MATCH (d:Drug {id: '114'}), (c:Category {name: '胰岛素'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 103/108: 艾塞那肽注射液（自启式注射笔） ------
MERGE (d115:Drug {id: '115', name: '艾塞那肽注射液（自启式注射笔）', en_name: 'Bydureon BCise'});
MATCH (d:Drug {id: '115'}), (c:Category {name: 'GLP-1激动剂'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 104/108: 瑞格列奈片 ------
MERGE (d116:Drug {id: '116', name: '瑞格列奈片', en_name: '孚来迪 / Repaglinide'});
MATCH (d:Drug {id: '116'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 105/108: 伏格列波糖片 ------
MERGE (d117:Drug {id: '117', name: '伏格列波糖片', en_name: '快步 / Voglibose', timing: '餐前'});
MATCH (d:Drug {id: '117'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 106/108: 磷酸西格列汀片 ------
MERGE (d118:Drug {id: '118', name: '磷酸西格列汀片', en_name: '捷诺维 50mg/25mg 规格'});
MATCH (d:Drug {id: '118'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 107/108: 那格列奈片 ------
MERGE (d119:Drug {id: '119', name: '那格列奈片', en_name: '唐力 60mg 规格', timing: '餐前'});
MATCH (d:Drug {id: '119'}), (c:Category {name: '磺脲类'}) MERGE (d)-[:BELONGS_TO]->(c);

// ------ 药品 108/108: 阿卡波糖胶囊 ------
MERGE (d120:Drug {id: '120', name: '阿卡波糖胶囊', en_name: '卡博平', timing: '随餐'});
MERGE (b120_5533:Brand {name: '卡博平'});
MATCH (d:Drug {id: '120'}), (b:Brand {name: '卡博平'}) MERGE (b)-[:IS_BRAND_OF]->(d);
MATCH (d:Drug {id: '120'}), (c:Category {name: 'α-糖苷酶抑制剂'}) MERGE (d)-[:BELONGS_TO]->(c);

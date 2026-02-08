# Neo4j环境设置指南

## 方案一: Docker方式(推荐)

### 1. 安装Docker Desktop
访问: https://www.docker.com/products/docker-desktop/

### 2. 启动Neo4j容器
```bash
docker run \
    --name neo4j-diabetes \
    --publish=7474:7474 --publish=7687:7687 \
    --env NEO4J_AUTH=neo4j/password123 \
    --volume=$HOME/neo4j/data:/data \
    --volume=$HOME/neo4j/logs:/logs \
    neo4j:5.15
```

### 3. 访问Neo4j Browser
打开浏览器访问: http://localhost:7474
- 用户名: neo4j
- 密码: password123

### 4. 导入数据
```bash
cd /Users/jindeng/project/tnb_llm
pip install neo4j
python import_to_neo4j.py
```

---

## 方案二: 本地安装Neo4j

### 1. 下载Neo4j Community Edition
访问: https://neo4j.com/download-center/#community

### 2. 解压并启动
```bash
cd neo4j-community-5.x
bin/neo4j start
```

### 3. 设置密码
首次访问 http://localhost:7474 时会要求设置密码

### 4. 导入数据
```bash
cd /Users/jindeng/project/tnb_llm
pip install neo4j
python import_to_neo4j.py
```

---

## 方案三: Neo4j Aura(云端,免费套餐)

### 1. 注册账号
访问: https://neo4j.com/cloud/aura-free/

### 2. 创建数据库
- 选择 AuraDB Free
- 记录连接凭据(URI, username, password)

### 3. 修改连接配置
编辑 `import_to_neo4j.py` 中的连接参数:
```python
NEO4J_URI = "neo4j+s://xxxxx.databases.neo4j.io"  # 从Aura复制
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "你的密码"
```

### 4. 导入数据
```bash
pip install neo4j
python import_to_neo4j.py
```

---

## 快速验证安装

安装Neo4j后,运行以下命令测试:
```bash
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password123')); driver.verify_connectivity(); print('✅ 连接成功!')"
```

---

## 当前项目文件清单

已生成的文件:
- ✅ `parse_drugs.py` - Markdown解析器
- ✅ `extract_entities.py` - 实体提取器
- ✅ `generate_cypher.py` - Cypher生成器
- ✅ `drugs_structured.json` - 结构化数据(108个药品)
- ✅ `graph_data.json` - 图谱数据
- ✅ `import_graph.cypher` - Neo4j导入脚本(2293条语句)
- ✅ `import_to_neo4j.py` - 自动化导入工具

---

## 导入后的查询示例

### 查询1: eGFR<30患者不能使用的药品
```cypher
MATCH (d:Drug)-[r:CONTRAINDICATED_IF]->(m:Metric {name: 'eGFR'})
WHERE r.operator = '<' AND r.value = 30
RETURN d.name, r.severity
```

### 查询2: 找到所有双胍类药物
```cypher
MATCH (d:Drug)-[:BELONGS_TO]->(c:Category {name: '双胍类'})
RETURN d.name, d.max_daily_dose
```

### 查询3: 心力衰竭患者禁用的药物
```cypher
MATCH (d:Drug)-[:FORBIDDEN_FOR]->(dis:Disease)
WHERE dis.name CONTAINS '心力衰竭'
RETURN d.name
```

### 查询4: 复杂多跳查询 - SGLT2抑制剂的禁忌
```cypher
MATCH (c:Category {name: 'SGLT2抑制剂'})<-[:BELONGS_TO]-(d:Drug)
MATCH (d)-[r]->(target)
WHERE type(r) IN ['CONTRAINDICATED_IF', 'FORBIDDEN_FOR']
RETURN d.name, type(r), target.name, r
```

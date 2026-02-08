# 🚀 服务器部署指南：指南结构化 (RAG Engine)

由于本地网络下载模型较慢，将在服务器上执行PDF解析和向量化任务。

## 1. 文件同步
请确保以下文件已上传至服务器项目目录：
- `process_guidelines.py` (核心处理脚本)
- `中国糖尿病防治指南（2024版）.pdf` (源文件)

## 2. 环境安装 (关键!)
为了避免 `FlagEmbedding`、`transformers` 和 `peft` 之间的版本冲突，请**严格按照以下顺序和版本**安装依赖：

```bash
# 1. 基础RAG依赖
pip install pymupdf pdfplumber chromadb

# 2. 安装特定版本的 transformers (解决 FlagEmbedding兼容性)
pip install "transformers<4.40.0"

# 3. 安装特定版本的 peft (解决 ImportError: EncoderDecoderCache)
pip install "peft<0.10.0"

# 4. 最后安装 FlagEmbedding
pip install FlagEmbedding
```

## 3. 运行处理脚本
建议使用 `nohup` 或 `tmux` 运行，因为会自动下载 BGE-M3 模型 (约1.5GB) 并进行向量化计算。

```bash
# 后台运行并记录日志
nohup python process_guidelines.py > process.log 2>&1 &

# 查看进度
tail -f process.log
```

## 4. 预期输出
脚本运行完成后，将在当前目录下生成 `chroma_db` 文件夹，其中包含向量索引。

## 5. 验证检索
脚本执行完毕后，可以使用以下Python代码简单测试：

```python
import chromadb
from FlagEmbedding import BGEM3FlagModel

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="diabetes_guidelines_2024")
model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

query = "二甲双胍的禁忌症"
query_vec = model.encode([query])['dense_vecs'][0].tolist()

results = collection.query(
    query_embeddings=[query_vec],
    n_results=3
)

for doc in results['documents'][0]:
    print("-" * 30)
    print(doc)
```

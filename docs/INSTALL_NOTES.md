# 依赖安装说明

## 为什么安装这么慢？

### 主要原因

1. **包体积大**:
   - `chromadb`: ~100MB
   - `FlagEmbedding`: ~500MB（包含 PyTorch 等深度学习框架）
   - `transformers` (FlagEmbedding的依赖): ~400MB
   - 总计: **1-2GB** 下载量

2. **依赖链复杂**:
   ```
   FlagEmbedding
     ├── transformers
     │   ├── torch (或 tensorflow)
     │   ├── tokenizers
     │   └── safetensors
     ├── sentence-transformers
     └── numpy, scipy 等
   
   chromadb
     ├── onnxruntime
     ├── pydantic
     ├── fastapi
     └── sqlite 等
   ```

3. **编译时间**:
   - 某些包可能需要编译 C 扩展（如 onnx, tokenizers）
   - 在没有预编译二进制包的情况下会更慢

### 预估时间

- 快速网络: 5-10 分钟
- 普通网络: 10-20 分钟
- 慢速网络或需编译: 20-30 分钟

---

## 替代方案

### 方案 1: 分步安装（推荐）

```bash
conda activate tnb_llm

# 先安装轻量级的
pip install jieba neo4j rank-bm25  # ~1分钟

# 再安装 chromadb（中等）
pip install chromadb  # ~5分钟

# 最后安装 FlagEmbedding（最大）
pip install FlagEmbedding  # ~10-15分钟
```

### 方案 2: 使用清华镜像加速

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    chromadb FlagEmbedding rank-bm25 jieba neo4j
```

### 方案 3: 只安装必需包，暂时跳过模型

```bash
# 最小安装（仅测试代码逻辑，不加载模型）
pip install jieba neo4j rank-bm25
```

然后修改代码，延迟加载模型：
```python
# 在 retrieval_engine.py 中添加
try:
    from hybrid_retriever import HybridRetriever
    self.hybrid_retriever = HybridRetriever()
except ImportError:
    print("⚠️  ChromaDB 未安装，跳过混合检索")
    self.hybrid_retriever = None
```

---

## 当前建议

由于你的安装已经运行了 13+ 分钟，应该快完成了。

**检查进度**:
```bash
# 查看正在下载/安装的包
tail -f ~/.pip/pip.log  # 如果有日志

# 或查看网络活动
nethogs  # 查看下载速度
```

**耐心等待** 或 **手动中断**后使用镜像加速：
```bash
# Ctrl+C 中断当前安装
conda activate tnb_llm
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple chromadb FlagEmbedding
```

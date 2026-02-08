import fitz  # PyMuPDF
import pdfplumber
import chromadb
from chromadb.config import Settings
from FlagEmbedding import BGEM3FlagModel
import os
import re

# 配置
PDF_PATH = "中国糖尿病防治指南（2024版）.pdf"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "diabetes_guidelines_2024"

def extract_tables_to_markdown(pdf_path):
    """使用pdfplumber提取表格并转换为Markdown格式"""
    tables_md = {}
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                if not table: continue
                # 简单的Markdown转换
                header = table[0]
                rows = table[1:]
                
                # 清理None值
                header = [str(h).replace('\n', ' ') if h else '' for h in header]
                
                md = f"| {' | '.join(header)} |\n"
                md += f"| {' | '.join(['---'] * len(header))} |\n"
                
                for row in rows:
                    clean_row = [str(c).replace('\n', ' ') if c else '' for c in row]
                    md += f"| {' | '.join(clean_row)} |\n"
                
                # 存储: {页码_索引: markdown}
                key = f"{i}_{tables.index(table)}"
                tables_md[key] = md
    return tables_md

def parse_pdf_with_headers(pdf_path, tables_dict):
    """解析PDF，基于字体大小识别标题进行切片"""
    doc = fitz.open(pdf_path)
    chunks = []
    
    current_header = "前言/未分类"
    current_text = ""
    
    # 字体大小统计，用于识别标题
    font_sizes = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        font_sizes.append(s["size"])
    
    # 假设标题是大字体（取前10%大的字体作为标题候选）
    font_sizes.sort(reverse=True)
    if font_sizes:
        header_threshold = font_sizes[int(len(font_sizes) * 0.05)]
    else:
        header_threshold = 12

    print(f"标题字体阈值: {header_threshold}")

    for page_num, page in enumerate(doc):
        # 1. 提取文本块
        blocks = page.get_text("dict")["blocks"]
        
        # 2. 检查是否有表格
        # (简单起见，我们将表格追加到该页的文本末尾，或者尝试插入)
        # 这里简化处理：如果在该页有表格，就追加到该页的chunk中
        
        for b in blocks:
            if "lines" in b:
                block_text = ""
                is_header = False
                
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip()
                        if not text: continue
                        
                        # 检查是否为标题
                        if s["size"] >= header_threshold and len(text) < 50:
                            is_header = True
                            # 保存上一个chunk
                            if current_text:
                                chunks.append({
                                    "header": current_header,
                                    "text": current_text,
                                    "page": page_num
                                })
                            current_header = text
                            current_text = "" # 重置文本
                        
                        block_text += text + " "
                
                if not is_header:
                    current_text += block_text + "\n"
        
        # 检查该页是否有表格
        # pdfplumber的页码从0开始，与fitz一致
        # 我们查找以该页开头的表格key
        for key, md in tables_dict.items():
            if key.startswith(f"{page_num}_"):
                current_text += f"\n\n【表格】\n{md}\n\n"

    # 添加最后一个chunk
    if current_text:
        chunks.append({
            "header": current_header,
            "text": current_text,
            "page": page_num
        })
        
    return chunks

def vectorize_and_store(chunks):
    """向量化并存入ChromaDB"""
    print("正在加载BGE-M3模型...")
    model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True) 
    
    print(f"初始化ChromaDB: {CHROMA_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # 获取或创建集合
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        print("集合已存在，正在删除旧数据...")
        client.delete_collection(name=COLLECTION_NAME)
        collection = client.create_collection(name=COLLECTION_NAME)
    except:
        collection = client.create_collection(name=COLLECTION_NAME)
        
    print("开始向量化和入库...")
    batch_size = 10
    total = len(chunks)
    
    for i in range(0, total, batch_size):
        batch = chunks[i:i+batch_size]
        
        # 准备数据
        ids = [f"chunk_{i+j}" for j in range(len(batch))]
        documents = [f"【章节】{c['header']}\n{c['text']}" for c in batch]
        metadatas = [{"header": c['header'], "page": c['page']} for c in batch]
        
        # 生成Embedding
        embeddings = model.encode(documents, batch_size=len(batch))['dense_vecs']
        
        # 存入
        collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas
        )
        print(f"进度: {min(i+batch_size, total)}/{total}")
        
    print("入库完成!")
    return collection

def main():
    if not os.path.exists(PDF_PATH):
        print(f"错误: 找不到文件 {PDF_PATH}")
        return

    print("1. 提取表格...")
    tables = extract_tables_to_markdown(PDF_PATH)
    print(f"提取了 {len(tables)} 个表格")
    
    print("2. 解析PDF并切分...")
    chunks = parse_pdf_with_headers(PDF_PATH, tables)
    print(f"生成了 {len(chunks)} 个切片")
    
    print("3. 向量化入库...")
    vectorize_and_store(chunks)
    
    print("\n✅ 指南结构化完成!")

if __name__ == "__main__":
    main()

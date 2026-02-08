#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown解析器 - 将data.md解析为结构化JSON

功能:
1. 分割120个药品条目
2. 提取基础信息(通用名、商品名、英文名)
3. 提取临床信息(适应症、禁忌、用法用量等)
4. 输出为JSON格式
"""

import re
import json
from dataclasses import dataclass, asdict, field
from typing import Optional, List
from pathlib import Path


@dataclass
class Drug:
    """药品数据结构"""
    id: str
    name: str  # 通用名
    en_name: str  # 英文名
    brand_names: List[str]  # 商品名列表
    ingredients: str  # 成份
    indications: str  # 适应症
    dosage: str  # 用法用量
    adverse_reactions: str  # 不良反应
    contraindications: str  # 禁忌
    precautions: str  # 注意事项
    pharmacology: str = ""  # 药理毒理(可选)
    interactions: str = ""  # 药物相互作用(可选)
    raw_text: str = field(repr=False, default="")  # 原始文本(用于调试)


def extract_field(pattern: str, text: str, default: str = "") -> str:
    """通用字段提取函数"""
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else default


def extract_brands(text: str) -> List[str]:
    """提取商品名,处理多个商品名的情况"""
    match = re.search(r'商品名称[:：]\s*(.+?)(?:\n|$)', text)
    if not match:
        return []
    
    brand_text = match.group(1).strip()
    # 处理 "格华止 / 卡司平" 或 "格华止"
    brands = [b.strip() for b in re.split(r'[/／]', brand_text)]
    return [b for b in brands if b]  # 过滤空字符串


def extract_section_content(section_title: str, text: str) -> str:
    """
    提取章节内容
    匹配: **【章节名】** 后的内容,直到下一个 **【 或 --- 或文本结束
    """
    # 处理中英文标点
    title_pattern = section_title.replace('【', r'[【\[]').replace('】', r'[】\]]')
    pattern = rf'\*\*{title_pattern}\*\*\s*(.*?)(?=\*\*[【\[]|---|$)'
    
    match = re.search(pattern, text, re.DOTALL)
    if match:
        content = match.group(1).strip()
        # 清理多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        return content
    return ""


def split_into_drugs(content: str) -> List[str]:
    """
    将整个文件按药品条目分割
    匹配: ### 第 X 个：药品名
    """
    # 分割标记
    pattern = r'###\s*第\s*\d+\s*个[：:]'
    
    # 找到所有分割点
    splits = list(re.finditer(pattern, content))
    
    drug_texts = []
    for i, match in enumerate(splits):
        start = match.start()
        # 下一个药品的开始位置,或文本结束
        end = splits[i + 1].start() if i + 1 < len(splits) else len(content)
        drug_texts.append(content[start:end])
    
    return drug_texts


def parse_drug_entry(text: str, index: int) -> Drug:
    """
    解析单个药品条目
    
    Args:
        text: 药品的原始markdown文本
        index: 序号(用于ID)
    
    Returns:
        Drug对象
    """
    # 提取标题中的ID和名称
    title_match = re.search(r'###\s*第\s*(\d+)\s*个[：:]\s*(.+?)\s*\((.+?)\)', text)
    
    if title_match:
        drug_id = title_match.group(1)
        zh_name = title_match.group(2).strip()
        en_name = title_match.group(3).strip()
    else:
        # 备用方案:如果格式不标准
        drug_id = str(index + 1)
        zh_name = f"药品{drug_id}"
        en_name = ""
    
    # 提取基础信息
    name_section = extract_section_content('【药品名称】', text)
    通用名 = extract_field(r'通用名称[:：]\s*(.+?)(?:\n|$)', name_section, zh_name)
    英文名 = extract_field(r'英文名称[:：]\s*(.+?)(?:\n|$)', name_section, en_name)
    
    # 提取商品名
    brands = extract_brands(name_section)
    
    # 提取各个临床信息章节
    成份 = extract_section_content('【成份】', text)
    适应症 = extract_section_content('【适应症】', text)
    用法用量 = extract_section_content('【用法用量】', text)
    不良反应 = extract_section_content('【不良反应】', text)
    禁忌 = extract_section_content('【禁忌】', text)
    注意事项 = extract_section_content('【注意事项】', text)
    药理毒理 = extract_section_content('【药理毒理】|【药理作用】', text)
    药物相互作用 = extract_section_content('【药物相互作用】', text)
    
    return Drug(
        id=drug_id,
        name=通用名,
        en_name=英文名,
        brand_names=brands,
        ingredients=成份,
        indications=适应症,
        dosage=用法用量,
        adverse_reactions=不良反应,
        contraindications=禁忌,
        precautions=注意事项,
        pharmacology=药理毒理,
        interactions=药物相互作用,
        raw_text=text[:500]  # 保留前500字符用于调试
    )


def parse_all_drugs(filepath: str) -> List[Drug]:
    """
    解析整个data.md文件
    
    Args:
        filepath: data.md的路径
    
    Returns:
        Drug对象列表
    """
    print(f"📖 正在读取文件: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 文件大小: {len(content)} 字符")
    
    # 分割药品条目
    drug_texts = split_into_drugs(content)
    print(f"✂️  找到 {len(drug_texts)} 个药品条目")
    
    # 解析每个药品
    drugs = []
    for i, text in enumerate(drug_texts):
        try:
            drug = parse_drug_entry(text, i)
            drugs.append(drug)
            print(f"✅ [{i+1}/{len(drug_texts)}] {drug.name}")
        except Exception as e:
            print(f"❌ [{i+1}/{len(drug_texts)}] 解析失败: {e}")
            continue
    
    print(f"\n🎉 成功解析 {len(drugs)} 个药品!")
    return drugs


def save_to_json(drugs: List[Drug], output_path: str):
    """保存为JSON文件"""
    data = [asdict(drug) for drug in drugs]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 已保存到: {output_path}")
    print(f"📊 文件大小: {Path(output_path).stat().st_size / 1024:.1f} KB")


def main():
    """主函数"""
    # 输入输出路径
    input_file = "data.md"
    output_file = "drugs_structured.json"
    
    print("=" * 60)
    print("🏥 糖尿病药品数据解析器")
    print("=" * 60)
    
    # 检查文件是否存在
    if not Path(input_file).exists():
        print(f"❌ 错误: 找不到文件 {input_file}")
        return
    
    # 解析所有药品
    drugs = parse_all_drugs(input_file)
    
    if not drugs:
        print("❌ 错误: 没有成功解析任何药品")
        return
    
    # 保存为JSON
    save_to_json(drugs, output_file)
    
    # 打印统计信息
    print("\n" + "=" * 60)
    print("📈 数据统计")
    print("=" * 60)
    print(f"总药品数: {len(drugs)}")
    print(f"有商品名的: {sum(1 for d in drugs if d.brand_names)}")
    print(f"有英文名的: {sum(1 for d in drugs if d.en_name)}")
    print(f"有禁忌信息的: {sum(1 for d in drugs if d.contraindications)}")
    print(f"有用法用量的: {sum(1 for d in drugs if d.dosage)}")
    
    # 显示前3个药品示例
    print("\n" + "=" * 60)
    print("📋 前3个药品示例")
    print("=" * 60)
    for drug in drugs[:3]:
        print(f"\n{drug.id}. {drug.name}")
        print(f"   英文名: {drug.en_name}")
        print(f"   商品名: {', '.join(drug.brand_names) if drug.brand_names else '无'}")
        print(f"   禁忌长度: {len(drug.contraindications)} 字符")


if __name__ == "__main__":
    main()

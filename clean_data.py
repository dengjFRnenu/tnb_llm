#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗脚本:从data.md中提取纯药品信息,删除所有说明性文字
"""

def clean_data_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    skip_mode = False
    buffer = []
    
    for i, line in enumerate(lines):
        # 检测说明性段落的开始
        if any(keyword in line for keyword in [
            '明白，作为研一学生',
            '这是 **第',
            '这一组包含了',
            '这些数据对于你构建',
            '在构建大模型',
            '我为你提供的内容',
            '为什么这对你的项目',
            '作为一个计算机专业',
            '为了帮你真正',
            '一、 糖尿病药品 Markdown 统一模板',
            '二、 第 41-50 号药品',
            '### 为什么',
            '### 第 5 组（Batch',
        ]):
            skip_mode = True
            buffer = []
            continue
        
        # 检测药品条目的开始(恢复正常模式)
        if line.startswith('### 第') or line.startswith('#### 第') or line.startswith('第 '):
            skip_mode = False
            # 如果有缓存的分隔线,先添加
            if buffer and '---' in ''.join(buffer):
                cleaned_lines.append('---\n\n')
            buffer = []
            # 统一格式为 ###
            if line.startswith('#### 第'):
                line = line.replace('#### ', '### ')
            elif line.startswith('第 ') and '个：' in line:
                line = '### ' + line
            cleaned_lines.append(line)
            continue
        
        # 跳过模板代码块
        if '```' in line and 'markdown' in line:
            skip_mode = True
            continue
        if skip_mode and '```' in line and 'markdown' not in line:
            skip_mode = False
            continue
            
        # 非跳过模式下,正常添加
        if not skip_mode:
            # 过滤掉markdown的列表标记(如 *   **)
            if line.strip().startswith('*') and '**【' in line:
                # 这是bullet point格式的字段,需要转换
                line = line.replace('*   **【', '**【')
            cleaned_lines.append(line)
        else:
            # 跳过模式下,缓存可能的分隔线
            if line.strip() == '---':
                buffer.append(line)
    
    # 写入清洗后的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print(f"清洗完成!")
    print(f"原始行数: {len(lines)}")
    print(f"清洗后行数: {len(cleaned_lines)}")
    print(f"删除了 {len(lines) - len(cleaned_lines)} 行")

if __name__ == '__main__':
    clean_data_file('data.md', 'data_cleaned.md')

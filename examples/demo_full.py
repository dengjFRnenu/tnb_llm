#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dia-Agent 完整使用示例
演示如何接入大模型进行智能诊疗
"""

import sys
import os
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def demo_with_llm():
    """使用大模型的完整诊疗示例"""
    from src.agent import DiaAgent
    from src.llm_client import create_llm_api
    
    print("=" * 70)
    print("🏥 Dia-Agent 智能诊疗演示 (含 LLM)")
    print("=" * 70)
    
    # 检测可用的 API
    llm_api = None
    
    if os.getenv("DASHSCOPE_API_KEY"):
        print("📡 使用通义千问 API")
        llm_api = create_llm_api("qwen")
    elif os.getenv("DEEPSEEK_API_KEY"):
        print("📡 使用 DeepSeek API")
        llm_api = create_llm_api("deepseek")
    elif os.getenv("OPENAI_API_KEY"):
        print("📡 使用 OpenAI API")
        llm_api = create_llm_api("openai")
    else:
        print("⚠️ 未检测到 API 密钥，使用规则模式")
        print("   设置环境变量以启用 LLM:")
        print("   export DASHSCOPE_API_KEY=your-key")
    
    # 创建 Agent
    agent = DiaAgent(llm_api=llm_api, verbose=True)
    
    # 测试病例
    case = """
    患者张某，男，58岁，因"口渴多饮、多尿2月，双下肢麻木1周"入院。

    现病史：
    - 2月前无明显诱因出现口渴多饮，日饮水量约3000ml
    - 多尿，夜尿增多至3-4次
    - 近1周出现双下肢麻木、蚁走感
    - 体重下降约4kg

    既往史：
    - 高血压病史8年，服用氨氯地平5mg qd，血压控制可
    - 否认冠心病、脑血管病史
    - 否认肝炎、结核等传染病史

    个人史：
    - 吸烟20年，20支/日，未戒烟
    - 偶饮酒

    查体：
    - 身高：172cm，体重：82kg，BMI：27.7
    - 血压：142/88 mmHg
    - 双足痛觉、温度觉减退

    辅助检查：
    - 空腹血糖：12.3 mmol/L
    - 餐后2h血糖：18.6 mmol/L
    - HbA1c：9.8%
    - 血肌酐：145 μmol/L
    - eGFR：48 mL/min/1.73m²
    - UACR：156 mg/g
    - 尿常规：葡萄糖 3+，蛋白 1+
    - TC：6.2 mmol/L，TG：2.8 mmol/L，LDL：3.8 mmol/L

    初步诊断：
    1. 2型糖尿病
       糖尿病肾病 CKD 3a期
       糖尿病周围神经病变
    2. 高血压病2级 高危
    3. 血脂异常
    """
    
    # 执行诊疗
    print("\n" + "=" * 70)
    print("📋 开始诊疗咨询")
    print("=" * 70)
    
    report = agent.consult(case)
    
    # 输出报告
    print("\n" + "=" * 70)
    print("📋 诊疗报告")
    print("=" * 70)
    print(report.to_markdown())
    
    agent.close()


def demo_quick_check():
    """快速风险检查演示（无需 LLM）"""
    from src.agent import DiaAgent
    
    print("=" * 70)
    print("🔍 快速用药风险检查演示")
    print("=" * 70)
    
    agent = DiaAgent(verbose=False)
    
    # 场景1: 肾功能不全患者
    print("\n📋 场景1: CKD 4期患者用药检查")
    report = agent.quick_risk_check(
        medications=["二甲双胍", "恩格列净", "格列美脲"],
        egfr=25,
        complications=["糖尿病肾病", "高血压"]
    )
    print(report.to_text())
    
    # 场景2: 心衰患者
    print("\n📋 场景2: 心力衰竭患者用药检查")
    report = agent.quick_risk_check(
        medications=["吡格列酮", "西格列汀"],
        egfr=55,
        complications=["心力衰竭", "冠心病"]
    )
    print(report.to_text())
    
    agent.close()


def demo_kg_query():
    """知识图谱查询演示"""
    from src.graph import LangChainCypherRetriever
    
    print("=" * 70)
    print("📊 知识图谱查询演示")
    print("=" * 70)
    
    retriever = LangChainCypherRetriever()
    
    queries = [
        "eGFR小于30禁用哪些药物？",
        "SGLT2抑制剂有哪些？",
        "心力衰竭患者禁用哪些药物？",
    ]
    
    for q in queries:
        print(f"\n❓ 问题: {q}")
        result = retriever.query(q, use_llm=False)
        
        if result.success:
            print(f"✅ 查询成功 (来源: {result.source})")
            print(f"📊 结果数: {len(result.results)}")
            for r in result.results[:3]:
                print(f"   - {r}")
        else:
            print(f"❌ 查询失败: {result.error}")
    
    retriever.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Dia-Agent 使用示例")
    parser.add_argument(
        "--mode",
        choices=["full", "quick", "kg", "all"],
        default="quick",
        help="演示模式: full=完整诊疗, quick=快速检查, kg=知识图谱, all=全部"
    )
    
    args = parser.parse_args()
    
    if args.mode == "full" or args.mode == "all":
        demo_with_llm()
    
    if args.mode == "quick" or args.mode == "all":
        demo_quick_check()
    
    if args.mode == "kg" or args.mode == "all":
        demo_kg_query()
    
    print("\n✅ 演示完成")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dia-Agent Gradio GUI
糖尿病智能诊疗助手 - Web界面
"""

import gradio as gr
import sys
from pathlib import Path
from typing import Optional, Tuple
import time

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()


# ============================================
# 全局变量 - 预加载（启动时加载一次）
# ============================================

_agent = None
_llm_api = None


def get_agent():
    """获取 Agent 单例（预加载模式）"""
    global _agent, _llm_api
    
    if _agent is None:
        from src.llm_client import create_llm_api
        from src.agent import DiaAgent
        
        # 创建 LLM API
        _llm_api = create_llm_api('siliconflow')
        
        # 创建 Agent（模型只加载一次）
        _agent = DiaAgent(llm_api=_llm_api, verbose=False)
    
    return _agent


# ============================================
# 核心功能
# ============================================

def consult(case_text: str, progress=gr.Progress()) -> Tuple[str, str, str]:
    """
    执行诊疗咨询
    
    Returns:
        (患者信息, 风险提示, 诊疗建议)
    """
    if not case_text.strip():
        return "请输入病历文本", "", ""
    
    try:
        progress(0.1, desc="正在初始化...")
        agent = get_agent()
        
        progress(0.3, desc="正在分析病历...")
        report = agent.consult(case_text)
        
        progress(0.9, desc="生成报告...")
        
        # 格式化输出
        patient_info = f"""
**诊断**: {report.patient_summary}
"""
        
        # 风险提示
        risk_text = ""
        critical_risks = [w for w in report.risk_warnings if w.severity.value in ['CRITICAL', '严重']]
        other_risks = [w for w in report.risk_warnings if w.severity.value not in ['CRITICAL', '严重']]
        
        if critical_risks:
            risk_text += "### 🚨 严重风险\n"
            for w in critical_risks[:5]:
                risk_text += f"- **{w.drug_name}**: {w.reason}\n"
        
        if other_risks:
            risk_text += "\n### ⚠️ 需关注\n"
            for w in other_risks[:5]:
                risk_text += f"- {w.drug_name}: {w.reason}\n"
        
        if not risk_text:
            risk_text = "✅ 未检测到明显用药风险"
        
        # 诊疗建议
        advice_text = ""
        for i, rec in enumerate(report.recommendations[:10], 1):
            source = rec.evidence[0].source_type if rec.evidence else "临床经验"
            advice_text += f"### {i}. {rec.action}\n"
            if rec.reason:
                advice_text += f"**原因**: {rec.reason}\n"
            advice_text += f"*来源: {source}*\n\n"
        
        # AI 分析
        if hasattr(report, 'llm_analysis') and report.llm_analysis:
            advice_text += f"\n---\n## 🤖 AI 综合分析\n{report.llm_analysis}"
        
        progress(1.0, desc="完成")
        
        return patient_info, risk_text, advice_text
        
    except Exception as e:
        return f"❌ 错误: {str(e)}", "", ""


def quick_check(medications: str, egfr: float) -> str:
    """快速风险检查"""
    if not medications.strip():
        return "请输入用药列表"
    
    try:
        agent = get_agent()
        
        med_list = [m.strip() for m in medications.split(',') if m.strip()]
        report = agent.quick_risk_check(
            medications=med_list,
            egfr=egfr if egfr > 0 else None
        )
        
        return report.to_text()
        
    except Exception as e:
        return f"❌ 错误: {str(e)}"


# ============================================
# 示例病历
# ============================================

EXAMPLE_CASES = [
    """患者男，55岁，因"发现血糖升高10年，双下肢麻木3月"入院。

现病史：患者10年前体检发现血糖升高，诊断2型糖尿病，长期服用二甲双胍0.5g tid治疗。近3月出现双下肢麻木、感觉减退。

查体：身高172cm，体重76kg，BMI 25.7。

辅助检查：
- HbA1c: 8.2%
- FPG: 8.5 mmol/L
- eGFR: 28 mL/min/1.73m²

诊断：
1. 2型糖尿病
   糖尿病肾病 CKD 4期
   糖尿病周围神经病变""",
    
    """患者女，62岁，2型糖尿病15年。
当前用药：格列美脲2mg qd，阿卡波糖50mg tid
检查：HbA1c 7.8%，eGFR 55 mL/min
合并：高血压、冠心病、心力衰竭""",
    
    """患者男，45岁，新诊断2型糖尿病。
体重85kg，身高175cm，BMI 27.8
检查：HbA1c 9.5%，FPG 12.3 mmol/L
肝肾功能正常"""
]


# ============================================
# Gradio 界面
# ============================================

# 自定义 CSS
custom_css = """
.doctor-avatar {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    margin: 20px auto;
    display: block;
}
.title-text {
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    color: #2563eb;
}
"""

# 医生头像 (使用 emoji 代替图片)
DOCTOR_AVATAR = """
<div style="text-align: center; padding: 20px;">
    <div style="font-size: 80px;">👨‍⚕️</div>
    <h3 style="color: #2563eb;">Dia-Agent</h3>
    <p style="color: #666;">糖尿病智能诊疗助手</p>
</div>
"""


def create_demo():
    """创建 Gradio 界面"""
    
    with gr.Blocks(
        title="Dia-Agent 智能诊疗助手",
        css=custom_css,
        theme=gr.themes.Soft()
    ) as demo:
        
        # 标题
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0;">🏥 Dia-Agent 智能诊疗助手</h1>
            <p style="color: #e0e0e0; margin: 5px 0 0 0;">基于 GraphRAG 的糖尿病临床决策支持系统</p>
        </div>
        """)
        
        with gr.Row():
            # 左侧 - 医生头像
            with gr.Column(scale=1):
                gr.HTML(DOCTOR_AVATAR)
                
                gr.Markdown("""
                ### 📋 使用说明
                1. 在右侧输入病历文本
                2. 点击"开始诊疗"按钮
                3. 等待系统分析（约10-30秒）
                4. 查看诊疗建议
                
                ### ⚠️ 免责声明
                本系统仅供参考，不能替代医生诊断。
                """)
            
            # 右侧 - 输入和输出
            with gr.Column(scale=3):
                
                with gr.Tab("📋 完整诊疗"):
                    # 输入区
                    case_input = gr.Textbox(
                        label="病历文本",
                        placeholder="请输入患者病历信息...\n\n例如：患者男，55岁，2型糖尿病10年...",
                        lines=10
                    )
                    
                    with gr.Row():
                        submit_btn = gr.Button("🚀 开始诊疗", variant="primary", size="lg")
                        clear_btn = gr.Button("🗑️ 清空", size="lg")
                    
                    # 示例选择
                    gr.Examples(
                        examples=EXAMPLE_CASES,
                        inputs=case_input,
                        label="📝 示例病历（点击选择）"
                    )
                    
                    # 输出区
                    gr.Markdown("---")
                    gr.Markdown("## 📊 诊疗报告")
                    
                    with gr.Row():
                        patient_output = gr.Markdown(label="患者信息")
                    
                    with gr.Row():
                        with gr.Column():
                            risk_output = gr.Markdown(label="⚠️ 风险提示")
                        with gr.Column():
                            advice_output = gr.Markdown(label="💊 诊疗建议")
                
                with gr.Tab("⚡ 快速检查"):
                    gr.Markdown("### 快速用药风险检查\n无需完整病历，只需输入用药和关键指标")
                    
                    med_input = gr.Textbox(
                        label="当前用药（用逗号分隔）",
                        placeholder="例如：二甲双胍, 恩格列净"
                    )
                    egfr_input = gr.Number(label="eGFR (mL/min)", value=0)
                    
                    quick_btn = gr.Button("🔍 快速检查", variant="primary")
                    quick_output = gr.Markdown(label="检查结果")
        
        # 事件绑定
        submit_btn.click(
            fn=consult,
            inputs=[case_input],
            outputs=[patient_output, risk_output, advice_output]
        )
        
        clear_btn.click(
            fn=lambda: ("", "", "", ""),
            outputs=[case_input, patient_output, risk_output, advice_output]
        )
        
        quick_btn.click(
            fn=quick_check,
            inputs=[med_input, egfr_input],
            outputs=[quick_output]
        )
    
    return demo


# ============================================
# 主程序
# ============================================

if __name__ == "__main__":
    print("🏥 启动 Dia-Agent GUI...")
    print("=" * 50)
    
    demo = create_demo()
    
    # 启动服务
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dia-Agent Gradio GUI
糖尿病智能诊疗助手 - Web 界面
"""

import gradio as gr
import html
import os
import sys
import threading
import time
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Generator, List, Tuple

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
_agent_lock = threading.Lock()
_agent_ready = threading.Event()


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


AGENT_MODE = os.getenv("DIA_AGENT_MODE", "fast").strip().lower()
LLM_PROVIDER = os.getenv("DIA_LLM_PROVIDER", "siliconflow").strip()
USE_FAST_AGENT = AGENT_MODE != "full"
SKIP_RAG = _env_bool("DIA_SKIP_RAG", True)
SKIP_RERANKER = _env_bool("DIA_SKIP_RERANKER", True)
LLM_CASE_EXTRACTION = _env_bool("DIA_LLM_CASE_EXTRACTION", False)
USE_REFLECTION = _env_bool("DIA_USE_REFLECTION", False)
ENABLE_PREWARM = _env_bool("DIA_PREWARM", True)


def _build_agent():
    """构建 Agent 实例"""
    global _llm_api
    from src.llm_client import create_llm_api

    _llm_api = create_llm_api(LLM_PROVIDER)

    if USE_FAST_AGENT:
        from src.agent.dia_agent_fast import DiaAgentFast

        return DiaAgentFast(
            llm_api=_llm_api,
            verbose=False,
            skip_reranker=SKIP_RERANKER,
            skip_rag=SKIP_RAG,
            llm_case_extraction=LLM_CASE_EXTRACTION,
            use_reflection=USE_REFLECTION,
        )

    from src.agent import DiaAgent

    return DiaAgent(llm_api=_llm_api, verbose=False)


def get_agent():
    """获取 Agent 单例（预加载模式）"""
    global _agent
    if _agent is None:
        with _agent_lock:
            if _agent is None:
                _agent = _build_agent()
                _agent_ready.set()
    return _agent


def prewarm_agent_async():
    """后台预热 Agent，避免首请求阻塞"""
    if not ENABLE_PREWARM or _agent_ready.is_set():
        return

    def _worker():
        t0 = time.time()
        try:
            get_agent()
            print(f"✅ Agent 预热完成 ({time.time() - t0:.1f}s)")
        except Exception as exc:
            print(f"⚠️ Agent 预热失败: {exc}")

    threading.Thread(target=_worker, daemon=True).start()


# ============================================
# 核心渲染函数
# ============================================

THINKING_STEPS = [
    "正在解析病例中的关键生化指标...",
    "正在检索《中国2型糖尿病防治指南2024版》相关章节...",
    "正在 Neo4j 图谱中校验药物禁忌关系...",
    "正在整合循证医学证据生成诊疗建议...",
]

PROGRESS_LABELS = [
    "正在解析病例...",
    "正在检索指南...",
    "正在校验图谱...",
    "正在生成诊疗建议...",
]


def _safe_text(value: str) -> str:
    return html.escape(str(value)) if value is not None else ""


def _text_to_html(value: str) -> str:
    return _safe_text(value).replace("\n", "<br>")


def _render_progress_bar(percent: int, status: str = "", visible: bool = True) -> str:
    """渲染进度条（浅灰底线 + 蓝色覆盖）"""
    if not visible:
        return '<div class="diag-progress-wrap is-hidden"></div>'

    pct = max(0, min(100, int(percent)))
    label = _safe_text(status or "处理中...")
    return f"""
<div class="diag-progress-wrap">
  <div class="diag-progress-meta">
    <span>{label}</span>
    <span>{pct}%</span>
  </div>
  <div class="diag-progress-track">
    <div class="diag-progress-fill" style="width:{pct}%;"></div>
  </div>
</div>
"""


def _render_thinking_module(
    completed_steps: int = 0,
    current_text: str = "",
    visible: bool = False,
    done: bool = False,
) -> str:
    """渲染 Thinking 模块（可折叠详情）"""
    if not visible:
        return '<div class="thinking-wrap is-hidden"></div>'

    total_steps = len(THINKING_STEPS)
    completed_steps = max(0, min(total_steps, int(completed_steps)))
    current_text = (current_text or "").strip()

    if done:
        headline = "Thinking 已完成"
        subline = "推理完成，正在展示最终诊断结果。"
        icon = "🧠"
        cursor = ""
    else:
        headline = "Thinking..."
        active_text = (
            current_text
            if current_text
            else THINKING_STEPS[min(completed_steps, total_steps - 1)]
        )
        subline = f"正在深度检索与推理：{active_text}"
        icon = "✨"
        cursor = '<span class="typing-dot"></span>'

    rows = []
    for idx, step in enumerate(THINKING_STEPS):
        step_label = step
        if done or idx < completed_steps:
            cls = "done"
            marker = "✓"
        elif idx == completed_steps and not done:
            cls = "active"
            marker = "•"
            step_label = current_text or step
        else:
            cls = "pending"
            marker = "○"
        rows.append(
            f"""
<li class="{cls}">
  <span class="step-marker">{marker}</span>
  <span>{_safe_text(step_label)}</span>
</li>
"""
        )

    return f"""
<div class="thinking-wrap">
  <details class="thinking-details">
    <summary>
      <span class="thinking-icon">{icon}</span>
      <div class="thinking-brief">
        <div class="thinking-title">{headline}</div>
        <div class="thinking-current">{_safe_text(subline)}{cursor}</div>
      </div>
      <span class="thinking-toggle">展开详情</span>
    </summary>
    <ol class="thinking-list">
      {''.join(rows)}
    </ol>
  </details>
</div>
"""


def _render_result_placeholder(visible: bool = False) -> str:
    if not visible:
        return '<div class="result-shell is-hidden"></div>'
    return """
<div class="result-shell result-enter">
  <section class="result-section">
    <h3>诊断结果</h3>
    <div class="empty-note">诊断结果将在此处展示。</div>
  </section>
</div>
"""


def _render_notice_result(message: str, level: str = "warning") -> str:
    level_map = {
        "warning": "risk-warning",
        "critical": "risk-critical",
        "info": "risk-info",
    }
    cls = level_map.get(level, "risk-info")
    return f"""
<div class="result-shell result-enter">
  <section class="result-section">
    <h3>状态提示</h3>
    <div class="risk-card {cls}">
      <div class="risk-head"><span>系统提示</span></div>
      <p>{_safe_text(message)}</p>
    </div>
  </section>
</div>
"""


def _build_result_html(report) -> str:
    """渲染最终诊断结果区域"""
    summary_text = getattr(report, "patient_summary", "") or "未提取到患者摘要。"
    summary_html = _text_to_html(summary_text)

    # 风险预警区
    risk_cards: List[str] = []
    risk_warnings = getattr(report, "risk_warnings", []) or []
    for warning in risk_warnings[:8]:
        severity_raw = getattr(warning, "severity", "")
        severity_label = getattr(severity_raw, "value", str(severity_raw))
        severity_upper = severity_label.upper()
        if "严重" in severity_label or "CRITICAL" in severity_upper:
            cls = "risk-critical"
        elif "高" in severity_label or "HIGH" in severity_upper:
            cls = "risk-warning"
        else:
            cls = "risk-info"

        risk_cards.append(
            f"""
<article class="risk-card {cls}">
  <div class="risk-head">
    <span>{_safe_text(getattr(warning, "drug_name", "未知药物"))}</span>
    <span>{_safe_text(severity_label)}</span>
  </div>
  <p>{_safe_text(getattr(warning, "reason", "无"))}</p>
</article>
"""
        )

    if not risk_cards:
        risk_cards.append(
            """
<article class="risk-card risk-safe">
  <div class="risk-head">
    <span>风险筛查</span>
    <span>通过</span>
  </div>
  <p>未检测到明显的药物禁忌或高危冲突。</p>
</article>
"""
        )

    # 循证建议区
    recommendations = sorted(
        getattr(report, "recommendations", []) or [],
        key=lambda item: getattr(item, "priority", 99),
    )
    advice_items: List[str] = []
    for idx, rec in enumerate(recommendations[:10], 1):
        action = _safe_text(getattr(rec, "action", "未命名建议"))
        reason = _safe_text(getattr(rec, "reason", "") or "无")
        evidence_list = getattr(rec, "evidence", []) or []
        source_type = (
            _safe_text(getattr(evidence_list[0], "source_type", "临床经验"))
            if evidence_list
            else "临床经验"
        )
        advice_items.append(
            f"""
<article class="advice-item">
  <h4>{idx}. {action}</h4>
  <p>{reason}</p>
  <span class="advice-source">来源：{source_type}</span>
</article>
"""
        )

    if not advice_items:
        advice_items.append(
            """
<article class="advice-item">
  <h4>暂无可执行建议</h4>
  <p>当前病例缺少关键诊疗信息，建议补充检查结果后重试。</p>
</article>
"""
        )

    # 参考来源
    seen_refs = set()
    references: List[Tuple[str, str]] = []
    for rec in recommendations:
        for evidence in getattr(rec, "evidence", []) or []:
            source = str(getattr(evidence, "source_type", "evidence")).strip()
            reference = str(getattr(evidence, "reference", "") or "").strip()
            content_fallback = str(getattr(evidence, "content", "") or "").strip()
            ref_text = reference or content_fallback
            if not ref_text:
                continue
            key = (source, ref_text)
            if key in seen_refs:
                continue
            seen_refs.add(key)
            references.append(key)

    if not references:
        references = [("guideline", "《中国2型糖尿病防治指南2024版》")]

    ref_items = []
    for idx, (source, ref_text) in enumerate(references[:12], 1):
        escaped_ref = _safe_text(ref_text)
        if ref_text.startswith(("http://", "https://")):
            ref_node = (
                f'<a href="{escaped_ref}" target="_blank" '
                f'rel="noopener noreferrer">{escaped_ref}</a>'
            )
        else:
            ref_node = escaped_ref
        ref_items.append(
            f"<li>[{idx}] <span class='ref-source'>{_safe_text(source)}</span> {ref_node}</li>"
        )

    llm_response = getattr(report, "llm_response", "") or ""
    llm_block = ""
    if llm_response.strip():
        llm_block = f"""
<section class="result-section">
  <h3>综合分析</h3>
  <div class="analysis-box">{_text_to_html(llm_response)}</div>
</section>
"""

    return f"""
<div class="result-shell result-enter">
  <section class="result-section">
    <h3>患者概况</h3>
    <div class="summary-box">{summary_html}</div>
  </section>
  <section class="result-section">
    <h3>风险预警区</h3>
    <div class="risk-grid">
      {''.join(risk_cards)}
    </div>
  </section>
  <section class="result-section">
    <h3>循证建议区</h3>
    <div class="advice-list">
      {''.join(advice_items)}
    </div>
  </section>
  {llm_block}
  <section class="result-section">
    <h3>参考来源</h3>
    <ol class="ref-list">
      {''.join(ref_items)}
    </ol>
  </section>
</div>
"""


# ============================================
# 历史记录
# ============================================


def _parse_iso_datetime(value: str) -> datetime:
    if not value:
        return datetime.now()
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.now()


def _make_case_title(case_text: str) -> str:
    lines = [line.strip() for line in (case_text or "").splitlines() if line.strip()]
    if not lines:
        return "未命名病例"
    title = lines[0]
    return title if len(title) <= 26 else f"{title[:26]}..."


def _group_history(history_records: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    today_records: List[Dict] = []
    yesterday_records: List[Dict] = []
    week_records: List[Dict] = []

    today = date.today()
    ordered = sorted(
        history_records,
        key=lambda item: _parse_iso_datetime(item.get("created_at", "")),
        reverse=True,
    )

    for item in ordered:
        created = _parse_iso_datetime(item.get("created_at", "")).date()
        delta = (today - created).days
        if delta == 0:
            today_records.append(item)
        elif delta == 1:
            yesterday_records.append(item)
        elif 2 <= delta <= 7:
            week_records.append(item)

    return today_records, yesterday_records, week_records


def _format_history_choice(item: Dict) -> Tuple[str, str]:
    created = _parse_iso_datetime(item.get("created_at", ""))
    label = f"🧾 {item.get('title', '未命名病例')} · {created.strftime('%H:%M')}"
    return label, item.get("id", "")


def _history_radio_updates(
    history_records: List[Dict],
) -> Tuple[gr.update, gr.update, gr.update]:
    today_records, yesterday_records, week_records = _group_history(history_records)

    today_choices = [_format_history_choice(item) for item in today_records]
    yesterday_choices = [_format_history_choice(item) for item in yesterday_records]
    week_choices = [_format_history_choice(item) for item in week_records]

    return (
        gr.update(choices=today_choices, value=None, label=f"今天 ({len(today_choices)})"),
        gr.update(
            choices=yesterday_choices,
            value=None,
            label=f"昨天 ({len(yesterday_choices)})",
        ),
        gr.update(
            choices=week_choices,
            value=None,
            label=f"近 7 天 ({len(week_choices)})",
        ),
    )


def _append_history(history_records: List[Dict], case_text: str, result_html: str) -> List[Dict]:
    new_item = {
        "id": uuid.uuid4().hex[:10],
        "title": _make_case_title(case_text),
        "case_text": case_text,
        "result_html": result_html,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    merged = [new_item] + list(history_records or [])
    return merged[:80]


def _typing_slices(text: str, step: int = 2):
    text = text or ""
    if not text:
        yield ""
        return
    for idx in range(1, len(text) + 1):
        if idx == len(text) or idx % step == 0:
            yield text[:idx]


# ============================================
# 核心业务逻辑
# ============================================


def consult(
    case_text: str,
    history_records: List[Dict],
    workflow_state: str,  # noqa: ARG001 - 通过状态机驱动 UI
) -> Generator[Tuple, None, None]:
    """
    执行诊断咨询

    状态流转:
    Idle -> Processing -> Completed
    """
    history_records = list(history_records or [])
    no_history_change = (gr.update(), gr.update(), gr.update())
    hidden_result = _render_result_placeholder(visible=False)

    if not (case_text or "").strip():
        yield (
            _render_progress_bar(0, "请先输入病历文本", visible=True),
            _render_thinking_module(visible=False),
            _render_notice_result("请先输入患者病历、检查结果或当前用药信息。", level="warning"),
            history_records,
            *no_history_change,
            "Idle",
        )
        return

    try:
        init_desc = "正在准备模型（首次调用会稍慢）..." if not _agent_ready.is_set() else "正在初始化诊断流程..."
        yield (
            _render_progress_bar(6, init_desc, visible=True),
            _render_thinking_module(
                completed_steps=0,
                current_text=THINKING_STEPS[0][:8],
                visible=True,
                done=False,
            ),
            hidden_result,
            history_records,
            *no_history_change,
            "Processing",
        )

        agent = get_agent()

        stage_ranges = [(8, 28), (28, 50), (50, 72)]
        for idx, (start_pct, end_pct) in enumerate(stage_ranges):
            step_text = THINKING_STEPS[idx]
            label = PROGRESS_LABELS[idx]
            for chunk in _typing_slices(step_text, step=2):
                ratio = len(chunk) / max(len(step_text), 1)
                pct = int(start_pct + (end_pct - start_pct) * ratio)
                yield (
                    _render_progress_bar(pct, label, visible=True),
                    _render_thinking_module(
                        completed_steps=idx,
                        current_text=chunk,
                        visible=True,
                        done=False,
                    ),
                    hidden_result,
                    history_records,
                    *no_history_change,
                    "Processing",
                )
                time.sleep(0.02)

        yield (
            _render_progress_bar(78, "正在执行综合推理与生成...", visible=True),
            _render_thinking_module(
                completed_steps=3,
                current_text=THINKING_STEPS[3][:10],
                visible=True,
                done=False,
            ),
            hidden_result,
            history_records,
            *no_history_change,
            "Processing",
        )

        report = agent.consult(case_text)

        step_text = THINKING_STEPS[3]
        for chunk in _typing_slices(step_text, step=2):
            ratio = len(chunk) / max(len(step_text), 1)
            pct = int(78 + (95 - 78) * ratio)
            yield (
                _render_progress_bar(pct, PROGRESS_LABELS[3], visible=True),
                _render_thinking_module(
                    completed_steps=3,
                    current_text=chunk,
                    visible=True,
                    done=False,
                ),
                hidden_result,
                history_records,
                *no_history_change,
                "Processing",
            )
            time.sleep(0.02)

        result_html = _build_result_html(report)
        history_records = _append_history(history_records, case_text, result_html)
        today_u, yesterday_u, week_u = _history_radio_updates(history_records)

        yield (
            _render_progress_bar(100, "诊断完成", visible=True),
            _render_thinking_module(
                completed_steps=len(THINKING_STEPS),
                current_text="推理流程完成",
                visible=True,
                done=True,
            ),
            result_html,
            history_records,
            today_u,
            yesterday_u,
            week_u,
            "Completed",
        )

    except Exception as exc:
        yield (
            _render_progress_bar(100, "执行失败", visible=True),
            _render_thinking_module(
                completed_steps=len(THINKING_STEPS),
                current_text="流程中断，请检查配置与日志。",
                visible=True,
                done=True,
            ),
            _render_notice_result(f"诊断执行失败: {exc}", level="critical"),
            history_records,
            *no_history_change,
            "Idle",
        )


def start_new_diagnosis():
    """重置到 Idle 状态，用于 + 新诊断"""
    return (
        "",
        _render_progress_bar(0, "", visible=False),
        _render_thinking_module(visible=False),
        _render_result_placeholder(visible=False),
        gr.update(value=None),
        gr.update(value=None),
        gr.update(value=None),
        "Idle",
    )


def delete_selected_history(
    today_id: str,
    yesterday_id: str,
    week_id: str,
    history_records: List[Dict],
    current_state: str,
):
    """删除当前选中的历史记录"""
    history_records = list(history_records or [])
    selected_id = today_id or yesterday_id or week_id

    if not selected_id:
        today_u, yesterday_u, week_u = _history_radio_updates(history_records)
        return (
            gr.update(),
            gr.update(),
            gr.update(),
            _render_notice_result("请先在左侧选择要删除的历史记录。", level="warning"),
            history_records,
            today_u,
            yesterday_u,
            week_u,
            current_state,
        )

    filtered_records = [item for item in history_records if item.get("id") != selected_id]
    today_u, yesterday_u, week_u = _history_radio_updates(filtered_records)
    return (
        "",
        _render_progress_bar(0, "", visible=False),
        _render_thinking_module(visible=False),
        _render_result_placeholder(visible=False),
        filtered_records,
        today_u,
        yesterday_u,
        week_u,
        "Idle",
    )


def _load_history_record(
    record_id: str,
    history_records: List[Dict],
    source_group: str,
    current_state: str,
):
    if not record_id:
        return (
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            current_state,
        )

    target = None
    for item in history_records or []:
        if item.get("id") == record_id:
            target = item
            break

    if not target:
        return (
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
            current_state,
        )

    today_update = gr.update(value=record_id if source_group == "today" else None)
    yesterday_update = gr.update(value=record_id if source_group == "yesterday" else None)
    week_update = gr.update(value=record_id if source_group == "week" else None)

    return (
        target.get("case_text", ""),
        _render_progress_bar(100, "历史诊断已载入", visible=True),
        _render_thinking_module(
            completed_steps=len(THINKING_STEPS),
            current_text="已恢复该病例的推理与结论",
            visible=True,
            done=True,
        ),
        target.get("result_html", _render_result_placeholder(visible=True)),
        today_update,
        yesterday_update,
        week_update,
        "Completed",
    )


def load_history_today(record_id: str, history_records: List[Dict], current_state: str):
    return _load_history_record(record_id, history_records, "today", current_state)


def load_history_yesterday(record_id: str, history_records: List[Dict], current_state: str):
    return _load_history_record(record_id, history_records, "yesterday", current_state)


def load_history_week(record_id: str, history_records: List[Dict], current_state: str):
    return _load_history_record(record_id, history_records, "week", current_state)


# ============================================
# 样式
# ============================================

custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');

:root {
  --primary: #007AFF;
  --warning: #FF9500;
  --bg: #F9F9F9;
  --surface: #FFFFFF;
  --line: #E6EAF0;
  --text-main: #0F172A;
  --text-sub: #475569;
  --critical: #EF4444;
  --safe: #16A34A;
}

body {
  background: #f4f5f7;
}

.gradio-container {
  max-width: 1300px !important;
  margin: 0 auto !important;
  padding: 14px 14px 24px !important;
  font-family: "Manrope", "Noto Sans SC", "Microsoft YaHei", sans-serif !important;
  color: var(--text-main);
}

.layout-row {
  align-items: flex-start !important;
  gap: 16px !important;
}

.history-column {
  max-width: 280px !important;
  min-width: 280px !important;
  background: #eef0f3;
  border: 1px solid #dee3ea;
  border-radius: 14px;
  padding: 14px !important;
  box-shadow: none;
  position: sticky;
  top: 12px;
}

.history-title {
  margin: 4px 0 10px;
  font-size: 17px;
  font-weight: 700;
  color: #111827;
}

.history-radio {
  margin-top: 8px;
}

.history-radio label {
  font-weight: 700;
  color: #334155;
}

.history-radio .wrap {
  gap: 8px;
}

.history-radio .wrap label {
  border: 1px solid #d9dee7;
  border-radius: 10px;
  padding: 8px 10px;
  background: #f9fafb;
  transition: all 0.2s ease;
}

.history-radio .wrap label:hover {
  border-color: #b4bcc9;
  transform: translateY(-1px);
}

.history-radio .wrap label:has(input:checked) {
  border-color: #9ca3af;
  box-shadow: 0 2px 8px rgba(17, 24, 39, 0.08);
}

.stage-column {
  max-width: 900px !important;
  margin: 0 auto !important;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 20px !important;
  box-shadow: 0 4px 16px rgba(17, 24, 39, 0.06);
}

.main-header {
  text-align: center;
  margin-bottom: 12px;
}

.main-header h1 {
  margin: 0;
  font-size: 30px;
  line-height: 1.2;
  color: #0b2d5a;
}

.main-header p {
  margin: 6px 0 0;
  color: var(--text-sub);
  font-size: 14px;
}

#diagnose-btn button {
  border-radius: 12px !important;
  background: #007AFF !important;
  border: none !important;
  color: #ffffff !important;
  font-weight: 700 !important;
  box-shadow: 0 6px 14px rgba(0, 122, 255, 0.25);
}

#add-case-btn button,
#delete-case-btn button {
  min-width: 52px;
  border-radius: 12px !important;
  border: 1px solid #d7dde7 !important;
  background: #ffffff !important;
  color: #1f2937 !important;
  font-weight: 700 !important;
}

#delete-case-btn button {
  color: #dc2626 !important;
  border-color: #f1c0c0 !important;
}

.case-input textarea {
  border-radius: 14px !important;
  border: 1px solid #d8e2ed !important;
  background: #fbfdff !important;
  min-height: 230px !important;
}

.diag-progress-wrap {
  margin-top: 8px;
}

.diag-progress-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #334155;
  margin-bottom: 8px;
}

.diag-progress-track {
  position: relative;
  height: 3px;
  border-radius: 99px;
  background: #E0E0E0;
  overflow: hidden;
}

.diag-progress-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 0;
  border-radius: 99px;
  background: #007AFF;
  transition: width 0.42s ease;
}

.thinking-wrap {
  margin-top: 10px;
  border: 1px solid #dce8f7;
  border-radius: 14px;
  background: #f7fbff;
}

.thinking-details summary {
  list-style: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
}

.thinking-details summary::-webkit-details-marker {
  display: none;
}

.thinking-icon {
  font-size: 16px;
}

.thinking-brief {
  flex: 1;
  min-width: 0;
}

.thinking-title {
  font-weight: 700;
  color: #0f2740;
  font-size: 13px;
}

.thinking-current {
  margin-top: 2px;
  font-size: 12px;
  color: #37516b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.thinking-toggle {
  font-size: 12px;
  color: #2563eb;
}

.typing-dot {
  display: inline-block;
  width: 6px;
  height: 14px;
  margin-left: 4px;
  background: #007AFF;
  vertical-align: -2px;
  animation: blink 1s step-end infinite;
}

.thinking-list {
  margin: 0;
  padding: 0 14px 12px 14px;
  list-style: none;
  border-top: 1px dashed #d6e3f2;
}

.thinking-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  line-height: 1.45;
  color: #475569;
  padding-top: 8px;
}

.thinking-list li.done {
  color: #0f766e;
}

.thinking-list li.active {
  color: #1d4ed8;
  font-weight: 600;
}

.thinking-list li.pending {
  color: #64748b;
}

.result-shell {
  margin-top: 14px;
}

.result-shell.is-hidden {
  display: none;
}

.result-enter {
  animation: resultFade 0.45s ease both;
}

.result-section {
  border: 1px solid #e3eaf2;
  background: #fbfdff;
  border-radius: 14px;
  padding: 12px;
  margin-bottom: 10px;
}

.result-section h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #0f2740;
}

.summary-box,
.analysis-box {
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid #e6edf5;
  padding: 10px;
  line-height: 1.55;
  color: #1e293b;
}

.risk-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.risk-card {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  padding: 10px;
}

.risk-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 6px;
}

.risk-card p {
  margin: 0;
  line-height: 1.45;
  color: #334155;
  font-size: 13px;
}

.risk-critical {
  border-color: #fecaca;
  background: #fff5f5;
}

.risk-warning {
  border-color: #fed7aa;
  background: #fff8ef;
}

.risk-info {
  border-color: #bfdbfe;
  background: #f4f9ff;
}

.risk-safe {
  border-color: #bbf7d0;
  background: #f0fdf4;
}

.advice-list {
  display: grid;
  gap: 8px;
}

.advice-item {
  border: 1px solid #dbe5f0;
  border-radius: 12px;
  background: #ffffff;
  padding: 10px;
}

.advice-item h4 {
  margin: 0 0 6px 0;
  color: #0f2740;
  font-size: 14px;
}

.advice-item p {
  margin: 0;
  line-height: 1.5;
  color: #334155;
  font-size: 13px;
}

.advice-source {
  display: inline-block;
  margin-top: 6px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #e8f2ff;
  color: #0f4f8e;
  font-size: 12px;
}

.ref-list {
  margin: 0;
  padding-left: 18px;
  color: #334155;
  line-height: 1.5;
  font-size: 13px;
}

.ref-source {
  display: inline-block;
  margin-right: 6px;
  color: #2563eb;
}

.footnote {
  margin-top: 10px;
  color: #64748b !important;
  font-size: 12px !important;
  text-align: center;
}

@keyframes blink {
  50% { opacity: 0; }
}

@keyframes resultFade {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 960px) {
  .layout-row {
    flex-direction: column !important;
  }

  .history-column {
    position: static;
    max-width: 100% !important;
    min-width: 0 !important;
    width: 100% !important;
  }

  .stage-column {
    max-width: 100% !important;
    width: 100% !important;
  }

  .main-header h1 {
    font-size: 24px;
  }
}
"""


# ============================================
# Gradio 入口
# ============================================


def create_demo():
    with gr.Blocks(
        title="Dia-Agent 糖尿病决策支持系统",
        css=custom_css,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="amber",
            neutral_hue="slate",
            font=["Manrope", "Noto Sans SC", "sans-serif"],
        ),
    ) as demo:
        history_state = gr.State([])
        workflow_state = gr.State("Idle")

        with gr.Row(elem_classes=["layout-row"]):
            with gr.Column(scale=1, min_width=280, elem_classes=["history-column"]):
                gr.HTML('<div class="history-title">历史记录</div>')

                today_radio = gr.Radio(
                    label="今天 (0)",
                    choices=[],
                    value=None,
                    interactive=True,
                    elem_classes=["history-radio"],
                )
                yesterday_radio = gr.Radio(
                    label="昨天 (0)",
                    choices=[],
                    value=None,
                    interactive=True,
                    elem_classes=["history-radio"],
                )
                week_radio = gr.Radio(
                    label="近 7 天 (0)",
                    choices=[],
                    value=None,
                    interactive=True,
                    elem_classes=["history-radio"],
                )

            with gr.Column(scale=3, min_width=680, elem_classes=["stage-column"]):
                gr.HTML(
                    """
<div class="main-header">
  <h1>Dia-Agent 🏥 糖尿病决策支持系统</h1>
  <p>输入病例后开始智能诊断、图谱校验与循证分析</p>
</div>
"""
                )

                case_input = gr.Textbox(
                    label="",
                    lines=11,
                    placeholder="在此输入患者病历、检查结果或当前用药...",
                    elem_classes=["case-input"],
                )

                with gr.Row():
                    diagnose_btn = gr.Button(
                        "开始诊断",
                        variant="primary",
                        size="lg",
                        elem_id="diagnose-btn",
                    )
                    plus_btn = gr.Button("＋", variant="secondary", size="lg", elem_id="add-case-btn")
                    delete_btn = gr.Button("🗑", variant="secondary", size="lg", elem_id="delete-case-btn")

                progress_output = gr.HTML(_render_progress_bar(0, "", visible=False))
                thinking_output = gr.HTML(_render_thinking_module(visible=False))

                result_output = gr.HTML(_render_result_placeholder(visible=False))
                gr.Markdown(
                    "注：本系统提供临床决策支持，不替代医生最终诊断。",
                    elem_classes=["footnote"],
                )

        diagnose_btn.click(
            fn=consult,
            inputs=[case_input, history_state, workflow_state],
            outputs=[
                progress_output,
                thinking_output,
                result_output,
                history_state,
                today_radio,
                yesterday_radio,
                week_radio,
                workflow_state,
            ],
            show_progress="hidden",
        )

        plus_btn.click(
            fn=start_new_diagnosis,
            outputs=[
                case_input,
                progress_output,
                thinking_output,
                result_output,
                today_radio,
                yesterday_radio,
                week_radio,
                workflow_state,
            ],
            show_progress="hidden",
        )

        delete_btn.click(
            fn=delete_selected_history,
            inputs=[today_radio, yesterday_radio, week_radio, history_state, workflow_state],
            outputs=[
                case_input,
                progress_output,
                thinking_output,
                result_output,
                history_state,
                today_radio,
                yesterday_radio,
                week_radio,
                workflow_state,
            ],
            show_progress="hidden",
        )

        today_radio.change(
            fn=load_history_today,
            inputs=[today_radio, history_state, workflow_state],
            outputs=[
                case_input,
                progress_output,
                thinking_output,
                result_output,
                today_radio,
                yesterday_radio,
                week_radio,
                workflow_state,
            ],
            show_progress="hidden",
        )

        yesterday_radio.change(
            fn=load_history_yesterday,
            inputs=[yesterday_radio, history_state, workflow_state],
            outputs=[
                case_input,
                progress_output,
                thinking_output,
                result_output,
                today_radio,
                yesterday_radio,
                week_radio,
                workflow_state,
            ],
            show_progress="hidden",
        )

        week_radio.change(
            fn=load_history_week,
            inputs=[week_radio, history_state, workflow_state],
            outputs=[
                case_input,
                progress_output,
                thinking_output,
                result_output,
                today_radio,
                yesterday_radio,
                week_radio,
                workflow_state,
            ],
            show_progress="hidden",
        )

    return demo


# ============================================
# 主程序
# ============================================

if __name__ == "__main__":
    print("🏥 启动 Dia-Agent GUI...")
    print("=" * 50)
    print(f"Mode: {'Fast' if USE_FAST_AGENT else 'Full'}")
    if USE_FAST_AGENT:
        print(
            f"FastConfig: skip_rag={SKIP_RAG}, skip_reranker={SKIP_RERANKER}, "
            f"llm_case_extraction={LLM_CASE_EXTRACTION}, use_reflection={USE_REFLECTION}"
        )

    prewarm_agent_async()
    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )

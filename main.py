import streamlit as st

from config import SESSION_DEFAULTS
from agents import create_researcher, create_planner, create_reviewer
from ui.styles import get_custom_css
from ui.sidebar import render_sidebar
from ui.itinerary import render_itinerary_section
from utils.export import parse_days


def validate_inputs(api_key, origin, destination, num_days, num_people):
    """校验输入，返回错误信息列表"""
    errors = []
    if not api_key:
        errors.append("请输入 DeepSeek API Key")
    if not origin or not origin.strip():
        errors.append("请输入出发地")
    if not destination or not destination.strip():
        errors.append("请输入目的地")
    if num_days < 1:
        errors.append("旅行天数至少为 1 天")
    if num_people < 1:
        errors.append("人数至少为 1")
    return errors


def stream_agent_output(agent, prompt, placeholder, label):
    """通用流式输出：运行 agent 并实时显示输出"""
    text = ""
    placeholder.markdown(label)
    try:
        for chunk in agent.run(prompt, stream=True):
            if st.session_state.stop_generation:
                break
            if chunk.content:
                text += chunk.content
                placeholder.markdown(text + "▌")
    except Exception as e:
        return None, e
    return text, None


def compress_research_text(text, max_chars=1000):
    """压缩搜索结果，保留关键信息"""
    if len(text) <= max_chars:
        return text
    paragraphs = text.split('\n\n')
    if len(paragraphs) <= 3:
        return text[:max_chars] + "..."
    result = paragraphs[0] + "\n\n...(已压缩)...\n\n" + paragraphs[-1]
    return result if len(result) <= max_chars else text[:max_chars] + "..."


def clean_markdown(text):
    """去除 AI 生成的 Markdown 标记符号"""
    for ch in ["**", "__", "~~~"]:
        text = text.replace(ch, "")
    return text


# 页面设置
st.set_page_config(page_title="逐光")

# 侧边栏
sidebar_values = render_sidebar()
budget_per_person = sidebar_values['budget_per_person']
num_people = sidebar_values['num_people']
total_budget = sidebar_values['total_budget']
dark_mode = sidebar_values['dark_mode']
departure_date = sidebar_values['departure_date']

# CSS
st.markdown(get_custom_css(dark_mode), unsafe_allow_html=True)

# 横幅
st.markdown("""
<div class="banner">
    <h1>逐光</h1>
    <p>输入目的地和天数，AI 自动生成完整行程计划</p>
</div>
""", unsafe_allow_html=True)

# 初始化 session state
for key, default in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default

# API 提供商选择
api_provider = st.radio(
    "API 提供商",
    options=["deepseek", "bailian"],
    format_func=lambda x: {"deepseek": "DeepSeek 官方 API", "bailian": "阿里云百炼平台"}[x],
    horizontal=True,
)

key_label = {
    "deepseek": "输入 DeepSeek API Key（platform.deepseek.com）",
    "bailian": "输入阿里云百炼 API Key（bailian.console.aliyun.com）",
}[api_provider]
deepseek_api_key = st.text_input(key_label, type="password")

# 用户输入
disabled = st.session_state.generating
input_cols = st.columns(3)
with input_cols[0]:
    origin = st.text_input("出发地", placeholder="北京", disabled=disabled)
with input_cols[1]:
    destination = st.text_input("目的地", placeholder="北京, 西安, 上海", disabled=disabled)
with input_cols[2]:
    num_days = st.number_input("旅行天数", min_value=1, max_value=30, value=7, disabled=disabled)

st.session_state.current_destination = destination

# 校验
errors = validate_inputs(deepseek_api_key, origin, destination, num_days, num_people)
can_generate = len(errors) == 0 and bool(deepseek_api_key)
if not can_generate and not st.session_state.generating:
    for err in errors:
        st.warning(err)

if can_generate:
    # 创建 Agent
    researcher = create_researcher(deepseek_api_key, api_provider, num_people, budget_per_person, total_budget)
    planner = create_planner(deepseek_api_key, api_provider, num_people, budget_per_person, total_budget)
    reviewer = create_reviewer(deepseek_api_key, api_provider)

    # 生成按钮
    if st.button("生成行程", type="primary"):
        st.session_state.generating = True
        st.session_state.stop_generation = False
        st.session_state.itinerary = None
        st.session_state.day_contents = {}
        st.rerun()

    # ============================================================
    # 生成阶段（流式输出 + 停止按钮）
    # ============================================================
    if st.session_state.generating:

        def _stop():
            st.session_state.stop_generation = True
            st.session_state.generating = False

        st.button("停止生成", on_click=_stop, type="secondary")

        if not st.session_state.stop_generation:
            # ---- 阶段1：研究员搜索 ----
            research_placeholder = st.empty()
            research_text, err = stream_agent_output(
                researcher,
                f"从{origin}出发，搜索 {destination} 的旅游信息，行程 {num_days} 天，"
                f"人数 {num_people} 人，人均预算 {budget_per_person} 元，总预算 {total_budget} 元",
                research_placeholder,
                "正在搜索目的地信息..."
            )
            if err:
                st.warning(f"搜索服务暂时不可用，已跳过搜索阶段。错误：{err}")
                research_text = "(搜索结果获取失败)"

            # ---- 阶段2：规划师生成行程 ----
            if not st.session_state.stop_generation and research_text:
                plan_placeholder = st.empty()
                compressed = compress_research_text(research_text, 1000)
                prompt = f"""
                出发地：{origin}
                目的地：{destination}
                人数：{num_people} 人
                天数：{num_days} 天
                人均预算：{budget_per_person} 元
                总预算：{total_budget} 元

                搜索结果：{compressed}

                请根据以上信息，生成一份详细的中文行程计划。
                包含从{origin}到{destination}的交通方式和费用建议，
                合理分配天数和预算到每个目的地，每项标注花费，末尾汇总预算使用情况。
                """
                plan_text, err = stream_agent_output(planner, prompt, plan_placeholder, "正在为你生成个性化行程...")
                if err:
                    st.error(f"AI 服务暂时不可用，请检查 API Key 或稍后重试。错误：{err}")
                    st.session_state.generating = False
                    st.rerun()

                if not st.session_state.stop_generation and plan_text:
                    plan_text = clean_markdown(plan_text)

                    # ---- 阶段3：Reviewer 审查 ----
                    review_placeholder = st.empty()
                    review_text, _ = stream_agent_output(
                        reviewer,
                        f"请审查以下行程计划：\n\n{plan_text}\n\n预算：{total_budget} 元，人数：{num_people} 人",
                        review_placeholder,
                        "正在审查行程质量..."
                    )
                    if review_text and "APPROVED" not in review_text:
                        st.info(f"审查建议：{review_text[:300]}")

                    st.session_state.itinerary = plan_text
                    st.session_state.day_contents = dict(parse_days(plan_text))
                    st.session_state.generating = False
                    st.rerun()

    # ============================================================
    # 显示行程
    # ============================================================
    if st.session_state.itinerary and st.session_state.day_contents:
        render_itinerary_section(
            st.session_state.itinerary, st.session_state.day_contents,
            destination, total_budget, num_people, origin
        )

    # ============================================================
    # 重新生成某一天
    # ============================================================
    if st.session_state.regenerating_day is not None:
        day_num = st.session_state.regenerating_day
        context_lines = []
        for d in sorted(st.session_state.day_contents.keys()):
            if d == day_num:
                context_lines.append(f"第{d}天：[需要重新生成]")
            else:
                summary = st.session_state.day_contents[d][:50].replace('\n', ' ').strip()
                context_lines.append(f"第{d}天：{summary}...")
        context_str = "\n".join(context_lines)

        prompt = f"""
        出发地：{origin}
        目的地：{destination}
        人数：{num_people} 人
        总预算：{total_budget} 元

        请重新生成第{day_num}天的行程。

        用户偏好/要求：
        {st.session_state.day_preference if st.session_state.day_preference else "无特殊要求，按常规安排"}

        参考其他天的行程（保持整体协调）：
        {context_str}

        请只输出第{day_num}天的完整行程安排，包含活动、餐饮、住宿和预估花费。
        不要包含其他天的内容。
        """

        regen_placeholder = st.empty()
        regen_text, err = stream_agent_output(planner, prompt, regen_placeholder, f"正在重新生成第{day_num}天...")
        if err:
            st.warning(f"重新生成失败：{err}")
            st.session_state.regenerating_day = None
            st.rerun()

        if not st.session_state.stop_generation and regen_text:
            regen_text = clean_markdown(regen_text)
            st.session_state.day_contents[day_num] = regen_text
            lines = [f"第{d}天：{st.session_state.day_contents[d]}" for d in sorted(st.session_state.day_contents.keys())]
            st.session_state.itinerary = "\n\n".join(lines)
            st.session_state.regenerating_day = None
            st.session_state.day_preference = ''
            st.session_state.regen_mode = {}
            st.rerun()
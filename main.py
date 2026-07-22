import streamlit as st

from config import SESSION_DEFAULTS
from agents import create_researcher, create_planner
from ui.styles import get_custom_css
from ui.sidebar import render_sidebar
from ui.itinerary import render_itinerary_section
from utils.export import parse_days


def validate_inputs(api_key: str, origin: str, destination: str, num_days: int, num_people: int) -> list[str]:
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


def compress_research_text(text: str, max_chars: int = 1000) -> str:
    """压缩搜索结果，保留关键信息"""
    if len(text) <= max_chars:
        return text
    paragraphs = text.split('\n\n')
    if len(paragraphs) <= 3:
        return text[:max_chars] + "..."
    result = paragraphs[0] + "\n\n...(已压缩)...\n\n" + paragraphs[-1]
    if len(result) > max_chars:
        result = text[:max_chars] + "..."
    return result


def clean_markdown(text: str) -> str:
    """去除 AI 生成的 Markdown 标记符号"""
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("~~~", "")
    return text


# Streamlit 页面设置
st.set_page_config(page_title="逐光")

# 侧边栏
sidebar_values = render_sidebar()
budget_per_person = sidebar_values['budget_per_person']
num_people = sidebar_values['num_people']
total_budget = sidebar_values['total_budget']
dark_mode = sidebar_values['dark_mode']
departure_date = sidebar_values['departure_date']

# 注入自定义 CSS
st.markdown(get_custom_css(dark_mode), unsafe_allow_html=True)

# 横幅区域
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

# 获取 DeepSeek API Key
deepseek_api_key = st.text_input("输入 DeepSeek API Key（用于调用 DeepSeek Chat 模型）", type="password")

# 用户输入
disabled = st.session_state.generating

input_cols = st.columns(3)
with input_cols[0]:
    origin = st.text_input("出发地", placeholder="北京", disabled=disabled)
with input_cols[1]:
    destination = st.text_input("目的地", placeholder="北京, 西安, 上海", disabled=disabled)
with input_cols[2]:
    num_days = st.number_input("旅行天数", min_value=1, max_value=30, value=7, disabled=disabled)

# 保存目的地到 session_state（用于侧边栏打包清单推荐）
st.session_state.current_destination = destination

# 校验
errors = validate_inputs(deepseek_api_key, origin, destination, num_days, num_people)
can_generate = len(errors) == 0 and bool(deepseek_api_key)

if not can_generate and not st.session_state.generating:
    for err in errors:
        st.warning(err)

if can_generate:
    # 创建 Agent
    researcher = create_researcher(deepseek_api_key, num_people, budget_per_person, total_budget)
    planner = create_planner(deepseek_api_key, num_people, budget_per_person, total_budget)

    # 生成行程按钮
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
        # 停止按钮
        def _stop_generation():
            st.session_state.stop_generation = True
            st.session_state.generating = False

        st.button("停止生成", on_click=_stop_generation, type="secondary")

        if not st.session_state.stop_generation:
            # ---- 阶段1：研究员搜索（流式） ----
            research_placeholder = st.empty()
            research_placeholder.markdown("正在搜索目的地信息...")

            research_text = ""
            try:
                for chunk in researcher.run(
                    f"从{origin}出发，搜索 {destination} 的旅游信息，行程 {num_days} 天，"
                    f"人数 {num_people} 人，人均预算 {budget_per_person} 元，总预算 {total_budget} 元",
                    stream=True
                ):
                    if st.session_state.stop_generation:
                        break
                    if chunk.content:
                        research_text += chunk.content
                        research_placeholder.markdown(research_text + "▌")
            except Exception as e:
                st.warning(f"搜索服务暂时不可用，已跳过搜索阶段。错误：{str(e)}")
                research_text = "(搜索结果获取失败)"

            # ---- 阶段2：规划师生成行程（流式） ----
            if not st.session_state.stop_generation and research_text:
                plan_placeholder = st.empty()
                plan_placeholder.markdown("正在为你生成个性化行程...")

                # 压缩搜索结果
                compressed_research = compress_research_text(research_text, 1000)

                prompt = f"""
                出发地：{origin}
                目的地：{destination}
                人数：{num_people} 人
                天数：{num_days} 天
                人均预算：{budget_per_person} 元
                总预算：{total_budget} 元

                搜索结果：{compressed_research}

                请根据以上信息，生成一份详细的中文行程计划。
                包含从{origin}到{destination}的交通方式和费用建议，
                合理分配天数和预算到每个目的地，每项标注花费，末尾汇总预算使用情况。
                """

                plan_text = ""
                try:
                    for chunk in planner.run(prompt, stream=True):
                        if st.session_state.stop_generation:
                            break
                        if chunk.content:
                            plan_text += chunk.content
                            plan_placeholder.markdown(plan_text + "▌")
                except Exception as e:
                    st.error(f"AI 服务暂时不可用，请检查 API Key 或稍后重试。错误：{str(e)}")
                    st.session_state.generating = False
                    st.rerun()

                if not st.session_state.stop_generation and plan_text:
                    plan_text = clean_markdown(plan_text)
                    st.session_state.itinerary = plan_text
                    st.session_state.day_contents = dict(parse_days(plan_text))
                    st.session_state.generating = False
                    st.rerun()

    # ============================================================
    # 显示行程
    # ============================================================
    if st.session_state.itinerary and st.session_state.day_contents:
        render_itinerary_section(
            st.session_state.itinerary,
            st.session_state.day_contents,
            destination,
            total_budget,
            num_people,
            origin
        )

    # ============================================================
    # 重新生成某一天
    # ============================================================
    if st.session_state.regenerating_day is not None:
        day_num = st.session_state.regenerating_day

        # 构建上下文：其他天的行程摘要（节省 token）
        context_lines = []
        for d in sorted(st.session_state.day_contents.keys()):
            if d == day_num:
                context_lines.append(f"第{d}天：[需要重新生成]")
            else:
                content = st.session_state.day_contents[d]
                summary = content[:50].replace('\n', ' ').strip()
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
        regen_placeholder.markdown(f"正在重新生成第{day_num}天...")

        regen_text = ""
        try:
            for chunk in planner.run(prompt, stream=True):
                if st.session_state.stop_generation:
                    break
                if chunk.content:
                    regen_text += chunk.content
                    regen_placeholder.markdown(regen_text + "▌")
        except Exception as e:
            st.warning(f"重新生成失败：{str(e)}")
            st.session_state.regenerating_day = None
            st.rerun()

        if not st.session_state.stop_generation and regen_text:
            regen_text = clean_markdown(regen_text)
            st.session_state.day_contents[day_num] = regen_text
            # 更新完整行程文本
            lines = []
            for d in sorted(st.session_state.day_contents.keys()):
                lines.append(f"第{d}天：{st.session_state.day_contents[d]}")
            st.session_state.itinerary = "\n\n".join(lines)
            st.session_state.regenerating_day = None
            st.session_state.day_preference = ''
            st.session_state.regen_mode = {}
            st.rerun()
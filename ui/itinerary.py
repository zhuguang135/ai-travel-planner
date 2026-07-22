"""行程展示区域"""
import streamlit as st
from utils.export import generate_html_content, generate_ics_content
from utils.poi import extract_pois, render_poi_links


def render_itinerary_section(itinerary: str, day_contents: dict, destination: str,
                              total_budget: int, num_people: int, origin: str):
    """渲染行程详情、重新生成、下载区域"""
    st.markdown("### 行程详情")
    for day_num in sorted(day_contents.keys()):
        st.markdown(f'<div class="card">', unsafe_allow_html=True)
        st.markdown(f"#### 第{day_num}天")
        st.markdown(day_contents[day_num])

        # 攻略链接
        pois = extract_pois(day_contents[day_num], destination)
        if pois:
            st.markdown(render_poi_links(pois), unsafe_allow_html=True)

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(f"重新生成", key=f"regen_btn_{day_num}"):
                st.session_state.regen_mode[day_num] = not st.session_state.regen_mode.get(day_num, False)

        if st.session_state.regen_mode.get(day_num, False):
            with col2:
                preference = st.text_area(
                    "想去的地方或偏好（可选）",
                    placeholder="例：想去华山、不辣、不要太赶",
                    key=f"pref_{day_num}"
                )
                if st.button(f"按偏好生成", key=f"regen_pref_{day_num}"):
                    st.session_state.regenerating_day = day_num
                    st.session_state.day_preference = preference
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # 下载按钮
    col_dl = st.columns(2)
    with col_dl[0]:
        html_content = generate_html_content(itinerary, destination, total_budget, origin=origin)
        st.download_button(
            label="下载PDF (.html)", data=html_content,
            file_name="travel_itinerary.html", mime="text/html"
        )
    with col_dl[1]:
        ics_content = generate_ics_content(itinerary)
        st.download_button(
            label="下载行程日历 (.ics)", data=ics_content,
            file_name="travel_itinerary.ics", mime="text/calendar"
        )
"""侧边栏组件"""
from datetime import datetime, timedelta
import streamlit as st
from utils.packing import render_packing_list


def render_sidebar() -> dict:
    """渲染侧边栏，返回所有设置值"""
    with st.sidebar:
        st.header("设置")
        st.divider()

        budget_per_person = st.number_input("人均预算（元）", min_value=0, max_value=100000, step=100, value=3000)
        num_people = st.number_input("人数", min_value=1, max_value=20, value=2)
        total_budget = budget_per_person * num_people
        dark_mode = st.toggle("暗色模式", value=False)

        st.divider()
        departure_date = st.date_input("出发日期", value=datetime.today() + timedelta(days=7))

        # 倒计时
        delta = (departure_date - datetime.today().date()).days
        if delta > 0:
            st.markdown(f"**距离出发还有 {delta} 天**")
        elif delta == 0:
            st.markdown("**今天出发，旅途愉快！**")
        else:
            st.markdown("**已在旅途中，祝玩得开心！**")

        # 打包清单
        st.divider()
        destination = st.session_state.get('current_destination', '')
        render_packing_list(destination)

        return {
        'budget_per_person': budget_per_person,
        'num_people': num_people,
        'total_budget': total_budget,
        'dark_mode': dark_mode,
        'departure_date': departure_date,
    }
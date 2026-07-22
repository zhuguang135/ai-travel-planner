"""打包清单数据与推荐逻辑"""

from config import PACKING_ITEMS, EXTRA_ITEMS
import streamlit as st


def get_extra_items(destination: str) -> list:
    """根据目的地关键词推荐额外物品"""
    extra = []
    if not destination:
        return extra
    dest_lower = destination.lower()
    for keyword, items in EXTRA_ITEMS.items():
        if keyword in dest_lower:
            extra.extend(items)
    return list(set(extra))


def render_packing_list(destination: str = ""):
    """在侧边栏渲染打包清单 UI"""
    st.markdown("### 打包清单")

    extra_items = get_extra_items(destination)

    checked_count = 0
    total_count = 0

    for category, items in PACKING_ITEMS.items():
        all_items = list(items)
        if extra_items and category in ("衣物类", "其他"):
            for item in extra_items:
                label = f"{item}（推荐）"
                if label not in all_items:
                    all_items.append(label)

        with st.expander(category, expanded=False):
            for item in all_items:
                key = f"packing_{category}_{item}"
                if key not in st.session_state:
                    st.session_state[key] = False
                checked = st.checkbox(item, key=key)
                if checked:
                    checked_count += 1
                total_count += 1

    if total_count > 0:
        st.progress(checked_count / total_count, text=f"{checked_count}/{total_count}")
    if st.button("重置清单"):
        for key in list(st.session_state.keys()):
            if key.startswith("packing_"):
                del st.session_state[key]
        st.rerun()
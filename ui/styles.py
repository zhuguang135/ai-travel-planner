"""CSS 生成与主题管理"""
from config import COLOR_THEME


def get_custom_css(dark_mode: bool) -> str:
    """根据暗色模式返回现代极简风格 CSS"""
    theme = COLOR_THEME["dark" if dark_mode else "light"]
    return f"""
    <style>
    .stApp {{
        background-color: {theme['bg']};
        color: {theme['text']};
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
                     'Microsoft YaHei', sans-serif;
    }}

    /* Banner */
    .banner {{
        padding: 24px 0 16px 0;
        margin-bottom: 24px;
        border-bottom: 1px solid {theme['border']};
    }}
    .banner h1 {{
        color: {theme['text']};
        margin: 0;
        font-size: 1.8em;
        font-weight: 600;
        letter-spacing: -0.02em;
    }}
    .banner p {{
        color: {theme['text_secondary']};
        margin: 6px 0 0 0;
        font-size: 0.95em;
    }}

    /* 行程卡片 */
    .card {{
        background-color: {theme['card_bg']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
        padding: 20px 20px 20px 24px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        position: relative;
        transition: box-shadow 0.2s ease;
    }}
    .card:hover {{
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    .card::before {{
        content: '';
        position: absolute;
        left: 0;
        top: 12px;
        bottom: 12px;
        width: 3px;
        background: {theme['accent']};
        border-radius: 2px;
    }}

    /* 预算摘要 */
    .budget-summary {{
        background-color: {theme['card_bg']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
        padding: 14px 18px;
        margin: 16px 0;
        font-size: 0.9em;
    }}

    /* 输入框 */
    .stTextInput input, .stNumberInput input {{
        border-radius: 6px !important;
        border: 1px solid {theme['border']} !important;
    }}
    .stTextInput input:focus, .stNumberInput input:focus {{
        border-color: {theme['accent']} !important;
        box-shadow: 0 0 0 2px rgba(230, 126, 34, 0.15) !important;
    }}

    /* 文本区域 */
    .stTextArea textarea {{
        font-size: 14px;
        line-height: 1.7;
        border-radius: 6px;
    }}

    /* 按钮 */
    .stButton button {{
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.15s ease;
    }}

    /* 分割线 */
    hr {{
        margin: 20px 0;
        border-color: {theme['border']};
    }}

    /* 侧边栏 */
    section[data-testid="stSidebar"] {{
        background-color: {theme['card_bg']};
    }}
    </style>
    """
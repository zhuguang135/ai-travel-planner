"""导出功能：HTML 和 ICS 生成"""
import re
from datetime import datetime, timedelta
from icalendar import Calendar, Event


def parse_days(plan_text: str) -> list[tuple[int, str]]:
    """将行程文本按天解析为 [(day_num, content), ...]"""
    day_pattern = re.compile(
        r'(?:第\s*(\d+)\s*天|Day\s+(\d+))[：:\s]+(.*?)(?=(?:第\s*\d+\s*天|Day\s+\d+)[：:\s]|$)',
        re.DOTALL
    )
    matches = day_pattern.findall(plan_text)
    if not matches:
        return [(1, plan_text)]
    result = []
    for day_num_a, day_num_b, content in matches:
        day_num = int(day_num_a or day_num_b)
        result.append((day_num, content.strip()))
    return result


def generate_html_content(plan_text: str, destination: str, budget: int, origin: str = "") -> str:
    """将行程文本生成格式化的 HTML 文档"""
    days = parse_days(plan_text)
    days_html = "".join(
        f"""
        <div class="day-card">
            <div class="day-number">第{day_num}天</div>
            <div class="day-content">{content.replace(chr(10), '<br>')}</div>
        </div>
        """
        for day_num, content in days
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>行程计划 - {destination}</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
        color: #2D2D2D;
        line-height: 1.8;
        max-width: 800px;
        margin: 0 auto;
        padding: 40px 24px;
        background: #FAFAFA;
    }}
    .header {{
        background: linear-gradient(135deg, #E67E22, #F39C12);
        color: #fff;
        padding: 32px 28px;
        border-radius: 12px;
        margin-bottom: 28px;
    }}
    .header h1 {{ font-size: 24px; font-weight: 600; margin-bottom: 8px; }}
    .header .meta {{ font-size: 14px; opacity: 0.9; line-height: 1.6; }}
    .budget-box {{
        background: #FFF8F0;
        border: 1px solid #FDE6CC;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 24px;
        font-size: 14px;
        color: #666;
    }}
    .budget-box strong {{ color: #E67E22; }}
    .day-card {{
        background: #fff;
        border: 1px solid #E8E8E8;
        border-radius: 10px;
        padding: 0;
        margin-bottom: 20px;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }}
    .day-number {{
        background: #E67E22;
        color: #fff;
        font-size: 15px;
        font-weight: 600;
        padding: 10px 20px;
    }}
    .day-content {{
        padding: 16px 20px;
        font-size: 14px;
        line-height: 1.9;
    }}
    .day-content br {{ content: ""; display: block; margin: 6px 0; }}
    @media print {{
        body {{ background: #fff; padding: 0; }}
        .day-card {{ break-inside: avoid; }}
    }}
</style>
</head>
<body>
    <div class="header">
        <h1>🗺️ {destination} 行程计划</h1>
        <div class="meta">
            {'✈️ 出发地：' + origin if origin else ''}
            {'  ' if origin else ''}💰 预算：{budget} 元
        </div>
    </div>
    {days_html}
</body>
</html>"""


def generate_ics_content(plan_text: str, start_date: datetime = None) -> bytes:
    """将行程文本生成 ICS 日历文件"""
    cal = Calendar()
    cal.add('prodid', '-//AI Travel Planner//github.com//')
    cal.add('version', '2.0')
    if start_date is None:
        start_date = datetime.today()

    days = parse_days(plan_text)
    if not days:
        event = Event()
        event.add('summary', "旅行行程")
        event.add('description', plan_text)
        event.add('dtstart', start_date.date())
        event.add('dtend', start_date.date())
        event.add("dtstamp", datetime.now())
        cal.add_component(event)
    else:
        for day_num, day_content in days:
            current_date = start_date + timedelta(days=day_num - 1)
            event = Event()
            event.add('summary', f"第{day_num}天 行程")
            event.add('description', day_content.strip())
            event.add('dtstart', current_date.date())
            event.add('dtend', current_date.date())
            event.add("dtstamp", datetime.now())
            cal.add_component(event)
    return cal.to_ical()
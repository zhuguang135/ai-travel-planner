"""景点提取与攻略链接生成"""
import re

# ── 非景点名词排除列表 ──────────────────────────────────────────────
EXCLUDE_WORDS = {
    # 住宿
    "酒店", "宾馆", "民宿", "青旅", "客栈", "旅馆", "公寓", "招待所",
    # 餐饮-食物
    "臭豆腐", "火锅", "烧烤", "串串", "麻辣烫", "小龙虾", "烤鸭",
    "面条", "拉面", "饺子", "包子", "馒头", "米饭", "炒饭", "炒面",
    "凉皮", "肉夹馍", "煎饼", "烤串", "烤鱼", "海鲜", "生煎", "小笼包",
    "螺蛳粉", "米线", "酸辣粉", "炸鸡", "薯条", "披萨", "汉堡",
    "咖啡", "奶茶", "果汁", "甜品", "蛋糕", "面包", "冰淇淋", "酸奶",
    "早餐", "午餐", "晚餐", "早饭", "午饭", "晚饭", "早茶", "夜宵",
    "美食", "小吃", "菜肴", "菜品", "菜系", "风味", "口味",
    # 餐饮-场所
    "餐厅", "饭馆", "饭店", "食堂", "小吃街", "美食街", "夜市",
    # 交通
    "步行", "打车", "开车", "公交", "地铁", "出租", "包车", "骑行",
    "骑车", "自驾", "高铁", "火车", "飞机", "轮船", "索道", "缆车",
    "自行车", "电动车", "摩托车", "出租车", "网约车", "大巴",
    # 时间
    "上午", "下午", "晚上", "中午", "早上", "清晨", "傍晚", "夜间",
    "今天", "明天", "后天", "昨日", "今日", "明日", "白天", "夜晚",
    # 动作/状态
    "出发", "抵达", "到达", "前往", "返回", "休息", "入住", "退房",
    "起床", "睡觉", "集合", "出来", "进去", "出发地", "目的地",
    # 费用
    "时间", "费用", "门票", "价格", "预算", "花费", "价钱", "收费",
    "免费", "人均", "合计", "总计", "共计", "花费", "开销",
    # 通用修饰
    "推荐", "建议", "注意", "提示", "攻略", "特色", "著名", "必去",
    "不错", "好吃", "好玩", "好看", "方便", "值得", "经典", "热门",
    "附近", "周边", "旁边", "对面", "路上", "沿途", "当地",
    "文化", "历史", "自然", "风景", "风光", "景色", "景观", "美景",
    "老字号", "网红", "打卡", "拍照", "体验", "参观", "游览",
    "中心", "广场", "大街", "商业街", "步行街", "古街", "老街",
    "之一", "最多", "第一", "第二", "第三", "最佳",
    "市区", "郊区", "古城", "老城", "新城", "城内", "城外",
    "东部", "西部", "南部", "北部", "中部", "东南", "西南", "东北", "西北",
    # 常见城市名（避免搜索时冗余）
    "北京", "上海", "广州", "深圳", "成都", "重庆", "杭州", "武汉",
    "西安", "南京", "长沙", "苏州", "天津", "郑州", "青岛", "大连",
    "厦门", "昆明", "丽江", "大理", "三亚", "海口", "哈尔滨", "拉萨",
    "乌鲁木齐", "兰州", "西宁", "银川", "呼和浩特", "贵阳", "南宁",
    # 以下为知名景点，保留在排除列表中表示"不单独作为链接"
    # 但如果 AI 行程中明确写了"去长城""参观故宫"，仍会被动词规则提取
    # 故仅排除纯城市名，景点名保留让用户自行搜索
}

# 时间上下文词——逗号/顿号前的名称如果包含这些时间词，说明不是纯景点名
_TIME_WORDS = {"上午", "下午", "晚上", "中午", "早上", "清晨", "傍晚", "夜间",
               "今天", "明天", "后天", "昨天", "今日", "明日", "白天", "夜晚"}

# 动词前缀——匹配"参观XX""爬XX"等结构中的动词
ACTION_VERBS = "去|到|参观|游览|逛|玩|爬|登|游|前往|探访|走进|进入|探索|来到|路过"

# 趋向补语——动词后紧跟的方位词，不可能是景点名的一部分
_DIRECTIONAL = "上|下|进|出|到|回|过|上来|下去|进来|出去|回来|过去"

# 景点名常见后缀——用于校验逗号分隔提取的结果
_POI_SUFFIXES = {
    # 单字后缀
    "馆", "园", "寺", "庙", "塔", "山", "峰", "湖", "海", "河", "江",
    "岛", "湾", "滩", "洞", "谷", "峡", "崖", "陵", "墓", "祠",
    "宫", "殿", "阁", "楼", "台", "亭", "桥", "街", "巷", "村",
    "寨", "堡", "城", "墙", "门", "堂", "院", "场", "港", "道",
    "路", "井", "屯", "庄", "关", "坛", "堤", "渠", "廊", "屿", "岩", "瀑", "泉", "垵", "俑", "里", "珠",
    # 双字及以上后缀
    "公园", "广场", "码头", "遗址", "故居", "旧址", "古街", "老街",
    "博物馆", "纪念馆", "美术馆", "艺术馆", "科技馆", "体育馆",
    "展览馆", "图书馆", "文化馆", "规划馆", "陈列馆",
    "植物园", "动物园", "游乐园", "影视城", "度假区", "风景区",
    "保护区", "旅游区", "观光区", "老街", "古城", "古镇",
    "市场", "集市", "商业街", "步行街", "美食街", "夜市", "基地", "中心",
    "大学", "学院", "校区", "教堂", "寺庙", "道观",
}

# 使用负向前瞻排除"的"字进入匹配
_NO_DE_CHAR = r"(?:(?!的)[一-鿿])"


def _ends_with_poi_suffix(name: str) -> bool:
    """检查名称是否以景点后缀结尾"""
    for suffix in _POI_SUFFIXES:
        if name.endswith(suffix):
            return True
    return False


def _starts_with_pattern(name: str, pattern: str) -> bool:
    """检查名称是否以指定模式开头"""
    if len(name) >= 2 and re.match(rf'^(?:{pattern})', name[:2]):
        return True
    if re.match(rf'^(?:{pattern})', name[0]):
        return True
    return False

_starts_with_verb = lambda n: _starts_with_pattern(n, ACTION_VERBS)
_starts_with_directional = lambda n: _starts_with_pattern(n, _DIRECTIONAL)


def _is_valid_attraction(name: str) -> bool:
    """基础有效性检查：长度、排除词、"的"字"""
    if len(name) < 2:
        return False
    if "的" in name:
        return False
    if name in EXCLUDE_WORDS:
        return False
    return True


def _is_substring_of_any(name: str, candidates: list[str]) -> bool:
    """检查 name 是否是 candidates 中某个名称的子串"""
    return any(name in existing for existing in candidates)


def extract_pois(text: str, destination: str = "") -> list[str]:
    """从行程文本中提取景点/地点名称，去重保持顺序

    提取规则：
    1. 动词+景点名（如"参观故宫博物院"）—— 排除趋向补语
    2. 景点名（门票（如"故宫博物院（门票60元"）
    3. 逗号/顿号分隔的景点（如"南锣鼓巷、鼓楼"）—— 需景点后缀 + 排除动词前缀

    Args:
        text: 行程文本
        destination: 目的地城市名，用于过滤城市名本身

    Returns:
        list[str]: 提取的景点名称列表，最多5个
    """
    seen = set()
    pois = []

    # ── 规则1: 动词+景点名（如"参观故宫博物院"）──────────────
    verb_pattern = re.compile(
        rf'(?:{ACTION_VERBS})\s*({_NO_DE_CHAR}{{2,12}})(?:\s|，|。|；|、|\)|（|$|的)'
    )
    for m in verb_pattern.finditer(text):
        name = m.group(1).strip()
        # 排除趋向补语："登上"→"登"匹配但"上"不是景点
        if _starts_with_directional(name):
            continue
        if not _is_valid_attraction(name):
            continue
        if name in seen:
            continue
        # 动词规则的名词也需以景点后缀结尾（过滤"去夜市吃臭豆腐"）
        if not _ends_with_poi_suffix(name):
            continue
        # 避免子串重复
        if _is_substring_of_any(name, pois):
            continue
        seen.add(name)
        pois.append(name)

    # ── 规则2: 景点名（门票（如"故宫博物院（门票60元"）────────
    bracket_pattern = re.compile(
        rf'({_NO_DE_CHAR}{{2,12}})（(?:门票|价格|开放|需|建议|需|收费|提前)'
    )
    for m in bracket_pattern.finditer(text):
        name = m.group(1).strip()
        if not _is_valid_attraction(name):
            continue
        if name in seen:
            continue
        # 避免子串重复
        if _is_substring_of_any(name, pois):
            continue
        seen.add(name)
        pois.append(name)

    # ── 规则3: 逗号/顿号分隔的景点（如"南锣鼓巷、鼓楼"）─────
    # 该规则最容易产生噪音，故附加限制：
    #   a) 名称必须以景点后缀结尾
    #   b) 名称不能以动词开头（避免"逛栈桥"）
    #   c) 名称不能包含时间上下文（避免"下午去西湖"）
    comma_pattern = re.compile(
        rf'({_NO_DE_CHAR}{{2,8}})(?:[、，,]|$)',
        re.MULTILINE
    )
    for m in comma_pattern.finditer(text):
        name = m.group(1).strip()
        if not _is_valid_attraction(name):
            continue
        if name in seen:
            continue
        # 必须以景点后缀结尾
        if not _ends_with_poi_suffix(name):
            continue
        # 不能以动词开头
        if _starts_with_verb(name):
            continue
        # 不能包含时间上下文词
        if any(tw in name for tw in _TIME_WORDS):
            continue
        # 不能包含动词（如"午参观故宫博物院"含"参观"）
        if re.search(rf'(?:{ACTION_VERBS})', name):
            continue
        # 避免子串重复
        if _is_substring_of_any(name, pois):
            continue
        seen.add(name)
        pois.append(name)

    # ── 过滤目的地城市名本身 ──────────────────────────────────
    if destination:
        for city_part in destination.replace("，", ",").split(","):
            city_part = city_part.strip()
            if city_part in seen:
                seen.discard(city_part)
                pois = [p for p in pois if p != city_part]

    return pois[:5]


def render_poi_links(pois: list[str]) -> str:
    """生成攻略链接 HTML

    Args:
        pois: 景点名称列表

    Returns:
        str: 攻略链接的 HTML 片段，如无景点则返回空字符串
    """
    if not pois:
        return ""

    links_html = ""
    for name in pois:
        encoded_name = name.replace(" ", "")
        links_html += (
            f'<a href="https://www.xiaohongshu.com/search_result?keyword={encoded_name}" '
            f'target="_blank" rel="noopener noreferrer" style="color: #E67E22; text-decoration: none; '
            f'font-size: 0.8em; margin-right: 12px; '
            f'border: 1px solid #E67E22; border-radius: 4px; padding: 2px 10px; '
            f'transition: background 0.2s;">'
            f'📕 小红书 {name}</a>'
        )

    return f'<div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #eee;">' \
           f'<span style="color: #999; font-size: 0.75em; margin-right: 8px;">攻略：</span>{links_html}</div>'
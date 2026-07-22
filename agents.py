"""Agent 定义 — Researcher（多轮搜索）+ Planner（规划）+ Reviewer（审查）

两个函数均接受 provider 参数以支持 DeepSeek 官方 API 或阿里云百炼平台。
"""
from textwrap import dedent
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.baidusearch import BaiduSearchTools


API_PROVIDERS = {
    "deepseek": {
        "label": "DeepSeek 官方 API",
        "base_url": None,
        "model_id": "deepseek-chat",
    },
    "bailian": {
        "label": "阿里云百炼平台",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model_id": "deepseek-v4-flash",
    },
}


def _create_deepseek_model(api_key, provider):
    """根据提供商创建 DeepSeek 模型实例"""
    config = API_PROVIDERS[provider]
    kwargs = {"id": config["model_id"], "api_key": api_key, "use_thinking": True}
    if config["base_url"]:
        kwargs["base_url"] = config["base_url"]
    return DeepSeek(**kwargs)


def _budget_info(num_people, budget_per_person, total_budget):
    return f"人数：{num_people}，人均预算：{budget_per_person} 元，总预算：{total_budget} 元"


def create_researcher(api_key, provider, num_people, budget_per_person, total_budget):
    return Agent(
        name="Researcher",
        role="搜索旅行目的地、活动和住宿信息",
        model=_create_deepseek_model(api_key, provider),
        tool_call_limit=3,
        description=dedent("""\
            为旅行目的地收集关键信息，尽量在一次搜索中覆盖多个方面。
            如果信息不足再补充搜索，最多 3 次。
        """),
        instructions=[
            "你的任务是收集目的地旅行的关键信息。",
            "每次搜索尽量用多个关键词覆盖不同方面（景点、美食、交通、住宿）。",
            "如果搜索后仍有明显的信息缺口，再补充搜索。",
            "目的地可能有多个（用逗号分隔），覆盖每个目的地。",
            "目的地均为中国国内城市，只搜索和推荐中国境内信息。",
            _budget_info(num_people, budget_per_person, total_budget),
        ],
        tools=[BaiduSearchTools()],
        add_datetime_to_context=True,
    )


def create_planner(api_key, provider, num_people, budget_per_person, total_budget):
    return Agent(
        name="Planner",
        role="根据用户偏好和研究结果生成行程计划",
        model=_create_deepseek_model(api_key, provider),
        reasoning=True,
        description=dedent("""\
            根据用户输入和研究结果，生成一份详细的行程计划。
        """),
        instructions=[
            "使用「第1天」「第2天」……的格式标注每一天。",
            "目的地可能有多个（用逗号分隔），合理分配天数和预算。",
            "目的地均为中国国内城市。",
            _budget_info(num_people, budget_per_person, total_budget),
            "根据人数推荐合适的住宿、交通和餐饮份量。",
            "在每项活动/住宿/餐饮后标注预估花费。",
            "行程末尾汇总预估总花费，显示剩余预算，超预算时给出调整建议。",
        ],
        add_datetime_to_context=True,
    )


def create_reviewer(api_key, provider):
    return Agent(
        name="Reviewer",
        role="审查行程计划的质量和完整性",
        model=_create_deepseek_model(api_key, provider),
        description=dedent("""\
            审查行程计划，检查完整性、预算合理性、实用性。
            如果一切合理则输出 APPROVED，否则输出具体改进建议。
        """),
        instructions=[
            "审查以下方面：",
            "1. 完整性：每天是否有足够的活动安排？",
            "2. 预算合理性：花费是否在预算范围内？",
            "3. 实用性：交通时间是否合理，景点顺序是否顺路？",
            "如果发现问题，输出具体的改进建议。",
            "如果一切合理，输出 'APPROVED'。",
        ],
    )
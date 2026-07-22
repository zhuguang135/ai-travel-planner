"""Agent 定义（Researcher + Planner）

两个函数均接受 provider 参数以支持 DeepSeek 官方 API 或阿里云百炼平台。
"""
from textwrap import dedent
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.baidusearch import BaiduSearchTools


# API 提供商配置
API_PROVIDERS = {
    "deepseek": {
        "label": "DeepSeek 官方 API",
        "base_url": None,  # 使用默认值 https://api.deepseek.com
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
    kwargs = {
        "id": config["model_id"],
        "api_key": api_key,
        "use_thinking": True,
    }
    if config["base_url"]:
        kwargs["base_url"] = config["base_url"]
    return DeepSeek(**kwargs)


def create_researcher(api_key, provider, num_people, budget_per_person, total_budget):
    return Agent(
        name="Researcher",
        role="搜索旅行目的地、活动和住宿信息",
        model=_create_deepseek_model(api_key, provider),
        description=dedent("""\\
            根据用户输入的目的地和旅行天数，搜索相关旅行活动和住宿信息，
            返回最相关的 10 条结果。
        """),
        instructions=[
            "根据用户输入的目的地和旅行天数，生成 3 个搜索关键词，用百度搜索。",
            "从搜索结果中筛选出最相关的 10 条信息。",
            "目的地可能有多个（用逗号分隔），请搜索每个目的地的相关信息。",
            "目的地均为中国国内城市，只搜索和推荐中国境内信息。",
            f"出行人数：{num_people} 人，预算为人均 {budget_per_person} 元，总预算 {total_budget} 元。",
        ],
        tools=[BaiduSearchTools()],
        add_datetime_to_context=True,
    )


def create_planner(api_key, provider, num_people, budget_per_person, total_budget):
    return Agent(
        name="Planner",
        role="根据用户偏好和研究结果生成行程计划",
        model=_create_deepseek_model(api_key, provider),
        description=dedent("""\\
            根据用户输入的目的地、旅行天数和研究结果，
            生成一份详细的行程计划。
        """),
        instructions=[
            "生成详细的行程计划，包括每天的活动安排和住宿建议。",
            "使用「第1天」「第2天」……的格式标注每一天。",
            "目的地可能有多个（用逗号分隔），合理分配天数和预算。",
            "目的地均为中国国内城市。",
            f"出行人数：{num_people} 人。",
            f"预算为人均 {budget_per_person} 元，总预算 {total_budget} 元。",
            "根据人数推荐合适的住宿、交通和餐饮份量。",
            "在每项活动/住宿/餐饮后标注预估花费。",
            "行程末尾汇总预估总花费，显示剩余预算，超预算时给出调整建议。",
        ],
        add_datetime_to_context=True,
    )

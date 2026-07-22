# 逐光 — AI 旅行规划师

> 基于 DeepSeek V4 Flash + 百度搜索的智能行程规划工具。输入目的地和天数，AI 自动搜索信息、生成完整旅行计划，并审查质量。
>
> 本应用基于 [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) 的 AI Travel Agent 修改扩展，感谢原项目。

---

## 功能

| 功能 | 说明 |
|------|------|
| **三 Agent 架构** | Researcher 搜索 + Planner 生成 + Reviewer 审查，分工协作，质量可控 |
| **多轮搜索** | Researcher 自动多轮搜索，覆盖景点、美食、交通、住宿 |
| **质量审查** | Reviewer 自动检查行程完整性、预算合理性、实用性，输出改进建议 |
| **DeepSeek V4 Flash** | 支持 DeepSeek 官方 API 和阿里云百炼平台，均可调用 V4 Flash 模型 |
| **API 提供商选择** | 一键切换 DeepSeek 官方 / 阿里云百炼，API Key 提示自动联动 |
| **流式输出** | 搜索、生成、审查过程实时显示，所见即所得 |
| **多目的地** | 支持一次规划多个城市，AI 自动分配天数和预算 |
| **出发地** | 包含从出发地到目的地的交通建议和费用预估 |
| **多人预算** | 设置人数和人均预算，AI 智能分配花费 |
| **出发倒计时** | 侧边栏显示距离出发还有多少天 |
| **智能打包清单** | 根据目的地特色（海边、山区、雪地等）自动推荐额外物品 |
| **每日重新生成** | 可针对某一天输入偏好重新生成，其他天保持不变 |
| **攻略链接** | 自动提取景点名称，生成小红书搜索链接 |
| **HTML 下载** | 生成格式化的 HTML 行程文档，可打印/保存 |
| **日历导出** | 生成 ICS 日历文件，导入手机日历 |
| **暗色模式** | 一键切换明暗主题 |
| **Markdown 净化** | 自动去除 AI 输出的冗余 Markdown 符号 |

## 技术栈

- **前端框架:** [Streamlit](https://streamlit.io/)
- **AI 框架:** [agno](https://github.com/agno-agi/agno)（支持多 Agent 编排、ReAct 循环、工具调用）
- **模型:** DeepSeek V4 Flash（DeepSeek 官方 API / 阿里云百炼平台）
- **搜索工具:** 百度搜索 API
- **语言:** 全中文界面

## 快速开始

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
streamlit run main.py
```

### 部署到 Streamlit Cloud

1. 将本仓库推送到你的 GitHub
2. 打开 [share.streamlit.io](https://share.streamlit.io)
3. 点击 **New app**，选择本仓库
4. Branch: `main`，Main file path: `main.py`
5. 点击 Deploy，约 2 分钟即获得公网链接

### 获取 API Key

本应用支持 **DeepSeek 官方 API** 和 **阿里云百炼平台** 两种方式，在界面中一键切换：

- **DeepSeek 官方 API**：访问 [platform.deepseek.com](https://platform.deepseek.com/) 注册并创建 API Key
- **阿里云百炼平台**：访问 [bailian.console.aliyun.com](https://bailian.console.aliyun.com/) 开通服务并创建 API Key

## 使用方式

1. 选择 API 提供商（DeepSeek 官方 API 或阿里云百炼平台），输入对应的 API Key
2. 在侧边栏设置预算、人数、出发日期
3. 输入出发地和目的地（支持多个城市，用逗号分隔）
4. 设置旅行天数
5. 点击生成行程，AI 自动完成：搜索信息 → 规划行程 → 审查质量
6. 生成后可按天重新生成，或下载 HTML/ICS

## 项目结构

```
ai_travel_agent/
├── main.py              # 主入口：页面布局、生成流程控制、重新生成逻辑
├── agents.py            # Agent 定义：Researcher（搜索）+ Planner（规划）+ Reviewer（审查）
├── config.py            # 配置常量：打包清单、主题色、Session 默认值
├── requirements.txt     # 依赖列表
├── ui/
│   ├── sidebar.py       # 侧边栏：预算、人数、出发日期、暗色模式
│   ├── itinerary.py     # 行程展示：每日详情、重新生成按钮、下载按钮
│   └── styles.py        # CSS 主题：明暗模式样式
└── utils/
    ├── export.py        # HTML/ICS 导出
    ├── packing.py       # 智能打包清单
    └── poi.py           # 景点提取与小红书攻略链接生成
```

## 许可

本项目基于 [awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) 修改，遵循原项目许可证。

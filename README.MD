# 逐光 — AI 旅行规划师

> 基于 DeepSeek V4 + 百度搜索的智能行程规划工具，输入目的地和天数，AI 自动生成完整旅行计划。
>
> 本项目基于 [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) 的 AI Travel Agent 修改扩展，感谢原项目。

---

## 功能

| 功能 | 说明 |
|------|------|
| **双 Agent 架构** | Researcher 搜索目的地信息 + Planner 生成行程，分工协作 |
| **AI 搜索引擎** | 基于百度搜索，实时获取景点、活动、住宿信息 |
| **DeepSeek V4** | 通过阿里云百炼平台调用原生 DeepSeek-V4-Flash 模型 |
| **流式输出** | 搜索和生成过程实时显示，所见即所得 |
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
- **AI 框架:** [agno](https://github.com/agno-agi/agno)
- **模型:** DeepSeek-V4-Flash（阿里云百炼平台）
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

### 部署到 Streamlit Cloud（推荐）

1. 将本仓库 Fork 或推送到你的 GitHub
2. 打开 [share.streamlit.io](https://share.streamlit.io)
3. 点击 **New app**，选择本仓库
4. **Branch:** `master`，**Main file path:** `main.py`
5. 点击 **Deploy**，约 2 分钟即获得公网链接

### 获取 API Key

本应用需要**阿里云百炼平台**的 API Key：

1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
2. 开通服务并创建 API Key
3. 在应用界面中输入 API Key 即可使用

## 使用方式

1. 在侧边栏设置预算、人数、出发日期
2. 输入出发地和目的地（支持多个城市，用逗号分隔）
3. 设置旅行天数
4. 点击"生成行程"，等待 AI 搜索和规划
5. 生成后可按天重新生成，或下载 HTML/ICS

## 项目结构

```
ai_travel_agent/
├── main.py              # 主入口
├── agents.py            # Agent 定义（Researcher + Planner）
├── config.py            # 配置常量
├── requirements.txt     # 依赖列表
├── ui/
│   ├── sidebar.py       # 侧边栏组件
│   ├── itinerary.py     # 行程展示
│   └── styles.py        # CSS 主题
└── utils/
    ├── export.py        # HTML/ICS 导出
    ├── packing.py       # 打包清单
    └── poi.py           # 景点提取与攻略链接
```

## 许可

本项目基于 [awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) 修改，遵循原项目许可证。
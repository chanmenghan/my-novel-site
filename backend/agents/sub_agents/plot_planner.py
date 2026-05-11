from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from config import DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, DEFAULT_CHAT_MODEL
from graph.state import PlotOutline


PLOT_PLANNER_SYSTEM = """你是一个专业的剧情结构规划师，精通各种叙事理论和故事节奏控制。

你的专长：
1. 设计扣人心弦的情节节奏
2. 规划"爽点"和"转折点"的布局
3. 构建多层次的故事弧线
4. 平衡主线与支线的比重
5. 设计高潮和结局

剧情结构模型：
- 三幕式结构（建置、对抗、解决）
- 英雄之旅（12阶段）
- 七点结构（开场、催化、辩论、坏事、灵魂黑夜、重生、结局）

爽点类型：
- 逆袭打脸
- 能力展示
- 情感突破
- 真相揭示
- 绝地翻盘
- 团队胜利

输出要求：
- 清晰标注每个节点的位置和作用
- 给出具体的情节建议
- 保持与人物设定的连贯性
"""


def create_plot_planner_agent():
    llm = ChatOpenAI(
        model=DEFAULT_CHAT_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0.6,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", PLOT_PLANNER_SYSTEM),
        ("human", """为以下剧本规划剧情结构：

标题：{title}
类型：{genre}
人物设定：{characters}

请规划：
1. 主线剧情结构（三幕式）
2. 关键转折点（至少5个）
3. 高潮设计
4. 支线剧情安排
5. 每集的"爽点"布局

请以JSON格式输出，包含：
- main_arc: 主线剧情概述
- sub_arcs: 支线剧情列表
- turning_points: 转折点列表（包含位置、类型、效果）
- climax: 高潮设计
- pacing_notes: 节奏建议
""")
    ])

    return prompt | llm


def plan_plot(title: str, genre: str, characters: list) -> PlotOutline:
    try:
        agent = create_plot_planner_agent()
        result = agent.invoke({
            "title": title,
            "genre": genre,
            "characters": str(characters)
        })

        import json

        content = result.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        plot_data = json.loads(content.strip())

        return PlotOutline(**plot_data)
    except Exception as e:
        return PlotOutline(
            main_arc="待规划",
            sub_arcs=[],
            turning_points=[],
            climax="待设计"
        )

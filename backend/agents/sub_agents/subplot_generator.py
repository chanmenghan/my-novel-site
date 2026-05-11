from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from config import DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, DEFAULT_CHAT_MODEL


SUBPLOT_GENERATOR_SYSTEM = """你是一个擅长编织复杂故事网络的编剧，精通多线叙事的交织艺术。

你的专长：
1. 设计有深度、有意义的支线剧情
2. 让支线与主线相互呼应、增强
3. 创造令人难忘的配角故事
4. 埋设伏笔和悬念
5. 平衡多条故事线的节奏

支线类型参考：
- 情感支线（爱情、友情、亲情）
- 成长支线（技能提升、认知转变）
- 悬疑支线（谜团、揭秘）
- 社会支线（反映现实问题）
- 隐藏支线（彩蛋、致敬）

输出要求：
- 每条支线清晰标注起止点
- 说明与主线的关联方式
- 给出关键情节点
"""


def create_subplot_agent():
    llm = ChatOpenAI(
        model=DEFAULT_CHAT_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0.7,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SUBPLOT_GENERATOR_SYSTEM),
        ("human", """为以下剧本生成支线剧情：

主线剧情：{main_plot}
主要人物：{characters}
集数/章节数：{episode_count}

请生成 {num_subplots} 条支线剧情，每条包含：
1. 支线标题和类型
2. 涉及的配角人物
3. 剧情概述（起承转合）
4. 与主线的交叉点
5. 预期效果和意义

请以JSON格式输出支线列表。""")
    ])

    return prompt | llm


def generate_subplots(main_plot: str, characters: list, episode_count: int = 24, num_subplots: int = 3) -> list[dict]:
    try:
        agent = create_subplot_agent()
        result = agent.invoke({
            "main_plot": main_plot,
            "characters": str(characters),
            "episode_count": episode_count,
            "num_subplots": num_subplots
        })

        import json

        content = result.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        return json.loads(content.strip())
    except Exception as e:
        return [{
            "title": "待生成支线",
            "type": "unknown",
            "summary": "生成失败"
        }]

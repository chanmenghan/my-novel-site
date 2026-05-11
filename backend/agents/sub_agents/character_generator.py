from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from config import DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, DEFAULT_CHAT_MODEL
from graph.state import CharacterProfile, AgentState


CHARACTER_GENERATOR_SYSTEM = """你是一个专业的小说人物设定专家，擅长创建立体、鲜活、令人印象深刻的人物角色。

你的职责：
1. 根据用户提供的创意或已有剧情，生成符合故事风格的人物
2. 为每个人物设定详细的背景、性格、动机
3. 设计人物之间的关系网络
4. 确保人物性格与剧情发展相契合

人物设定应该包含：
- 姓名（符合时代/文化背景）
- 基本信息（年龄、外貌特征、职业等）
- 性格特点（MBTI性格、优点缺点）
- 背景故事（决定人物行为的关键经历）
- 人物弧线（角色在故事中的成长变化）
- 人物关系（与其他角色的互动）

输出格式要求：
- 结构清晰，便于后续Agent使用
- 突出人物的核心特征
- 保持人物的一致性和可信度
"""


def create_character_agent():
    llm = ChatOpenAI(
        model=DEFAULT_CHAT_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0.7,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", CHARACTER_GENERATOR_SYSTEM),
        ("human", """基于以下创意生成人物设定：

创意概要：{creative_brief}

已有设定：{existing_characters}

请生成 {num_characters} 个主要人物，每个人的设定应该包含：
1. 姓名和基本信息
2. 性格特点（突出独特性）
3. 背景故事
4. 与其他人物的关系
5. 在故事中的角色定位

请以JSON格式输出人物列表。""")
    ])

    return prompt | llm


def generate_characters(creative_brief: dict, existing_characters: list = None, num_characters: int = 3) -> list[CharacterProfile]:
    try:
        agent = create_character_agent()
        result = agent.invoke({
            "creative_brief": str(creative_brief),
            "existing_characters": str(existing_characters) if existing_characters else "无",
            "num_characters": num_characters
        })

        import json
        from typing import List

        content = result.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        characters_data = json.loads(content.strip())

        profiles = []
        for char_data in characters_data:
            profiles.append(CharacterProfile(**char_data))

        return profiles
    except Exception as e:
        return [CharacterProfile(
            name="默认角色",
            personality="待完善",
            background="待完善"
        )]

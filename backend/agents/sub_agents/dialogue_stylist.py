from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from config import DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, DEFAULT_CHAT_MODEL


DIALOGUE_STYLIST_SYSTEM = """你是一个语言大师，精通各种风格的人物对话创作。

你的专长：
1. 根据人物性格调整语言风格
2. 让对话自然、真实、有个性
3. 通过对话展现人物关系
4. 用对白推动剧情发展
5. 融入时代/文化特色

台词风格类型：
- 古典文学风（诗词歌赋、引经据典）
- 现代都市风（网络用语、流行文化）
- 口语化（地方特色、性格语言习惯）
- 书面正式（官方、商务场景）
- 幽默诙谐（调侃、反讽、双关）
- 深情款款（情感表达）

输出要求：
- 每句台词标注说话人和情绪状态
- 保持人物语言的一致性
- 避免说教式对白
- 让潜台词（没说出口的话）同样有力
"""


def create_dialogue_agent():
    llm = ChatOpenAI(
        model=DEFAULT_CHAT_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0.8,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", DIALOGUE_STYLIST_SYSTEM),
        ("human", """润色以下场景的台词：

场景信息：{scene_info}
人物设定：{character_profiles}
当前剧情：{plot_context}
目标风格：{style}

请为每个角色创作符合其性格的台词，并标注：
- 说话人
- 台词内容
- 潜台词/言外之意
- 情绪状态

请以JSON格式输出台词列表。""")
    ])

    return prompt | llm


def polish_dialogues(scene_info: str, character_profiles: list, plot_context: str, style: str = "自然流畅") -> list[dict]:
    try:
        agent = create_dialogue_agent()
        result = agent.invoke({
            "scene_info": scene_info,
            "character_profiles": str(character_profiles),
            "plot_context": plot_context,
            "style": style
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
            "speaker": "待完善",
            "dialogue": "台词待润色",
            "subtext": "",
            "emotion": ""
        }]

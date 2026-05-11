from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from config import DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, DEFAULT_CHAT_MODEL
from graph.state import EvaluationResult


QUALITY_REVIEWER_SYSTEM = """你是一个严格而专业的剧本质量评审专家，拥有多年影视剧本审稿经验。

你的评审标准：
1. 故事完整性（结构是否完整、有头有尾）
2. 人物塑造（是否立体、真实、可信）
3. 情节逻辑（是否合理、连贯）
4. 情感共鸣（能否打动观众）
5. 节奏把控（是否张弛有度）
6. 对话质量（是否自然、有个性）
7. 创新性（是否有独特之处）
8. 市场潜力（是否符合观众需求）

评分体系：
- 0-3分：较差，需要大幅修改
- 4-6分：合格，有改进空间
- 7-8分：优秀，有minor问题
- 9-10分：卓越，可直接采用

输出要求：
- 给出具体分数和理由
- 列出主要优点和不足
- 提供可执行的修改建议
"""


def create_quality_reviewer_agent():
    llm = ChatOpenAI(
        model=DEFAULT_CHAT_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0.3,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", QUALITY_REVIEWER_SYSTEM),
        ("human", """请评审以下剧本/剧情内容：

类型：{content_type}
内容：{content}

评审维度：
1. 故事结构（20%）
2. 人物塑造（20%）
3. 情节设计（20%）
4. 对话质量（15%）
5. 节奏控制（15%）
6. 创新性（10%）

请以JSON格式输出，包含：
- score: 总分(0-10)
- strengths: 优点列表
- weaknesses: 不足列表
- suggestions: 修改建议
""")
    ])

    return prompt | llm


def evaluate_content(content: str, content_type: str = "剧本") -> EvaluationResult:
    try:
        agent = create_quality_reviewer_agent()
        result = agent.invoke({
            "content_type": content_type,
            "content": content
        })

        import json

        content_text = result.content
        if "```json" in content_text:
            content_text = content_text.split("```json")[1].split("```")[0]
        elif "```" in content_text:
            content_text = content_text.split("```")[1].split("```")[0]

        eval_data = json.loads(content_text.strip())

        return EvaluationResult(**eval_data)
    except Exception as e:
        return EvaluationResult(
            score=5.0,
            strengths=["评估系统异常"],
            weaknesses=["无法完成评估"],
            suggestions=["请稍后重试"]
        )

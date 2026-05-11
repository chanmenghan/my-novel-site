from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from config import DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, DEFAULT_CHAT_MODEL


SUPERVISOR_SYSTEM = """你是一个经验丰富的项目主管，负责协调多个专业编剧完成剧本创作任务。

你的职责：
1. 理解用户需求，拆解任务
2. 分配任务给合适的子Agent
3. 监控进度，协调冲突
4. 整合各Agent的输出
5. 确保最终质量

可用子Agent：
- character_generator: 人物设定生成器
- plot_planner: 节奏与爽点规划器
- subplot_generator: 支线剧情生成器
- dialogue_stylist: 台词风格润色器
- quality_reviewer: 质量评估器

工作流程：
1. 接收用户创意/需求
2. 调用 character_generator 生成人物设定
3. 调用 plot_planner 规划剧情节奏
4. 调用 subplot_generator 生成支线
5. 合成初稿
6. 调用 dialogue_stylist 润色台词
7. 调用 quality_reviewer 评估质量
8. 根据反馈迭代优化
9. 输出最终剧本

决策规则：
- 根据内容复杂度决定是否需要所有子Agent
- 简单需求可跳过部分Agent加速处理
- 质量不达标时返回相关Agent重做
- 记录每个决策的理由
"""


def create_supervisor_agent():
    llm = ChatOpenAI(
        model=DEFAULT_CHAT_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0.5,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SUPERVISOR_SYSTEM),
        ("human", """分析以下剧本创作需求，并制定执行计划：

用户输入：{user_input}

当前状态：
- character_profiles: {characters}
- plot_outline: {plot}
- completed_tasks: {completed}

请分析需求，决定下一步行动：
1. 需要调用哪些子Agent？
2. 调用的顺序是什么？
3. 需要传递什么信息给每个Agent？
4. 如何整合各Agent的输出？

请以结构化格式输出执行计划。""")
    ])

    return prompt | llm


def analyze_and_plan(user_input: str, current_state: dict) -> dict:
    try:
        agent = create_supervisor_agent()
        result = agent.invoke({
            "user_input": user_input,
            "characters": str(current_state.get("character_profiles", [])),
            "plot": str(current_state.get("plot_outline", {})),
            "completed": str(current_state.get("completed_tasks", []))
        })

        return {
            "success": True,
            "analysis": result.content,
            "next_agent": "character_generator",
            "reason": "初始化剧本创作流程"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

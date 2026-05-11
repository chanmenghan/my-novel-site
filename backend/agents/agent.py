"""简单Agent实现 - 直接使用OpenAI API调用"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from config import DEEPSEEK_API_KEY, DEFAULT_CHAT_MODEL


def get_llm():
    """获取LLM实例"""
    return ChatOpenAI(
        model=DEFAULT_CHAT_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
        temperature=0.7,
    )


def create_agent(tools: List[Any], system_prompt: str):
    """创建Agent - 简单实现"""

    def agent_executor(input_data: dict) -> dict:
        user_input = input_data.get("input", "")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]

        llm = get_llm()
        response = llm.invoke(messages)

        return {"output": response.content}

    return agent_executor


_writing_agent = None


def get_writing_agent() -> Any:
    """获取写作Agent单例"""
    global _writing_agent
    if _writing_agent is None:
        from agents.tools import get_writing_tools
        from agents.prompts import WRITING_ASSISTANT_SYSTEM_PROMPT

        tools = get_writing_tools()
        _writing_agent = create_agent(tools, WRITING_ASSISTANT_SYSTEM_PROMPT)
    return _writing_agent


def invoke_writing_agent(
    agent_executor: Any,
    user_input: str,
    user_id: Optional[int] = None,
    chat_history: Optional[list] = None,
) -> str:
    """调用写作Agent"""
    try:
        result = agent_executor({"input": user_input})
        return result["output"]
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"抱歉，处理您的请求时出错了：{str(e)}"

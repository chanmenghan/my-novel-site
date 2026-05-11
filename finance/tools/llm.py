"""LLM工具函数"""
from langchain_openai import ChatOpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEFAULT_CHAT_MODEL


def get_llm(temperature: float = 0.7):
    """获取LLM实例"""
    return ChatOpenAI(
        model=DEFAULT_CHAT_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=temperature,
    )


def extract_json_text(text: str) -> str:
    """从AI响应中提取JSON字符串"""
    content = text.strip()
    if "```json" in content:
        parts = content.split("```json")
        if len(parts) > 1:
            content = parts[1].split("```")[0]
    elif "```" in content:
        parts = content.split("```")
        if len(parts) > 1:
            content = parts[1].split("```")[0]
    return content.strip()

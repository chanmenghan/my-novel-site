"""MCP RAG 服务器 - 提供剧本知识库检索工具"""
import json
from fastmcp import FastMCP
from mcp_tools.rag_server import rag_knowledge_base

mcp = FastMCP("Screenplay-RAG-Server")


@mcp.tool()
def retrieve_screenplay_knowledge(query: str, top_k: int = 5) -> str:
    """从剧本知识库中检索相关信息。

    Args:
        query: 检索查询语句，如"重生复仇剧本结构"、"都市重生人物设定"
        top_k: 返回结果的数量，默认为5

    Returns:
        包含检索结果的JSON字符串
    """
    try:
        results = rag_knowledge_base.retrieve(query, top_k)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def retrieve_character_knowledge(query: str, top_k: int = 3) -> str:
    """从人物设定库中检索相关信息。

    Args:
        query: 检索查询语句，如"都市重生人物性格"、"复仇者设定"
        top_k: 返回结果的数量，默认为3

    Returns:
        包含检索结果的JSON字符串
    """
    try:
        results = rag_knowledge_base.retrieve(
            query, top_k, collection_name="character_kb"
        )
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def retrieve_dialogue_knowledge(query: str, top_k: int = 3) -> str:
    """从台词风格库中检索相关信息。

    Args:
        query: 检索查询语句，如"霸气台词风格"、"复仇对话"
        top_k: 返回结果的数量，默认为3

    Returns:
        包含检索结果的JSON字符串
    """
    try:
        results = rag_knowledge_base.retrieve(
            query, top_k, collection_name="dialogue_kb"
        )
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def retrieve_template_knowledge(query: str, top_k: int = 3) -> str:
    """从剧本模板库中检索相关信息。

    Args:
        query: 检索查询语句，如"系统流模板"、"短剧剧本格式"
        top_k: 返回结果的数量，默认为3

    Returns:
        包含检索结果的JSON字符串
    """
    try:
        results = rag_knowledge_base.retrieve(
            query, top_k, collection_name="template_kb"
        )
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def get_knowledge_base_stats() -> str:
    """获取知识库统计信息。

    Returns:
        包含知识库状态的JSON字符串
    """
    try:
        stats = {
            "status": "active",
            "knowledge_base": "ChromaDB",
            "embedding_model": "text-embedding-v3",
            "collections": ["screenplay_kb", "character_kb", "dialogue_kb", "template_kb"]
        }
        return json.dumps(stats, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")

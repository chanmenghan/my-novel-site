import json
import asyncio
from typing import Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server
from rag_server import get_rag_tools, rag_knowledge_base


server = Server("screenplay-rag-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    tools = get_rag_tools()

    return [
        Tool(
            name=tool.name,
            description=tool.description,
            inputSchema={
                "type": "object",
                "properties": {
                    p.name: {"type": "string", "description": p.description}
                    for p in tool.args
                },
                "required": [p.name for p in tool.args if p.required]
            }
        )
        for tool in tools
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    tools = {tool.name: tool for tool in get_rag_tools()}

    if name not in tools:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    tool = tools[name]

    try:
        result = tool.invoke(arguments)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

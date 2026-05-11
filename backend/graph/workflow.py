"""LangGraph 工作流 - 基于 MCP RAG 工具的剧本生成"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from typing import Optional, Any, List, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from config import DEEPSEEK_API_KEY, DEFAULT_CHAT_MODEL, REDIS_URL
from graph.state import AgentState, CharacterProfile, PlotOutline
import json

MCP_AVAILABLE = False
print("[DEBUG] 使用直接调用 RAG 模式（MCP 初始化有问题，暂时禁用）")

checkpointer = MemorySaver()

print(f"[DEBUG] Checkpointer 已初始化（内存存储）")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from skills.skill_library import skill_library


def get_llm(temperature: float = 0.7):
    """获取LLM实例"""
    return ChatOpenAI(
        model=DEFAULT_CHAT_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
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


def get_skill_context(skill_ids: List[str] = None, genre: str = None) -> str:
    """获取技能库上下文"""
    if not skill_ids and not genre:
        return ""

    context_parts = ["\n\n=== 技能库参考 ===\n"]

    if skill_ids:
        for sid in skill_ids:
            skill = skill_library.get_skill(sid)
            if skill:
                context_parts.append(f"【{skill.name}】\n{skill.description}\n")

    if genre:
        skills = skill_library.list_skills(genre)
        for s in skills[:2]:
            context_parts.append(f"【{s.name}】\n{s.description}\n")

    return "".join(context_parts)


mcp_agent = None
mcp_tools = []


async def init_mcp_tools_async():
    """异步初始化 MCP 工具（供 FastAPI 启动时调用）"""
    global mcp_agent, mcp_tools

    if not MCP_AVAILABLE:
        return

    try:
        mcp_server_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "mcp_tools", "mcp_rag_server.py"
        )

        if not os.path.exists(mcp_server_path):
            print(f"[WARN] MCP 服务器文件不存在: {mcp_server_path}")
            return

        client = MultiServerMCPClient(
            {
                "screenplay_rag": {
                    "command": "python",
                    "args": [mcp_server_path],
                    "transport": "stdio",
                }
            }
        )

        mcp_tools = await client.get_tools()
        print(f"[DEBUG] MCP 工具加载成功: {len(mcp_tools)} 个工具")

        llm = get_llm(0.7)
        mcp_agent = create_react_agent(llm, mcp_tools)
        print("[DEBUG] MCP Agent 初始化成功")

    except Exception as e:
        print(f"[WARN] MCP 工具初始化失败: {e}")
        mcp_agent = None
        mcp_tools = []


def run_mcp_retrieve(query: str, top_k: int = 5) -> str:
    """通过 MCP Agent 执行检索"""
    if not mcp_agent:
        return json.dumps({"error": "MCP Agent 未初始化", "results": []})

    try:
        result = mcp_agent.invoke({
            "messages": [HumanMessage(content=f"请使用 retrieve_screenplay_knowledge 工具查询：{query}")]
        })

        messages = result.get("messages", [])
        if messages:
            last_msg = messages[-1]
            if hasattr(last_msg, "content"):
                return last_msg.content

        return json.dumps({"results": []})
    except Exception as e:
        return json.dumps({"error": str(e), "results": []})


def rag_retrieve_node(state: AgentState) -> AgentState:
    """节点1：RAG 检索"""
    global mcp_agent, mcp_tools

    print("\n[DEBUG] ===== rag_retrieve 开始 =====")

    creative_brief = state.get("creative_brief", {})
    enable_rag = creative_brief.get("enable_rag", True)

    if not enable_rag:
        print("[DEBUG] RAG 已禁用，跳过检索")
        return {**state, "metadata": {**state.get("metadata", {}), "rag_used": False}}

    metadata = state.get("metadata", {})
    genre = creative_brief.get("genre", "都市")
    description = creative_brief.get("description", "")

    query = f"{genre} {description}"
    skill_context = get_skill_context(genre=genre)

    knowledge_context = ""

    if MCP_AVAILABLE and mcp_tools:
        try:
            print(f"[DEBUG] 通过 MCP 工具检索，查询: {query}")
            rag_result = run_mcp_retrieve(query, top_k=5)
            rag_data = json.loads(rag_result)

            if "results" in rag_data:
                docs = rag_data["results"]
                if docs:
                    knowledge_context = "\n\n=== 知识库参考 ===\n"
                    for doc in docs[:3]:
                        content = doc.get("content", "")[:500]
                        knowledge_context += f"- {content}\n"
                    print(f"[DEBUG] MCP 检索到 {len(docs)} 条结果")
        except Exception as e:
            print(f"[WARN] MCP 检索失败: {e}")
            knowledge_context = ""
    else:
        try:
            from mcp_tools.rag_server import rag_knowledge_base
            print(f"[DEBUG] 使用直接调用 RAG，查询: {query}")
            results = rag_knowledge_base.retrieve(query, top_k=5)
            if results and "results" in results:
                docs = results["results"]
                if docs:
                    knowledge_context = "\n\n=== 知识库参考 ===\n"
                    for doc in docs[:3]:
                        content = doc.get("content", "")[:500]
                        knowledge_context += f"- {content}\n"
                    print(f"[DEBUG] 直接调用 RAG 检索到 {len(docs)} 条结果")
        except Exception as e:
            print(f"[WARN] 直接 RAG 调用失败: {e}")
            knowledge_context = ""

    metadata["knowledge_context"] = knowledge_context
    metadata["skill_context"] = skill_context
    metadata["rag_used"] = bool(knowledge_context)

    print(f"[DEBUG] ===== rag_retrieve 结束 =====\n")
    return {**state, "metadata": metadata}


def skip_rag_node(state: AgentState) -> AgentState:
    """节点1b：跳过 RAG"""
    print("[DEBUG] ===== skip_rag（跳过RAG）=====")
    metadata = state.get("metadata", {})
    metadata["rag_used"] = False
    metadata["knowledge_context"] = ""
    metadata["skill_context"] = get_skill_context(genre=state.get("creative_brief", {}).get("genre"))
    return {**state, "metadata": metadata}


def generate_characters(state: AgentState) -> AgentState:
    """节点2：生成人物设定（使用 MCP RAG + Skill 增强）"""
    print("\n[DEBUG] ===== generate_characters 开始 =====")

    try:
        llm = get_llm(0.7)
        creative_brief = state["creative_brief"]
        metadata = state.get("metadata", {})

        genre = creative_brief.get("genre", "都市")
        description = creative_brief.get("description", "")

        knowledge_context = metadata.get("knowledge_context", "")
        skill_context = metadata.get("skill_context", "")

        prompt = f"""根据以下创意概要，生成3-5个主要人物设定。

{knowledge_context}

{skill_context}

类型：{genre}
创意概要：{description}

请为每个主要人物设定：
1. 姓名（符合类型风格，体现人物特色）
2. 年龄、性别、外貌特征
3. 性格特点（结合类型套路）
4. 背景故事（利用知识库中的经典设定进行创新）
5. 与其他人物的关系
6. 在剧情中的作用定位

请用JSON数组格式输出每个人物，不要用其他格式。直接输出JSON数组，不要其他文字。"""

        print(f"[DEBUG] generate_characters: 发送请求到 DeepSeek...")
        response = llm.invoke([HumanMessage(content=prompt)])
        raw_response = response.content

        json_text = extract_json_text(raw_response)

        try:
            characters_data = json.loads(json_text)
            if isinstance(characters_data, dict):
                characters_data = characters_data.get("characters", [characters_data])
            if not isinstance(characters_data, list):
                characters_data = [characters_data]

            characters = []
            for char_data in characters_data:
                if isinstance(char_data, dict):
                    rel = char_data.get("relationships", {})
                    if isinstance(rel, str):
                        try:
                            rel = json.loads(rel)
                        except:
                            rel = {"关系": rel}

                    name = char_data.get("name") or char_data.get("姓名") or "未知"
                    age = char_data.get("age") or char_data.get("年龄")
                    if age and isinstance(age, str):
                        try:
                            age = int(age)
                        except:
                            age = None
                    personality = char_data.get("personality") or char_data.get("性格特点") or char_data.get("性格") or ""
                    background = char_data.get("background") or char_data.get("背景故事") or char_data.get("背景") or ""

                    char = CharacterProfile(
                        name=name,
                        age=age,
                        personality=personality,
                        background=background,
                        relationships=rel
                    )
                    characters.append(char)

            print(f"[DEBUG] 生成人物数量: {len(characters)}")
            print("[DEBUG] ===== generate_characters 结束 =====\n")

            return {"character_profiles": characters}

        except json.JSONDecodeError as e:
            print(f"[WARN] JSON 解析失败: {e}")
            return {"character_profiles": []}

    except Exception as e:
        print(f"[ERROR] generate_characters 出错: {e}")
        import traceback
        traceback.print_exc()
        return {"character_profiles": []}


def plan_plot(state: AgentState) -> AgentState:
    """节点3：规划剧情大纲"""
    print("\n[DEBUG] ===== plan_plot 开始 =====")

    try:
        llm = get_llm(0.7)
        creative_brief = state["creative_brief"]
        metadata = state.get("metadata", {})
        characters = state["character_profiles"]

        genre = creative_brief.get("genre", "都市")
        title = creative_brief.get("title", "")

        knowledge_context = metadata.get("knowledge_context", "")
        skill_context = metadata.get("skill_context", "")

        char_names = [c.name for c in characters] if characters else "待定"

        prompt = f"""为以下小说规划专业级剧情大纲。

{knowledge_context}

{skill_context}

标题：{title}
类型：{genre}
主要人物：{', '.join(char_names)}

请规划：
1. 主线剧情（起承转合）
2. 支线剧情（辅助主线）
3. 关键转折点（至少3个）
4. 高潮设计

请用JSON格式输出，包含 main_arc, sub_arcs, turning_points, climax 字段。"""

        print(f"[DEBUG] plan_plot: 发送请求...")
        response = llm.invoke([HumanMessage(content=prompt)])
        raw_response = response.content

        json_text = extract_json_text(raw_response)

        try:
            plot_data = json.loads(json_text)

            def dict_to_str(d):
                if isinstance(d, dict):
                    return ", ".join([f"{k}: {v}" for k, v in d.items()])
                return str(d)

            main_arc = plot_data.get("main_arc", "")
            if isinstance(main_arc, dict):
                main_arc = dict_to_str(main_arc)

            sub_arcs = plot_data.get("sub_arcs", [])
            sub_arcs = [dict_to_str(a) if isinstance(a, dict) else a for a in sub_arcs]

            turning_points = plot_data.get("turning_points", [])
            if isinstance(turning_points, str):
                turning_points = [turning_points]
            turning_points = [dict_to_str(tp) if isinstance(tp, dict) else tp for tp in turning_points]

            climax = plot_data.get("climax", "")
            if isinstance(climax, dict):
                climax = dict_to_str(climax)

            plot_outline = PlotOutline(
                main_arc=main_arc,
                sub_arcs=sub_arcs,
                turning_points=turning_points,
                climax=climax
            )

            print(f"[DEBUG] 剧情大纲生成成功")
            print("[DEBUG] ===== plan_plot 结束 =====\n")

            return {"plot_outline": plot_outline}

        except json.JSONDecodeError as e:
            print(f"[WARN] JSON 解析失败: {e}")
            return {"plot_outline": None}

    except Exception as e:
        print(f"[ERROR] plan_plot 出错: {e}")
        import traceback
        traceback.print_exc()
        return {"plot_outline": None}


def generate_content(state: AgentState) -> AgentState:
    """节点4：生成剧本正文"""
    print("\n[DEBUG] ===== generate_content 开始 =====")

    try:
        llm = get_llm(0.9)
        creative_brief = state["creative_brief"]
        metadata = state.get("metadata", {})
        plot_outline = state["plot_outline"]

        title = creative_brief.get("title", "")
        genre = creative_brief.get("genre", "都市")
        description = creative_brief.get("description", "")

        knowledge_context = metadata.get("knowledge_context", "")
        skill_context = metadata.get("skill_context", "")

        turning_points = plot_outline.turning_points if plot_outline and plot_outline.turning_points else []

        prompt = f"""创作小说第一章正文。

{knowledge_context}

{skill_context}

标题：{title}
类型：{genre}
创意概要：{description}

剧情大纲：
主线：{plot_outline.main_arc if plot_outline and plot_outline.main_arc else '待定'}
转折点：{', '.join(turning_points) if turning_points else '待定'}

要求：
1. 开篇抓人眼球（黄金三章原则）
2. 迅速建立主角目标/困境
3. 埋下伏笔和钩子
4. 字数3000-5000字
5. 符合知识库中的成功套路

请直接输出正文，不要包含其他说明。"""

        print(f"[DEBUG] generate_content: 发送请求...")
        response = llm.invoke([HumanMessage(content=prompt)])
        raw_response = response.content

        print(f"[DEBUG] 正文长度: {len(raw_response)}")
        print(f"[DEBUG] 预览(前200字): {raw_response[:200]}...")
        print("[DEBUG] ===== generate_content 结束 =====\n")

        return {"screenplay_draft": raw_response}

    except Exception as e:
        print(f"[ERROR] generate_content 出错: {e}")
        import traceback
        traceback.print_exc()
        return {"screenplay_draft": ""}


def should_use_rag(state: AgentState) -> Literal["rag_retrieve", "skip_rag"]:
    """条件边：判断是否使用 RAG"""
    creative_brief = state.get("creative_brief", {})
    enable_rag = creative_brief.get("enable_rag", True)

    if enable_rag and mcp_tools:
        return "rag_retrieve"
    return "skip_rag"


def should_generate_content(state: AgentState) -> Literal["generate_content", "end"]:
    """条件边：判断是否生成正文"""
    if state.get("plot_outline") is None:
        print("[WARN] 没有剧情大纲，跳过正文生成")
        return "end"
    return "generate_content"


def create_screenplay_graph():
    """创建 LangGraph 工作流（集成 MCP RAG + Skill）"""

    workflow = StateGraph(AgentState)

    workflow.add_node("rag_retrieve", rag_retrieve_node)
    workflow.add_node("skip_rag", skip_rag_node)
    workflow.add_node("generate_characters", generate_characters)
    workflow.add_node("plan_plot", plan_plot)
    workflow.add_node("generate_content", generate_content)

    workflow.set_entry_point("rag_retrieve")

    workflow.add_conditional_edges(
        "rag_retrieve",
        should_use_rag,
        {
            "rag_retrieve": "generate_characters",
            "skip_rag": "skip_rag"
        }
    )

    workflow.add_edge("skip_rag", "generate_characters")
    workflow.add_edge("generate_characters", "plan_plot")

    workflow.add_conditional_edges(
        "plan_plot",
        should_generate_content,
        {
            "generate_content": "generate_content",
            "end": END
        }
    )

    workflow.add_edge("generate_content", END)

    return workflow.compile(checkpointer=checkpointer)


screenplay_graph = create_screenplay_graph()


def create_screenplay_workflow():
    """兼容旧接口，返回可调用的工作流"""
    return screenplay_graph


def screenplay_workflow(initial_state: AgentState, thread_id: str = None) -> AgentState:
    """执行工作流

    Args:
        initial_state: 初始状态
        thread_id: 会话ID，用于持久化记忆
    """
    print("\n" + "=" * 60)
    print("[DEBUG] ===== screenplay_workflow 开始 =====")
    print("=" * 60)

    creative_brief = initial_state.get("creative_brief", {})
    print(f"[DEBUG] 标题: {creative_brief.get('title', 'N/A')}")
    print(f"[DEBUG] 类型: {creative_brief.get('genre', 'N/A')}")
    print(f"[DEBUG] RAG启用: {creative_brief.get('enable_rag', True)}")
    print(f"[DEBUG] Thread ID: {thread_id or '无（使用内存存储）'}")
    print(f"[DEBUG] MCP 工具数量: {len(mcp_tools)}")

    try:
        import uuid
        thread_id = thread_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        result = screenplay_graph.invoke(initial_state, config=config)

        characters = result.get("character_profiles", [])
        plot = result.get("plot_outline")
        draft = result.get("screenplay_draft", "")
        metadata = result.get("metadata", {})

        print(f"[DEBUG] 生成人物数量: {len(characters)}")
        print(f"[DEBUG] 剧情规划完成: {plot is not None}")
        print(f"[DEBUG] 正文字数: {len(draft) if draft else 0}")
        print(f"[DEBUG] 使用RAG: {metadata.get('rag_used', False)}")

        result["quality_score"] = 0.85

        print("=" * 60)
        print("[DEBUG] ===== screenplay_workflow 完成 =====")
        print("=" * 60 + "\n")

        return result

    except Exception as e:
        print(f"[ERROR] screenplay_workflow 出错: {e}")
        import traceback
        traceback.print_exc()
        raise

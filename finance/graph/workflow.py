"""金融投资研究助手工作流"""
import json
import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import AgentState, StockQuery, ResearchReport
from tools.llm import get_llm, extract_json_text


class FinanceWorkflow:
    """金融工作流"""

    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self):
        """构建工作流图"""
        workflow = StateGraph(AgentState)

        workflow.add_node("route_query", self.route_query_node)
        workflow.add_node("rag_retrieve", self.rag_retrieve_node)
        workflow.add_node("stock_query", self.stock_query_node)
        workflow.add_node("research_summary", self.research_summary_node)
        workflow.add_node("knowledge_qa", self.knowledge_qa_node)

        workflow.set_entry_point("route_query")

        workflow.add_conditional_edges(
            "route_query",
            self.route_by_intent,
            {
                "stock": "stock_query",
                "research": "research_summary",
                "knowledge": "rag_retrieve",
                "general": "knowledge_qa"
            }
        )

        workflow.add_conditional_edges(
            "stock_query",
            self.route_stock_query_result,
            {
                "success": END,
                "rag_fallback": "knowledge_qa"
            }
        )
        workflow.add_edge("research_summary", END)
        workflow.add_edge("rag_retrieve", "knowledge_qa")
        workflow.add_edge("knowledge_qa", END)

        checkpointer = MemorySaver()
        return workflow.compile(checkpointer=checkpointer)

    def route_query_node(self, state: AgentState) -> AgentState:
        """路由节点"""
        print("\n[DEBUG] ===== route_query 开始 =====")

        user_input = state.get("user_input", "")
        print(f"[DEBUG] 用户输入: {user_input[:50]}...")

        return {**state}

    def route_by_intent(self, state: AgentState) -> str:
        """根据意图路由"""
        user_input = state.get("user_input", "").lower()

        if any(kw in user_input for kw in ["股价", "股票", "市值", "财报", "季度", "pe", "市盈率"]):
            return "stock"
        elif any(kw in user_input for kw in ["研报", "报告", "分析", "评级", "目标价"]):
            return "research"
        elif any(kw in user_input for kw in ["知识库", "检索", "查找", "请简述", "概念"]):
            return "knowledge"
        else:
            return "general"

    def route_stock_query_result(self, state: AgentState) -> str:
        """根据股票查询结果路由"""
        metadata = state.get("metadata", {})
        if metadata.get("rag_fallback"):
            return "rag_fallback"
        return "success"

    def rag_retrieve_node(self, state: AgentState) -> AgentState:
        """RAG检索节点"""
        print("\n[DEBUG] ===== rag_retrieve 开始 =====")

        try:
            from knowledge_base.rag_server import rag_knowledge_base

            user_input = state.get("user_input", "")
            results = rag_knowledge_base.retrieve(user_input, top_k=5)

            knowledge_context = ""
            if results.get("results"):
                knowledge_context = "\n\n=== 知识库参考 ===\n"
                for doc in results["results"][:3]:
                    content = doc.get("content", "")[:500]
                    knowledge_context += f"- {content}\n"

            print(f"[DEBUG] RAG检索到 {len(results.get('results', []))} 条结果")

            metadata = state.get("metadata", {})
            metadata["knowledge_context"] = knowledge_context

            return {**state, "metadata": metadata}
        except Exception as e:
            print(f"[ERROR] RAG检索失败: {e}")
            return state

    def stock_query_node(self, state: AgentState) -> AgentState:
        """股票查询节点"""
        print("\n[DEBUG] ===== stock_query 开始 =====")

        user_input = state.get("user_input", "")

        try:
            from knowledge_base.rag_server import akshare_fetcher
            from knowledge_base.rag_server import rag_knowledge_base

            symbol_prompt = f"""从以下文本中提取股票代码或名称：
            {user_input}
            只输出股票代码或名称，不要其他内容。"""

            llm = get_llm(0.3)
            response = llm.invoke([HumanMessage(content=symbol_prompt)])
            symbol = response.content.strip()

            import akshare as ak
            from requests.exceptions import ConnectionError, ReadTimeout
            import time

            max_retries = 3
            df = None

            for attempt in range(max_retries):
                try:
                    print(f"[DEBUG] 尝试获取股票数据 (尝试 {attempt + 1}/{max_retries})...")
                    df = ak.stock_zh_a_spot_em()
                    break
                except (ConnectionError, ReadTimeout) as e:
                    print(f"[WARN] 第 {attempt + 1} 次尝试失败: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                    continue

            stock_data = None
            if df is not None:
                stock_data = df[df['代码'] == symbol]
                if stock_data.empty:
                    stock_data = df[df['名称'].str.contains(symbol, na=False)]

            if stock_data is not None and not stock_data.empty:
                row = stock_data.iloc[0]
                stock_info = {
                    "股票代码": row.get('代码', 'N/A'),
                    "股票名称": row.get('名称', 'N/A'),
                    "最新价": row.get('最新价', 'N/A'),
                    "涨跌幅": row.get('涨跌幅', 'N/A'),
                    "涨跌额": row.get('涨跌额', 'N/A'),
                    "成交量": row.get('成交量', 'N/A'),
                    "成交额": row.get('成交额', 'N/A'),
                    "最高": row.get('最高', 'N/A'),
                    "最低": row.get('最低', 'N/A'),
                    "今开": row.get('今开', 'N/A'),
                    "昨收": row.get('昨收', 'N/A'),
                    "市盈率": row.get('市盈率-动态', 'N/A'),
                }

                stock_query = StockQuery(symbol=stock_info["股票代码"], query_type="realtime")
                metadata = state.get("metadata", {})
                metadata["stock_query_result"] = stock_info

                print(f"[DEBUG] 股票查询成功: {stock_info['股票名称']} {stock_info['最新价']}")

                return {**state, "stock_query": stock_query, "metadata": metadata}
            else:
                print(f"[WARN] AKShare实时数据获取失败，降级到RAG知识库检索...")
                rag_results = rag_knowledge_base.retrieve(user_input, top_k=5)
                knowledge_context = ""
                if rag_results.get("results"):
                    knowledge_context = "\n\n=== 知识库参考 ===\n"
                    for doc in rag_results["results"][:3]:
                        content = doc.get("content", "")[:800]
                        knowledge_context += f"- {content}\n"

                metadata = state.get("metadata", {})
                metadata["stock_query_result"] = {"symbol": symbol, "source": "RAG知识库"}
                metadata["knowledge_context"] = knowledge_context
                metadata["rag_fallback"] = True

                print(f"[DEBUG] RAG检索到 {len(rag_results.get('results', []))} 条结果")

                return {**state, "metadata": metadata}

        except Exception as e:
            print(f"[ERROR] 股票查询失败: {e}")
            metadata = state.get("metadata", {})
            metadata["stock_query_result"] = {"error": str(e)}
            return state

    def research_summary_node(self, state: AgentState) -> AgentState:
        """研报摘要节点"""
        print("\n[DEBUG] ===== research_summary 开始 =====")

        user_input = state.get("user_input", "")
        knowledge_context = state.get("metadata", {}).get("knowledge_context", "")

        prompt = f"""你是一个专业的金融投研分析师。请根据以下信息生成研报摘要。

用户需求: {user_input}

知识库参考:
{knowledge_context}

请生成结构化的研报摘要，包含:
1. 核心观点（3-5条）
2. 财务数据变化
3. 评级变动（如有）
4. 简明中文摘要

请用JSON格式输出，包含 title, author, date, target_price, rating, key_points, financial_changes, summary_cn 字段。"""

        try:
            llm = get_llm(0.7)
            response = llm.invoke([HumanMessage(content=prompt)])
            json_text = extract_json_text(response.content)
            report_data = json.loads(json_text)

            research_report = ResearchReport(**report_data)

            metadata = state.get("metadata", {})
            metadata["research_generated"] = True

            return {**state, "research_report": research_report, "metadata": metadata}
        except Exception as e:
            print(f"[ERROR] 研报摘要生成失败: {e}")
            return state

    def knowledge_qa_node(self, state: AgentState) -> AgentState:
        """知识问答节点"""
        print("\n[DEBUG] ===== knowledge_qa 开始 =====")

        user_input = state.get("user_input", "")
        knowledge_context = state.get("metadata", {}).get("knowledge_context", "")

        prompt = f"""你是一个专业的金融投资研究助手。请根据以下知识库内容回答用户问题。

用户问题: {user_input}

知识库参考:
{knowledge_context}

请给出专业、准确的回答。如果知识库中没有相关信息，请基于你的金融知识回答。"""

        try:
            llm = get_llm(0.7)
            response = llm.invoke([HumanMessage(content=prompt)])
            answer = response.content

            messages = state.get("messages", [])
            messages.append({
                "role": "assistant",
                "content": answer,
                "type": "knowledge_qa"
            })

            metadata = state.get("metadata", {})
            metadata["answer"] = answer

            return {**state, "messages": messages, "metadata": metadata}
        except Exception as e:
            print(f"[ERROR] 知识问答失败: {e}")
            return state

    def invoke(self, input_data: Dict[str, Any], thread_id: str = None) -> Dict[str, Any]:
        """执行工作流"""
        print("\n" + "=" * 60)
        print("[DEBUG] ===== Finance Workflow 开始 =====")
        print("=" * 60)

        try:
            if thread_id:
                config = {"configurable": {"thread_id": thread_id}}
                result = self.graph.invoke(input_data, config=config)
            else:
                result = self.graph.invoke(input_data)

            print(f"[DEBUG] ===== Finance Workflow 完成 =====\n")
            return result
        except Exception as e:
            print(f"[ERROR] Finance Workflow 出错: {e}")
            import traceback
            traceback.print_exc()
            raise


finance_workflow = FinanceWorkflow()

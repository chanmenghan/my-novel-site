"""金融投资研究助手状态定义"""
from typing import TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StockQuery(BaseModel):
    """股票查询"""
    symbol: str = Field(description="股票代码，如 AAPL, TSLA")
    query_type: str = Field(description="查询类型：price, financial, news, analysis")
    time_range: Optional[str] = Field(default="latest", description="时间范围")


class ResearchReport(BaseModel):
    """研报摘要"""
    title: str = Field(description="研报标题")
    author: str = Field(description="作者/机构")
    date: str = Field(description="发布日期")
    target_price: Optional[str] = Field(default=None, description="目标价")
    rating: Optional[str] = Field(default=None, description="评级")
    key_points: List[str] = Field(description="核心观点")
    financial_changes: Dict[str, Any] = Field(description="财务数据变化")
    summary_cn: str = Field(description="中文摘要")


class KnowledgeBaseResult(BaseModel):
    """知识库检索结果"""
    source: str = Field(description="来源：research_report, theory, stock_data")
    content: str = Field(description="内容")
    relevance_score: float = Field(description="相关度分数")


class AgentState(TypedDict):
    """LangGraph 状态"""
    user_input: str = Field(default="", description="用户输入")

    stock_query: Optional[StockQuery] = Field(default=None, description="股票查询")

    research_report: Optional[ResearchReport] = Field(default=None, description="研报摘要")

    knowledge_context: str = Field(default="", description="RAG检索的知识上下文")

    messages: List[Dict] = Field(default_factory=list, description="对话历史")

    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    quality_score: float = Field(default=0.0, description="质量分数")

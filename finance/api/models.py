"""API数据模型"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(description="用户查询内容")
    thread_id: Optional[str] = Field(default=None, description="对话线程ID")
    type: str = Field(default="general", description="查询类型：general, stock, research, knowledge")


class QueryResponse(BaseModel):
    """查询响应"""
    answer: Optional[str] = Field(default=None, description="回答内容")
    stock_query: Optional[Dict[str, Any]] = Field(default=None, description="股票查询结果")
    research_report: Optional[Dict[str, Any]] = Field(default=None, description="研报摘要")
    knowledge_used: bool = Field(default=False, description="是否使用了知识库")
    quality_score: float = Field(default=0.0, description="质量分数")


class IngestRequest(BaseModel):
    """文档摄入请求"""
    file_path: str = Field(description="文件路径")
    collection: str = Field(default="finance_kb", description="集合名称")


class IngestResponse(BaseModel):
    """文档摄入响应"""
    success: bool
    message: str
    chunks: Optional[int] = None

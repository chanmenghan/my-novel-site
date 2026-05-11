"""API路由"""
from fastapi import APIRouter, HTTPException
from api.models import QueryRequest, QueryResponse, IngestRequest, IngestResponse
from graph.workflow import finance_workflow

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """处理用户查询"""
    try:
        import uuid
        input_data = {"user_input": request.query}

        if request.type == "stock":
            input_data["user_input"] = f"【股票查询】{request.query}"
        elif request.type == "research":
            input_data["user_input"] = f"【研报解读】{request.query}"
        elif request.type == "knowledge":
            input_data["user_input"] = f"【知识检索】{request.query}"

        thread_id = request.thread_id or str(uuid.uuid4())

        result = finance_workflow.invoke(
            input_data,
            thread_id=thread_id
        )

        metadata = result.get("metadata", {})

        research_report = None
        if result.get("research_report"):
            research_report = result.get("research_report").model_dump()
            research_report = {
                "title": getattr(result.get("research_report"), 'title', ''),
                "rating": getattr(result.get("research_report"), 'rating', ''),
                "target_price": getattr(result.get("research_report"), 'target_price', ''),
                "summary_cn": getattr(result.get("research_report"), 'summary_cn', ''),
                "key_points": getattr(result.get("research_report"), 'key_points', []),
            }

        stock_query_result = metadata.get("stock_query_result")
        stock_query_response = None
        if stock_query_result:
            if isinstance(stock_query_result, dict) and "error" not in stock_query_result:
                stock_query_response = stock_query_result
            else:
                stock_query_response = {"symbol": "N/A", "error": "查询失败"}

        response = QueryResponse(
            answer=metadata.get("answer"),
            stock_query=stock_query_response,
            research_report=research_report,
            knowledge_used=bool(metadata.get("knowledge_context")),
            quality_score=metadata.get("quality_score", 0.8)
        )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    """摄入文档到知识库"""
    try:
        from knowledge_base.rag_server import rag_knowledge_base

        result = rag_knowledge_base.ingest_document(request.file_path, request.collection)

        if result.get("success"):
            return IngestResponse(
                success=True,
                message="文档摄入成功",
                chunks=result.get("chunks")
            )
        else:
            return IngestResponse(
                success=False,
                message=f"文档摄入失败: {result.get('error')}"
            )
    except Exception as e:
        return IngestResponse(success=False, message=str(e))


@router.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "service": "finance-agent"}

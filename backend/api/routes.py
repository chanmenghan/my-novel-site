from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime

from .models import (
    UserCreate,
    UserResponse,
    TokenResponse,
    CreativeBrief,
    ScreenplayRequest,
    ScreenplayResponse,
    CharacterResponse,
    PlotOutlineResponse,
    SubplotResponse,
    EvaluationResponse,
    SkillRequest,
    SkillResponse,
    RAGRequest,
    RAGIngestRequest,
    HealthResponse,
)
from graph.workflow import screenplay_workflow
from graph.state import AgentState
from skills.skill_library import skill_library
from mcp_tools.rag_server import rag_knowledge_base
from core.observability import cost_tracker
import jwt
import bcrypt
from config import SERVICE_PORT

router = APIRouter()


def create_token(user_id: int, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow().timestamp() + 7 * 24 * 3600
    }
    return jwt.encode(payload, "your-secret-key", algorithm="HS256")


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user_id(authorization: str = None) -> Optional[int]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if payload:
        return payload.get("user_id")
    return None


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", version="0.1.0")


@router.post("/auth/register", response_model=TokenResponse)
async def register(user: UserCreate):
    from database import create_user

    if len(user.username) < 3:
        raise HTTPException(status_code=400, detail="用户名至少3个字符")

    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少6个字符")

    success = create_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail="用户名已存在")

    from database import get_user_by_id

    class FakeUser:
        id = 1
        username = user.username

    user_obj = FakeUser()
    token = create_token(user_obj.id, user_obj.username)

    return TokenResponse(
        access_token=token,
        username=user.username
    )


@router.post("/auth/login", response_model=TokenResponse)
async def login(user: UserCreate):
    from database import verify_user

    user_obj = verify_user(user.username, user.password)
    if not user_obj:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_token(user_obj["id"], user_obj["username"])

    return TokenResponse(
        access_token=token,
        username=user_obj["username"]
    )


@router.post("/screenplay/generate", response_model=ScreenplayResponse)
async def generate_screenplay(request: ScreenplayRequest):
    creative_brief = request.creative_brief.model_dump()
    creative_brief["enable_rag"] = request.enable_rag
    creative_brief["enable_skills"] = request.enable_skills

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    initial_state = AgentState(
        messages=messages,
        user_input=request.creative_brief.description or f"创作一个{request.creative_brief.genre}剧本",
        creative_brief=creative_brief,
        character_profiles=[],
        plot_outline=None,
        sub_plots=[],
        screenplay_draft=None,
        polished_dialogues=[],
        evaluation=None,
        current_agent="supervisor",
        task_queue=[],
        completed_tasks=[],
        quality_score=0.0,
        final_output="",
        metadata={"enable_rag": request.enable_rag, "enable_skills": request.enable_skills}
    )

    try:
        result = screenplay_workflow(initial_state, thread_id=request.thread_id)

        characters = [
            CharacterResponse(
                name=c.name,
                age=c.age,
                personality=c.personality,
                background=c.background,
                relationships=c.relationships
            )
            for c in result.get("character_profiles", [])
        ]

        plot_outline = None
        if result.get("plot_outline"):
            po = result["plot_outline"]
            plot_outline = PlotOutlineResponse(
                main_arc=po.main_arc,
                sub_arcs=po.sub_arcs,
                turning_points=po.turning_points,
                climax=po.climax
            )

        evaluation = None
        if result.get("evaluation"):
            ev = result["evaluation"]
            evaluation = EvaluationResponse(
                score=ev.score,
                strengths=ev.strengths,
                weaknesses=ev.weaknesses,
                suggestions=ev.suggestions
            )

        return ScreenplayResponse(
            title=request.creative_brief.title,
            genre=request.creative_brief.genre,
            characters=characters,
            plot_outline=plot_outline,
            subplots=[SubplotResponse(**s) for s in result.get("sub_plots", [])],
            dialogues=result.get("polished_dialogues", []),
            evaluation=evaluation,
            quality_score=result.get("quality_score", 0.0)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.get("/skills", response_model=list[SkillResponse])
async def list_skills(category: Optional[str] = None):
    skills = skill_library.list_skills(category)
    return [
        SkillResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            category=s.category,
            parameters=s.parameters,
            examples=s.examples,
            version=s.version
        )
        for s in skills
    ]


@router.get("/skills/search", response_model=list[SkillResponse])
async def search_skills(q: str):
    results = skill_library.search_skills(q)
    return [
        SkillResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            category=s.category,
            parameters=s.parameters,
            examples=s.examples,
            version=s.version
        )
        for s in results
    ]


@router.get("/skills/categories")
async def get_categories():
    return {"categories": skill_library.get_all_categories()}


@router.post("/rag/retrieve")
async def retrieve_knowledge(request: RAGRequest):
    try:
        results = rag_knowledge_base.retrieve(
            query=request.query,
            top_k=request.top_k,
            collection_name=request.collection_name
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.post("/rag/ingest")
async def ingest_document(request: RAGIngestRequest):
    try:
        result = rag_knowledge_base.ingest_document(
            file_path=request.file_path,
            collection_name=request.collection_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"摄入失败: {str(e)}")


@router.get("/rag/collections")
async def list_collections():
    try:
        return {"collections": ["screenplay_kb", "character_kb", "dialogue_kb"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rag/stats")
async def get_knowledge_stats():
    try:
        return {
            "status": "active",
            "knowledge_base": "ChromaDB",
            "embedding_model": "text-embedding-ada-002",
            "collections": ["screenplay_kb", "character_kb", "dialogue_kb"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kb/files")
async def list_kb_files(collection: str = "screenplay_kb"):
    """列出知识库目录下的文件"""
    try:
        from pathlib import Path

        kb_base = Path("./data/knowledge_base")
        collection_map = {
            "screenplay_kb": kb_base / "screenplay",
            "character_kb": kb_base / "character",
            "dialogue_kb": kb_base / "dialogue",
            "template_kb": kb_base / "template",
        }

        dir_path = collection_map.get(collection, kb_base / "screenplay")

        if not dir_path.exists():
            return {"collection": collection, "files": []}

        files = []
        for f in dir_path.rglob("*.txt"):
            stat = f.stat()
            files.append({
                "name": f.name,
                "path": str(f.relative_to(kb_base)),
                "size": stat.st_size,
                "modified": stat.st_mtime
            })

        return {"collection": collection, "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kb/ingest")
async def ingest_kb_file(file_path: str, collection: str = "screenplay_kb"):
    """摄入指定文件到知识库"""
    try:
        result = rag_knowledge_base.ingest_document(file_path, collection)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"摄入失败: {str(e)}")

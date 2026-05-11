from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    password: str


class UserCreate(UserBase):
    pass


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class CreativeBrief(BaseModel):
    title: str = Field(..., description="剧本标题")
    genre: str = Field(default="都市", description="剧本类型")
    setting: str = Field(default="现代都市", description="故事背景")
    style: str = Field(default="爽文", description="写作风格")
    episodes: int = Field(default=24, description="集数")
    num_characters: int = Field(default=3, description="主要人物数量")
    description: Optional[str] = Field(None, description="创意描述")


class Message(BaseModel):
    role: str = Field(default="user", description="角色: user/assistant/system")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[datetime] = Field(None)


class ScreenplayRequest(BaseModel):
    creative_brief: CreativeBrief
    user_id: Optional[int] = Field(None, description="用户ID，可选")
    enable_rag: bool = Field(default=True, description="是否启用RAG知识库")
    enable_skills: bool = Field(default=True, description="是否启用技能库")
    messages: list[Message] = Field(default_factory=list, description="对话历史消息")
    thread_id: Optional[str] = Field(None, description="会话ID，用于LangGraph Redis持久化")


class CharacterResponse(BaseModel):
    name: str
    age: Optional[int] = None
    personality: str
    background: str
    relationships: dict = {}


class PlotOutlineResponse(BaseModel):
    main_arc: str
    sub_arcs: list[str] = []
    turning_points: list[str] = []
    climax: str


class SubplotResponse(BaseModel):
    title: str
    type: str
    summary: str
    characters: list[str] = []
    connection_points: list[str] = []


class DialogueResponse(BaseModel):
    speaker: str
    dialogue: str
    subtext: str = ""
    emotion: str = ""


class EvaluationResponse(BaseModel):
    score: float
    strengths: list[str] = []
    weaknesses: list[str] = []
    suggestions: list[str] = []


class ScreenplayResponse(BaseModel):
    title: str
    genre: str
    characters: list[CharacterResponse] = []
    plot_outline: Optional[PlotOutlineResponse] = None
    subplots: list[SubplotResponse] = []
    dialogues: list[DialogueResponse] = []
    evaluation: Optional[EvaluationResponse] = None
    quality_score: float = 0.0


class SkillRequest(BaseModel):
    skill_id: Optional[str] = None
    category: Optional[str] = None
    search_query: Optional[str] = None


class SkillResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    parameters: dict = {}
    examples: list[str] = []
    version: str = "1.0"


class RAGRequest(BaseModel):
    query: str = Field(..., description="检索查询")
    top_k: int = Field(default=5, description="返回结果数量")
    collection_name: str = Field(default="screenplay_kb", description="知识库集合名称")


class RAGIngestRequest(BaseModel):
    file_path: str = Field(..., description="文档路径")
    collection_name: str = Field(default="screenplay_kb", description="知识库集合名称")


class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"
    timestamp: datetime = Field(default_factory=datetime.now)

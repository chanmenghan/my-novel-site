"""LangGraph 状态定义"""
from typing import TypedDict, Optional, Any, List
from pydantic import BaseModel, Field

# 描述剧本中一个角色的核心属性
class CharacterProfile(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    personality: str = ""
    background: str = ""
    relationships: dict = Field(default_factory=dict)

# 承载剧本的情节大纲结构
class PlotOutline(BaseModel):
    main_arc: str = ""
    sub_arcs: list[str] = Field(default_factory=list)
    turning_points: list[str] = Field(default_factory=list)
    climax: str = ""

# 表示单个场景的完整内容
class SceneContent(BaseModel):
    scene_id: str = ""
    location: str = ""
    time: str = ""
    characters: list[str] = Field(default_factory=list)
    content: str = ""
    dialogues: list[dict] = Field(default_factory=list)

# 聚合剧本草稿的全部组成部分
class ScreenplayDraft(BaseModel):
    title: str = ""
    genre: str = ""
    setting: str = ""
    characters: list[CharacterProfile] = Field(default_factory=list)
    plot_outline: Optional[PlotOutline] = None
    scenes: list[SceneContent] = Field(default_factory=list)
    dialogue_style: str = "自然流畅"

# 存储剧本质量评估的输出
class EvaluationResult(BaseModel):
    score: float = Field(default=0.0, ge=0, le=10)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class AgentState(TypedDict):
    """工作流状态定义"""
    messages: List[Any]
    user_input: str
    creative_brief: dict
    character_profiles: List[CharacterProfile]
    plot_outline: Optional[PlotOutline]
    sub_plots: List[dict]
    screenplay_draft: str
    polished_dialogues: List[dict]
    evaluation: Optional[EvaluationResult]
    current_agent: str
    task_queue: List[str]
    completed_tasks: List[str]
    quality_score: float
    final_output: str
    metadata: dict

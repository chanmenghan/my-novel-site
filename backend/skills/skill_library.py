from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
import json


class Skill(BaseModel):
    id: str
    name: str
    description: str
    category: str
    prompt_template: str
    parameters: dict = Field(default_factory=dict)
    examples: list[str] = Field(default_factory=list)
    version: str = "1.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True


class SkillLibrary:
    def __init__(self):
        self.skills: dict[str, Skill] = {}

        self._register_default_skills()

    def _register_default_skills(self):
        default_skills = [
            Skill(
                id="skill_resurrection_revenge",
                name="重生复仇模板",
                description="适用于重生复仇类剧本的开局设定和复仇节奏把控",
                category="template",
                prompt_template="""你是一个重生复仇类剧本创作专家。

核心要素：
1. 开局冤死设定 - 让主角以最惨烈的方式领盒饭
2. 重生回溯点 - 选择情绪张力最强的时间点
3. 信息差利用 - 前世记忆成为最大金手指
4. 复仇节奏 - 小高潮不断，大高潮爆燃

节奏模板：
- 第1阶段：回溯觉醒（1-3集）
- 第2阶段：布局蓄势（4-8集）
- 第3阶段：首次反击（9-12集）
- 第4阶段：矛盾激化（13-18集）
- 第5阶段：终极对决（19-24集）

请根据用户设定创作符合此模板的剧本。""",
                parameters={
                    "death_way": "死亡方式",
                    "rebirth_point": "重生时间点",
                    "revenge_targets": "复仇对象"
                },
                examples=["医毒双绝重生复仇", "首富重生追妻火葬场"]
            ),
            Skill(
                id="skill_system_stream",
                name="系统流模板",
                description="适用于系统流剧本的任务系统和能力成长设计",
                category="template",
                prompt_template="""你是一个系统流剧本创作专家。

核心要素：
1. 系统设定 - 独特新颖的系统机制
2. 任务系统 - 驱动剧情发展的核心动力
3. 属性面板 - 让读者有代入感的数值系统
4. 副本挑战 - 提供爽感的战斗场景

系统类型：
- 医术系统/签到系统/选择系统/攻略系统
- 每种系统对应不同的爽点节奏

成长节奏：
- 新手期：10章内首胜
- 成长期：每50章一个台阶
- 巅峰期：跨级挑战+越杀越多

请根据用户设定创作符合此模板的剧本。""",
                parameters={
                    "system_type": "系统类型",
                    "main_growth_line": "成长主线"
                },
                examples=["神医系统", "末日签到系统"]
            ),
            Skill(
                id="skill_romance_multi",
                name="恋爱多选一模板",
                description="适用于攻略类恋爱剧本的多线平衡和选择机制",
                category="template",
                prompt_template="""你是一个恋爱攻略剧本创作专家。

核心要素：
1. 多攻略对象 - 人设各有特色，避免同质化
2. 平等机会 - 每条线都有独立发展空间
3. 暧昧互动 - 制造心跳的甜蜜场景
4. 选择机制 - 玩家投票决定最终CP

人设平衡原则：
- 性格互补（如：冰山vs暖男/活泼vs内敛）
- 身份对等（避免某条线明显弱势）
- 独立剧情线（不依附主线）

甜宠要素：
- 英雄救美（经典但有效）
- 日常互怼（欢喜冤家）
- 隐藏守护（暖心细节）
- 身份反差（表面冷漠内心火热）

请根据用户设定创作符合此模板的剧本。""",
                parameters={
                    "genre": "类型（现代/古言/奇幻）",
                    "num_candidates": "攻略对象数量"
                },
                examples=["现代霸总多选一", "古言皇子们争宠"]
            ),
            Skill(
                id="skill_rhythm_analysis",
                name="节奏分析",
                description="分析剧本节奏，提出爽点布局和节奏优化建议",
                category="analysis",
                prompt_template="""分析以下剧本内容的节奏：

{content}

请从以下维度进行分析：
1. 开局抓人程度（黄金三章是否达标）
2. 章节末尾钩子设置
3. 高潮分布密度
4. 节奏张弛是否有度
5. 伏笔埋设与回收

输出改进建议。""",
                parameters={
                    "content": "待分析剧本内容"
                },
                examples=[]
            ),
            Skill(
                id="skill_dialogue_conversion",
                name="台词风格转换",
                description="将台词转换为不同风格（古风/现代/口语化等）",
                category="conversion",
                prompt_template="""将以下台词转换为{style}风格：

原文：
{dialogue}

角色设定：
{character_profile}

要求：
1. 保持原意
2. 符合目标风格
3. 体现角色性格
4. 自然流畅

请输出转换后的台词。""",
                parameters={
                    "dialogue": "原始台词",
                    "style": "目标风格",
                    "character_profile": "角色设定"
                },
                examples=["古风台词转现代", "现代台词转古言"]
            ),
            Skill(
                id="skill_user_feedback_retrieval",
                name="用户反馈检索",
                description="根据读者反馈关键词检索相似剧本参考",
                category="retrieval",
                prompt_template="""根据以下反馈检索相关剧本参考：

反馈关键词：{keywords}

请分析：
1. 读者喜欢什么（爽点/情节/人物）
2. 读者讨厌什么（毒点/雷区）
3. 市场趋势
4. 改进建议

反馈来源：
{feedback_content}""",
                parameters={
                    "keywords": "反馈关键词",
                    "feedback_content": "反馈内容原文"
                },
                examples=[]
            ),
        ]

        for skill in default_skills:
            self.skills[skill.id] = skill

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        return self.skills.get(skill_id)

    def list_skills(self, category: Optional[str] = None) -> list[Skill]:
        if category:
            return [s for s in self.skills.values() if s.category == category and s.is_active]
        return [s for s in self.skills.values() if s.is_active]

    def search_skills(self, query: str) -> list[Skill]:
        results = []
        query_lower = query.lower()
        for skill in self.skills.values():
            if (query_lower in skill.name.lower() or
                query_lower in skill.description.lower() or
                query_lower in skill.category.lower()):
                results.append(skill)
        return results

    def add_skill(self, skill: Skill) -> bool:
        if skill.id in self.skills:
            return False
        self.skills[skill.id] = skill
        return True

    def update_skill(self, skill_id: str, updates: dict) -> bool:
        if skill_id not in self.skills:
            return False
        skill = self.skills[skill_id]
        for key, value in updates.items():
            if hasattr(skill, key):
                setattr(skill, key, value)
        skill.updated_at = datetime.now()
        return True

    def delete_skill(self, skill_id: str) -> bool:
        if skill_id not in self.skills:
            return False
        self.skills[skill_id].is_active = False
        return True

    def get_all_categories(self) -> list[str]:
        return list(set(s.category for s in self.skills.values() if s.is_active))


skill_library = SkillLibrary()

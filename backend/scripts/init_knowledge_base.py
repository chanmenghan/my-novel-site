"""知识库初始化和管理脚本"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from config import CHROMA_PERSIST_DIR


def ensure_kb_dirs():
    """确保知识库目录存在"""
    kb_base = Path("./data/knowledge_base")
    dirs = {
        "screenplay": kb_base / "screenplay",
        "character": kb_base / "character",
        "dialogue": kb_base / "dialogue",
        "template": kb_base / "template",
    }

    for name, path in dirs.items():
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 目录已就绪: {path}")

    return dirs


def create_sample_files(kb_dirs: dict):
    """创建示例知识库文件"""
    screenplay_dir = kb_dirs["screenplay"]
    character_dir = kb_dirs["character"]
    dialogue_dir = kb_dirs["dialogue"]
    template_dir = kb_dirs["template"]

    resurrection_sample = """
# 重生复仇类剧本结构分析

## 经典开局模式

### 1. 冤死开局
- 主角前世被陷害，死状凄惨
- 临死前留下强烈执念或金手指
- 典型场景：被未婚妻背叛、被家族除名、被合作伙伴坑害

### 2. 重生回溯点选择
- 大学时代（青春成长型）
- 婚礼前夜（婚恋逆袭型）
- 关键抉择前（事业逆转型）
- 死亡前一刻（直接重生型）

## 复仇节奏模板

### 第一阶段：觉醒期（1-3集）
- 发现重生事实
- 确认时间线
- 初步规划

### 第二阶段：布局期（4-8集）
- 收集情报
- 拉拢盟友
- 设下陷阱

### 第三阶段：反击期（9-16集）
- 小目标达成
- 媒体曝光
- 法律手段

### 第四阶段：终局（17-24集）
- 终极对决
- 翻盘胜利
- 完美收官

## 人物关系模板

### 复仇对象
- 表面身份：未婚妻/丈夫、商业伙伴、亲戚
- 隐藏身份：幕后黑手、真正凶手
- 弱点：贪婪、好色、嫉妒、傲慢

### 金手指类型
- 前世记忆
- 医术/毒术
- 商业头脑
- 人脉网络

## 经典台词模板

1. "这一世，我不会再任人宰割。"
2. "你们欠我的，我会一笔一笔讨回来。"
3. "看着吧，这只是开始。"
"""

    system_stream_sample = """
# 系统流剧本结构

## 系统类型分类

### 1. 签到系统
- 每日签到获取奖励
- 连续签到加成
- 特殊日子多倍奖励

### 2. 任务系统
- 主线任务：推动剧情
- 支线任务：获取资源
- 隐藏任务：惊喜奖励

### 3. 选择系统
- 关键剧情选择
- 不同路线分支
- 选择影响属性

### 4. 攻略系统
- 可攻略对象
- 好感度机制
- 专属剧情线

## 属性面板设计

```
宿主：[姓名]
等级：Lv.1
经验值：0/100

体质：10
力量：10
智力：10
魅力：10
运气：10

[已解锁技能]
1. 基础拳法
2. 快速恢复
```

## 副本设计原则

### 副本类型
- 新手副本（1-10章）：教学为主
- 精英副本（11-30章）：资源获取
- 世界副本（31章+）：推动主线

### 副本结构
1. 副本入口
2. 关卡挑战
3. BOSS战
4. 通关奖励
5. 结算评价

## 升级节奏

- 10章内：首胜建立信心
- 30章内：首次危机
- 50章内：第一次死亡威胁
- 100章：巅峰对决
"""

    character_sample = """
# 人物设定库 - 都市重生类

## 经典人物模板

### 医圣重生
- 姓名：顾长安
- 职业：天才医生/医学教授
- 性格：沉稳冷静、心思缜密、重情重义
- 前世：被徒弟背叛、陷害入狱、惨死狱中
- 金手指：绝世医术、毒术、前世记忆
- 目标：复仇、传承中医、守护家人

### 兵王回归
- 姓名：叶修
- 职业：特种兵王/战神
- 性格：铁血柔情、护短、不服就干
- 前世：为国捐躯、战友牺牲
- 金手指：战斗技能、体能极限、军事素养
- 目标：守护家人、找出内鬼、替战友复仇

### 金融巨鳄
- 姓名：沈墨
- 职业：投资天才/金融教父
- 性格：精于算计、儒雅外表、狠辣内心
- 前世：被家族除名、破产流浪
- 金手指：未来记忆、商业头脑、人脉网络
- 目标：夺回一切、登顶巅峰、护短

## 女性角色模板

### 白月光
- 身份：青梅竹马/初恋
- 性格：温柔善良、坚强独立
- 作用：情感寄托、精神支柱
- 特点：始终相信主角

### 黑莲花
- 身份：竞争对手/合作伙伴
- 性格：聪明果断、心机深沉
- 作用：推动剧情、势均力敌
- 特点：从对手到爱人
"""

    dialogue_sample = """
# 台词风格库

## 重生复仇风格

### 霸气型
- "这一世，我命由我，不由天！"
- "你们以为能踩我一辈子？可笑。"
- "欠债还钱，欠命...也得还！"

### 冷漠型
- "我只是回来收拾残局的。"
- "别急，好戏才刚开始。"
- "你们...还不够格让我亲自动手。"

### 腹黑型
- "谢谢你的'帮助'，我会好好报答的。"
- "啊，不小心说了实话，真是抱歉。"
- "做人嘛，最重要的是...开心。"

## 都市情感风格

### 甜宠型
- "遇到你之后，我才知道什么是心动。"
- "我只对你一个人好，够不够？"
- "你的笑容，是我最大的满足。"

### 虐心型
- "我可以放弃一切，唯独放不下你。"
- "如果这就是爱，我宁愿从未遇见你。"
- "你不知道，我有多想你。"

### 搞笑型
- "我这辈子最大的运气，就是遇见你。"
- "别说话，吻我。"
- "你负责可爱，我负责宠你。"
"""

    template_sample = """
# 剧本模板库

## 都市重生复仇模板

**类型**：都市重生 / 逆袭 / 复仇
**篇幅**：24集 x 3000字
**目标受众**：男性读者为主

**核心爽点**：
1. 信息差碾压（我知道你不知道的）
2. 打脸逆袭（你看不惯我又干不掉我）
3. 实力装逼（低调奢华有内涵）
4. 情感满足（美人环绕、兄弟同心）

**节奏公式**：
- 每3集一个小高潮
- 每6集一个转折点
- 每12集一个大事件
- 大结局必须爽

**开头模板**：
[主角死亡/濒死场景]
[意外重生]
[确认时间线]
[制定计划]
[第一步行动]

**结尾模板**：
[最终决战]
[反派落败]
[正义伸张]
[情感升华]
[展望未来]
"""

    files = [
        (screenplay_dir / "重生复仇类剧本结构.txt", resurrection_sample),
        (screenplay_dir / "系统流剧本结构.txt", system_stream_sample),
        (character_dir / "人物设定库_都市重生.txt", character_sample),
        (dialogue_dir / "台词风格库.txt", dialogue_sample),
        (template_dir / "剧本模板库.txt", template_sample),
    ]

    for file_path, content in files:
        if not file_path.exists():
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ 创建示例文件: {file_path}")
        else:
            print(f"⏭️  文件已存在: {file_path}")


def init_chroma():
    """初始化Chroma向量数据库"""
    from mcp_tools.rag_server import rag_knowledge_base

    print("\n📦 初始化Chroma向量数据库...")
    print(f"   存储路径: {CHROMA_PERSIST_DIR}")

    rag_knowledge_base.vectorstore = None
    print("✅ Chroma初始化完成")


def ingest_all_documents():
    """摄入所有知识库文档"""
    from mcp_tools.rag_server import rag_knowledge_base

    kb_base = Path("./data/knowledge_base")
    collections = {
        "screenplay_kb": kb_base / "screenplay",
        "character_kb": kb_base / "character",
        "dialogue_kb": kb_base / "dialogue",
        "template_kb": kb_base / "template",
    }

    print("\n📚 开始摄入文档到知识库...")

    for collection_name, dir_path in collections.items():
        if not dir_path.exists():
            continue

        txt_files = list(dir_path.glob("*.txt"))
        if not txt_files:
            print(f"   ⏭️  {collection_name}: 无文档")
            continue

        print(f"\n   📂 {collection_name}:")
        for txt_file in txt_files:
            try:
                print(f"      摄入: {txt_file.name}...", end=" ")
                result = rag_knowledge_base.ingest_document(
                    str(txt_file),
                    collection_name=collection_name
                )
                if result.get("success"):
                    print(f"✅ {result.get('chunk_count')} chunks")
                else:
                    print(f"❌ {result.get('message', '失败')}")
            except Exception as e:
                print(f"❌ 错误: {e}")


def show_status():
    """显示知识库状态"""
    from mcp_tools.rag_server import rag_knowledge_base

    print("\n📊 知识库状态:")
    print(f"   Chroma路径: {CHROMA_PERSIST_DIR}")
    print(f"   集合列表: screenplay_kb, character_kb, dialogue_kb, template_kb")


def main():
    print("=" * 50)
    print("🎬 剧本创作知识库初始化脚本")
    print("=" * 50)

    print("\n[1/4] 创建目录结构...")
    kb_dirs = ensure_kb_dirs()

    print("\n[2/4] 创建示例文件...")
    create_sample_files(kb_dirs)

    print("\n[3/4] 初始化向量数据库...")
    init_chroma()

    print("\n[4/4] 摄入文档到知识库...")
    ingest_all_documents()

    print("\n[完成] 知识库初始化完成！")
    show_status()

    print("\n📝 下一步:")
    print("   1. 将你的剧本/人物/台词文件放入 data/knowledge_base/ 对应目录")
    print("   2. 运行 python -m scripts.ingest_kb 重新摄入")
    print("   3. 启动后端 python run.py")


if __name__ == "__main__":
    main()

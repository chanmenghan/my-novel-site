#!/usr/bin/env python3
"""Generate a one-page Chinese resume PDF tailored to AI feed-ad video roles."""

from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
pdfmetrics.registerFont(TTFont("WQY", FONT_PATH))

PAGE_W, PAGE_H = A4
MARGIN_X = 16 * mm
HEADER_H = 34 * mm

INK = HexColor("#1F2328")
MUTED = HexColor("#5C6570")
LINE = HexColor("#D8DEE6")
ACCENT = HexColor("#C45C26")
HEADER_BG = HexColor("#1B2430")
CHIP_BG = HexColor("#F4EBE4")
RULE = HexColor("#C45C26")


def text_width(text: str, size: float) -> float:
    return pdfmetrics.stringWidth(text, "WQY", size)


PUNCT_KEEP = set("，。、；：！？,.!?;:）)」」』】…—-")


def wrap_text(text: str, size: float, max_w: float) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        trial = current + ch
        if text_width(trial, size) <= max_w:
            current = trial
            continue
        if current:
            lines.append(current)
        current = ch
    if current:
        lines.append(current)
    # Keep punctuation with the previous line instead of hanging at line start.
    cleaned: list[str] = []
    for line in lines:
        if cleaned and line and line[0] in PUNCT_KEEP:
            cleaned[-1] += line[0]
            line = line[1:]
        if line:
            cleaned.append(line)
    return cleaned


def draw_wrapped(c: canvas.Canvas, text: str, x: float, y: float, size: float, max_w: float, leading: float, color=INK) -> float:
    c.setFillColor(color)
    c.setFont("WQY", size)
    for line in wrap_text(text, size, max_w):
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_section_title(c: canvas.Canvas, title: str, y: float) -> float:
    c.setFillColor(ACCENT)
    c.rect(MARGIN_X, y + 1, 2.2 * mm, 4.2 * mm, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("WQY", 11.5)
    c.drawString(MARGIN_X + 4.2 * mm, y + 1.4, title)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    c.line(MARGIN_X, y - 2.2, PAGE_W - MARGIN_X, y - 2.2)
    return y - 8.2 * mm


def draw_bullet(c: canvas.Canvas, text: str, y: float, max_w: float) -> float:
    c.setFillColor(ACCENT)
    c.circle(MARGIN_X + 1.6 * mm, y + 1.5, 0.85 * mm, fill=1, stroke=0)
    return draw_wrapped(c, text, MARGIN_X + 5.2 * mm, y, 8.6, max_w - 5.2 * mm, 12.2, INK)


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    out_path = out_dir / "陈梦涵_AI信息流广告视频简历.pdf"
    c = canvas.Canvas(str(out_path), pagesize=A4)
    c.setTitle("陈梦涵 - AI信息流广告视频简历")
    c.setAuthor("陈梦涵")

    # Header
    c.setFillColor(HEADER_BG)
    c.rect(0, PAGE_H - HEADER_H, PAGE_W, HEADER_H, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(0, PAGE_H - HEADER_H, 3.2 * mm, HEADER_H, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("WQY", 22)
    c.drawString(MARGIN_X, PAGE_H - 15 * mm, "陈梦涵")
    c.setFont("WQY", 10)
    c.setFillColor(HexColor("#F0D2C0"))
    c.drawString(MARGIN_X, PAGE_H - 22.2 * mm, "AI信息流广告视频  ·  短剧编导  ·  Prompt / 角色资产管理")

    c.setFillColor(HexColor("#D5DCE6"))
    c.setFont("WQY", 8.4)
    c.drawString(MARGIN_X, PAGE_H - 28.6 * mm, "邮箱  chanmenghan@163.com     GitHub  github.com/chanmenghan     求职意向  一线电商品牌视频部 · AI信息流广告")

    y = PAGE_H - HEADER_H - 10 * mm
    content_w = PAGE_W - 2 * MARGIN_X

    y = draw_section_title(c, "专业摘要", y)
    summary = (
        "专注AI短剧工业化生产与信息流广告内容，能独立完成「创意策划 → 脚本分镜 → AI素材生成 → 后期成片 → 按反馈迭代」全流程。"
        "长期攻坚人物一致性、实拍质感、黄金3秒冲突钩子，并沉淀可复用的Prompt库与角色资产，服务电商投放向视频的稳定量产。"
    )
    y = draw_wrapped(c, summary, MARGIN_X, y, 8.8, content_w, 12.6, INK)
    y -= 5.5 * mm

    y = draw_section_title(c, "核心技能（对照岗位）", y)
    skills = [
        "AI工具：可灵、即梦、Runway、Midjourney、Image 2.5；多参考生视频、图生图、台词替换、产品替换。",
        "编导能力：独立写分镜脚本；懂镜头语言、构图、6秒节奏；熟悉黄金3秒、冲突升级、结尾钩子。",
        "工业化资产：Prompt模板库、角色/场景锁定、口型与对白控制；解决崩脸、串台、原声污染、抠图感。",
        "电商调性：高端产品质感（木纹/首饰盒）、人物剧情带货、信息流竖屏成片；能按反馈快速改提示词复投。",
    ]
    for item in skills:
        y = draw_bullet(c, item, y, content_w)
        y -= 2.4
    y -= 4.2 * mm

    y = draw_section_title(c, "相关经历", y)
    c.setFillColor(INK)
    c.setFont("WQY", 10)
    c.drawString(MARGIN_X, y, "AI信息流短剧 / 电商广告内容生产")
    c.setFillColor(MUTED)
    c.setFont("WQY", 8.4)
    c.drawRightString(PAGE_W - MARGIN_X, y, "2024 — 至今")
    y -= 12.4
    c.setFillColor(MUTED)
    c.setFont("WQY", 8.2)
    c.drawString(MARGIN_X, y, "全流程制作  ·  脚本分镜  ·  AI生成  ·  成片迭代")
    y -= 13.2

    jobs = [
        "独立完成信息流广告闭环：创意策划、分镜脚本、多参考AI生成、成片输出，并按观感/反馈连续改提示词。",
        "搭建人物+产品双资产生产线：机场当众决裂短剧（首饰盒冲突钩子）、高端首饰盒产品片、非洲实拍向/人物纪实向素材。",
        "黄金3秒冲突设计：第一帧即拉扯拦路、动作先于台词；后段抢话、围观、肢体升级，服务完播与停留。",
        "质感专项：去噪点、去油亮、哑光木纹+柔和掠光、现场光与接触阴影，让人物和产品更像手机实拍而非CG。",
        "角色一致性与台词控制：锁脸锁景锁服装；参考视频只借情绪不借原词，解决「念了原视频台词」等串台问题。",
        "沉淀标准化Prompt规范（实拍感 / 产品替换 / 一镜拼接 / 多参考生视频），便于团队复用和新人接手。",
    ]
    for item in jobs:
        y = draw_bullet(c, item, y, content_w)
        y -= 2.2
    y -= 4.8 * mm

    c.setFillColor(INK)
    c.setFont("WQY", 10)
    c.drawString(MARGIN_X, y, "AI剧本与角色资产系统")
    c.setFillColor(MUTED)
    c.setFont("WQY", 8.4)
    c.drawRightString(PAGE_W - MARGIN_X, y, "个人项目")
    y -= 12.4
    c.setFillColor(MUTED)
    c.setFont("WQY", 8.2)
    c.drawString(MARGIN_X, y, "github.com/chanmenghan/my-novel-site")
    y -= 13.2
    projects = [
        "建设角色设定库、台词风格库、剧本/分镜模板，把短剧编导能力沉淀成可复用工作流。",
        "覆盖都市冲突、对白节奏、人物关系，与信息流短剧的角色资产库、崩脸治理同一套方法。",
    ]
    for item in projects:
        y = draw_bullet(c, item, y, content_w)
        y -= 2.2
    y -= 5.2 * mm

    y = draw_section_title(c, "代表作品方向（可附成片）", y)
    works = [
        "6秒机场吵架信息流短剧：当众决裂 + 首饰盒消费冲突，台词替换、口型锁定、开头强冲突。",
        "森物社首饰盒高级广告：人物开场 → 产品环绕掠光 → 人物定格，淡入淡出转场，木纹质感可控。",
        "非洲实拍向 / 「林总在非洲」人物纪实向素材：阴天漫射光、接触阴影、去抠图感。",
        "产品替换专项：场景保留、商品替换、盒面哑光丝光（有木纹、不油亮、不脏颗粒）。",
    ]
    for item in works:
        y = draw_bullet(c, item, y, content_w)
        y -= 2.2
    y -= 5.2 * mm

    y = draw_section_title(c, "为什么匹配这个岗位", y)
    fit = [
        "岗位要的不是「会点AI」，而是能把创意做成可投放成片。我已经按这条产线在跑：脚本、分镜、提示词、生成、返修。",
        "熟悉信息流爆款逻辑，尤其黄金3秒和冲突设计；能根据「不像实拍 / 崩脸 / 台词不对 / 开头没钩子」快速迭代。",
        "正在把零散出片变成标准流程：Prompt库、角色资产、质感规范，方便带人和提效。",
    ]
    for item in fit:
        y = draw_bullet(c, item, y, content_w)
        y -= 2.2

    c.setFillColor(MUTED)
    c.setFont("WQY", 7.4)
    c.drawCentredString(PAGE_W / 2, 11 * mm, "电话 / 作品集链接可按实际补全    ·    一页纸针对性简历，投递时可替换公司名与数据指标")
    c.save()
    print(out_path)


if __name__ == "__main__":
    main()

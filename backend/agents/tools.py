from typing import Optional
from langchain_core.tools import tool
from database import (
    get_book_by_id,
    get_books_by_user,
    update_book_settings,
    add_chapter,
    update_chapter,
)
import json


@tool
def get_user_books_tool(user_id: int) -> str:
    """获取用户的所有书籍列表
    
    Args:
        user_id: 用户ID
    
    Returns:
        JSON格式的书籍列表，包含书籍ID、标题、风格、字数等信息
    """
    try:
        books = get_books_by_user(user_id)
        return json.dumps(books, ensure_ascii=False)
    except Exception as e:
        return f"获取书籍列表失败: {str(e)}"


@tool
def get_book_detail_tool(user_id: int, book_id: int) -> str:
    """获取指定书籍的详细信息，包括章节、设置等
    
    Args:
        user_id: 用户ID
        book_id: 书籍ID
    
    Returns:
        JSON格式的书籍详细信息
    """
    try:
        book = get_book_by_id(book_id, user_id)
        if book:
            return json.dumps(book, ensure_ascii=False)
        return "未找到该书籍"
    except Exception as e:
        return f"获取书籍详情失败: {str(e)}"


@tool
def update_book_settings_tool(user_id: int, book_id: int, settings_json: str) -> str:
    """更新书籍的设置（世界观、大纲、人物设定等）
    
    Args:
        user_id: 用户ID
        book_id: 书籍ID
        settings_json: JSON格式的设置字符串，包含 world, outline, character, inspiration 字段
    
    Returns:
        操作结果信息
    """
    try:
        settings = json.loads(settings_json)
        success = update_book_settings(book_id, user_id, settings)
        if success:
            return "书籍设置更新成功"
        return "更新失败，未找到该书籍"
    except json.JSONDecodeError:
        return "JSON格式错误"
    except Exception as e:
        return f"更新设置失败: {str(e)}"


@tool
def add_chapter_tool(user_id: int, book_id: int, title: str, content: str) -> str:
    """为书籍添加新章节
    
    Args:
        user_id: 用户ID
        book_id: 书籍ID
        title: 章节标题
        content: 章节内容
    
    Returns:
        包含新章节ID的JSON信息
    """
    try:
        chapter_id = add_chapter(book_id, user_id, title, content)
        if chapter_id:
            return json.dumps({"id": chapter_id, "message": "章节添加成功"}, ensure_ascii=False)
        return "添加章节失败"
    except Exception as e:
        return f"添加章节失败: {str(e)}"


@tool
def update_chapter_tool(user_id: int, chapter_id: int, title: Optional[str] = None, content: Optional[str] = None) -> str:
    """更新章节内容
    
    Args:
        user_id: 用户ID
        chapter_id: 章节ID
        title: 新的章节标题（可选）
        content: 新的章节内容（可选）
    
    Returns:
        操作结果信息
    """
    try:
        success = update_chapter(chapter_id, user_id, title, content)
        if success:
            return "章节更新成功"
        return "更新失败，未找到该章节"
    except Exception as e:
        return f"更新章节失败: {str(e)}"


@tool
def generate_text_tool(prompt: str) -> str:
    """根据提示生成写作内容
    
    Args:
        prompt: 写作提示词
    
    Returns:
        生成的文本内容
    """
    try:
        return f"正在生成内容: {prompt}"
    except Exception as e:
        return f"生成失败: {str(e)}"


def get_writing_tools() -> list:
    """获取所有写作相关的工具"""
    return [
        get_user_books_tool,
        get_book_detail_tool,
        update_book_settings_tool,
        add_chapter_tool,
        update_chapter_tool,
        generate_text_tool,
    ]

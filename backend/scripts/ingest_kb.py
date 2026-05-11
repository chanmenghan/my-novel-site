"""文档摄入脚本 - 将知识库文档摄入向量数据库"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path
from typing import Optional


def ingest_file(file_path: str, collection: str = "screenplay_kb") -> dict:
    """摄入单个文件到知识库"""
    from mcp_tools.rag_server import rag_knowledge_base

    try:
        result = rag_knowledge_base.ingest_document(file_path, collection)
        return result
    except Exception as e:
        return {"success": False, "message": str(e), "file": file_path}


def ingest_directory(dir_path: str, collection: str = "screenplay_kb", file_types: list = None) -> dict:
    """摄入整个目录的文档"""
    if file_types is None:
        file_types = [".txt", ".md", ".pdf"]

    dir_path = Path(dir_path)
    if not dir_path.exists():
        return {"success": False, "message": f"目录不存在: {dir_path}"}

    results = {
        "success": 0,
        "failed": 0,
        "files": []
    }

    for file_path in dir_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in file_types:
            print(f"   摄入: {file_path.name}...", end=" ")
            result = ingest_file(str(file_path), collection)
            if result.get("success"):
                print(f"✅ {result.get('chunk_count', 0)} chunks")
                results["success"] += 1
            else:
                print(f"❌ {result.get('message', '失败')}")
                results["failed"] += 1
            results["files"].append({
                "file": str(file_path),
                "result": result
            })

    return results


def list_collection_docs(collection: str = "screenplay_kb") -> list:
    """列出已摄入的文档"""
    kb_path = Path("./data/knowledge_base")

    collection_map = {
        "screenplay_kb": kb_path / "screenplay",
        "character_kb": kb_path / "character",
        "dialogue_kb": kb_path / "dialogue",
        "template_kb": kb_path / "template",
    }

    dir_path = collection_map.get(collection, kb_path)
    if not dir_path.exists():
        return []

    return [str(f.relative_to(kb_path)) for f in dir_path.rglob("*.txt")]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="文档摄入工具")
    parser.add_argument("--file", "-f", help="摄入单个文件路径")
    parser.add_argument("--dir", "-d", help="摄入整个目录")
    parser.add_argument("--collection", "-c", default="screenplay_kb",
                        choices=["screenplay_kb", "character_kb", "dialogue_kb", "template_kb"],
                        help="知识库集合名称")
    parser.add_argument("--list", "-l", action="store_true", help="列出已摄入的文档")

    args = parser.parse_args()

    if args.list:
        print(f"\n📚 {args.collection} 已摄入文档:")
        docs = list_collection_docs(args.collection)
        if docs:
            for doc in docs:
                print(f"   - {doc}")
        else:
            print("   (空)")
        return

    if args.file:
        print(f"\n📄 摄入文件: {args.file}")
        result = ingest_file(args.file, args.collection)
        if result.get("success"):
            print(f"✅ 成功! 文档数: {result.get('document_count')}, Chunks: {result.get('chunk_count')}")
        else:
            print(f"❌ 失败: {result.get('message')}")

    elif args.dir:
        print(f"\n📂 摄入目录: {args.dir}")
        print(f"   集合: {args.collection}")
        results = ingest_directory(args.dir, args.collection)
        print(f"\n📊 结果: 成功 {results['success']}, 失败 {results['failed']}")

    else:
        print("\n用法:")
        print("  python -m scripts.ingest_kb --file path/to/file.txt --collection screenplay_kb")
        print("  python -m scripts.ingest_kb --dir path/to/directory --collection character_kb")
        print("  python -m scripts.ingest_kb --list --collection screenplay_kb")
        print("\n可用集合: screenplay_kb, character_kb, dialogue_kb, template_kb")


if __name__ == "__main__":
    main()

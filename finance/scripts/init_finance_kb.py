"""初始化金融知识库向量数据库"""
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

from knowledge_base.finance_rag_kb import finance_rag_kb
from config import KNOWLEDGE_BASE_DIR, MARKET_DATA_DIR, RESEARCH_REPORTS_DIR, FINANCIAL_THEORY_DIR


def main():
    print("=" * 60)
    print("金融知识库向量数据库初始化")
    print("=" * 60)
    print()

    collections = [
        {
            "name": "market_data",
            "dir": MARKET_DATA_DIR,
            "description": "市场行情数据"
        },
        {
            "name": "research_reports",
            "dir": RESEARCH_REPORTS_DIR,
            "description": "研报数据"
        },
        {
            "name": "financial_theory",
            "dir": FINANCIAL_THEORY_DIR,
            "description": "投资理论"
        },
    ]

    total_chunks = 0

    for coll in collections:
        print(f"[{coll['description']}]")
        print(f"  目录: {coll['dir']}")

        if not coll['dir'].exists():
            print(f"  ! 目录不存在，跳过")
            continue

        result = finance_rag_kb.ingest_directory(
            str(coll['dir']),
            collection_name=coll['name']
        )

        if result.get("success"):
            chunks = result.get("chunk_count", 0)
            total_chunks += chunks
            print(f"  ✓ 成功摄入 {result.get('document_count', 0)} 个文档，{chunks} 个文本块")
        else:
            print(f"  ✗ 失败: {result.get('message', '未知错误')}")
        print()

    print("=" * 60)
    print(f"初始化完成！总计摄入 {total_chunks} 个文本块")
    print("=" * 60)


if __name__ == "__main__":
    main()

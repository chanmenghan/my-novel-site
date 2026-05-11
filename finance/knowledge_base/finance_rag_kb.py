"""金融 RAG 知识库模块 - 参考 backend/mcp_tools/rag_server.py"""
from typing import Optional, List, Dict, Any
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader
from langchain_core.documents import Document
from langchain_core.tools import tool
import json

from config import (
    DASHSCOPE_API_KEY,
    CHROMA_PERSIST_DIR,
    KNOWLEDGE_BASE_DIR,
    RESEARCH_REPORTS_DIR,
    FINANCIAL_THEORY_DIR,
)


class FinanceRAGKnowledgeBase:
    """金融知识库 RAG 服务"""

    def __init__(self):
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v3",
            dashscope_api_key=DASHSCOPE_API_KEY,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=64,
            length_function=len,
        )
        self.vectorstore = None

    def load_document(self, file_path: str) -> List[Document]:
        """加载文档"""
        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if content.strip():
                    return [Document(page_content=content, metadata={"source": file_path})]
                return []
            elif ext == '.pdf':
                loader = PyPDFLoader(file_path)
                return loader.load()
            elif ext in ['.doc', '.docx']:
                loader = UnstructuredWordDocumentLoader(file_path)
                return loader.load()
            else:
                return []
        except Exception as e:
            print(f"[ERROR] Failed to load {file_path}: {e}")
            return []

    def ingest_document(self, file_path: str, collection_name: str = "finance_kb") -> Dict[str, Any]:
        """摄入单个文档"""
        docs = self.load_document(file_path)
        if not docs:
            return {"success": False, "message": "无法加载文档"}

        texts = self.text_splitter.split_documents(docs)

        self.vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
            collection_name=collection_name,
        )

        return {
            "success": True,
            "document_count": len(docs),
            "chunk_count": len(texts),
            "collection": collection_name
        }

    def ingest_directory(self, dir_path: str, collection_name: str = "finance_kb") -> Dict[str, Any]:
        """摄入整个目录"""
        if not os.path.exists(dir_path):
            return {"success": False, "message": f"目录不存在: {dir_path}"}

        all_docs = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(('.txt', '.pdf', '.doc', '.docx')):
                    file_path = os.path.join(root, file)
                    docs = self.load_document(file_path)
                    all_docs.extend(docs)

        if not all_docs:
            return {"success": False, "message": "目录中没有找到文档"}

        texts = self.text_splitter.split_documents(all_docs)

        self.vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
            collection_name=collection_name,
        )

        return {
            "success": True,
            "document_count": len(all_docs),
            "chunk_count": len(texts),
            "collection": collection_name
        }

    def retrieve(self, query: str, top_k: int = 5, collection_name: str = "finance_kb") -> List[Dict[str, Any]]:
        """向量检索"""
        try:
            vectorstore = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                collection_name=collection_name,
                embedding_function=self.embeddings,
            )
            results = vectorstore.similarity_search(query, k=top_k)

            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": 0.0
                }
                for doc in results
            ]
        except Exception as e:
            print(f"[ERROR] retrieve failed: {e}")
            return []

    def hybrid_retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """混合检索"""
        bm25_results = self.keyword_search(query, top_k)
        vector_results = self.retrieve(query, top_k)

        merged = {}
        for r in bm25_results + vector_results:
            key = r["content"][:100]
            if key not in merged:
                merged[key] = r

        reranked = sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:top_k]
        return reranked

    def keyword_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """关键词检索（预留）"""
        return []

    def get_collection_stats(self, collection_name: str = "finance_kb") -> Dict[str, Any]:
        """获取知识库统计信息"""
        try:
            vectorstore = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                collection_name=collection_name,
                embedding_function=self.embeddings,
            )
            count = vectorstore._collection.count()
            return {"collection": collection_name, "document_count": count}
        except Exception as e:
            return {"collection": collection_name, "document_count": 0, "error": str(e)}


finance_rag_kb = FinanceRAGKnowledgeBase()


@tool
def retrieve_finance_knowledge(query: str, top_k: int = 5) -> str:
    """从金融知识库检索相关信息

    Args:
        query: 检索查询
        top_k: 返回结果数量

    Returns:
        检索结果列表
    """
    try:
        results = finance_rag_kb.retrieve(query, top_k)
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"检索失败: {str(e)}"


@tool
def ingest_finance_document(file_path: str, collection_name: str = "finance_kb") -> str:
    """向金融知识库添加文档

    Args:
        file_path: 文档路径
        collection_name: 知识库集合名称

    Returns:
        添加结果
    """
    try:
        result = finance_rag_kb.ingest_document(file_path, collection_name)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"文档摄入失败: {str(e)}"


def get_finance_rag_tools():
    return [
        retrieve_finance_knowledge,
        ingest_finance_document,
    ]

from typing import Optional
import os

from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader
from langchain_core.documents import Document
import json
from config import (
    DASHSCOPE_API_KEY,
    CHROMA_PERSIST_DIR,
    DASHSCOPE_EMBEDDING_DIM,
)


class RAGKnowledgeBase:
    def __init__(self):
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v3",
            dashscope_api_key=DASHSCOPE_API_KEY,
        )
        self._embedding_dim = DASHSCOPE_EMBEDDING_DIM
        self.vectorstore = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=64,
            length_function=len,
        )

    def load_document(self, file_path: str) -> list:
        from langchain_core.documents import Document
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
            raise

    def ingest_document(self, file_path: str, collection_name: str = "screenplay_kb"):
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

    def retrieve(self, query: str, top_k: int = 5, collection_name: str = "screenplay_kb") -> list:
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

    def hybrid_retrieve(self, query: str, top_k: int = 5) -> list:
        bm25_results = self.keyword_search(query, top_k)
        vector_results = self.retrieve(query, top_k)

        merged = {}
        for r in bm25_results + vector_results:
            key = r["content"][:100]
            if key not in merged:
                merged[key] = r

        reranked = sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:top_k]

        return reranked

    def keyword_search(self, query: str, top_k: int = 5) -> list:
        return []


rag_knowledge_base = RAGKnowledgeBase()


@tool
def retrieve_screenplay_knowledge(query: str, top_k: int = 5) -> str:
    """从剧本知识库检索相关信息

    Args:
        query: 检索查询
        top_k: 返回结果数量

    Returns:
        检索结果列表
    """
    try:
        results = rag_knowledge_base.retrieve(query, top_k)
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"检索失败: {str(e)}"


@tool
def ingest_document_tool(file_path: str, collection_name: str = "screenplay_kb") -> str:
    """向知识库添加文档

    Args:
        file_path: 文档路径
        collection_name: 知识库集合名称

    Returns:
        添加结果
    """
    try:
        result = rag_knowledge_base.ingest_document(file_path, collection_name)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"文档摄入失败: {str(e)}"


@tool
def search_screenplay_templates(template_type: str) -> str:
    """搜索剧本模板

    Args:
        template_type: 模板类型（如：重生复仇、系统流、恋爱多选一等）

    Returns:
        模板内容
    """
    templates = {
        "重生复仇": {
            "type": "重生复仇",
            "structure": "开篇冤死 -> 重生回溯 -> 布局复仇 -> 逐个击破 -> 最终翻盘",
            "key_elements": ["前世记忆", "信息差", "人脉重建", "复仇节奏"],
            "popular_tags": ["#重生 #复仇 #逆袭 #爽文"]
        },
        "系统流": {
            "type": "系统流",
            "structure": "普通人获系统 -> 任务获取资源 -> 能力成长 -> 挑战更强",
            "key_elements": ["系统任务", "属性面板", "技能兑换", "副本挑战"],
            "popular_tags": ["#系统 #任务 #升级 #爽文"]
        },
        "恋爱多选一": {
            "type": "恋爱多选一",
            "structure": "多男主/女主 -> 接触各线 -> 暧昧发展 -> 感情抉择 -> 结局",
            "key_elements": ["人设多样", "各线平衡", "暧昧互动", "攻略选择"],
            "popular_tags": ["#恋爱 #多选一 #甜宠 #攻略"]
        },
    }

    template = templates.get(template_type, templates["重生复仇"])
    return json.dumps(template, ensure_ascii=False, indent=2)


def get_rag_tools():
    return [
        retrieve_screenplay_knowledge,
        ingest_document_tool,
        search_screenplay_templates,
    ]

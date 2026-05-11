"""金融知识库RAG服务 + AKShare实时数据"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

from typing import List, Dict, Any, Optional
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from config import CHROMA_PERSIST_DIR, DASHSCOPE_API_KEY, RESEARCH_REPORTS_DIR, FINANCIAL_THEORY_DIR


class AKShareDataFetcher:
    """AKShare 数据获取器"""

    def __init__(self):
        self.last_update = None

    def get_stock_realtime_quote(self, symbol: str = "000001") -> Dict:
        """获取股票实时行情"""
        try:
            import akshare as ak
            from requests.exceptions import ConnectionError, ReadTimeout
            import time

            max_retries = 3
            df = None

            for attempt in range(max_retries):
                try:
                    time.sleep(3)
                    df = ak.stock_zh_a_spot_em()
                    break
                except (ConnectionError, ReadTimeout) as e:
                    print(f"[WARN] 获取股票数据尝试 {attempt + 1} 失败: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(5)
                    continue

            if df is None:
                return {"error": f"获取股票 {symbol} 数据失败"}

            stock_data = df[df['代码'] == symbol]

            if stock_data.empty:
                return {"error": f"未找到股票 {symbol} 的数据"}

            row = stock_data.iloc[0]
            return {
                "股票代码": symbol,
                "股票名称": row.get('名称', 'N/A'),
                "最新价": row.get('最新价', 'N/A'),
                "涨跌幅": row.get('涨跌幅', 'N/A'),
                "涨跌额": row.get('涨跌额', 'N/A'),
                "成交量": row.get('成交量', 'N/A'),
                "成交额": row.get('成交额', 'N/A'),
                "最高": row.get('最高', 'N/A'),
                "最低": row.get('最低', 'N/A'),
                "今开": row.get('今开', 'N/A'),
                "昨收": row.get('昨收', 'N/A'),
                "市值": row.get('总市值', 'N/A'),
                "市盈率": row.get('市盈率-动态', 'N/A'),
            }
        except Exception as e:
            return {"error": f"获取股票 {symbol} 数据失败: {str(e)}"}

    def get_stock_history(self, symbol: str = "000001", period: str = "daily",
                         start_date: str = None, end_date: str = None) -> List[Dict]:
        """获取股票历史 K 线数据"""
        try:
            import akshare as ak
            from datetime import datetime, timedelta

            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            if end_date is None:
                end_date = datetime.now().strftime("%Y%m%d")

            df = ak.stock_zh_a_hist(symbol=symbol, period=period,
                                    start_date=start_date, end_date=end_date,
                                    adjust="qfq")

            records = []
            for _, row in df.tail(30).iterrows():
                records.append({
                    "日期": str(row.get('日期', '')),
                    "开盘": float(row.get('开盘', 0)),
                    "收盘": float(row.get('收盘', 0)),
                    "最高": float(row.get('最高', 0)),
                    "最低": float(row.get('最低', 0)),
                    "成交量": int(row.get('成交量', 0)),
                    "涨跌幅": float(row.get('涨跌幅', 0)),
                })

            return records
        except Exception as e:
            return [{"error": f"获取股票 {symbol} 历史数据失败: {str(e)}"}]

    def get_index_realtime(self, symbol: str = "000001") -> Dict:
        """获取指数实时行情"""
        try:
            import akshare as ak
            df = ak.stock_zh_index_spot_em()
            index_data = df[df['代码'] == symbol]

            if index_data.empty:
                return {"error": f"未找到指数 {symbol} 的数据"}

            row = index_data.iloc[0]
            return {
                "指数代码": symbol,
                "指数名称": row.get('名称', 'N/A'),
                "最新价": row.get('最新价', 'N/A'),
                "涨跌幅": row.get('涨跌幅', 'N/A'),
                "涨跌额": row.get('涨跌额', 'N/A'),
            }
        except Exception as e:
            return {"error": f"获取指数 {symbol} 数据失败: {str(e)}"}

    def search_stock_by_keyword(self, keyword: str) -> List[Dict]:
        """根据关键词搜索股票"""
        try:
            import akshare as ak
            from requests.exceptions import ConnectionError, ReadTimeout
            import time

            max_retries = 3
            df = None

            for attempt in range(max_retries):
                try:
                    df = ak.stock_zh_a_spot_em()
                    break
                except (ConnectionError, ReadTimeout) as e:
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return [{"error": f"搜索失败，已重试 {max_retries} 次: {str(e)}"}]

            if df is None:
                return [{"error": "搜索失败，获取数据为空"}]

            results = df[df['名称'].str.contains(keyword, na=False)]

            stocks = []
            for _, row in results.head(10).iterrows():
                stocks.append({
                    "代码": row.get('代码', 'N/A'),
                    "名称": row.get('名称', 'N/A'),
                    "最新价": row.get('最新价', 'N/A'),
                    "涨跌幅": row.get('涨跌幅', 'N/A'),
                })
            return stocks
        except Exception as e:
            return [{"error": f"搜索失败: {str(e)}"}]


akshare_fetcher = AKShareDataFetcher()


class FinanceKnowledgeBase:
    """金融知识库"""

    def __init__(self):
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v3",
            dashscope_api_key=DASHSCOPE_API_KEY
        )
        self.vectorstore = None
        self._init_vectorstore()

    def _init_vectorstore(self):
        """初始化向量数据库"""
        try:
            self.vectorstore = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings
            )
            print(f"[DEBUG] Chroma向量数据库已加载，路径: {CHROMA_PERSIST_DIR}")
        except Exception as e:
            print(f"[WARN] 加载已有向量库失败: {e}")
            self.vectorstore = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings
            )

    def ingest_document(self, file_path: str, collection: str = "finance_kb") -> Dict[str, Any]:
        """摄入单个文档"""
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            docs = text_splitter.split_documents(documents)

            texts = [doc.page_content for doc in docs]
            metadatas = [{"source": file_path, "collection": collection} for _ in docs]

            self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
            self.vectorstore.persist()

            return {"success": True, "chunks": len(docs)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def retrieve(self, query: str, top_k: int = 5, collection: Optional[str] = None) -> Dict[str, Any]:
        """检索知识"""
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=top_k)

            docs = []
            for doc, score in results:
                docs.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "score": float(score)
                })

            return {"results": docs}
        except Exception as e:
            print(f"[ERROR] 检索失败: {e}")
            return {"results": []}


rag_knowledge_base = FinanceKnowledgeBase()


def ingest_directory(dir_path: str, collection: str = "finance_kb") -> Dict[str, Any]:
    """摄入整个目录"""
    try:
        loader = DirectoryLoader(dir_path, glob="**/*.txt", loader_cls=TextLoader)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        docs = text_splitter.split_documents(documents)

        texts = [doc.page_content for doc in docs]
        metadatas = [{"source": doc.metadata.get("source", dir_path), "collection": collection} for doc in docs]

        vectorstore = Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=rag_knowledge_base.embeddings
        )
        vectorstore.add_texts(texts=texts, metadatas=metadatas)
        vectorstore.persist()

        return {"success": True, "chunks": len(docs)}
    except Exception as e:
        return {"success": False, "error": str(e)}

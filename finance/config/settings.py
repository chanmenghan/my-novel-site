"""金融投资研究助手配置"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEFAULT_CHAT_MODEL = os.getenv("DEFAULT_CHAT_MODEL", "deepseek-chat")

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5001"))
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_CHECKPOINT_TTL = int(os.getenv("REDIS_CHECKPOINT_TTL", "86400"))

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "data" / "chroma"))

LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "finance-agent")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")

KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
MARKET_DATA_DIR = KNOWLEDGE_BASE_DIR / "market_data"
RESEARCH_REPORTS_DIR = KNOWLEDGE_BASE_DIR / "research_reports"
FINANCIAL_THEORY_DIR = KNOWLEDGE_BASE_DIR / "financial_theory"
STOCK_DATA_DIR = KNOWLEDGE_BASE_DIR / "stock_data"

print(f"[DEBUG] Finance Agent 配置加载完成")
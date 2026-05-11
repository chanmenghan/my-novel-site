import os
from dotenv import load_dotenv

load_dotenv()


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DEFAULT_CHAT_MODEL = "deepseek-chat"


DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '123456'),
    'database': os.environ.get('DB_NAME', 'xiaoshuo'),
    'charset': 'utf8mb4'
}


SERVICE_PORT = 5000


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_CHECKPOINT_TTL = int(os.getenv("REDIS_CHECKPOINT_TTL", 86400 * 7))


LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "screenplay-agent")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true") == "true"


RAGFLOW_BASE_URL = os.getenv("RAGFLOW_BASE_URL", "http://localhost:9380")
RAGFLOW_API_KEY = os.getenv("RAGFLOW_API_KEY", "")


CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
DASHSCOPE_EMBEDDING_MODEL = os.getenv("DASHSCOPE_EMBEDDING_MODEL", "text-embedding-v3")
DASHSCOPE_EMBEDDING_DIM = 1024

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

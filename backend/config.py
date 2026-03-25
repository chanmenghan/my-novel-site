import os
from dotenv import load_dotenv

# 加载私密配置
load_dotenv()

# DeepSeek API 配置
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEFAULT_CHAT_MODEL = "deepseek-chat" # 需要推理就改成 "deepseek-reasoner"

# Flask服务配置
SERVICE_PORT = 5000 # 后端服务端口，默认用5000就行
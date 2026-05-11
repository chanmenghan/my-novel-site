"""启动脚本"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from config import SERVICE_PORT, SERVICE_HOST

if __name__ == "__main__":
    print(f"启动金融投资研究助手服务...")
    print(f"API文档: http://localhost:{SERVICE_PORT}/docs")
    uvicorn.run(
        "api.main:app",
        host=SERVICE_HOST,
        port=SERVICE_PORT,
        reload=True,
        reload_dirs=[os.path.dirname(__file__)]
    )

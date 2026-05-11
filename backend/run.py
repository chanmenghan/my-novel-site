import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from config import SERVICE_PORT

    print(f"启动服务器在 http://localhost:{SERVICE_PORT}")
    print(f"API文档: http://localhost:{SERVICE_PORT}/docs")
    uvicorn.run("api.main:app", host="0.0.0.0", port=SERVICE_PORT, reload=True)

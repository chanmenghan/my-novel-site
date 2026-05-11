from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from api.routes import router
from core.observability import setup_logging, setup_opentelemetry
from config import SERVICE_PORT

setup_logging()
tracer = setup_opentelemetry("screenplay-agent")

app = FastAPI(
    title="企业级剧本创作多智能体系统",
    description="基于 LangGraph + MCP 的剧本创作平台",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FastAPIInstrumentor.instrument_app(app)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "企业级剧本创作多智能体系统",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)

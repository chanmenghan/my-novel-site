"""可观测性模块 - 日志、追踪、成本计量"""
import structlog
import os
from typing import Optional, Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource

try:
    from langchain_core.tracers import LangSmithTracer
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    LangSmithTracer = None

from config import LANGSMITH_API_KEY, LANGSMITH_PROJECT, LANGSMITH_TRACING, LOG_LEVEL


def setup_logging():
    """配置结构化日志"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    print("[DEBUG] 日志系统已初始化")


def setup_langsmith_tracing() -> Optional[Any]:
    """配置 LangSmith 追踪"""
    if not LANGSMITH_TRACING:
        print("[DEBUG] LangSmith追踪未启用 (LANGSMITH_TRACING=false)")
        return None

    if not LANGSMITH_API_KEY:
        print("[DEBUG] LangSmith追踪未配置 (缺少LANGSMITH_API_KEY)")
        return None

    if not LANGSMITH_AVAILABLE:
        print("[DEBUG] LangSmithTracer不可用，跳过")
        return None

    try:
        tracer = LangSmithTracer(
            project_name=LANGSMITH_PROJECT,
            api_key=LANGSMITH_API_KEY,
        )
        print(f"[DEBUG] LangSmith追踪已配置，项目: {LANGSMITH_PROJECT}")
        return tracer
    except Exception as e:
        print(f"[WARN] LangSmith追踪配置失败: {e}")
        return None


def setup_opentelemetry(service_name: str = "screenplay-agent"):
    """配置 OpenTelemetry 追踪"""
    try:
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
        tracer = trace.get_tracer(service_name)
        print(f"[DEBUG] OpenTelemetry已初始化，服务: {service_name}")
        return tracer
    except Exception as e:
        print(f"[WARN] OpenTelemetry配置失败: {e}")
        return None


class CostTracker:
    """成本追踪器"""
    def __init__(self):
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_cost = 0.0
        self.request_count = 0

    def record(self, prompt_tokens: int, completion_tokens: int, cost_per_token: float = 0.0001):
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens += prompt_tokens + completion_tokens
        self.total_cost += (prompt_tokens + completion_tokens) * cost_per_token
        self.request_count += 1
        print(f"[DEBUG] Cost recorded: prompt={prompt_tokens}, completion={completion_tokens}")

    def get_stats(self) -> dict:
        return {
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_cost": round(self.total_cost, 6),
            "request_count": self.request_count,
        }

    def reset(self):
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_cost = 0.0
        self.request_count = 0


cost_tracker = CostTracker()
print("[DEBUG] CostTracker已初始化")

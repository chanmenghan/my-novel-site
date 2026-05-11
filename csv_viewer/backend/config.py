"""CSV 查看器配置"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5002"))
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
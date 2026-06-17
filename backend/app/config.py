import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# 音频缓存目录
AUDIO_CACHE_DIR = BASE_DIR / "audio_cache"
AUDIO_CACHE_DIR.mkdir(exist_ok=True)

# 数据库
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR / 'history.db'}"

# CORS 支持多域名列表
_cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
CORS_ORIGINS: list[str] = [o.strip() for o in _cors_raw.split(",") if o.strip()]

# RAGFlow（允许为空，未配置时 Chat Tab 显示引导）
RAGFLOW_API_URL: str = os.getenv("RAGFLOW_API_URL", "")
RAGFLOW_API_KEY: str = os.getenv("RAGFLOW_API_KEY", "")
RAGFLOW_CHAT_ID: str = os.getenv("RAGFLOW_CHAT_ID", "")

# LRU 缓存上限
AUDIO_CACHE_MAX_FILES: int = int(os.getenv("AUDIO_CACHE_MAX_FILES", "1000"))

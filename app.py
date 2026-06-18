"""
Hugging Face Spaces 入口文件

HF Spaces 要求应用监听 0.0.0.0:7860。
此文件作为根目录入口，将 uvicorn 指向 backend/app/main.py 中的 FastAPI 实例。
"""
import sys
import os
from pathlib import Path

# 将 backend 目录加入模块搜索路径，使 `from app.xxx import ...` 正常工作
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# 读取 backend/.env（如果存在），方便本地测试
_env_file = Path(__file__).parent / "backend" / ".env"
if _env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_file)

# HF Spaces 要求监听 7860，CORS 需放开 Spaces 域名
# 用户也可以在 Spaces Settings → Variables 里配置以下环境变量：
#   RAGFLOW_API_URL / RAGFLOW_API_KEY / RAGFLOW_CHAT_ID
#   CORS_ORIGINS（默认已允许所有来源）

import uvicorn
from app.main import app  # noqa: F401 — 导入 FastAPI 实例

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )

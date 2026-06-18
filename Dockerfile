# ── Stage 1: 构建前端 ────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci --prefer-offline

COPY frontend/ ./
RUN npm run build


# ── Stage 2: 运行后端 ─────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 复制前端构建产物到 frontend/dist（FastAPI 会自动检测并挂载）
COPY --from=frontend-builder /build/frontend/dist ./frontend/dist/

# 复制根入口
COPY app.py ./

# HF Spaces 要求监听 7860
EXPOSE 7860

# 启动服务
# PYTHONPATH 指向 backend 目录，使 `from app.xxx import ...` 正常工作
ENV PYTHONPATH=/app/backend
CMD ["python", "app.py"]

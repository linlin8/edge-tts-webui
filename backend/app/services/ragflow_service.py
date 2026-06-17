import httpx
from typing import AsyncGenerator, Optional
from app.config import RAGFLOW_API_URL, RAGFLOW_API_KEY, RAGFLOW_CHAT_ID

_client: Optional[httpx.AsyncClient] = None


class RagflowUnavailableError(Exception):
    pass


def is_configured() -> bool:
    return bool(RAGFLOW_API_URL and RAGFLOW_API_KEY and RAGFLOW_CHAT_ID)


async def init_client():
    global _client
    if not is_configured():
        return
    _client = httpx.AsyncClient(
        base_url=RAGFLOW_API_URL,
        headers={
            "Authorization": f"Bearer {RAGFLOW_API_KEY}",
            "Content-Type": "application/json",
        },
        timeout=httpx.Timeout(connect=10.0, read=120.0, write=10.0, pool=10.0),
    )


async def close_client():
    global _client
    if _client:
        await _client.aclose()
        _client = None


async def chat_stream(
    question: str,
    session_id: Optional[str] = None,
) -> AsyncGenerator[dict, None]:
    """
    调用 RAGFlow SSE 接口，逐步 yield {"delta": str, "session_id": str}
    不可用时抛 RagflowUnavailableError
    """
    if not is_configured() or _client is None:
        raise RagflowUnavailableError("RAGFlow 未配置")

    payload: dict = {"question": question, "stream": True}
    if session_id:
        payload["session_id"] = session_id

    try:
        async with _client.stream(
            "POST",
            f"/api/v1/chats/{RAGFLOW_CHAT_ID}/completions",
            json=payload,
        ) as resp:
            resp.raise_for_status()
            current_session_id = session_id
            sent_len = 0  # 已发送的字符数（RAGFlow answer 是累计全文，需计算增量）
            async for line in resp.aiter_lines():
                if not line.startswith("data:"):
                    continue
                raw = line[5:].strip()
                if raw == "[DONE]" or not raw:
                    continue
                import json
                try:
                    data = json.loads(raw)
                except Exception:
                    continue

                # RAGFlow 响应结构：data.answer 是累计全文，需取增量部分
                answer = data.get("data", {})
                if isinstance(answer, dict):
                    full_text = answer.get("answer", "")
                    sid = answer.get("session_id", current_session_id)
                    if sid:
                        current_session_id = sid
                    # 只 yield 本次新增的部分
                    if len(full_text) > sent_len:
                        delta = full_text[sent_len:]
                        sent_len = len(full_text)
                        yield {"delta": delta, "session_id": current_session_id or ""}
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
        raise RagflowUnavailableError(str(e))

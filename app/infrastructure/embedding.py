"""
文本向量化客户端：调用独立部署的 embedding 服务（配置见 settings.embedding_*）。

服务契约：POST /embed，请求体 {"inputs": ["文本", ...]}，
响应体 {"embeddings": [[float, ...], ...]}（与 TEI 兼容，也接受直接返回二维数组）。
"""
import logging
from typing import List

from app.config.config import settings
from app.infrastructure import http

logger = logging.getLogger(__name__)


class EmbeddingUnavailableError(RuntimeError):
    """embedding 服务不可用或返回结构不符合约定。"""


def _endpoint() -> str:
    return f"http://{settings.embedding_host}:{settings.embedding_port}/embed"


async def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    try:
        response = await http.http_client.post(_endpoint(), json={"inputs": texts}, timeout=60.0)
        response.raise_for_status()
        payload = response.json()
    except Exception as e:
        raise EmbeddingUnavailableError(f"embedding 服务调用失败: {e}") from e

    embeddings = payload.get("embeddings") if isinstance(payload, dict) else payload
    if not isinstance(embeddings, list) or len(embeddings) != len(texts):
        raise EmbeddingUnavailableError("embedding 服务返回结构不符合约定")

    return [[float(value) for value in vector] for vector in embeddings]


async def embed_text(text: str) -> List[float]:
    return (await embed_texts([text]))[0]

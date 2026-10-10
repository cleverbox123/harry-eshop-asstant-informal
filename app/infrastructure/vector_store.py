"""
向量库封装（Qdrant）。

优先连接 settings.qdrant_host:settings.qdrant_port 的 Qdrant 服务；
服务不可达时回退到本地持久化模式（settings.qdrant_local_path），保证开发环境可直接运行。
"""
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config.config import settings

logger = logging.getLogger(__name__)

_project_root = Path(__file__).resolve().parents[2]


class VectorStore:
    def __init__(self) -> None:
        self._client = self._connect()

    def _connect(self) -> QdrantClient:
        try:
            client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                timeout=3,
                check_compatibility=False,
            )
            client.get_collections()
            logger.info("Qdrant 服务连接成功 %s:%s", settings.qdrant_host, settings.qdrant_port)
            return client
        except Exception as e:
            local_path = _project_root / settings.qdrant_local_path
            logger.warning("Qdrant 服务不可达(%s)，回退本地持久化模式: %s", e, local_path)
            return QdrantClient(path=str(local_path))

    def ensure_collection(self, name: str) -> None:
        existing = {c.name for c in self._client.get_collections().collections}
        if name in existing:
            return
        self._client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=settings.qdrant_embedding_size,
                distance=Distance.COSINE,
            ),
        )
        logger.info("创建向量集合 %s (dim=%s)", name, settings.qdrant_embedding_size)

    def count(self, name: str) -> int:
        return int(self._client.get_collection(name).points_count or 0)

    def upsert(self, name: str, points: List[PointStruct]) -> None:
        if not points:
            return
        self._client.upsert(collection_name=name, points=points)

    def search(
        self,
        name: str,
        vector: List[float],
        top_k: int = 3,
        score_threshold: Optional[float] = None,
    ) -> List[Tuple[dict, float]]:
        response = self._client.query_points(
            collection_name=name,
            query=vector,
            limit=top_k,
            score_threshold=score_threshold,
        )
        return [(hit.payload or {}, float(hit.score)) for hit in response.points]


_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store

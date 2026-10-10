"""
知识库种子数据：把 FAQ / RAG 语料向量化后写入 Qdrant（幂等）。
"""
import logging
import uuid
from typing import List

from qdrant_client.models import PointStruct

from app.infrastructure.embedding import embed_texts
from app.infrastructure.vector_store import get_vector_store
from app.knowledge.documents import (
    FAQ_COLLECTION,
    FAQ_DOCUMENTS,
    RAG_COLLECTION,
    RAG_DOCUMENTS,
    faq_embedding_text,
    rag_embedding_text,
)

logger = logging.getLogger(__name__)

_NAMESPACE = uuid.UUID("6f1d4c2e-8a3b-4e5f-9c6d-2b7a8e1f0d3c")


def _point_id(collection: str, doc_id: str) -> str:
    return str(uuid.uuid5(_NAMESPACE, f"{collection}:{doc_id}"))


async def _seed_collection(collection: str, docs: List[dict], texts: List[str]) -> int:
    store = get_vector_store()
    store.ensure_collection(collection)

    if store.count(collection) >= len(docs):
        logger.info("集合 %s 已有 %s 条数据，跳过种子写入", collection, store.count(collection))
        return 0

    vectors = await embed_texts(texts)
    points = [
        PointStruct(id=_point_id(collection, doc["id"]), vector=vector, payload=dict(doc))
        for doc, vector in zip(docs, vectors)
    ]
    store.upsert(collection, points)
    logger.info("集合 %s 写入 %s 条种子数据", collection, len(points))
    return len(points)


async def seed_knowledge() -> None:
    """
    应用启动时调用；embedding 或 Qdrant 不可用时仅告警，不影响应用启动。
    """
    try:
        await _seed_collection(
            FAQ_COLLECTION,
            list(FAQ_DOCUMENTS),
            [faq_embedding_text(doc) for doc in FAQ_DOCUMENTS],
        )
        await _seed_collection(
            RAG_COLLECTION,
            list(RAG_DOCUMENTS),
            [rag_embedding_text(doc) for doc in RAG_DOCUMENTS],
        )
    except Exception as e:
        logger.warning("知识库种子数据写入失败（知识检索将降级）: %s", e)

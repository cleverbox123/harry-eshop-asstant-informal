import asyncio
import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List

from app.config.config import settings
from app.domain.state import DialogueState
from app.infrastructure.commerce import fetch_logistics, fetch_order, fetch_product
from app.infrastructure.embedding import embed_text
from app.infrastructure.vector_store import get_vector_store
from app.knowledge.documents import FAQ_COLLECTION, RAG_COLLECTION

logger = logging.getLogger(__name__)

_ORDER_ID_RE = re.compile(r"[A-Z]{2}\d{6,}")
_PRODUCT_ID_RE = re.compile(r"(?<![A-Z0-9])P\d{4,}")


@dataclass(slots=True)
class KnowledgeChunk:
    content: str


class KnowledgeProvider(ABC):
    provider_id = ""  # 提供商的ID

    @abstractmethod
    async def retrieve(  # 提供检索方法
            self,
            state: DialogueState,
    ) -> list[KnowledgeChunk]:
        pass


def _user_text(state: DialogueState) -> str:
    if state.pending_turn is None or state.pending_turn.user_message is None:
        return ""
    return state.pending_turn.user_message.text or ""


class ProductAPIProvider(KnowledgeProvider):
    provider_id = 'api.product'

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        product_id = state.active_task.slots.get("product_id") if state.active_task else None
        if not product_id:
            match = _PRODUCT_ID_RE.search(_user_text(state))
            product_id = match.group(0) if match else None
        if not product_id:
            return [KnowledgeChunk(content="商品信息:\n用户未提供商品ID，无法查询具体商品。")]

        data = await fetch_product(product_id)
        if data is None:
            return [KnowledgeChunk(content=f"商品信息:\n未查询到商品 {product_id} 的信息。")]
        text = json.dumps(data, ensure_ascii=False, indent=2)
        return [KnowledgeChunk(content=f"商品信息:\n{text}")]


class OrderAPIProvider(KnowledgeProvider):
    provider_id = 'api.order'

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        order_number = state.active_task.slots.get("order_number") if state.active_task else None
        match = _ORDER_ID_RE.search(_user_text(state))
        order_number = order_number or (match.group(0) if match else None)
        if not order_number:
            return [KnowledgeChunk(content="订单与物流信息：\n用户未提供订单号，无法查询具体订单。")]

        order_payload, logistics_payload = await asyncio.gather(
            fetch_order(order_number),
            fetch_logistics(order_number),
        )
        if order_payload is None and logistics_payload is None:
            return [KnowledgeChunk(content=f"订单与物流信息：\n未查询到订单 {order_number} 的信息。")]

        return [
            KnowledgeChunk(
                content="订单与物流信息：\n"
                        + json.dumps(
                    {
                        "order_number": order_number,
                        "order": order_payload,
                        "logistics": logistics_payload,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        ]


class FAQProvider(KnowledgeProvider):
    provider_id = 'faq.default'

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        hits = await _search(FAQ_COLLECTION, _user_text(state))
        if hits is None:
            return [KnowledgeChunk(content="（FAQ 知识库暂不可用，未检索到相关问题）")]
        if not hits:
            return [KnowledgeChunk(content="（FAQ 知识库中未检索到相关问题）")]
        return [
            KnowledgeChunk(content=f"FAQ：{payload.get('question', '')}\n答案：{payload.get('answer', '')}")
            for payload, _ in hits
        ]


class RAGProvider(KnowledgeProvider):
    provider_id = 'rag.default'

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        hits = await _search(RAG_COLLECTION, _user_text(state))
        if hits is None:
            return [KnowledgeChunk(content="（RAG 知识库暂不可用，未检索到相关信息）")]
        if not hits:
            return [KnowledgeChunk(content="（RAG 知识库中未检索到相关信息）")]
        return [
            KnowledgeChunk(content=f"《{payload.get('title', '')}》\n{payload.get('content', '')}")
            for payload, _ in hits
        ]


async def _search(collection: str, query: str) -> List[tuple] | None:
    """
    向量检索；返回 [(payload, score)]，服务不可用时返回 None。
    """
    if not query.strip():
        return []
    try:
        vector = await embed_text(query)
        hits = get_vector_store().search(
            collection, vector,
            top_k=settings.knowledge_top_k,
            score_threshold=settings.knowledge_score_threshold,
        )
        logger.debug(
            "向量检索 collection=%s query=%r 命中=%d scores=%s",
            collection, query[:30], len(hits),
            [round(score, 4) for _, score in hits],
        )
        return hits
    except Exception as e:
        logger.warning("向量检索失败 collection=%s err=%s", collection, e)
        return None

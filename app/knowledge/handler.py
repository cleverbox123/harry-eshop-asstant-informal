from typing import Dict, Any

import logging

from app.domain.state import DialogueState
from app.knowledge.intents import KnowledgeIntent
from app.knowledge.provider import KnowledgeChunk
from app.knowledge.registry import KnowledgeProviderRegistry
from app.knowledge.responder import KnowledgeResponder
from app.domain.messages import BotMessage

logger = logging.getLogger(__name__)


class KnowLedgeHandler:

    def __init__(self,
                 knowledge_intents: Dict[str, KnowledgeIntent],
                 provider_registry: KnowledgeProviderRegistry,
                 knowledge_responder: KnowledgeResponder
                 ):
        self.knowledge_intents = knowledge_intents
        self.provider_registry = provider_registry
        self.knowledge_responder = knowledge_responder

    async def handle(self, state: DialogueState,
                     knowledge_intents: list[str]) -> list[BotMessage]:

        # ① 根据意图寻找知识来源
        provider_ids: list[str] = self._get_provider_ids_by_intents(knowledge_intents)
        logger.info("知识意图=%s -> provider_ids=%s", knowledge_intents, provider_ids)

        # ② 从每个 provider 检索知识片段
        chunks: list[KnowledgeChunk] = []
        for provider_id in provider_ids:
            provider = self.provider_registry.get(provider_id)
            current_chunks = await provider.retrieve(state)
            logger.info("provider=%s 检索到 %d 个片段", provider_id, len(current_chunks))
            chunks.extend(current_chunks)

        # ③ 用知识生成回复
        return await self.knowledge_responder.respond(
            user_message=state.pending_turn.user_message,
            recent_turns=state.turns[-5:],
            chunks=chunks
        )

    # 请问这件商品的退款以及退货政策是什么-----> intents=["return_policy","refund_policy"]
    def _get_provider_ids_by_intents(self, knowledge_intents: list[str]) -> list[str]:
        provider_ids: list[str] = []
        for intent in knowledge_intents:
            provider_ids.extend(self.knowledge_intents[intent].provider_ids)
        return list(set(provider_ids))

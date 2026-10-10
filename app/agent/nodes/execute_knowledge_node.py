import logging
from typing import Any, Dict

from app.domain.state import DialogueState
from app.domain.messages import BotMessage
from app.knowledge.handler import KnowLedgeHandler

logger = logging.getLogger(__name__)


def make_execute_knowledge_node(knowledge_handler: KnowLedgeHandler):
    async def execute_knowledge_node(state: Dict[str, Any]) -> Dict[str, Any]:
        dialogue_state: DialogueState = state["dialogue_state"]
        intents = state["turn_plan"].knowledge.intents
        messages: list[BotMessage] = await knowledge_handler.handle(dialogue_state, intents)
        logger.info("知识库轨道执行完成: %d 条消息", len(messages))
        return {"bot_messages": messages}

    return execute_knowledge_node

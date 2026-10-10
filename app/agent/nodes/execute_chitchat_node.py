import logging
from typing import Any, Dict

from app.domain.state import DialogueState
from app.domain.messages import BotMessage
from app.chitchat.handler import ChitChatHandler

logger = logging.getLogger(__name__)


def make_execute_chitchat_node(chitchat_handler: ChitChatHandler):
    async def execute_chitchat_node(state: Dict[str, Any]) -> Dict[str, Any]:
        dialogue_state: DialogueState = state["dialogue_state"]
        messages: list[BotMessage] = await chitchat_handler.handle(dialogue_state)
        logger.info("闲聊轨道执行完成: %d 条消息", len(messages))
        return {"bot_messages": messages}

    return execute_chitchat_node

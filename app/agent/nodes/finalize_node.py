import logging
from typing import Any, Dict

from app.domain.state import DialogueState
from app.domain.messages import ProcessResult

logger = logging.getLogger(__name__)


def finalize_node(state: Dict[str, Any]) -> Dict[str, Any]:
    dialogue_state: DialogueState = state["dialogue_state"]
    user_message = state["user_message"]
    bot_messages = state.get("bot_messages", [])

    if dialogue_state.pending_turn is not None:
        dialogue_state.pending_turn.bot_messages.extend(bot_messages)

    process_result = ProcessResult(
        sender_id=user_message.sender_id,
        message_id=user_message.message_id,
        session_id=dialogue_state.session_id,
        messages=bot_messages,
    )
    logger.info("finalize: %d 条回复消息", len(bot_messages))
    return {"process_result": process_result}

import logging
from typing import Any, Dict

from app.domain.state import DialogueState
from app.domain.messages import BotMessage
from app.clarify.responder import ClarifyResponder
from app.plan.turn_plan import ClarifyReason

logger = logging.getLogger(__name__)


def make_execute_clarify_node(clarify_responder: ClarifyResponder):
    async def execute_clarify_node(state: Dict[str, Any]) -> Dict[str, Any]:
        dialogue_state: DialogueState = state["dialogue_state"]
        reason: ClarifyReason = state["validation"].reason
        messages: list[BotMessage] = await clarify_responder.respond(dialogue_state, reason)
        logger.info("澄清轨道执行完成: reason=%s", reason)
        return {"bot_messages": messages}

    return execute_clarify_node

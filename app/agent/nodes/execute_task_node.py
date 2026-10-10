import logging
from typing import Any, Dict

from app.domain.state import DialogueState
from app.domain.messages import BotMessage
from app.task.handler import TaskHandler

logger = logging.getLogger(__name__)


def make_execute_task_node(task_handler: TaskHandler):
    async def execute_task_node(state: Dict[str, Any]) -> Dict[str, Any]:
        dialogue_state: DialogueState = state["dialogue_state"]
        commands = state["turn_plan"].task.commands
        messages: list[BotMessage] = await task_handler.handle(dialogue_state, commands=commands)
        logger.info("任务轨道执行完成: %d 条消息", len(messages))
        return {"bot_messages": messages}

    return execute_task_node

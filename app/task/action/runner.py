import logging
from dataclasses import dataclass, field
from typing import Any
from app.task.action.registry import ActionRegistry
from app.task.action.base import ActionResult
from app.domain.state import DialogueState

logger = logging.getLogger(__name__)


@dataclass
class ActionCall:
    """
    FlowExecutor返回的
    """
    action_name: str
    action_kwargs: dict[str, Any] = field(default_factory=dict)


class ActionRunner:
    def __init__(self, registry: ActionRegistry) -> None:
        self.registry = registry

    async def run(self, action_call: ActionCall, state: DialogueState) -> ActionResult:
        # 1. 获取action的名字
        action_name = action_call.action_name
        logger.debug("执行动作 action=%s kwargs=%s", action_name, action_call.action_kwargs)

        # 2. 从Action注册中心获取名字对应的Action的实例对象
        action = self.registry.get(action_name)

        # 3. 调用具体Action的逻辑
        result = await action.run(state, action_call.action_kwargs)
        logger.debug("动作完成 action=%s messages=%s slot_updates=%s",
                     action_name, len(result.messages), list(result.slot_updates.keys()))
        return result

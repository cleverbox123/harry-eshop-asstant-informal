import logging
from typing import Any, Dict

from app.domain.state import DialogueState
from app.domain.messages import UserMessage, BotMessage
from app.plan.planner import TurnPlanner
from app.plan.turn_plan import TurnPlan
from app.infrastructure.llm_resilience import LLMUnavailableError

logger = logging.getLogger(__name__)


def make_plan_node(turn_planner: TurnPlanner, flows, intents):
    async def plan_node(state: Dict[str, Any]) -> Dict[str, Any]:
        dialogue_state: DialogueState = state["dialogue_state"]
        try:
            turn_plan: TurnPlan = await turn_planner.predict(
                dialogue_state, flows=flows, intents=intents
            )
            logger.info("意图识别成功: task=%s knowledge=%s chitchat=%s",
                        turn_plan.task is not None,
                        turn_plan.knowledge is not None,
                        turn_plan.chitchat is not None)
            return {"turn_plan": turn_plan, "plan_failed": False}
        except LLMUnavailableError:
            logger.warning("意图识别失败: LLM 不可用")
            return {"turn_plan": None, "plan_failed": True}
        except Exception as exc:
            logger.warning("意图识别异常: %s", exc)
            return {"turn_plan": None, "plan_failed": True}

    return plan_node

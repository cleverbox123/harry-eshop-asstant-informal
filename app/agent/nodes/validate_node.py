import logging
from typing import Any, Dict

from app.domain.state import DialogueState
from app.plan.turn_validator import TurnPlanValidator
from app.plan.turn_plan import TurnPlan, TurnPlanValidationResult

logger = logging.getLogger(__name__)


def make_validate_node(turn_validator: TurnPlanValidator, flows, intents):
    def validate_node(state: Dict[str, Any]) -> Dict[str, Any]:
        dialogue_state: DialogueState = state["dialogue_state"]
        turn_plan: TurnPlan = state["turn_plan"]
        result: TurnPlanValidationResult = turn_validator.validate(
            dialogue_state, turn_plan, flow_list=flows, intents=intents
        )
        logger.info("计划校验: valid=%s reason=%s", result.valid, result.reason)
        return {"validation": result}

    return validate_node

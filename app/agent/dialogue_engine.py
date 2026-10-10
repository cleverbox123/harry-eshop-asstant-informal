import logging
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import StateGraph, END, START

from app.domain.state import DialogueState
from app.domain.messages import UserMessage, BotMessage, ProcessResult
from app.plan.planner import TurnPlanner
from app.plan.turn_validator import TurnPlanValidator
from app.plan.turn_plan import TurnPlan, TurnPlanValidationResult, ClarifyReason
from app.task.command.models import Command
from app.task.handler import TaskHandler
from app.knowledge.handler import KnowLedgeHandler
from app.chitchat.handler import ChitChatHandler
from app.clarify.responder import ClarifyResponder
from app.agent.nodes import (
    make_plan_node,
    make_validate_node,
    make_execute_task_node,
    make_execute_knowledge_node,
    make_execute_chitchat_node,
    make_execute_clarify_node,
    fallback_node,
    finalize_node,
)

logger = logging.getLogger(__name__)


class DialogueGraphState(TypedDict, total=False):
    dialogue_state: DialogueState
    user_message: UserMessage
    bot_messages: List[BotMessage]
    turn_plan: Optional[TurnPlan]
    validation: Optional[TurnPlanValidationResult]
    commands: Optional[List[Command]]
    clarify_reason: Optional[ClarifyReason]
    plan_failed: bool
    process_result: Optional[ProcessResult]


class DialogueEngine:

    def __init__(self,
                 turn_planner: TurnPlanner,
                 turn_validator: TurnPlanValidator,
                 clarify_responder: ClarifyResponder,
                 task_handler: TaskHandler,
                 knowledge_handler: KnowLedgeHandler,
                 chit_chat_handler: ChitChatHandler):
        self.turn_planner = turn_planner
        self.turn_validator = turn_validator
        self.clarify_responder = clarify_responder
        self.task_handler = task_handler
        self.knowledge_handler = knowledge_handler
        self.chit_chat_handler = chit_chat_handler
        self.graph = self._build_graph()

    def _build_graph(self):
        flows = self.task_handler.flows
        intents = self.knowledge_handler.knowledge_intents

        g = StateGraph(DialogueGraphState)

        g.add_node("plan", make_plan_node(self.turn_planner, flows, intents))
        g.add_node("validate", make_validate_node(self.turn_validator, flows, intents))
        g.add_node("execute_task", make_execute_task_node(self.task_handler))
        g.add_node("execute_knowledge", make_execute_knowledge_node(self.knowledge_handler))
        g.add_node("execute_chitchat", make_execute_chitchat_node(self.chit_chat_handler))
        g.add_node("execute_clarify", make_execute_clarify_node(self.clarify_responder))
        g.add_node("fallback", fallback_node)
        g.add_node("finalize", finalize_node)

        g.add_edge(START, "plan")

        g.add_conditional_edges("plan", self._route_after_plan, {
            "validate": "validate",
            "fallback": "fallback",
        })

        g.add_conditional_edges("validate", self._route_after_validate, {
            "execute_task": "execute_task",
            "execute_knowledge": "execute_knowledge",
            "execute_chitchat": "execute_chitchat",
            "execute_clarify": "execute_clarify",
        })

        g.add_edge("execute_task", "finalize")
        g.add_edge("execute_knowledge", "finalize")
        g.add_edge("execute_chitchat", "finalize")
        g.add_edge("execute_clarify", "finalize")
        g.add_edge("fallback", "finalize")
        g.add_edge("finalize", END)

        return g.compile()

    @staticmethod
    def _route_after_plan(state: Dict[str, Any]) -> str:
        return "fallback" if state.get("plan_failed") else "validate"

    @staticmethod
    def _route_after_validate(state: Dict[str, Any]) -> str:
        validation: TurnPlanValidationResult = state["validation"]
        if not validation.valid:
            return "execute_clarify"
        turn_plan: TurnPlan = state["turn_plan"]
        if turn_plan.task is not None:
            return "execute_task"
        if turn_plan.knowledge is not None:
            return "execute_knowledge"
        return "execute_chitchat"

    async def handle_dialogue(self, dialogue_state: DialogueState, user_message: UserMessage) -> ProcessResult:
        initial: DialogueGraphState = {
            "dialogue_state": dialogue_state,
            "user_message": user_message,
            "bot_messages": [],
            "plan_failed": False,
        }
        result = await self.graph.ainvoke(initial)
        return result["process_result"]

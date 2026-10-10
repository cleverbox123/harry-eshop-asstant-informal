from pathlib import Path

from app.agent.dialogue_engine import DialogueEngine
from app.plan.planner import TurnPlanner
from app.plan.turn_validator import TurnPlanValidator
from app.clarify.responder import ClarifyResponder
from app.task.handler import TaskHandler
from app.task.command.processor import CommandProcessor
from app.task.flow.executor import FlowExecutor
from app.task.flow.loader import FlowLoader
from app.task.action.builder import build_action_runner
from app.knowledge.handler import KnowLedgeHandler
from app.knowledge.intents import KNOWLEDGE_INTENTS
from app.knowledge.registry import KnowledgeProviderRegistry
from app.knowledge.provider import ProductAPIProvider, OrderAPIProvider, FAQProvider, RAGProvider
from app.knowledge.responder import KnowledgeResponder
from app.chitchat.handler import ChitChatHandler
from app.chitchat.responder import ChitChatResponder

PROJECT_DIR = Path(__file__).resolve().parents[2]
FLOW_CONFIG_DIR = PROJECT_DIR / "flow_config"
FLOW_CONFIG_FILES = ["system_flows.yml", "user_flows.yml"]


def build_dialogue_engine() -> DialogueEngine:
    flow_list = FlowLoader().load_many([FLOW_CONFIG_DIR / f for f in FLOW_CONFIG_FILES])
    return DialogueEngine(
        turn_planner=TurnPlanner(),
        turn_validator=TurnPlanValidator(),
        clarify_responder=ClarifyResponder(),
        task_handler=TaskHandler(
            flows=flow_list,
            processor=CommandProcessor(),
            action_runner=build_action_runner(),
            flow_executor=FlowExecutor(),
        ),
        knowledge_handler=KnowLedgeHandler(
            knowledge_intents=KNOWLEDGE_INTENTS,
            provider_registry=KnowledgeProviderRegistry(
                providers=[ProductAPIProvider(), OrderAPIProvider(), FAQProvider(), RAGProvider()]
            ),
            knowledge_responder=KnowledgeResponder(),
        ),
        chit_chat_handler=ChitChatHandler(responder=ChitChatResponder()),
    )

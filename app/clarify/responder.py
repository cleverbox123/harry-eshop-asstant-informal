import json

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.domain.state import DialogueState
from app.plan.turn_plan import ClarifyReason
from app.prompts.history_builder import HistoryBuilder
from app.prompts.loader import load_prompt
from app.infrastructure.llm import llm
from app.infrastructure.llm_resilience import resilient_invoke, LLMUnavailableError
from app.domain.messages import BotMessage


class ClarifyResponder:
    """


    """

    async def respond(self, state: DialogueState, reason: ClarifyReason) -> list[BotMessage]:

        clarify_message = self.build_clarify_message(reason=reason, state=state)
        user_message = state.pending_turn.user_message
        user_message_str = HistoryBuilder._render_user_message(user_message)
        history_str = HistoryBuilder.build(state.turns[-10:])


        prompt_text = load_prompt("clarify_respond")
        prompt_template = PromptTemplate.from_template(template=prompt_text, template_format="jinja2")
        chain = prompt_template | llm | StrOutputParser()

        async def _call() -> str:
            return await chain.ainvoke({
                "user_message": user_message_str,
                "history": history_str,

                "clarify_message": clarify_message,
                "reason": reason.value
            })

        try:
            rewritten = await resilient_invoke(_call, validate=lambda s: bool(s and s.strip()))
            return [BotMessage(text=rewritten)]
        except LLMUnavailableError:
            # 降级：LLM 不可用时直接使用确定性的澄清话术（无需模型）
            return [BotMessage(text=clarify_message)]


    def build_clarify_message(
            self,
            reason: ClarifyReason,
            state: DialogueState,
    ) -> str:
        if reason is ClarifyReason.MULTIPLE_TRACKS:
            return "你这次同时提到了多个方向。我们先处理一个，你想先办业务还是先咨询信息呢？"

        if reason is ClarifyReason.MISSING_KNOWLEDGE_INTENT:
            return "你是想了解商品信息、订单信息，还是售后配送规则呢？"

        if reason is ClarifyReason.MISSING_TRACK:
            return "你是想先处理业务问题，还是先咨询信息呢？"

        if reason is ClarifyReason.MISSING_TASK_COMMANDS:
            return "你这次是想办理什么业务呢？比如查订单、查物流，或者申请退款。"

        return "我还需要再确认一下你的意思，你可以换个更具体的说法告诉我。"

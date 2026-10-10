from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.domain.messages import UserMessage, BotMessage
from app.domain.state import Turn
from app.prompts.history_builder import HistoryBuilder
from app.prompts.loader import load_prompt
from app.infrastructure.llm import llm
from app.infrastructure.llm_resilience import resilient_invoke, LLMUnavailableError


class ChitChatResponder:

    # LLM 不可用时的确定性降级话术
    FALLBACK_TEXT = "抱歉，我这边暂时开小差了，请稍后再和我聊聊～"

    async def respond(self,
                      user_message: UserMessage,
                      recent_turns: list[Turn]):
        user_message = HistoryBuilder._render_user_message(user_message)
        history = HistoryBuilder.build(recent_turns)

        prompt_text = load_prompt("chitchat_respond")
        prompt = PromptTemplate.from_template(prompt_text, template_format="jinja2")
        chain = prompt | llm | StrOutputParser()

        async def _call() -> str:
            return await chain.ainvoke({
                "user_message": user_message,
                "history": history,
            })

        try:
            response = await resilient_invoke(_call, validate=lambda s: bool(s and s.strip()))
        except LLMUnavailableError:
            response = self.FALLBACK_TEXT

        return [BotMessage(text=response)]

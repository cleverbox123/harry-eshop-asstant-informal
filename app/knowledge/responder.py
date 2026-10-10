from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.infrastructure.llm import llm
from app.infrastructure.llm_resilience import resilient_invoke, LLMUnavailableError
from app.domain.messages import UserMessage, BotMessage
from app.domain.state import Turn
from app.prompts.history_builder import HistoryBuilder
from app.prompts.loader import  load_prompt
from app.knowledge.provider import KnowledgeChunk


class KnowledgeResponder:

    # LLM 不可用时的确定性降级话术
    FALLBACK_TEXT = "抱歉，智能助手暂时不可用，无法为你生成解答。请稍后再试，或换个说法描述你的问题。"

    async def respond(self,
                      user_message: UserMessage,
                      recent_turns: list[Turn],
                      chunks: list[KnowledgeChunk]
                      ) -> list[BotMessage]:
        # 准备提示词上下文
        user_message = HistoryBuilder._render_user_message(user_message)
        history = HistoryBuilder.build(recent_turns)
        knowledge_content = "\n\n".join([chunk.content for chunk in chunks])

        # 构造chain
        prompt_text = load_prompt("knowledge_respond")
        prompt = PromptTemplate.from_template(
            prompt_text,
            template_format="jinja2"
        )
        chain = prompt | llm | StrOutputParser()

        async def _call() -> str:
            return await chain.ainvoke({
                "user_message": user_message,
                "history": history,
                "knowledge_content": knowledge_content,
            })

        # 运行chain（带超时/重试；LLM 宕机或返回空内容时降级）
        try:
            response = await resilient_invoke(_call, validate=lambda s: bool(s and s.strip()))
        except LLMUnavailableError:
            response = self.FALLBACK_TEXT

        return [BotMessage(text=response)]

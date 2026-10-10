from app.domain.messages import BotMessage
from app.domain.state import DialogueState
from app.chitchat.responder import ChitChatResponder


class ChitChatHandler:
    def __init__(self, responder: ChitChatResponder):
        self.responder = responder

    async def handle(self, state: DialogueState) -> list[BotMessage]:
        pending_turn = state.pending_turn
        user_message = pending_turn.user_message
        recent_turns = state.turns[-5:]

        return await self.responder.respond(
            user_message=user_message,
            recent_turns=recent_turns,
        )

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any
from app.domain.contexts import TaskContext, SystemContext
from app.domain.messages import UserMessage, BotMessage


@dataclass(slots=True)
class Turn:
    turn_id: str
    user_message: UserMessage
    bot_messages: list[BotMessage]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "user_message": self.user_message.to_dict(),
            "bot_messages": [bot_message.to_dict() for bot_message in self.bot_messages]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Turn":
        return cls(
            turn_id=data['turn_id'],
            user_message=UserMessage.from_dict(data['user_message']),
            bot_messages=[BotMessage.from_dict(bot_msg_dict) for bot_msg_dict in data['bot_messages']]
        )


@dataclass(slots=True)
class DialogueState:
    sender_id: str
    session_id: str = ""
    create_at: float = field(default_factory=time.time)
    title: str = "新会话"
    active_task: TaskContext | None = None
    paused_tasks: list[TaskContext] = field(default_factory=list)
    active_system_task: SystemContext | None = None
    pending_turn: Turn | None = None
    turns: list[Turn] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "session_id": self.session_id,
            "create_at": self.create_at,
            "title": self.title,
            "active_task": self.active_task.to_dict() if self.active_task else None,
            "paused_tasks": [t.to_dict() for t in self.paused_tasks],
            "active_system_task": self.active_system_task.to_dict() if self.active_system_task else None,
            "turns": [t.to_dict() for t in self.turns],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DialogueState":
        return cls(
            sender_id=data['sender_id'],
            session_id=data.get('session_id', ''),
            create_at=data.get('create_at', time.time()),
            title=data.get('title', '新会话'),
            active_task=TaskContext.from_dict(data['active_task']) if data.get('active_task') else None,
            paused_tasks=[TaskContext.from_dict(t) for t in data.get('paused_tasks', [])],
            active_system_task=SystemContext.from_dict(data['active_system_task']) if data.get('active_system_task') else None,
            turns=[Turn.from_dict(t) for t in data.get('turns', [])],
            pending_turn=Turn.from_dict(data['pending_turn']) if data.get('pending_turn') else None,
        )

    # --------------任务相关--------------------------

    def start_active_system_task(self, active_system_task: SystemContext):
        self.active_system_task = active_system_task

    def end_active_system_task(self):
        self.active_system_task = None

    def start_active_task(self, active_task: TaskContext):
        self.active_task = active_task

    def end_active_task(self):
        self.active_task = None

    def interrupted_active_task(self):
        self.paused_tasks.append(self.active_task)
        self.active_task = None

    def resumed_active_task(self, flow_id: str | None = None) -> bool:
        if not self.paused_tasks:
            return False
        if flow_id is None:
            self.active_task = self.paused_tasks.pop()
            return True
        for i, paused_task in enumerate(self.paused_tasks):
            if paused_task.flow_id == flow_id:
                self.active_task = paused_task
                del self.paused_tasks[i]
                return True
        return False

    def cancel_active_task(self):
        self.active_task = None
        self.active_system_task = None

    # --------------槽位相关--------------------------

    def set_slots(self, slots: Dict[str, Any]):
        if self.active_task is not None:
            self.active_task.slots.update(slots)

    def remove_slot(self, slot_name: str):
        self.active_task.slots.pop(slot_name)

    # --------------当前信息--------------------------

    def current_active_task(self):
        return self.active_system_task or self.active_task

    # --------------turn相关--------------------------

    def begin_turn(self, message: UserMessage):
        self.pending_turn = Turn(turn_id=str(uuid.uuid4()), user_message=message, bot_messages=[])

    def commit_turn(self):
        if self.pending_turn is None:
            return
        self.turns.append(self.pending_turn)
        self.pending_turn = None

"""

消息类型：两种
UserMessage(用户)
BotMessage(机器人)

to_dict:将实例对象转成字典对象
from_dict:将字典对象转成实例对象

"""
from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass


class MessageType(Enum):
    TEXT = "text"  # 文本类型
    OBJECT = "object"  # 对象类型


@dataclass(slots=True)
class UserMessage:
    sender_id: str  # 用户ID(必填字段)
    session_id: str  # 会话ID(必填字段)
    message_id: str  # 消息ID(必填字段)
    type: MessageType  # 消息类型（text or object）必填字段
    text: str | None = None  # 文本消息

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "message_id": self.message_id,
            "session_id": self.session_id,
            "type": self.type.value,
            "text": self.text,

        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserMessage":
        return cls(
            sender_id=data['sender_id'],
            session_id=data['session_id'],
            message_id=data['message_id'],
            type=MessageType(data['type']),
            text=data.get('text'),

        )


@dataclass(slots=True)
class BotMessage:
    text: str | None = None               # 主要回复消息的内容


    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,


        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BotMessage":
        return cls(
            text=data.get('text'),

        )

@dataclass
class ProcessResult:
    sender_id: str                                 # 用户ID
    message_id: str
    session_id: str  # 会话ID(内部生成)
    messages: list[BotMessage]                     # 回复消息（机器人回复的所有消息都给前端）
    title: str | None = None                       # 会话标题（多会话列表展示）


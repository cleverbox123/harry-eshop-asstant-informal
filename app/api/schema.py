"""

定义接口数据模型
请求相关：
响应相关：
"""
from pydantic import BaseModel





class ChatRequest(BaseModel):
    sender_id: str  # 用户ID
    message_id: str | None = None  # 消息ID
    session_id: str | None = None  # 会话ID
    text: str | None = None  # 文本类型消息



class ChatBotMessage(BaseModel):
    text: str | None = None  # 现有能力：回复文本类型的消息



class ChatResponse(BaseModel):
    sender_id: str
    message_id: str
    session_id: str | None = None
    title: str | None = None  # 会话标题（多会话列表展示用）
    messages: list[ChatBotMessage]


# ------------------ 多会话（类 DeepSeek 侧边栏）------------------


class SessionItem(BaseModel):
    session_id: str
    title: str
    create_at: float
    updated_at: float


class SessionListResponse(BaseModel):
    sender_id: str
    sessions: list[SessionItem]


class SessionCreateRequest(BaseModel):
    sender_id: str
    title: str | None = None


class SessionRenameRequest(BaseModel):
    sender_id: str
    title: str


class SessionMessage(BaseModel):
    role: str  # user / assistant
    message_id: str | None = None
    type: str = "text"
    text: str | None = None


class SessionHistoryResponse(BaseModel):
    sender_id: str
    session_id: str
    title: str | None = None
    messages: list[SessionMessage]

from datetime import datetime

from app.model.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TEXT, String
from sqlalchemy.dialects.mysql import DATETIME as MySQLDateTime


class DialogueStateRecord(Base):
    __tablename__ = "dialogue_states"
    sender_id: Mapped[str] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(primary_key=True)
    create_at: Mapped[datetime] = mapped_column(MySQLDateTime(fsp=3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(MySQLDateTime(fsp=3), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False, default="新会话")
    state_json: Mapped[str] = mapped_column(TEXT, nullable=False, default={})  # 数据库长文本类型

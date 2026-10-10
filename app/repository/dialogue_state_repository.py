import json
import uuid
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.mysql import insert
from app.domain.state import DialogueState
from app.model.dialogue_state_record import DialogueStateRecord


def _dt_to_float(dt: datetime) -> float:
    return dt.timestamp()


def _float_to_dt(ts: float) -> datetime:
    return datetime.fromtimestamp(ts)


class DialogueStateRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def load(self, sender_id: str, session_id: str) -> DialogueState:
        """
        读操作
        :return:
        """

        # 1. 定义sql
        sql = select(DialogueStateRecord).where(DialogueStateRecord.sender_id == sender_id, DialogueStateRecord.session_id == session_id)

        # 2. 执行sql
        result = await self.session.execute(sql)

        # 3. 获取结果
        record = result.scalar_one_or_none()

        if record:
            state_dict = json.loads(record.state_json)
            dialogue_state = DialogueState.from_dict(state_dict)
            # 数据库列是会话元信息的权威来源
            dialogue_state.sender_id = sender_id
            dialogue_state.session_id = session_id
            dialogue_state.title = record.title
            return dialogue_state

        return DialogueState(sender_id=sender_id, session_id=session_id)

    async def save(self, dialogue_state: DialogueState):
        """
        写操作(插入、修改)
        传统：插入之前先查询该条件（sender_id）对应的记录是否存在，如果不存在 则插入，反之修改
        进阶：负责将插入sql直接升级为修改sql(主键重复机制判断)
        :return:
        """

        # 1. 得到DialogueState的json字符串
        session_id = dialogue_state.session_id
        state_json: str = json.dumps(dialogue_state.to_dict(), ensure_ascii=False)

        # 2. 定义插入的sql语句
        insert_stmt = insert(DialogueStateRecord).values(
            sender_id=dialogue_state.sender_id,
            session_id=session_id,
            create_at=_float_to_dt(dialogue_state.create_at),
            updated_at=datetime.now(),
            title=dialogue_state.title,
            state_json=state_json,
        )

        # 3. 升级update语句的sql
        update_stmt = insert_stmt.on_duplicate_key_update(
            state_json=insert_stmt.inserted.state_json,
            title=insert_stmt.inserted.title,
            updated_at=insert_stmt.inserted.updated_at,
        )

        # 4. 执行sql
        await  self.session.execute(update_stmt)

        # 5. 提交
        await self.session.commit()

    # ------------------ 多会话管理 ------------------

    async def list_sessions(self, sender_id: str) -> List[Dict[str, Any]]:
        """
        查询某用户的全部会话，按最近活跃时间倒序
        """
        sql = (
            select(
                DialogueStateRecord.session_id,
                DialogueStateRecord.title,
                DialogueStateRecord.create_at,
                DialogueStateRecord.updated_at,
            )
            .where(DialogueStateRecord.sender_id == sender_id)
            .order_by(DialogueStateRecord.updated_at.desc())
        )
        result = await self.session.execute(sql)
        return [
            {
                "session_id": row.session_id,
                "title": row.title,
                "create_at": _dt_to_float(row.create_at),
                "updated_at": _dt_to_float(row.updated_at),
            }
            for row in result.all()
        ]

    async def get_session_meta(self, sender_id: str, session_id: str) -> Dict[str, Any] | None:
        """
        读取会话元信息，不存在返回 None
        """
        sql = select(
            DialogueStateRecord.session_id,
            DialogueStateRecord.title,
            DialogueStateRecord.create_at,
            DialogueStateRecord.updated_at,
        ).where(
            DialogueStateRecord.sender_id == sender_id,
            DialogueStateRecord.session_id == session_id,
        )
        result = await self.session.execute(sql)
        row = result.one_or_none()
        if row is None:
            return None
        return {
            "session_id": row.session_id,
            "title": row.title,
            "create_at": _dt_to_float(row.create_at),
            "updated_at": _dt_to_float(row.updated_at),
        }

    async def create_session(self, sender_id: str, title: str = "新会话") -> Dict[str, Any]:
        """
        新建一个空会话（不写入 state_json，等待首条消息落库）
        """
        session_id = str(uuid.uuid4())
        now = datetime.now()
        now_float = now.timestamp()
        insert_stmt = insert(DialogueStateRecord).values(
            sender_id=sender_id,
            session_id=session_id,
            create_at=now,
            updated_at=now,
            title=title,
            state_json=json.dumps(
                DialogueState(sender_id=sender_id, session_id=session_id, create_at=now_float, title=title).to_dict(),
                ensure_ascii=False,
            ),
        )
        await self.session.execute(insert_stmt)
        await self.session.commit()
        return {
            "session_id": session_id,
            "title": title,
            "create_at": now_float,
            "updated_at": now_float,
        }

    async def rename_session(self, sender_id: str, session_id: str, title: str) -> bool:
        """
        重命名会话，返回是否命中记录
        """
        sql = (
            update(DialogueStateRecord)
            .where(
                DialogueStateRecord.sender_id == sender_id,
                DialogueStateRecord.session_id == session_id,
            )
            .values(title=title, updated_at=datetime.now())
        )
        result = await self.session.execute(sql)
        await self.session.commit()
        return result.rowcount > 0

    async def delete_session(self, sender_id: str, session_id: str) -> bool:
        """
        删除会话，返回是否命中记录
        """
        sql = delete(DialogueStateRecord).where(
            DialogueStateRecord.sender_id == sender_id,
            DialogueStateRecord.session_id == session_id,
        )
        result = await self.session.execute(sql)
        await self.session.commit()
        return result.rowcount > 0

    async def load_messages(self, sender_id: str, session_id: str) -> List[Dict[str, Any]]:
        """
        读取某个会话的历史消息（按对话轮次展开为扁平列表）
        """
        dialogue_state = await self.load(sender_id, session_id)

        messages: List[Dict[str, Any]] = []
        for turn in dialogue_state.turns:
            user_message = turn.user_message
            messages.append({
                "role": "user",
                "message_id": user_message.message_id,
                "type": user_message.type.value,
                "text": user_message.text,
            })
            for bot_message in turn.bot_messages:
                messages.append({
                    "role": "assistant",
                    "type": "text",
                    "text": bot_message.text,
                })
        return messages

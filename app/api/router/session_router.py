"""
多会话管理接口（类 DeepSeek 侧边栏）：
列表、新建、重命名、删除、历史消息
"""
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_dialogue_state_repository
from app.api.schema import (
    SessionCreateRequest,
    SessionHistoryResponse,
    SessionItem,
    SessionListResponse,
    SessionMessage,
    SessionRenameRequest,
)
from app.repository.dialogue_state_repository import DialogueStateRepository

router = APIRouter()


@router.get("/api/sessions", response_model=SessionListResponse)
async def list_sessions(
        sender_id: str,
        repository: DialogueStateRepository = Depends(get_dialogue_state_repository),
) -> SessionListResponse:
    sessions = await repository.list_sessions(sender_id)
    return SessionListResponse(
        sender_id=sender_id,
        sessions=[SessionItem(**session) for session in sessions],
    )


@router.post("/api/sessions", response_model=SessionItem)
async def create_session(
        request: SessionCreateRequest,
        repository: DialogueStateRepository = Depends(get_dialogue_state_repository),
) -> SessionItem:
    session = await repository.create_session(request.sender_id, request.title or "新会话")
    return SessionItem(**session)


@router.get("/api/sessions/{session_id}/messages", response_model=SessionHistoryResponse)
async def get_session_history(
        session_id: str,
        sender_id: str,
        repository: DialogueStateRepository = Depends(get_dialogue_state_repository),
) -> SessionHistoryResponse:
    meta = await repository.get_session_meta(sender_id, session_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="会话不存在")

    messages = await repository.load_messages(sender_id, session_id)
    return SessionHistoryResponse(
        sender_id=sender_id,
        session_id=session_id,
        title=meta["title"],
        messages=[SessionMessage(**message) for message in messages],
    )


@router.patch("/api/sessions/{session_id}", response_model=SessionItem)
async def rename_session(
        session_id: str,
        request: SessionRenameRequest,
        repository: DialogueStateRepository = Depends(get_dialogue_state_repository),
) -> SessionItem:
    title = request.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="标题不能为空")

    renamed = await repository.rename_session(request.sender_id, session_id, title[:64])
    if not renamed:
        raise HTTPException(status_code=404, detail="会话不存在")

    return SessionItem(**await repository.get_session_meta(request.sender_id, session_id))


@router.delete("/api/sessions/{session_id}")
async def delete_session(
        session_id: str,
        sender_id: str,
        repository: DialogueStateRepository = Depends(get_dialogue_state_repository),
) -> dict:
    deleted = await repository.delete_session(sender_id, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"session_id": session_id, "deleted": True}

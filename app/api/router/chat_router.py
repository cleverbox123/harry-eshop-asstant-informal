import uuid
from fastapi import APIRouter, Depends
from app.api.schema import ChatResponse, ChatRequest, ChatBotMessage
from app.domain.messages import UserMessage, MessageType,  ProcessResult
from app.api.dependencies import get_dialogue_service
from app.service.dialogue_service import DialogueService

router = APIRouter()


# 1. 定义路由接口


@router.post("/api/chat")
async def chat_endpoint(
        chat_request: ChatRequest,
        service: DialogueService = Depends(get_dialogue_service)
) -> ChatResponse:

    # 1. 处理输入接口模型
    user_message = _build_user_message(chat_request)

    # 2. 业务处理
    process_result: ProcessResult = await service.handle_message(user_message)

    # 3. 处理输出接口模型
    return _build_chat_response(process_result)


def _build_user_message(chat_request: ChatRequest) -> UserMessage:
    """
    将请求数据模型转换为领域数据模型 供业务使用
    :param chat_request:
    :return:
    """

    return UserMessage(
        sender_id=chat_request.sender_id,
        message_id=chat_request.message_id if chat_request.message_id else str(uuid.uuid4()),
        session_id=chat_request.session_id if chat_request.session_id else None,
        type=MessageType.TEXT if chat_request.text else MessageType.OBJECT,
        text=chat_request.text,

    )


def _build_chat_response(process_result: ProcessResult) -> ChatResponse:
    return ChatResponse(
        sender_id=process_result.sender_id,
        message_id=process_result.message_id,
        session_id=process_result.session_id,
        title=process_result.title,
        messages=[
            ChatBotMessage(
                text=bot_msg.text,
            )
            for bot_msg in process_result.messages
        ]
    )

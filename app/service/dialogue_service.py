import logging
import time
import uuid

from app.domain.messages import UserMessage, ProcessResult
from app.domain.state import DialogueState
from app.repository.dialogue_state_repository import DialogueStateRepository
from app.agent.dialogue_engine import DialogueEngine

logger = logging.getLogger(__name__)

DEFAULT_SESSION_TITLE = "新会话"
SESSION_TITLE_MAX_LENGTH = 30





class DialogueService:
    """
    处理对话的业务类
    """

    def __init__(self, dialogue_state_repository: DialogueStateRepository,
                 dialogue_engine: DialogueEngine):
        self.dialogue_repository = dialogue_state_repository
        self.dialogue_engine = dialogue_engine

    async def handle_message(self, user_message: UserMessage) -> ProcessResult:
        """
        核心处理逻辑(IO：很慢/计算:调用LLM以及执行引擎、比较慢)
        :param user_message:
        :return:
        """

        logger.info("收到消息 sender_id=%s message_id=%s session_id=%s type=%s",
                    user_message.sender_id, user_message.message_id, user_message.session_id, user_message.type.value)

        # 1. 如果session为空，以用户id，session为uuid，创建时间创建一个新对话
        # 如果session不为空，从数据库中加载对话
        dialogue_state = await self._get_or_create_dialogue_state(user_message)

        # 2. 开始新的 turn
        dialogue_state.begin_turn(user_message)

        # 3. 调用引擎使用对话状态对象 进行业务的各种计算操作(引擎)
        process_result = await self.dialogue_engine.handle_dialogue(dialogue_state, user_message)

        # 4. 提交 turn
        dialogue_state.commit_turn()

        # 5. 首条用户消息作为会话标题（多会话列表展示）
        self._apply_session_title(dialogue_state, user_message)

        # 6. 以新的state_json更新数据库
        await self.dialogue_repository.save(dialogue_state)

        # 7. 回填会话信息，便于前端同步侧边栏
        process_result.session_id = dialogue_state.session_id
        process_result.title = dialogue_state.title

        return process_result

    @staticmethod
    def _apply_session_title(dialogue_state: DialogueState, user_message: UserMessage) -> None:
        """
        会话仍是默认标题时，用首条用户消息生成标题
        :param dialogue_state:
        :param user_message:
        :return:
        """
        if dialogue_state.title != DEFAULT_SESSION_TITLE:
            return
        text = (user_message.text or "").strip()
        if not text:
            return
        dialogue_state.title = text[:SESSION_TITLE_MAX_LENGTH]

    async def _get_or_create_dialogue_state(self, user_message: UserMessage) -> DialogueState:
        """
        获取或创建对话状态
        :param user_message:
        :return:
        """
        if user_message.session_id:
            # 从数据库加载已有的对话状态
            dialogue_state = await self.dialogue_repository.load(
                sender_id=user_message.sender_id,
                session_id=user_message.session_id
            )
            logger.info("加载已有对话状态 sender_id=%s session_id=%s",
                       user_message.sender_id, user_message.session_id)
        else:
            # 创建新的对话状态
            session_id = str(uuid.uuid4())
            dialogue_state = DialogueState(
                sender_id=user_message.sender_id,
                session_id=session_id,
                create_at=time.time()
            )


            logger.info("创建新对话状态 sender_id=%s session_id=%s",
                       user_message.sender_id, session_id)

        return dialogue_state

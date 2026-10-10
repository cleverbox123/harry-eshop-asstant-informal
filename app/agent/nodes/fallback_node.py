import logging
from typing import Any, Dict

from app.domain.messages import BotMessage

logger = logging.getLogger(__name__)

PLAN_FALLBACK_TEXT = (
    "抱歉，智能助手暂时不可用，我无法理解你这次的请求。"
    "你可以稍后再试，或直接发送订单/商品卡片来办理业务。"
)


def fallback_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.warning("进入 fallback 节点：意图识别失败")
    return {"bot_messages": [BotMessage(text=PLAN_FALLBACK_TEXT)]}

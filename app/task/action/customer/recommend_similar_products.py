from typing import Any

from app.domain.state import DialogueState
from app.task.action.base import Action, ActionResult
from app.task.action.customer.shared import fetch_product, fetch_similar_products
from app.domain.messages import BotMessage


class RecommendSimilarProductsAction(Action):
    name = "action_recommend_similar_products"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        调用电商中台的相似商品接口，返回真实推荐列表
        :param state:
        :param action_kwargs:
        :return:
        """
        product_id = state.active_task.slots.get("product_id") if state.active_task else None
        if not product_id:
            return ActionResult(messages=[BotMessage(text="请告诉我想找哪件商品的相似款，提供商品编号即可。")])

        product = await fetch_product(product_id)
        similar = await fetch_similar_products(product_id)
        label = str((product or {}).get("title") or "").strip() or str(product_id)

        if not similar:
            return ActionResult(messages=[BotMessage(text=f"暂时没有与「{label}」相似的在售商品，你可以看看其他分类。")])

        lines = [
            f"{index}. {item.get('title', '未知商品')}（¥{item.get('price', '?')}）{item.get('selling_point', '')}".strip()
            for index, item in enumerate(similar, start=1)
        ]
        text = f"为「{label}」找到 {len(similar)} 款相似商品：\n" + "\n".join(lines)
        return ActionResult(messages=[BotMessage(text=text)])

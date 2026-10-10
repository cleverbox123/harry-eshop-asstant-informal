from typing import Any

from app.infrastructure.commerce import (  # noqa: F401  供业务动作复用
    fetch_logistics,
    fetch_order,
    fetch_product,
    fetch_similar_products,
)


def _build_order_summary(payload: dict[str, Any]) -> str:
    parts = []
    if payload.get("amount"):
        parts.append(f"订单金额 ¥{payload['amount']}")
    items = payload.get("items") or []
    if items:
        titles = [str(item.get("title_snapshot") or "").strip() for item in items[:2] if item.get("title_snapshot")]
        if titles:
            parts.append("商品：" + "、".join(titles))
    return "。".join(parts) + "。" if parts else ""

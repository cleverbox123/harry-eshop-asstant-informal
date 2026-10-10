"""
电商中台接口访问（订单 / 物流 / 商品 / 相似商品）。

响应约定：{"data": ...}；接口不可达或结构不符时返回 None / []，由调用方决定降级话术。
"""
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from app.config.config import settings
from app.infrastructure import http

logger = logging.getLogger(__name__)


def _base_url() -> str:
    return settings.commerce_api_base_url.rstrip("/")


def _extract_data(result: Any) -> Optional[Dict[str, Any]]:
    data = result.get("data") if isinstance(result, dict) else None
    return data if isinstance(data, dict) else None


async def fetch_order(order_id: str) -> Optional[Dict[str, Any]]:
    if not order_id:
        return None
    try:
        r = await http.http_client.get(f"{_base_url()}/orders/{quote(order_id)}")
        return _extract_data(r.json())
    except Exception as e:
        logger.warning("查询订单失败 order=%s err=%s", order_id, e)
        return None


async def fetch_logistics(order_id: str) -> Optional[Dict[str, Any]]:
    if not order_id:
        return None
    try:
        r = await http.http_client.get(f"{_base_url()}/orders/{quote(order_id)}/logistics")
        return _extract_data(r.json())
    except Exception as e:
        logger.warning("查询物流失败 order=%s err=%s", order_id, e)
        return None


async def fetch_product(product_id: str) -> Optional[Dict[str, Any]]:
    if not product_id:
        return None
    try:
        r = await http.http_client.get(f"{_base_url()}/products/{quote(product_id)}")
        return _extract_data(r.json())
    except Exception as e:
        logger.warning("查询商品失败 product=%s err=%s", product_id, e)
        return None


async def fetch_similar_products(product_id: str, limit: int = 3) -> List[Dict[str, Any]]:
    if not product_id:
        return []
    try:
        r = await http.http_client.get(
            f"{_base_url()}/products/{quote(product_id)}/similar",
            params={"limit": limit},
        )
        data = r.json().get("data") if isinstance(r.json(), dict) else None
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.warning("查询相似商品失败 product=%s err=%s", product_id, e)
        return []

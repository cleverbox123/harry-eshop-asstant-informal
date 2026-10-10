"""
电商中台替身服务（测试数据）。

接口与 app/infrastructure/commerce.py 的约定一致：{"code": 0, "data": ...}。
"""
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, Query

app = FastAPI(title="Mock Commerce API")

PRODUCTS: Dict[str, Dict[str, Any]] = {
    "P1001": {
        "product_id": "P1001",
        "title": "轻羽无线降噪耳机 Pro",
        "price": 499.0,
        "category": "audio",
        "status": "on_sale",
        "selling_point": "40dB 主动降噪，30 小时续航",
    },
    "P1002": {
        "product_id": "P1002",
        "title": "轻羽无线降噪耳机 Air",
        "price": 299.0,
        "category": "audio",
        "status": "on_sale",
        "selling_point": "轻量佩戴，通话降噪",
    },
    "P1003": {
        "product_id": "P1003",
        "title": "声阔头戴式监听耳机",
        "price": 699.0,
        "category": "audio",
        "status": "on_sale",
        "selling_point": "录音室级调音，可换线设计",
    },
    "P1004": {
        "product_id": "P1004",
        "title": "云厨不粘炒锅 32cm",
        "price": 189.0,
        "category": "kitchen",
        "status": "on_sale",
        "selling_point": "麦饭石涂层，少油烟",
    },
    "P1005": {
        "product_id": "P1005",
        "title": "云厨铸铁炖锅 24cm",
        "price": 259.0,
        "category": "kitchen",
        "status": "on_sale",
        "selling_point": "锁水焖炖，受热均匀",
    },
    "P1006": {
        "product_id": "P1006",
        "title": "净厨刀具七件套",
        "price": 329.0,
        "category": "kitchen",
        "status": "off_sale",
        "selling_point": "德国钢材，一体成型",
    },
}

ORDERS: Dict[str, Dict[str, Any]] = {
    "SO20261001001": {
        "order_id": "SO20261001001",
        "status": "shipped",
        "status_desc": "已发货",
        "amount": 798.0,
        "items": [
            {"title_snapshot": "轻羽无线降噪耳机 Pro", "price": 499.0, "quantity": 1},
            {"title_snapshot": "轻羽无线降噪耳机 Air", "price": 299.0, "quantity": 1},
        ],
    },
    "SO20261001002": {
        "order_id": "SO20261001002",
        "status": "pending_payment",
        "status_desc": "待付款",
        "amount": 189.0,
        "items": [
            {"title_snapshot": "云厨不粘炒锅 32cm", "price": 189.0, "quantity": 1},
        ],
    },
    "SO20261001003": {
        "order_id": "SO20261001003",
        "status": "completed",
        "status_desc": "已完成",
        "amount": 259.0,
        "items": [
            {"title_snapshot": "云厨铸铁炖锅 24cm", "price": 259.0, "quantity": 1},
        ],
    },
}

LOGISTICS: Dict[str, Dict[str, Any]] = {
    "SO20261001001": {
        "tracking_number": "SF1358274659321",
        "logistics_company": "顺丰速运",
        "status": "in_transit",
        "status_desc": "运输中（已到达杭州转运中心）",
    },
    "SO20261001003": {
        "tracking_number": "YT7733920154488",
        "logistics_company": "圆通速递",
        "status": "delivered",
        "status_desc": "已签收（本人签收）",
    },
}


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/orders/{order_id}")
async def get_order(order_id: str) -> Dict[str, Any]:
    return {"code": 0, "data": ORDERS.get(order_id)}


@app.get("/orders/{order_id}/logistics")
async def get_logistics(order_id: str) -> Dict[str, Any]:
    return {"code": 0, "data": LOGISTICS.get(order_id)}


@app.get("/products/{product_id}")
async def get_product(product_id: str) -> Dict[str, Any]:
    return {"code": 0, "data": PRODUCTS.get(product_id)}


@app.get("/products/{product_id}/similar")
async def get_similar(product_id: str, limit: int = Query(default=3, ge=1, le=10)) -> Dict[str, Any]:
    product = PRODUCTS.get(product_id)
    if product is None:
        return {"code": 0, "data": []}
    similar: List[Dict[str, Any]] = [
        p for pid, p in PRODUCTS.items()
        if pid != product_id and p["category"] == product["category"] and p["status"] == "on_sale"
    ]
    return {"code": 0, "data": similar[:limit]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=18081)

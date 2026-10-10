from dataclasses import dataclass, field
@dataclass
class KnowledgeIntent:
    id: str
    description: str
    provider_ids: list[str] = field(default_factory=list)


KNOWLEDGE_INTENTS: dict[str, KnowledgeIntent] = {
    "product_info": KnowledgeIntent(
        id="product_info", description="咨询某个具体商品的价格、卖点、规格、库存等（通常需要商品ID或商品链接）",
        provider_ids=["api.product"],
    ),
    "order_info": KnowledgeIntent(
        id="order_info", description="查询某一笔具体订单的状态或物流（针对用户自己的订单，需要订单号）",
        provider_ids=["api.order"],
    ),
    "refund_policy": KnowledgeIntent(
        id="refund_policy", description="退款政策咨询：退款条件、退款到账时间、退款进度规则等",
        provider_ids=["faq.default", "rag.default"],
    ),
    "return_policy": KnowledgeIntent(
        id="return_policy", description="退货政策咨询：七天无理由退货条件、退货运费承担、换货规则等",
        provider_ids=["faq.default", "rag.default"],
    ),
    "shipping_policy": KnowledgeIntent(
        id="shipping_policy", description="配送与运费政策咨询：包邮门槛、运费标准、发货时效、偏远地区配送规则等",
        provider_ids=["faq.default", "rag.default"],
    ),
    "platform_rule": KnowledgeIntent(
        id="platform_rule", description="平台通用规则与流程说明（不针对某笔具体订单）：订单状态有哪些及各自含义、下单/支付/售后流程、平台介绍、活动规则等",
        provider_ids=["rag.default"],
    ),
    "general_ecommerce_info": KnowledgeIntent(
        id="general_ecommerce_info", description="其他电商通用信息咨询：发票、积分、优惠券叠加、投诉维权等",
        provider_ids=["faq.default", "rag.default"],
    ),
}
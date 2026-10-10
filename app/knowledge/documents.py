"""
知识库测试语料：FAQ（售后政策类）与 RAG（平台通用知识类）。

启动时由 app.knowledge.seed 写入 Qdrant，供 FAQProvider / RAGProvider 检索。
"""
from typing import List, TypedDict

FAQ_COLLECTION = "faq_kb"
RAG_COLLECTION = "rag_kb"


class FaqDocument(TypedDict):
    id: str
    question: str
    answer: str


class RagDocument(TypedDict):
    id: str
    title: str
    content: str


FAQ_DOCUMENTS: List[FaqDocument] = [
    {
        "id": "faq-refund-time",
        "question": "退款申请通过后多久能到账？",
        "answer": "退款审核通过后，原路退回：余额支付实时到账，银行卡或信用卡一般 1-7 个工作日到账，"
                  "具体以银行处理时间为准。超过 7 个工作日未到账可联系人工客服核查。",
    },
    {
        "id": "faq-cancel-before-ship",
        "question": "订单还没发货可以取消吗？",
        "answer": "订单状态为待付款或待发货时，可以在订单详情页直接取消订单，取消后款项原路退回。"
                  "订单一旦发货则需要走退货流程。",
    },
    {
        "id": "faq-return-7day",
        "question": "七天无理由退货需要满足什么条件？",
        "answer": "自签收之日起 7 天内，商品保持完好、不影响二次销售（吊牌包装齐全、未洗涤使用），"
                  "可申请七天无理由退货。生鲜、定制类、拆封的音像制品等除外。",
    },
    {
        "id": "faq-return-freight",
        "question": "退货的运费由谁承担？",
        "answer": "因商品质量问题或发错货产生的退货，运费由平台承担；七天无理由退货的非包邮商品，"
                  "寄回运费由买家承担，包邮商品买家仅需承担寄回运费。",
    },
    {
        "id": "faq-shipping-time",
        "question": "下单后多久发货？",
        "answer": "现货商品一般在付款后 48 小时内发货，预售商品以商品页标注的发货时间为准。"
                  "大促期间发货时效可能顺延，以订单页提示为准。",
    },
    {
        "id": "faq-shipping-fee",
        "question": "运费和包邮规则是怎样的？",
        "answer": "单笔订单满 99 元包邮，未满 99 元收取 8 元基础运费；偏远地区（新疆、西藏、内蒙古等）"
                  "满 199 元包邮，未满收取 15 元运费。",
    },
    {
        "id": "faq-invoice",
        "question": "如何开具发票？",
        "answer": "订单完成后在订单详情页申请开票，支持电子普通发票与增值税专用发票。"
                  "电子发票一般 1 个工作日内开具并发送到预留邮箱。",
    },
    {
        "id": "faq-coupon-stack",
        "question": "优惠券可以和满减活动叠加使用吗？",
        "answer": "平台券与店铺券可叠加使用，但同一订单每类券限用一张；优惠券与满减活动是否叠加"
                  "以券面说明为准，标注不可叠加的券按优惠金额较高者生效。",
    },
    {
        "id": "faq-points",
        "question": "会员积分怎么获得和使用？",
        "answer": "确认收货后按实付金额 1 元积 1 分；积分可在下单时抵扣现金，100 积分抵 1 元，"
                  "单笔订单最多抵扣订单金额的 30%，积分有效期为获得后 12 个月。",
    },
    {
        "id": "faq-complaint-channel",
        "question": "遇到纠纷如何投诉维权？",
        "answer": "可先联系店铺客服协商；协商不成在订单页发起平台介入，平台客服会在 24 小时内响应，"
                  "一般 3 个工作日内给出处理结论。",
    },
]

RAG_DOCUMENTS: List[RagDocument] = [
    {
        "id": "rag-platform-intro",
        "title": "平台简介与业务范围",
        "content": "本平台是综合类电商购物平台，覆盖数码家电、服饰鞋包、美妆个护、食品生鲜、家居日用等品类，"
                   "支持自营与第三方商家两种经营模式，自营商品由平台负责发货与售后。",
    },
    {
        "id": "rag-order-status",
        "title": "订单状态流转说明",
        "content": "订单状态依次为：待付款、待发货、已发货、已完成、已取消。付款后进入待发货，"
                   "商家出库后变为已发货并生成物流单号，买家确认收货或发货满 15 天后自动变为已完成。",
    },
    {
        "id": "rag-category-guide",
        "title": "商品分类与选购指南",
        "content": "数码家电类建议优先选择自营渠道以保障保修；服饰类注意查看尺码表与买家秀；"
                   "生鲜类注意配送范围与保鲜时效；大件家居类注意是否含送装服务。",
    },
    {
        "id": "rag-payment",
        "title": "支付方式使用说明",
        "content": "支持余额、银行卡、信用卡、第三方支付等方式。大额订单可能触发风控校验，"
                   "需短信验证；分期付款仅支持信用卡与部分第三方信用支付产品。",
    },
    {
        "id": "rag-delivery-range",
        "title": "物流配送范围与时效",
        "content": "自营商品由平台仓配一体配送，全国大部分城市次日或隔日达；第三方商家使用合作快递，"
                   "一般 3-5 天送达。乡镇地区可能由合作网点代收。",
    },
    {
        "id": "rag-aftersale-overview",
        "title": "售后服务总览",
        "content": "售后类型包括仅退款、退货退款、换货、维修四类。待发货订单支持仅退款；"
                   "已收货订单按七天无理由或质量问题发起对应售后，审核进度可在售后详情页查看。",
    },
    {
        "id": "rag-privacy",
        "title": "隐私与个人信息保护",
        "content": "平台仅收集完成交易必需的个人信息，收货信息在物流面单上默认脱敏展示，"
                   "用户可在设置中关闭个性化推荐并申请导出或删除个人数据。",
    },
    {
        "id": "rag-promotion-types",
        "title": "促销活动类型说明",
        "content": "常见促销包括满减、直降、秒杀、预售定金膨胀、跨店每满减。秒杀商品限购一件且不支持"
                  "价保；预售商品尾款支付后按尾款支付时间计算发货时效。",
    },
]


def faq_embedding_text(doc: FaqDocument) -> str:
    return f"{doc['question']} {doc['answer']}"


def rag_embedding_text(doc: RagDocument) -> str:
    return f"{doc['title']} {doc['content']}"

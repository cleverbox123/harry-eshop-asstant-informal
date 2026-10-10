"""
本地替身服务：电商中台 API 与文本向量化服务。

仅用于开发/测试环境，让业务流程与知识库检索在没有真实中台和模型服务时也能跑通。
启动方式：
    python -m mock_services.commerce_api      # 端口 18081
    python -m mock_services.embedding_server  # 端口 8081
"""

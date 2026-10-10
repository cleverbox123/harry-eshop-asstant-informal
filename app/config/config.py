from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str

    llm_model: str
    llm_base_url: str
    llm_api_key: str

    # ---- LLM 容错（有默认值，.env 中可选覆盖）----
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 2
    llm_retry_backoff_seconds: float = 0.5

    # ---- 电商中台接口（有默认值，.env 中可选覆盖）----
    commerce_api_base_url: str = "http://localhost:18081"

    # ---- 向量库 Qdrant（有默认值，.env 中可选覆盖）----
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_embedding_size: int = 1024
    qdrant_local_path: str = "data/qdrant"  # Qdrant 服务不可达时的本地持久化目录

    # ---- 文本向量化服务（有默认值，.env 中可选覆盖）----
    embedding_host: str = "localhost"
    embedding_port: int = 8081
    embedding_model: str = "BAAI/bge-large-zh-v1.5"

    # ---- 知识检索（有默认值，.env 中可选覆盖）----
    # 真实 bge-large-zh-v1.5：相关文档相似度通常 0.55~0.85，阈值 0.45 可兼顾召回与去噪；
    # 若退回到离线词法向量（区分度低），需把阈值降到 0.15 左右。
    knowledge_top_k: int = 3
    knowledge_score_threshold: float = 0.45

    # ---- 日志相关（有默认值，.env 中可选覆盖）----
    log_level: str = "INFO"  # 日志级别：DEBUG/INFO/WARNING/ERROR
    log_file: str = "logs/app.log"  # 日志文件路径（相对项目根）；置空则仅输出到控制台
    log_max_bytes: int = 10 * 1024 * 1024  # 单个日志文件最大字节数（轮转阈值）
    log_backup_count: int = 5  # 轮转保留的历史日志文件数


settings = Settings()

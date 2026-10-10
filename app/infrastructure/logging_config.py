"""
统一日志配置。

- 通过 setup_logging() 使用 dictConfig 装配 root logger（控制台 + 可选轮转文件）。
- 日志级别、文件路径、轮转参数均可由 settings（.env / 环境变量）控制。
- 关闭对已有 logger 的禁用（disable_existing_loggers=False），与 uvicorn 自带日志共存。
- 收敛第三方噪声日志（sqlalchemy / httpx / httpcore）。
"""
import logging
import logging.config
from pathlib import Path
from typing import Any, Dict

from app.config.config import settings

# app/infrastructure/logging_config.py -> parents[2] 即项目根目录
PROJECT_DIR = Path(__file__).resolve().parents[2]

_configured = False


def _resolve_log_file(log_file: str) -> Path | None:
    if not log_file:
        return None
    path = Path(log_file)
    if not path.is_absolute():
        path = PROJECT_DIR / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def setup_logging(force: bool = False) -> None:
    """
    装配全局日志。幂等：重复调用默认直接返回（force=True 可强制重配）。
    """
    global _configured
    if _configured and not force:
        return

    log_file = _resolve_log_file(settings.log_file)

    handlers: Dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        }
    }
    root_handlers = ["console"]

    if log_file is not None:
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": str(log_file),
            "maxBytes": settings.log_max_bytes,
            "backupCount": settings.log_backup_count,
            "encoding": "utf-8",
        }
        root_handlers.append("file")

    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": handlers,
        "root": {"level": settings.log_level.upper(), "handlers": root_handlers},
        "loggers": {
            # SQL 语句噪声较大，默认收敛；需要排查时把 root/该 logger 调到 INFO/DEBUG
            "sqlalchemy.engine": {"level": "WARNING"},
            "httpx": {"level": "WARNING"},
            "httpcore": {"level": "WARNING"},
        },
    }

    logging.config.dictConfig(config)
    _configured = True

    logging.getLogger(__name__).info(
        "日志已初始化: level=%s, file=%s", settings.log_level.upper(), log_file or "console-only"
    )

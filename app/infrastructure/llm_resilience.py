"""
LLM 容错工具。

统一封装「超时 + 有限次重试 + 结果校验」，用于所有调用大模型的边界。
当大模型服务器宕机（连接失败/超时）或返回不稳定数据（空内容、无法解析、
结构缺失）时，重试若干次后抛出 LLMUnavailableError，由调用方决定降级策略。
"""
import asyncio
import logging
from typing import Awaitable, Callable, Optional, TypeVar

from app.config.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class LLMUnavailableError(RuntimeError):
    """LLM 服务在重试后仍不可用，或返回的结果不可用。"""


async def resilient_invoke(
    factory: Callable[[], Awaitable[T]],
    *,
    validate: Optional[Callable[[T], bool]] = None,
    timeout: Optional[float] = None,
    max_retries: Optional[int] = None,
    backoff: Optional[float] = None,
) -> T:
    """
    以容错方式调用 LLM。

    :param factory: 无参可调用对象，每次调用返回一个 awaitable（便于重试时重新发起）
    :param validate: 结果校验函数，返回 False 视为「不稳定数据」触发重试
    :param timeout: 单次调用超时（秒），默认取配置
    :param max_retries: 失败后的重试次数（不含首次），默认取配置
    :param backoff: 重试退避基数（秒），线性递增，默认取配置
    :return: 校验通过的结果
    :raises LLMUnavailableError: 所有尝试均失败
    """
    timeout = settings.llm_timeout_seconds if timeout is None else timeout
    max_retries = settings.llm_max_retries if max_retries is None else max_retries
    backoff = settings.llm_retry_backoff_seconds if backoff is None else backoff

    attempts = max_retries + 1
    last_error: Optional[BaseException] = None

    for attempt in range(1, attempts + 1):
        try:
            result = await asyncio.wait_for(factory(), timeout=timeout)
            if validate is not None and not validate(result):
                raise ValueError("LLM 返回结果未通过校验（可能为空或结构不稳定）")
            return result
        except asyncio.TimeoutError as e:
            last_error = e
            logger.warning("LLM 调用超时 (第 %s/%s 次)", attempt, attempts)
        except Exception as e:  # noqa: BLE001 - 统一收敛为可降级信号
            last_error = e
            logger.warning("LLM 调用失败 (第 %s/%s 次): %s", attempt, attempts, e)

        if attempt < attempts:
            await asyncio.sleep(backoff * attempt)

    raise LLMUnavailableError(f"LLM 服务不可用: {last_error}") from last_error

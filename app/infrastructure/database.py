from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker

from app.config.config import settings


class MysqlClientManager:
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker] = None

    def _get_url(self) -> str:
        return (f"mysql+asyncmy://{settings.mysql_user}"
                f":{settings.mysql_password}@{settings.mysql_host}"
                f":{settings.mysql_port}/{settings.mysql_database}?charset=utf8mb4")

    def init(self):
        self.engine = create_async_engine(
            url=self._get_url(),
            pool_size=10,
            pool_pre_ping=True,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=True,
            autobegin=True,
            expire_on_commit=False,
        )

    async def close(self):
        if self.engine:
            await self.engine.dispose()

    def get_session(self) -> AsyncSession:
        return self.session_factory()

    def get_engine(self) -> AsyncEngine:
        return self.engine


mysql_client_manager = MysqlClientManager()


def async_session():
    return mysql_client_manager.get_session()

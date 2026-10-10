from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.database import mysql_client_manager
from app.infrastructure.http import init_http_client, close_http_client
from app.infrastructure.logging_config import setup_logging
from app.knowledge.seed import seed_knowledge
from app.api.router.chat_router import router as chat_router
from app.api.router.session_router import router as session_router
from app.api.dependencies import init_dialogue_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    mysql_client_manager.init()
    init_http_client()
    await seed_knowledge()
    init_dialogue_engine()
    yield
    await mysql_client_manager.close()
    await close_http_client()


app = FastAPI(
    title="LangGraph App",
    description="LangGraph AI Agent Application",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(session_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

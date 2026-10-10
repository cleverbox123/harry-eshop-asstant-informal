"""
文本向量化替身服务（端口 8081，契约与 TEI 兼容）。

优先加载 sentence-transformers 的 settings 模型（BAAI/bge-large-zh-v1.5）；
模型不可用时回退到基于 jieba 分词的词哈希向量化（1024 维、L2 归一化、跨进程稳定），
保证离线环境也能完成知识库写入与检索。
"""
import hashlib
import math
import os
from typing import List, Union

import jieba
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-zh-v1.5")
DIM = int(os.getenv("EMBEDDING_DIM", "1024"))

app = FastAPI(title="Mock Embedding Service")

_backend = "lexical-fallback"
_model = None


def _load_sentence_transformers() -> None:
    global _backend, _model
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(MODEL_NAME, local_files_only=True)
        if int(model.get_sentence_embedding_dimension()) != DIM:
            raise ValueError(f"模型维度 {model.get_sentence_embedding_dimension()} 与配置 {DIM} 不一致")
        _model = model
        _backend = "sentence-transformers"
    except Exception:
        _model = None
        _backend = "lexical-fallback"


def _token_index(token: str) -> int:
    digest = hashlib.md5(token.encode("utf-8")).hexdigest()
    return int(digest, 16) % DIM


def _lexical_vector(text: str) -> List[float]:
    vector = [0.0] * DIM
    for token in jieba.lcut(text):
        token = token.strip()
        if token:
            vector[_token_index(token)] += 1.0
    for i in range(len(text) - 1):
        gram = text[i:i + 2].strip()
        if gram:
            vector[_token_index(gram)] += 0.5
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


class EmbedRequest(BaseModel):
    inputs: Union[str, List[str]]


@app.post("/embed")
async def embed(request: EmbedRequest) -> dict:
    texts = [request.inputs] if isinstance(request.inputs, str) else list(request.inputs)
    if _model is not None:
        vectors = _model.encode(texts, normalize_embeddings=True).tolist()
    else:
        vectors = [_lexical_vector(text) for text in texts]
    return {"embeddings": vectors, "model": MODEL_NAME, "backend": _backend}


@app.get("/info")
async def info() -> dict:
    return {"model": MODEL_NAME, "backend": _backend, "dim": DIM}


if __name__ == "__main__":
    _load_sentence_transformers()
    uvicorn.run(app, host="0.0.0.0", port=8081)

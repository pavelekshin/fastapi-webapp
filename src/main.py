from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as aioredis
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src import redis
from src.exception_handlers import register_error_handlers
from src.settings import settings
from src.views import account, home, package, search, auth

REDIS_URL = str(settings.REDIS_URL)


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    pool = aioredis.ConnectionPool.from_url(
        REDIS_URL,
        max_connections=10,
        decode_responses=True,
    )
    redis.redis_client = aioredis.Redis(connection_pool=pool)
    yield
    await pool.disconnect()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=None,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.include_router(home.router)
app.include_router(package.router)
app.include_router(account.router)
app.include_router(search.router)
app.include_router(auth.router)

register_error_handlers(app=app)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

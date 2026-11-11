# 설정의 책임 분리 (Separation of Concerns)
import os
from dotenv import load_dotenv
import redis.asyncio as redis
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))        # 문자열 → 숫자
REDIS_DB = int(os.getenv("REDIS_DB", 0))               # 문자열 → 숫자
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None   # 빈 값이면 None

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    encoding="utf-8",
    decode_responses=True
)

@asynccontextmanager
async def start_redis_client(app: FastAPI):
    try:
        await redis_client.ping()      # 연결 확인
        print("Redis 연결 성공!")
        app.state.redis = redis_client
        yield
    finally:
        await redis_client.aclose()    # 서버 종료 시 연결 닫기

def get_redis_db(request: Request):
    return request.app.state.redis
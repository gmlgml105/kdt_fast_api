from fastapi import FastAPI
from app.security.cors import setup_cors
from app.security.security_headers import set_up_security
from contextlib import asynccontextmanager
from app.infrastructure.postgresql import engine, Base
from app.infrastructure.redis import start_redis_client
from app.infrastructure.s3 import start_s3_client
import app.models
from app.apis import member_api, post_api, auth_api, s3_api, ai_api
from app.services.ai_service import ai_service_instance

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 비동기 연결
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("PostgreSQL 연결 성공!")

    async with start_redis_client(app):
        print("Redis 연결 성공!")

        async with start_s3_client(app):
            print("S3 연결 성공!")

             # 4. 전이학습 모델 로드
            ai_service_instance.load_alexnet_model()
            print("Alexnet 모델 성공")

            yield

app = FastAPI(
    lifespan=lifespan,
    title="Fast API Service",
    description="파이썬 백엔드 구축!😎",
    version="1.0.0",
    docs_url="/docs", # Swagger
    redoc_url="/redoc"
)

setup_cors(app) 
set_up_security(app)

@app.get("/")
def health_check():
    return {"message": "Hello World"}

app.include_router(member_api.router, prefix="/members", tags=["members"])
app.include_router(post_api.router, prefix="/posts", tags=["posts"])
app.include_router(auth_api.router, prefix="/auth", tags=["auth"])
app.include_router(s3_api.router, prefix="/uploads", tags=["uploads"])
app.include_router(ai_api.router, prefix="/ai", tags=["AI"])

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
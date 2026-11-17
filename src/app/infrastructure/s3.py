import os
from dotenv import load_dotenv
from botocore.config import Config
import aioboto3
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

load_dotenv()

# 환경 변수로 들고오기
AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION=os.getenv("AWS_REGION")

session = aioboto3.Session()

s3_config = Config(
    signature_version="s3v4",
    s3 = {"addressing_style" : "virtual"}
)

@asynccontextmanager
async def start_s3_client(app: FastAPI):
    async with session.client(
        "s3",
        aws_access_key_id = AWS_ACCESS_KEY_ID,
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
        region_name = AWS_REGION,
        config = s3_config
    ) as client:
        app.state.s3 = client
        print("S3 클라이어느 연결 완료")

        try:
            yield

        finally:
            pass


# 의존성 팩토리 함수
def get_s3_client(request: Request):
    return request.app.state.s3


    

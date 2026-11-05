from fastapi import Depends
from app.repositories.default_repository import DefaultRepository, get_default_repository


# 예외처리
# 트랜잭션 관리
class DefaultService:

    def __init__(self, repo: DefaultRepository):
        self.repo = repo



# 레포지토리 주입 팩토리 함수
def get_default_service(repo: DefaultRepository = Depends(get_default_repository)):
    return DefaultService(repo)
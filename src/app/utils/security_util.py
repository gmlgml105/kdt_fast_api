from passlib.context import CryptContext

# CryptContext 사용하는 이유
# 1. 권장 방법이 아닌 코드를 사용할 때 자동 업데이트
# 2. 알고리즘 추상화
#     - 나중에 알고리즘이 바뀌어도 코드 수정이 최소화

pws_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pws_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pws_context.verify(plain_password, hashed_password)
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from app.repositories.redis_repository import get_redis_repository, RedisRepository
from app.services.member_service import get_member_service, MemberService
from app.utils.security_util import verify_password
from app.utils.jwt_token_util import (
    parse_token, generate_access_token, generate_refresh_token, reissue_access_token
)
from app.schemas.auth_schema import JwtTokenDTO, LoginRequestDTO, SocialLoginRequestDTO
from app.schemas.member_schema import MemberClaimDTO, MemberCreateDTO

load_dotenv()
TOKEN_BLACKLIST_PREFIX = os.getenv("TOKEN_BLACKLIST_PREFIX")
REFRESH_TOKEN_PREFIX = os.getenv("REFRESH_TOKEN_PREFIX")

# 예외처리
# 트랜잭션 관리
class AuthService:

    def __init__(
            self, 
            redis_repo: RedisRepository,
            member_service: MemberService
        ):
        self.redis_repo = redis_repo
        self.member_service = member_service


    # redis에 refresh_token 저장
    # key - 콜론 체이닝
    async def save_refresh_token(self, member_id: int, refresh_token: str) -> None:
        try:
            key=f"{REFRESH_TOKEN_PREFIX}{member_id}"
            ex = 60 * 60 * 24 * 30 # 30일
            await self.redis_repo.set(key, refresh_token, ex=ex)
            
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="save_refresh_token 오류"
            )

    # redis에 등록된 refresh_token가 유효한지 검사
    async def validate_refresh_token(self, member_id: int, refresh_token: str) -> bool:
        key=f"{REFRESH_TOKEN_PREFIX}{member_id}"
        saved_token = await self.redis_repo.get(key)
        return refresh_token == saved_token


    # redis에 등록된 refresh_token을 삭제 
    async def delete_refresh_token(self, member_id: int):
        key=f"{REFRESH_TOKEN_PREFIX}{member_id}"
        await self.redis_repo.delete(key)


    # redis에 등록된 access_token 무효화 -> 블랙리스트로 등록(로그아웃)
    async def save_blacklisted_token(self, access_token: str) -> None:
        try:
            key = f"{TOKEN_BLACKLIST_PREFIX}{access_token}"
            ex = 60 * 60 * 24

            await self.redis_repo.set(key, "blacklisted", ex=ex)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="save_blacklisted_token 오류"
            )


    # redis에 블랙리스트로 등록되어있는지 확인
    async def is_blacklisted_token(self, access_token: str) -> bool:
        key = f"{TOKEN_BLACKLIST_PREFIX}{access_token}"
        # True -> 블랙리스트
        # False -> 사용가능
        return await self.redis_repo.exists(key)

    # 로그인
    async def login(self, login_request_dto: LoginRequestDTO) -> JwtTokenDTO:
        # 1. 회원 조회
        member_in_db = await self.member_service.get_member_by_email_and_provider(
            login_request_dto.member_email, 
            login_request_dto.member_provider
        )

        # 2. 비밀번호 검증(단방향 검사)
        if not verify_password(
            login_request_dto.member_password, # 플레인 비밀번호
            member_in_db.member_password # 암호화된 비밀번호
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="verify_password 비밀번호 불일치"
            )

        # 3. JWT 토큰 만들기
        # - 유저의 정보 중 최소한의 정보만 claim에 담기
        member_id = member_in_db.id
        claims = MemberClaimDTO(
            id=member_id,
            member_email=member_in_db.member_email,
            member_provider=member_in_db.member_provider
        )

        # - 유틸 함수를 이용해서 토큰을 만든다(refresh, access)
        access_token = generate_access_token(claims)
        refresh_token = generate_refresh_token(claims)

        # 4. refresh를 redis에 저장
        await self.save_refresh_token(member_id, refresh_token)

        # 5. 토큰 반환
        return JwtTokenDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )


    # 소셜 로그인
    async def social_login_or_none(self, social_member: SocialLoginRequestDTO) -> JwtTokenDTO | None:
        member_in_db = await self.member_service.get_member_by_email_and_provider(
            social_member.member_email,
            social_member.member_provider
        )

        if not member_in_db:
            return None

        member_id = int(member_in_db.id)
        member_email=str(member_in_db.member_email)
        member_provider=str(member_in_db.member_provider)

        claims = MemberClaimDTO(
            id=member_id,
            member_email=member_email,
            member_provider=member_provider
        )

        access_token = generate_access_token(claims)
        refresh_token = generate_refresh_token(claims)
        await self.save_refresh_token(member_id, refresh_token)

        return JwtTokenDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )


     # 소셜 로그인(회원가입 버전)
    async def social_login_or_join(self, social_member: SocialLoginRequestDTO) -> JwtTokenDTO | None:

        member_email = social_member.member_email
        member_provider = social_member.member_provider
        member_provider_id = social_member.member_provider_id

        member_in_db = await self.member_service.get_member_by_email_and_provider(
            member_email=member_email,
            member_provider=member_provider,
        )

        if not member_in_db:
            new_member = MemberCreateDTO(
                member_email=member_email,
                member_provider=member_provider,
                member_provider_id=member_provider_id
            )
            claims = await self.member_service.join(new_member)
            member_id = claims.id

        else:
            member_id = int(member_in_db.id)
            member_email=str(member_in_db.member_email)
            member_provider=str(member_in_db.member_provider)

            claims = MemberClaimDTO(
                id=member_id,
                member_email=member_email,
                member_provider=member_provider
            )

        access_token = generate_access_token(claims)
        refresh_token = generate_refresh_token(claims)
        await self.save_refresh_token(member_id, refresh_token)

        return JwtTokenDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )


    # 로그아웃 (토큰이 만료·무효여도 실패하지 않게 처리)
    async def logout(self, access_token: str | None, refresh_token: str | None) -> None:
        # 1. access_token은 블랙리스트에 등록
        if access_token:
            await self.save_blacklisted_token(access_token)

        # 2. refresh_token에서 회원 id를 꺼내 redis에서 삭제
        if refresh_token:
            try:
                member_id = parse_token(refresh_token).id
                await self.delete_refresh_token(member_id)
            except Exception:
                pass
    

    # refresh -> access 재발급
    async def refresh(self, refresh_token: str) -> str:
        payload = parse_token(refresh_token)
        member_id = payload.id

        is_valid: bool = await self.validate_refresh_token(member_id, refresh_token)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 refresh token"
            )
        
        return reissue_access_token(refresh_token)

# 레포지토리 주입 팩토리 함수
def get_auth_service(
    redis_repo: RedisRepository = Depends(get_redis_repository),
    member_service: MemberService = Depends(get_member_service)
):
    return AuthService(redis_repo, member_service)




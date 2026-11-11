import os
from dotenv import load_dotenv
from fastapi import APIRouter, Query, Depends, Response, Request, HTTPException
import secrets
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.member_schema import MemberClaimDTO
from app.enums.member_enum import MemberProvider
from app.schemas.auth_schema import JwtTokenDTO, LoginRequestDTO, SocialLoginRequestDTO
from app.services.auth_service import AuthService, get_auth_service
from app.dependencies.auth_dependency import get_current_member, get_tokens

# 소셜 로그인용
import httpx # 추가 요청
from fastapi.responses import RedirectResponse, JSONResponse # 페이지 전환
from urllib.parse import urlencode # 요청주소를 조합하기 위한 라이브러리


load_dotenv()
router = APIRouter()

@router.post(
    "/login",
    response_model=ApiResponseDTO,
    summary="로컬 로그인",
    responses={
        200: {
            "description": "로그인 성공"
        },
        400: {
            "description": "비밀번호 불일치 등 잘못된 요청",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "아이디 또는 비밀번호가 일치하지 않습니다."
                    }
                }
            }
        },
        404: {
            "description": "존재하지 않는 회원",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "회원이 존재하지 않습니다."
                    }
                }
            }
        }
    }
)
async def login(
    login_member: LoginRequestDTO,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    login_member.member_provider = MemberProvider.LOCAL.value
    tokens = await auth_service.login(login_member)

    access_token = tokens.access_token
    refresh_token = tokens.refresh_token

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 30
    )

    return ApiResponseDTO(
        success=True,
        message="로그인 성공"
    )


GOOGLE_AUTH_URL=os.getenv("GOOGLE_AUTH_URL")
GOOGLE_TOKEN_URL=os.getenv("GOOGLE_TOKEN_URL")
GOOGLE_USERINFO_URL=os.getenv("GOOGLE_USERINFO_URL")
GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI=os.getenv("GOOGLE_REDIRECT_URI")
FRONTEND_URL=os.getenv("FRONTEND_URL")


# 구글 로그인
# /auth/google/
@router.get(
    "/google",
    summary="구글 로그인"
)
async def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }

    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)


# 구글 로그인 콜백
# /auth/google/callback
@router.get(
    "/google/callback",
    summary="구글 로그인 콜백"
)
async def google_login_callback(
    code: str,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )

        token_data = token_res.json()
        access_token = token_data.get("access_token")

        async with httpx.AsyncClient() as client:
            user_res = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )

        user = user_res.json()
        user_params = {
            "member_email": user.get("email"),
            "member_provider": MemberProvider.GOOGLE.value,
            "member_provider_id": user.get("sub")
        }

        return await _handle_social_login(user_params, auth_service)



# 환경 변수로 들고오기
KAKAO_CLIENT_ID=os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET=os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI=os.getenv("KAKAO_REDIRECT_URI")
KAKAO_AUTH_URL=os.getenv("KAKAO_AUTH_URL")
KAKAO_TOKEN_URL=os.getenv("KAKAO_TOKEN_URL")
KAKAO_USERINFO_URL=os.getenv("KAKAO_USERINFO_URL")

@router.get("/kakao", summary="카카오 로그인 리다이렉트")
async def kakao_login():
    params = {
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "response_type": "code",
    }

    url = f"{KAKAO_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/kakao/callback", summary="카카오 로그인 콜백")
async def kakao_login_callback(
    code: str,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            KAKAO_TOKEN_URL,
            data={
                "code": code,
                "client_id": KAKAO_CLIENT_ID,
                "client_secret": KAKAO_CLIENT_SECRET,
                "redirect_uri": KAKAO_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )

        token_data = token_res.json()
        access_token = token_data.get("access_token")

        async with httpx.AsyncClient() as client:
            user_res = await client.get(
                KAKAO_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )

        user = user_res.json()
        kakao_account = user.get("kakao_account") or {}
        member_email = kakao_account.get("email")
        member_profile_id = str(user.get("id"))

        if not member_email:
            print("kakao user", user)
            raise HTTPException(status_code=400, detail="카카오 계정의 이메일 정보를 가져오지 못했습니다.")

        user_params = {
            "member_email": member_email,
            "member_provider": MemberProvider.KAKAO.value,
            "member_provider_id": member_profile_id
        }

    return await _handle_social_login(user_params, auth_service)


NAVER_CLIENT_ID=os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET=os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI=os.getenv("NAVER_REDIRECT_URI")
NAVER_AUTH_URL=os.getenv("NAVER_AUTH_URL")
NAVER_TOKEN_URL=os.getenv("NAVER_TOKEN_URL")
NAVER_USERINFO_URL=os.getenv("NAVER_USERINFO_URL")


@router.get("/naver", summary="네이버 로그인 리다이렉트")
async def naver_login():
    params = {
        "client_id": NAVER_CLIENT_ID,
        "redirect_uri": NAVER_REDIRECT_URI,
        "response_type": "code",
        "state": secrets.token_urlsafe(16),   # 네이버는 state 필수
    }

    url = f"{NAVER_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/naver/callback", summary="네이버 로그인 콜백")
async def naver_login_callback(
    code: str,
    state: str,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            NAVER_TOKEN_URL,
            data={
                "code": code,
                "client_id": NAVER_CLIENT_ID,
                "client_secret": NAVER_CLIENT_SECRET,
                "redirect_uri": NAVER_REDIRECT_URI,
                "grant_type": "authorization_code",
                "state": state,
            }
        )

        token_data = token_res.json()
        access_token = token_data.get("access_token")

        async with httpx.AsyncClient() as client:
            user_res = await client.get(
                NAVER_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )

        user = user_res.json()
        print("naver user", user)

        naver_user = user.get("response") or {}
        member_email = naver_user.get("email")
        member_profile_id = str(naver_user.get("id"))

        if not member_email:
            raise HTTPException(status_code=400, detail="네이버 계정의 이메일 정보를 가져오지 못했습니다.")

        user_params = {
            "member_email": member_email,
            "member_provider": MemberProvider.NAVER.value,
            "member_provider_id": member_profile_id
        }

    return await _handle_social_login_or_join(user_params, auth_service) 


# 로그아웃
@router.post(
    "/logout",
    summary="로그아웃",
    response_model=ApiResponseDTO,
)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    # 로그인 상태 확인 없이 진행 (토큰이 만료·무효여도 로그아웃은 항상 성공)
    try:
        await auth_service.logout(
            request.cookies.get("access_token"),
            request.cookies.get("refresh_token"),
        )
    except Exception as e:
        print("logout cleanup skipped:", e)

    # 로그인 때 set_cookie와 같은 옵션으로 삭제
    response.delete_cookie("access_token", httponly=True, secure=False, samesite="lax")
    response.delete_cookie("refresh_token", httponly=True, secure=False, samesite="lax")

    return ApiResponseDTO(
        success=True,
        message="로그아웃 성공"
    )


@router.post(
    "/refresh",
    response_model=ApiResponseDTO,
    summary="토큰 재발급"
)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    # access_token이 만료돼도 재발급할 수 있도록 refresh_token 쿠키만 확인
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="refresh token이 없습니다.")
    try:
        access_token = await auth_service.refresh(refresh_token)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60 * 24 
        )

        return ApiResponseDTO(
            success=True,
            message="Access Token 재발급 성공"
        )
    
    except Exception as e:
        print("refresh failed:", e)
        # 쿠키를 지우는 401 응답 (프론트에서 response.ok == false 로 판단)
        error_response = JSONResponse(
            status_code=401,
            content={"detail": "Refresh Token 만료"}
        )
        error_response.delete_cookie("access_token", httponly=True, secure=False, samesite="lax")
        error_response.delete_cookie("refresh_token", httponly=True, secure=False, samesite="lax")
        return error_response



async def _handle_social_login(user_params: dict, auth_service: AuthService):
    social_member = SocialLoginRequestDTO.model_validate(user_params)
    tokens = await auth_service.social_login_or_none(social_member)

    # 비회원
    if not tokens:
        url = f"{FRONTEND_URL}/join-additional?{urlencode(user_params)}"
        return RedirectResponse(url)

    # 기존 회원 
    access_token = tokens.access_token
    refresh_token = tokens.refresh_token

    redirect_response = RedirectResponse(url=FRONTEND_URL)
    redirect_response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 
    )

    redirect_response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 30
    )

    return redirect_response

async def _handle_social_login_or_join(user_params: dict, auth_service: AuthService):
    social_member = SocialLoginRequestDTO.model_validate(user_params)
    tokens = await auth_service.social_login_or_join(social_member)

    access_token = tokens.access_token
    refresh_token = tokens.refresh_token

    redirect_response = RedirectResponse(url=FRONTEND_URL)
    redirect_response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 
    )

    redirect_response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 30
    )

    return redirect_response





























# 매번 로그인이 필요한 페이지들은 토큰 가져와야한다.
# 토큰을 디코드해서 payload가 필요하다.
# 한 번에 처리하자!
# 1. request -> access_token -> decode -> member claim

import os
from dotenv import load_dotenv
from fastapi import Response, Request, HTTPException, status

from app.schemas.member_schema import MemberClaimDTO
from app.schemas.auth_schema import JwtTokenDTO
from app.utils.jwt_token_util import parse_token

def get_current_member(request: Request) -> MemberClaimDTO:
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="get_current_member 로그인 세션이 만료되었습니다."
        )

    try: 
        claims = parse_token(access_token)
        return claims

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="get_current_member parse_token 유효하지 않은 토큰입니다."
        )

# 2. request -> access_token, refresh_token(JwtTokenDTO)
def get_tokens(request: Request) -> JwtTokenDTO:
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
                raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail="get_current_member 로그인 세션이 만료되었습니다."
                )
        return JwtTokenDTO(
             access_token=access_token,
             refresh_token=refresh_token
        )
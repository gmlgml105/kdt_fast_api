import os
from dotenv import load_dotenv
from fastapi import Response, Request, HTTPException, status

from app.schemas.member_schema import MemberClaimDTO
from app.schemas.auth_schema import JwtTokenDTO
from app.utils.jwt_token_util import parse_token

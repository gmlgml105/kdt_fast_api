from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # 클릭 재킹 방지
        response.headers["X-Frame-Options"] = "DENY"
        # MIME 스니핑 방지
        response.headers["X-Content-Type-Options"] = "nosniff"
        # XSS 방지(CSP)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' 'unsafe-inline' https:;"
        )
        return response

# 보안 미들웨어
def set_up_security(app: FastAPI):
    app.add_middleware(SecurityHeadersMiddleware)
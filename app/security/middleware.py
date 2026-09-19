from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from app.security.jwt import decode_access_token


class SlidingWindowRateLimiter:
    """Limitador local; produção com múltiplas réplicas deve usar armazenamento compartilhado."""

    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> int | None:
        now = monotonic()
        cutoff = now - window_seconds
        with self._lock:
            timestamps = self._requests[key]
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()
            if len(timestamps) >= limit:
                return max(1, int(window_seconds - (now - timestamps[0])) + 1)
            timestamps.append(now)
        return None

    def clear(self) -> None:
        with self._lock:
            self._requests.clear()


rate_limiter = SlidingWindowRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        window_seconds: int,
        default_limit: int,
        login_limit: int,
        client_token_limit: int,
    ) -> None:
        super().__init__(app)
        self.window_seconds = window_seconds
        self.default_limit = default_limit
        self.login_limit = login_limit
        self.client_token_limit = client_token_limit

    def _policy(self, path: str) -> tuple[str, int]:
        if path == "/api/v1/auth/token":
            return "human-login", self.login_limit
        if path == "/api/v1/auth/client-token":
            return "m2m-token", self.client_token_limit
        return "default", self.default_limit

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)
        policy, limit = self._policy(request.url.path)
        client_host = request.client.host if request.client else "unknown"
        retry_after = rate_limiter.check(
            f"{client_host}:{policy}",
            limit,
            self.window_seconds,
        )
        if retry_after is not None:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Limite de requisições excedido"},
                headers={"Retry-After": str(retry_after)},
            )
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        return response


class JWTContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.jwt_payload = None
        authorization = request.headers.get("Authorization", "")
        if authorization.lower().startswith("bearer "):
            try:
                request.state.jwt_payload = decode_access_token(authorization[7:].strip())
            except HTTPException as exc:
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"detail": exc.detail},
                    headers=exc.headers,
                )
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        return response

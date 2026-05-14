"""Rate Limiting Configuration.

Exposes a shared Limiter instance to be used across all routers.

By default the client IP comes from ``request.client.host``. Reading
``X-Forwarded-For`` is opt-in via ``Settings.rate_limit_trust_forwarded_for`` and
must only be enabled behind a **trusted** reverse proxy that sets/forwards that
header safely; otherwise clients can spoof IPs and bypass limits.
"""

from fastapi import Request
from slowapi import Limiter

from app.core.settings import get_settings


def rate_limit_key_func(request: Request) -> str:
    """Resolve client identity for SlowAPI; conservative default."""
    settings = get_settings()
    if settings.rate_limit_trust_forwarded_for:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# Global default limit of 100 requests per minute per IP (or XFF-first-hop when trusted)
limiter = Limiter(key_func=rate_limit_key_func, default_limits=["100/minute"])

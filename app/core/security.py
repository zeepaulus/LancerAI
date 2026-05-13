"""Auth primitives: password hashing and JWT helpers.

Uses bcrypt directly (avoids passlib/bcrypt>=4.0 incompatibility).
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.settings import get_settings

# Claims controlled by the server — must never originate from caller-supplied ``extra_claims``.
RESERVED_JWT_CLAIM_KEYS = frozenset({"sub", "tenant_id", "role", "exp", "iat", "nbf"})


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt for safe storage."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True iff ``plain`` matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except (ValueError, TypeError):
        # Invalid hash/salt or wrong types — treat as verification failure.
        return False


def create_access_token(
    subject: str,
    tenant_id: str,
    role: str = "user",
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Sign and return a short-lived access token."""
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.auth_access_token_ttl_minutes)

    if extra_claims:
        overlap = RESERVED_JWT_CLAIM_KEYS.intersection(extra_claims.keys())
        if overlap:
            sorted_overlap = ", ".join(sorted(overlap))
            raise ValueError(
                f"extra_claims must not contain reserved JWT claim keys: {sorted_overlap}. "
                "These claims are set only by the server."
            )

    now = datetime.now(UTC)
    payload: dict[str, Any] = dict(extra_claims) if extra_claims else {}
    payload.update(
        {
            "sub": subject,
            "tenant_id": tenant_id,
            "role": role,
            "iat": now,
            "exp": expire,
        }
    )

    return jwt.encode(payload, settings.auth_secret_key, algorithm=settings.auth_jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate ``token``; raise jwt.InvalidTokenError subclass on failure."""
    settings = get_settings()
    return jwt.decode(token, settings.auth_secret_key, algorithms=[settings.auth_jwt_algorithm], options={"verify_signature": True})

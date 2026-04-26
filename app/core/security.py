"""Auth primitives: password hashing and JWT helpers.

TODO:
    - Implement ``hash_password`` / ``verify_password`` (bcrypt or argon2).
    - Implement ``create_access_token`` / ``decode_access_token`` (PyJWT).
    - Token claims should at least carry: sub (user_id), tenant_id, role, exp.
"""

from typing import Any


def hash_password(plain: str) -> str:
    """Hash a plaintext password for safe storage."""
    raise NotImplementedError("security.hash_password is not implemented yet.")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True iff ``plain`` matches the stored hash."""
    raise NotImplementedError("security.verify_password is not implemented yet.")


def create_access_token(
    subject: str,
    tenant_id: str,
    role: str = "user",
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Sign and return a short-lived access token."""
    raise NotImplementedError("security.create_access_token is not implemented yet.")


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate ``token``; raise on failure."""
    raise NotImplementedError("security.decode_access_token is not implemented yet.")

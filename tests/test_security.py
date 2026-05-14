"""Tests for app/core/security.py — hashing and JWT primitives."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.security import (
    RESERVED_JWT_CLAIM_KEYS,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_verify_correct_password(self) -> None:
        hashed = hash_password("my-secret")
        assert verify_password("my-secret", hashed) is True

    def test_reject_wrong_password(self) -> None:
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_hashes_are_unique(self) -> None:
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # bcrypt uses random salt

    def test_invalid_hash_format_returns_false(self) -> None:
        assert verify_password("anything", "not-a-real-hash") is False


class TestJWTTokens:
    def test_roundtrip_sub_and_tenant(self) -> None:
        token = create_access_token("user-1", "tenant-1")
        payload = decode_access_token(token)
        assert payload["sub"] == "user-1"
        assert payload["tenant_id"] == "tenant-1"
        assert payload["role"] == "user"
        assert "iat" in payload

    def test_extra_claims_merged_and_visible(self) -> None:
        token = create_access_token("user-1", "tenant-1", extra_claims={"plan": "pro"})
        payload = decode_access_token(token)
        assert payload["plan"] == "pro"
        assert payload["sub"] == "user-1"

    def test_extra_claims_reserved_sub_raises(self) -> None:
        with pytest.raises(ValueError, match="reserved JWT claim"):
            create_access_token("user-1", "tenant-1", extra_claims={"sub": "evil"})

    def test_extra_claims_reserved_role_exp_raises(self) -> None:
        with pytest.raises(ValueError, match="reserved JWT claim"):
            create_access_token("user-1", "tenant-1", extra_claims={"role": "admin"})
        with pytest.raises(ValueError, match="reserved JWT claim"):
            create_access_token(
                "user-1",
                "tenant-1",
                extra_claims={"exp": datetime.now(UTC) + timedelta(days=365)},
            )

    def test_reserved_claim_keys_documented(self) -> None:
        assert {"sub", "tenant_id", "role", "exp", "iat", "nbf"} <= RESERVED_JWT_CLAIM_KEYS

    def test_expired_token_raises(self) -> None:
        from app.core.settings import get_settings

        s = get_settings()
        expired_payload = {
            "sub": "u",
            "tenant_id": "t",
            "role": "user",
            "exp": datetime.now(UTC) - timedelta(seconds=1),
        }
        token = jwt.encode(expired_payload, s.auth_secret_key, algorithm=s.auth_jwt_algorithm)
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_access_token(token)

    def test_tampered_token_raises(self) -> None:
        token = create_access_token("user-1", "tenant-1")
        parts = token.split(".")
        tampered = parts[0] + "." + parts[1] + ".badsignature"
        with pytest.raises(jwt.InvalidSignatureError):
            decode_access_token(tampered)

    def test_garbage_token_raises(self) -> None:
        with pytest.raises(jwt.InvalidTokenError):
            decode_access_token("not.a.jwt")

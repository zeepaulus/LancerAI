"""Security checks for job-matching URL fetch helpers."""

import socket

from app.service.matching.service import _is_public_http_url


def test_public_http_url_allows_public_dns(monkeypatch) -> None:
    def fake_getaddrinfo(hostname: str, port: int | None):
        assert hostname == "example.com"
        return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 0))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    assert _is_public_http_url("https://example.com/jobs/123") is True


def test_public_http_url_rejects_local_and_private_targets(monkeypatch) -> None:
    def fake_getaddrinfo(hostname: str, port: int | None):
        assert hostname == "internal.example"
        return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("10.0.0.5", 0))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    assert _is_public_http_url("http://localhost:8000/admin") is False
    assert _is_public_http_url("http://127.0.0.1:8000/admin") is False
    assert _is_public_http_url("http://169.254.169.254/latest/meta-data") is False
    assert _is_public_http_url("ftp://example.com/jobs") is False
    assert _is_public_http_url("https://internal.example/jobs") is False

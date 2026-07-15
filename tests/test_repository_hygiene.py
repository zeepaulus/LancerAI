from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _frontend_source() -> str:
    source_root = ROOT / "frontend" / "src"
    source_files = (
        path
        for pattern in ("*.js", "*.jsx", "*.css")
        for path in source_root.rglob(pattern)
    )
    return "\n".join(path.read_text(encoding="utf-8") for path in source_files)


def test_fake_social_authentication_is_absent() -> None:
    source = _frontend_source()
    auth_page = (ROOT / "frontend/src/pages/AuthPage.jsx").read_text(encoding="utf-8")

    assert "SocialLoginPassword123!" not in source
    assert "handleSocialLogin" not in auth_page
    assert "LANCERAI_MOCK_USER_LEGACY" not in source

    for name in ("google_logo.png", "microsoft_logo.png", "linkedin_logo.png", "github_logo.png"):
        assert not (ROOT / "frontend/src/assets/Logo" / name).exists()

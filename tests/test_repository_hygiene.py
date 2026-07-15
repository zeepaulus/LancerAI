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


OBSOLETE_TRACKED_PATHS = (
    "docs/superpowers",
    "frontend/src/assets/backgrounds/lancerai-grid.svg",
    "frontend/src/assets/icons/alert-triangle.svg",
    "frontend/src/assets/icons/badge-check.svg",
    "frontend/src/assets/icons/lightbulb.svg",
    "frontend/src/assets/icons/search.svg",
    "frontend/src/assets/landing_image.png",
    "frontend/src/assets/lottie/ai-thinking-dots.json",
    "frontend/src/assets/lottie/recording-pulse.json",
    "frontend/src/assets/illustrations/vendor/storyset",
)


def test_obsolete_tracked_artifacts_are_absent() -> None:
    for relative_path in OBSOLETE_TRACKED_PATHS:
        assert not (ROOT / relative_path).exists(), relative_path

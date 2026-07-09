import pytest

from app.service.matching.service import MatchingService


class EmbeddingUnavailableLLM:
    has_cloud = False

    async def embed(self, text: str) -> list[float]:
        return []

    async def generate(self, *args, **kwargs) -> str:
        raise RuntimeError("LLM unavailable")


@pytest.mark.asyncio
async def test_matching_excludes_missing_semantic_score_from_overall() -> None:
    service = MatchingService(
        llm_connector=EmbeddingUnavailableLLM(),
        vector_repository=None,
        job_match_repository=None,
    )
    cv = {
        "personal_info": {"name": "An"},
        "skills_matrix": {"languages": ["Python"], "frameworks": ["FastAPI"], "tools": ["Docker"]},
        "experience": [
            {
                "title": "Backend Developer",
                "company": "Acme",
                "descriptions": ["Built Python FastAPI services."],
                "tech_stack": ["Python", "FastAPI", "Docker"],
            }
        ],
    }

    result = await service.match_cv_to_jd(cv, "Need Python, FastAPI, Redis and Kubernetes experience.")

    assert result.semantic_score == 0.0
    assert result.overall_score > 0
    assert result.improvement_feedback
    assert any(gap.skill_name in {"Redis", "Kubernetes"} for gap in result.missing_skills)

"""Module 3 — Job matching.

Implements the Hybrid Scoring algorithm:
    final = 0.20 * frequency + 0.30 * position + 0.50 * semantic

The semantic component combines vector similarity (against the JD embedding)
and the LLM's deep matching analysis. The frequency / position components are
deterministic keyword scoring and stay on the CPU.
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import re
from typing import Any

import httpx

from app.core.llm_connector import LLMConnector
from app.models.job_match_result import JobMatchResult, MatchStatus
from app.repository.base_vector_repository import BaseVectorRepository
from app.repository.graph_repository import GraphRepository
from app.repository.relational_repository import RelationalRepository
from app.schema.response import JobMatchResponse, JobRecommendationResponse, SkillGap

logger = logging.getLogger(__name__)

WEIGHT_FREQUENCY = 0.20
WEIGHT_POSITION = 0.30
WEIGHT_SEMANTIC = 0.50

_MATCH_SYSTEM = """Bạn là chuyên gia tư vấn nghề nghiệp.
Nhiệm vụ: Phân tích sự phù hợp giữa CV ứng viên và Job Description.
Trả về JSON hợp lệ (không markdown):
{
  "missing_skills": [
    {"skill_name": "Tên kỹ năng", "impact_level": "critical|important|nice_to_have", "reason": "Lý do ngắn"}
  ],
  "improvement_feedback": "Nhận xét tổng thể 2-3 câu và gợi ý cải thiện CV/kỹ năng cụ thể."
}"""

# High-value CV sections for position scoring (higher weight = earlier in list)
_SECTION_WEIGHTS: dict[str, float] = {
    "skills_matrix": 1.0,
    "experience": 0.8,
    "projects": 0.6,
    "education": 0.4,
    "certifications": 0.3,
    "languages": 0.2,
}


class MatchingService:
    """CV-JD scoring + job recommendation engine."""

    def __init__(
        self,
        llm_connector: LLMConnector,
        vector_repository: BaseVectorRepository,
        job_match_repository: RelationalRepository[JobMatchResult],
        graph_repository: GraphRepository | None = None,
    ) -> None:
        self._llm = llm_connector
        self._vector_repo = vector_repository
        self._job_repo = job_match_repository
        self._graph_repo = graph_repository

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def match_cv_to_jd(
        self,
        cv_data: dict[str, Any],
        jd_text: str,
        jd_url: str = "",
    ) -> JobMatchResponse:
        """Score a CV against a Job Description using Hybrid Scoring.

        Pipeline:
          1. Fetch JD text from URL if provided.
          2. Compute frequency score (keyword TF-IDF overlap).
          3. Compute position score (section-weighted keyword hits).
          4. Compute semantic score (cosine similarity via embeddings).
          5. LLM feedback: missing skills + improvement suggestions.
          6. Return JobMatchResponse.
        """
        # 1. Fetch JD from URL if provided and jd_text is empty
        if jd_url and not jd_text.strip():
            jd_text = await _fetch_jd_from_url(jd_url)

        if not jd_text.strip():
            raise ValueError("JD text is empty — provide either jd_text or a reachable jd_url")

        # Extract tokens from JD and CV
        jd_tokens = _tokenize(jd_text)
        cv_flat_text = _flatten_cv(cv_data)
        cv_tokens = _tokenize(cv_flat_text)

        # 2. Frequency score (20%)
        freq_score = _frequency_score(cv_tokens, jd_tokens)

        # 3. Position score (30%)
        pos_score = _position_score(cv_data, jd_tokens)

        # 4. Semantic score (50%)
        sem_score = await self._semantic_score(cv_flat_text, jd_text)

        # 5. Overall weighted score (0-100)
        overall = (
            WEIGHT_FREQUENCY * freq_score
            + WEIGHT_POSITION * pos_score
            + WEIGHT_SEMANTIC * sem_score
        ) * 100
        overall = round(min(100.0, max(0.0, overall)), 1)

        # 6. LLM feedback
        missing_skills, improvement_feedback = await self._llm_feedback(cv_data, jd_text)

        # 7. Knowledge Graph adjustment
        if self._graph_repo is not None:
            cv_flat = _flatten_cv(cv_data)
            cv_tokens_set = {t.lower() for t in _tokenize(cv_flat)}
            for gap in missing_skills:
                try:
                    related = await self._graph_repo.get_related_skills(gap.skill_name, depth=2)
                    related_matches = [
                        r["name"] for r in related
                        if r["name"].lower() in cv_tokens_set
                    ]
                    if related_matches:
                        orig_reason = gap.reason or ""
                        gap.reason = (
                            f"{orig_reason} (Ứng viên có kỹ năng liên quan trong CV: "
                            f"{', '.join(related_matches[:3])})"
                        ).strip()
                        if gap.impact_level == "critical":
                            gap.impact_level = "important"
                        elif gap.impact_level == "important":
                            gap.impact_level = "nice_to_have"
                except Exception:
                    logger.warning("[MatchingService] Failed to query related skills from Neo4j for %s", gap.skill_name)

        logger.info(
            "[Matching] freq=%.2f pos=%.2f sem=%.2f → overall=%.1f",
            freq_score, pos_score, sem_score, overall,
        )

        return JobMatchResponse(
            overall_score=overall,
            frequency_score=round(freq_score * 100, 1),
            position_score=round(pos_score * 100, 1),
            semantic_score=round(sem_score * 100, 1),
            improvement_feedback=improvement_feedback,
            missing_skills=missing_skills,
        )

    async def get_recommendations(
        self,
        cv_data: dict[str, Any],
        limit: int = 10,
    ) -> list[JobRecommendationResponse]:
        """Return top-N matching jobs from the crawled corpus via vector search.

        Steps:
          1. Generate embedding for the CV.
          2. Query vector store for similar job listings.
          3. Enrich results with DB metadata.
        """
        cv_text = _flatten_cv(cv_data)
        embedding = await self._llm.embed(cv_text)
        if not embedding:
            logger.warning("[Matching] get_recommendations: embedding failed — returning empty list")
            return []

        similar = await self._vector_repo.search_similar(embedding, top_k=limit)
        if not similar:
            return []

        recommendations: list[JobRecommendationResponse] = []
        for hit in similar:
            job_id = hit.get("id", "")
            score = float(hit.get("score", 0.0))
            metadata = hit.get("metadata", {})

            recommendations.append(
                JobRecommendationResponse(
                    job_id=job_id,
                    title=metadata.get("title", "Unknown"),
                    company=metadata.get("company", ""),
                    location=metadata.get("location", ""),
                    match_score=round(score * 100, 1),
                    url=metadata.get("url", ""),
                )
            )

        return recommendations

    async def save_job(
        self,
        session: Any,
        user_id: str,
        cv_id: str,
        job_id: str,
    ) -> str:
        """Save a job listing to the user's saved list and return match_result_id."""
        record = await self._job_repo.create(
            session,
            user_id=user_id,
            cv_id=cv_id,
            job_id=job_id,
            match_score=0.0,
            matching_rationale={},
            missing_skills=[],
            status=MatchStatus.SAVED,
        )
        await session.commit()
        return str(record.id)

    async def update_match_status(
        self,
        session: Any,
        match_result_id: str,
        user_id: str,
        status: str,
    ) -> None:
        """Update the workflow status of a job match (saved / applied / rejected).

        Raises ValueError if the record is not found or doesn't belong to the user.
        """
        record: JobMatchResult | None = await self._job_repo.get_by_id(session, match_result_id)
        if record is None:
            raise ValueError(f"Match result '{match_result_id}' not found")
        if record.user_id != user_id:
            raise PermissionError(f"Match result '{match_result_id}' does not belong to user '{user_id}'")

        try:
            new_status = MatchStatus(status)
        except ValueError as err:
            raise ValueError(
                f"Invalid status '{status}'. Allowed: {[s.value for s in MatchStatus]}"
            ) from err

        await self._job_repo.update(session, match_result_id, status=new_status)
        await session.commit()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _semantic_score(self, cv_text: str, jd_text: str) -> float:
        """Compute cosine similarity between CV and JD embeddings."""
        cv_embed, jd_embed = await asyncio.gather(
            self._llm.embed(cv_text[:2000]),
            self._llm.embed(jd_text[:2000]),
        )
        if not cv_embed or not jd_embed or len(cv_embed) != len(jd_embed):
            return 0.5  # neutral fallback when embedding unavailable
        return _cosine_similarity(cv_embed, jd_embed)

    async def _llm_feedback(
        self,
        cv_data: dict[str, Any],
        jd_text: str,
    ) -> tuple[list[SkillGap], str]:
        """Ask the LLM to identify missing skills and generate improvement feedback."""
        cv_snippet = json.dumps(cv_data, ensure_ascii=False)[:3000]
        jd_snippet = jd_text[:2000]

        prompt = f"""## CV ứng viên
{cv_snippet}

## Job Description
{jd_snippet}

Phân tích kỹ năng còn thiếu và đưa ra phản hồi cải thiện:"""

        raw = ""
        try:
            raw = await self._llm.generate(
                prompt,
                system=_MATCH_SYSTEM,
                use_cloud=bool(self._llm._cloud_api_key),
                json_mode=True,
            )
            raw = raw.strip()
            if raw.startswith("```"):
                raw = "\n".join(raw.split("\n")[1:]).rstrip("`").strip()

            data: dict[str, Any] = json.loads(raw)
            missing_skills: list[SkillGap] = [
                SkillGap(**item) for item in data.get("missing_skills", [])
            ]
            feedback: str = data.get("improvement_feedback", "")
            return missing_skills, feedback

        except Exception as exc:
            logger.warning("[Matching] LLM feedback failed (%s) — raw=%r", exc, raw[:200])
            return [], ""


# ------------------------------------------------------------------
# Deterministic scoring helpers (CPU-only, no LLM)
# ------------------------------------------------------------------




def _tokenize(text: str) -> list[str]:
    """Lower-case word tokeniser, removes punctuation."""
    return re.findall(r"[a-zA-ZÀ-ỹ0-9\+#\.]+", text.lower())


def _flatten_cv(cv_data: dict[str, Any]) -> str:
    """Build a flat text string from a structured CV dict for embedding/scoring."""
    parts: list[str] = []

    pi = cv_data.get("personal_info", {})
    if pi.get("name"):
        parts.append(pi["name"])

    skills: dict[str, Any] = cv_data.get("skills_matrix", {})
    for cat in ("languages", "frameworks", "tools"):
        parts.extend(skills.get(cat, []))

    for exp in cv_data.get("experience", []):
        parts.append(f"{exp.get('title', '')} {exp.get('company', '')}")
        parts.extend(exp.get("key_impacts", []))
        parts.extend(exp.get("descriptions", []))
        parts.extend(exp.get("tech_stack", []))

    for proj in cv_data.get("projects", []):
        parts.append(proj.get("name", ""))
        parts.append(proj.get("description", ""))
        parts.extend(proj.get("tech_stack", []))
        parts.extend(proj.get("key_impacts", []))

    parts.extend(cv_data.get("certifications", []))
    return " ".join(str(p) for p in parts if p)


def _tf(tokens: list[str]) -> dict[str, float]:
    """Compute term frequency for a token list."""
    counts: dict[str, int] = {}
    for tok in tokens:
        counts[tok] = counts.get(tok, 0) + 1
    total = len(tokens) or 1
    return {k: v / total for k, v in counts.items()}


def _frequency_score(cv_tokens: list[str], jd_tokens: list[str]) -> float:
    """Keyword overlap score using TF-weighted matching.

    Score = Σ TF_jd(kw) * (1 if kw in cv_set else 0) / Σ TF_jd(kw)
    """
    if not jd_tokens:
        return 0.0
    cv_set = set(cv_tokens)
    jd_tf = _tf(jd_tokens)
    total_jd_weight = sum(jd_tf.values())
    if total_jd_weight == 0:
        return 0.0
    matched_weight = sum(w for kw, w in jd_tf.items() if kw in cv_set)
    return min(1.0, matched_weight / total_jd_weight)


def _position_score(cv_data: dict[str, Any], jd_tokens: list[str]) -> float:
    """Section-weighted keyword hit score.

    Each CV section contributes proportionally to its weight in
    ``_SECTION_WEIGHTS``. The score is the weighted fraction of JD keywords
    found in each section.
    """
    if not jd_tokens:
        return 0.0
    jd_set = set(jd_tokens)
    total_weight = sum(_SECTION_WEIGHTS.values())
    weighted_score = 0.0

    for section_key, weight in _SECTION_WEIGHTS.items():
        section_data = cv_data.get(section_key, {})
        section_text = json.dumps(section_data, ensure_ascii=False).lower()
        section_tokens = set(re.findall(r"[a-zA-ZÀ-ỹ0-9\+#\.]+", section_text))
        if not section_tokens or not jd_set:
            continue
        hit_ratio = len(jd_set & section_tokens) / len(jd_set)
        weighted_score += weight * hit_ratio

    return min(1.0, weighted_score / total_weight)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two equal-length float vectors."""
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


async def _fetch_jd_from_url(url: str) -> str:
    """Fetch and return plain text from a JD URL (best-effort)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()
            # Strip HTML tags with a simple regex (no extra dep)
            text = re.sub(r"<[^>]+>", " ", resp.text)
            text = re.sub(r"\s+", " ", text).strip()
            return text[:8000]
    except httpx.RequestError as exc:
        logger.warning("[Matching] Failed to fetch JD URL %r: %s", url, exc)
        return ""

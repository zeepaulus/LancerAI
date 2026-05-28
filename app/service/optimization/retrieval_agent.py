"""Retrieval agent.

First node in the CV optimization graph. Pulls industry benchmarks (must-have
skills, ATS criteria, top keywords) for the target role so downstream agents
have grounded context.

Strategy:
    1. Prompt the LLM to synthesise benchmark data for the target role/industry.
    2. Parse the JSON response into ``industry_benchmarks`` and
       ``keyword_frequency_map`` state fields.
    3. Optionally query the vector DB for similar JDs (when the index is populated).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.llm_connector import LLMConnector
from app.repository.graph_repository import GraphRepository
from app.service.optimization.state import CVOptimizationState

logger = logging.getLogger(__name__)

_RETRIEVAL_SYSTEM = """Bạn là chuyên gia tư vấn nghề nghiệp và tuyển dụng.
Nhiệm vụ: Cung cấp BENCHMARK ngành cho vị trí ứng tuyển.
Trả về JSON hợp lệ (không thêm markdown), theo schema sau:
{
  "must_have_skills": ["skill1", "skill2"],
  "nice_to_have_skills": ["skill3"],
  "ats_keywords": ["keyword1", "keyword2"],
  "typical_experience_years": 3,
  "common_certifications": ["cert1"],
  "industry_notes": "Nhận xét ngắn về thị trường tuyển dụng hiện tại cho vị trí này."
}"""


async def retrieval_agent(
    state: CVOptimizationState,
    llm: LLMConnector,
    graph_repo: GraphRepository | None = None,
) -> dict[str, Any]:
    """Return state updates for the Retrieval node.

    Queries the LLM for industry benchmark data based on ``target_job_title``
    and ``target_industry``. On failure, returns safe empty defaults so the
    pipeline can continue without crashing.
    """
    job_title = state.get("target_job_title", "Software Engineer")
    industry = state.get("target_industry", "technology")

    prompt = f"""Vị trí: {job_title}
Ngành: {industry}

Cung cấp benchmark ngành và các từ khóa ATS quan trọng nhất cho vị trí này:"""

    raw = ""
    try:
        raw = await llm.generate(
            prompt,
            system=_RETRIEVAL_SYSTEM,
            use_cloud=bool(llm._cloud_api_key),
            json_mode=True,
        )
        from app.core.json_extractor import clean_and_parse_json
        data: dict[str, Any] = clean_and_parse_json(raw)

        # Build keyword_frequency_map from all skill/keyword lists
        keyword_frequency_map: dict[str, int] = {}
        for kw in data.get("must_have_skills", []):
            keyword_frequency_map[str(kw)] = 10  # highest weight for must-have
        for kw in data.get("ats_keywords", []):
            if kw not in keyword_frequency_map:
                keyword_frequency_map[str(kw)] = 7
        for kw in data.get("nice_to_have_skills", []):
            if kw not in keyword_frequency_map:
                keyword_frequency_map[str(kw)] = 4

        if graph_repo is not None:
            # Query related skills of must-have skills
            must_haves = data.get("must_have_skills", [])
            for skill in must_haves:
                try:
                    related = await graph_repo.get_related_skills(str(skill), depth=1)
                    for r in related:
                        name = r.get("name")
                        if name and name not in keyword_frequency_map:
                            keyword_frequency_map[name] = 5  # related skills get a medium weight
                except Exception:
                    logger.warning("[retrieval_agent] Failed to fetch related skills from Neo4j for %s", skill)

        logger.info(
            "[retrieval_agent] Got benchmark for '%s' — %d keywords",
            job_title,
            len(keyword_frequency_map),
        )
        return {
            "industry_benchmarks": data,
            "keyword_frequency_map": keyword_frequency_map,
            "current_step": "retrieval_done",
        }

    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("[retrieval_agent] JSON parse failed (%s) — raw=%r", exc, raw[:200])
        return {
            "industry_benchmarks": {},
            "keyword_frequency_map": {},
            "current_step": "retrieval_done",
        }
    except Exception as exc:
        logger.error("[retrieval_agent] Failed: %s", exc)
        return {
            "industry_benchmarks": {},
            "keyword_frequency_map": {},
            "error_message": str(exc),
            "current_step": "retrieval_done",
        }

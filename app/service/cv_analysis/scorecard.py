"""Deterministic CV scorecard and interview grounding.

This borrows the reference project's key idea: make the factual grounding
deterministic first, then let the LLM explain or interview around those facts.
No score here depends on an external model.
"""

from __future__ import annotations

import re
from typing import Any

_ACTION_VERBS = {
    "achieved", "built", "created", "delivered", "designed", "developed", "improved",
    "increased", "launched", "led", "managed", "optimized", "reduced", "shipped",
    "triển khai", "xây dựng", "thiết kế", "tối ưu", "cải thiện", "dẫn dắt", "quản lý",
}
_VAGUE_TERMS = {
    "responsible for", "participated", "helped", "worked on", "familiar with",
    "phụ trách", "tham gia", "hỗ trợ", "làm việc với", "biết về", "có kiến thức",
}
_TECH_SKILLS = {
    "communication": {"communication", "communicate", "giao tiep", "giao tiếp"},
    "python": {"python"},
    "java": {"java"},
    "javascript": {"javascript", "js"},
    "typescript": {"typescript", "ts"},
    "html/css": {"html", "css", "html/css", "tailwind", "sass", "scss"},
    "react": {"react", "reactjs", "react.js"},
    "vue": {"vue", "vuejs", "vue.js"},
    "ui/ux": {"ui/ux", "ux/ui", "ui", "ux", "figma"},
    "node.js": {"node", "nodejs", "node.js"},
    "fastapi": {"fastapi"},
    "django": {"django"},
    "spring": {"spring", "spring boot"},
    "postgresql": {"postgres", "postgresql"},
    "mysql": {"mysql"},
    "mongodb": {"mongodb", "mongo"},
    "redis": {"redis"},
    "docker": {"docker"},
    "kubernetes": {"kubernetes", "k8s"},
    "aws": {"aws", "amazon web services"},
    "azure": {"azure"},
    "gcp": {"gcp", "google cloud"},
    "machine learning": {"machine learning", "ml"},
    "llm": {"llm", "large language model", "langchain", "rag"},
    "data analysis": {"data analysis", "analytics", "bi"},
    "etl": {"etl", "data pipeline", "pipeline"},
    "ci/cd": {"ci/cd", "github actions", "gitlab ci", "jenkins"},
    "git": {"git", "github", "gitlab"},
    "linux": {"linux", "ubuntu", "debian"},
    "mobile": {"mobile", "android", "ios", "flutter", "react native"},
    "android": {"android", "kotlin"},
    "ios": {"ios", "swift"},
    "flutter": {"flutter", "dart"},
    "react native": {"react native", "react-native"},
    "testing": {"testing", "unit test", "integration test", "jest", "pytest", "vitest"},
    "problem solving": {"problem solving", "problem-solving", "debugging", "troubleshooting"},
    "ownership": {"ownership", "owned", "owner", "chịu trách nhiệm", "phụ trách"},
    "learning agility": {"learning agility", "self-learning", "tự học", "hoc nhanh", "học nhanh"},
}
_ROLE_SKILLS = {
    "frontend": ["JavaScript", "TypeScript", "React", "HTML/CSS", "Testing", "UI/UX"],
    "backend": ["Python", "Java", "Node.js", "FastAPI", "PostgreSQL", "Redis", "Docker"],
    "fullstack": ["JavaScript", "TypeScript", "React", "Node.js", "PostgreSQL", "Docker"],
    "data": ["Python", "SQL", "Data Analysis", "Machine Learning", "ETL"],
    "ai": ["Python", "Machine Learning", "LLM", "RAG", "Data Analysis"],
    "devops": ["Docker", "Kubernetes", "CI/CD", "AWS", "Linux"],
    "mobile": ["Mobile", "Android", "iOS", "Flutter", "React Native"],
    "software engineer": ["JavaScript", "Python", "SQL", "Git", "Testing", "Problem Solving"],
    "software": ["JavaScript", "Python", "SQL", "Git", "Testing", "Problem Solving"],
    "developer": ["JavaScript", "Python", "SQL", "Git", "Testing", "Problem Solving"],
}


def build_cv_scorecard(
    cv_data: dict[str, Any],
    *,
    target_job_title: str = "",
    target_industry: str = "technology",
    jd_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic CV audit scorecard for product/report use."""
    jd_data = jd_data or {}
    flat_text = _flatten_cv(cv_data)
    cv_skills = _extract_cv_skills(cv_data, flat_text)
    required_skills = _infer_required_skills(target_job_title, target_industry, jd_data)
    matched_skills, missing_skills = _match_skills(cv_skills, required_skills, flat_text)

    section_scores = {
        "profile": _profile_score(cv_data),
        "experience": _experience_score(cv_data),
        "impact": _impact_score(cv_data),
        "skills": _skills_score(cv_skills, required_skills, matched_skills),
        "structure": _structure_score(cv_data),
        "target_alignment": _target_alignment_score(required_skills, matched_skills),
    }
    weights = {
        "profile": 0.15,
        "experience": 0.22,
        "impact": 0.22,
        "skills": 0.18,
        "structure": 0.10,
        "target_alignment": 0.13,
    }
    overall = round(sum(section_scores[key] * weight for key, weight in weights.items()), 1)
    strengths = _strengths(section_scores, matched_skills, cv_data)
    issues = _issues(section_scores, missing_skills, cv_data)
    competencies = _competencies(required_skills, missing_skills)

    return {
        "version": "cv_scorecard_v2",
        "overall_score": overall,
        "grade": _grade(overall),
        "target_role": target_job_title or jd_data.get("title") or "",
        "target_industry": target_industry,
        "section_scores": section_scores,
        "weights": weights,
        "cv_skills": cv_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "competencies": competencies,
        "strengths": strengths,
        "issues": issues,
        "interview_focus": _interview_focus(missing_skills, section_scores, cv_data),
        "evidence": {
            "quantified_bullets": _quantified_bullet_count(cv_data),
            "total_bullets": len(_bullet_texts(cv_data)),
            "recent_roles": _recent_roles(cv_data),
            "projects": _project_names(cv_data),
        },
    }


def skill_present(skill: str, text: str) -> bool:
    """Alias-aware skill matcher with token boundaries where possible."""
    lower = text.lower()
    aliases = _TECH_SKILLS.get(skill.lower(), {skill.lower()})
    return any(_contains_alias(lower, alias) for alias in aliases)


def _infer_required_skills(
    target_job_title: str,
    target_industry: str,
    jd_data: dict[str, Any],
) -> list[str]:
    explicit = _extract_jd_skills(jd_data)
    if explicit:
        return explicit[:10]

    text = f"{target_job_title} {target_industry}".lower()
    if not target_job_title.strip() and not jd_data:
        return []
    for role_key, skills in _ROLE_SKILLS.items():
        if role_key in text:
            return skills
    return []


def _match_skills(cv_skills: list[str], required_skills: list[str], flat_text: str) -> tuple[list[str], list[str]]:
    cv_text = f"{flat_text} {' '.join(cv_skills)}".lower()
    matched = [skill for skill in required_skills if skill_present(skill, cv_text)]
    missing = [skill for skill in required_skills if skill not in matched]
    return matched, missing


def _profile_score(cv_data: dict[str, Any]) -> float:
    personal = cv_data.get("personal_info") if isinstance(cv_data.get("personal_info"), dict) else {}
    score = 0.0
    contact_weights = {
        "name": 25.0,
        "email": 25.0,
        "phone": 20.0,
        "linkedin": 15.0,
        "location": 15.0,
    }
    for key, weight in contact_weights.items():
        if str(personal.get(key) or "").strip():
            score += weight
    if _first_text(cv_data, ("summary", "objective", "raw_text"), 300):
        score += 10.0
    if str(personal.get("headline") or personal.get("title") or "").strip():
        score += 5.0
    return min(100.0, score)


def _experience_score(cv_data: dict[str, Any]) -> float:
    experiences = cv_data.get("experience")
    if not isinstance(experiences, list) or not experiences:
        return 20.0
    score = min(45.0, len(experiences) * 15.0)
    for item in experiences[:4]:
        if not isinstance(item, dict):
            continue
        if item.get("company"):
            score += 5.0
        if item.get("title"):
            score += 5.0
        if item.get("period"):
            score += 4.0
        if item.get("descriptions") or item.get("key_impacts"):
            score += 6.0
    return min(100.0, score)


def _impact_score(cv_data: dict[str, Any]) -> float:
    bullets = _bullet_texts(cv_data)
    if not bullets:
        return 15.0
    quantified = sum(1 for bullet in bullets if _has_metric(bullet))
    action = sum(1 for bullet in bullets if _has_action_verb(bullet))
    vague = sum(1 for bullet in bullets if _has_vague_term(bullet))
    metric_ratio = quantified / len(bullets)
    action_ratio = action / len(bullets)
    vague_ratio = vague / len(bullets)
    return round(max(0.0, min(100.0, 35 + metric_ratio * 45 + action_ratio * 25 - vague_ratio * 20)), 1)


def _skills_score(cv_skills: list[str], required_skills: list[str], matched_skills: list[str]) -> float:
    breadth = min(1.0, len(cv_skills) / 10)
    if not required_skills:
        return round(breadth * 100, 1)
    alignment = len(matched_skills) / max(1, len(required_skills))
    return round((breadth * 35 + alignment * 65), 1)


def _structure_score(cv_data: dict[str, Any]) -> float:
    score = 0.0
    if cv_data.get("personal_info"):
        score += 25.0
    if cv_data.get("skills_matrix"):
        score += 25.0
    if cv_data.get("experience"):
        score += 30.0
    elif cv_data.get("projects"):
        score += 20.0
    if cv_data.get("education"):
        score += 10.0
    if cv_data.get("projects"):
        score += 10.0
    return round(min(100.0, score), 1)


def _target_alignment_score(required_skills: list[str], matched_skills: list[str]) -> float:
    if not required_skills:
        return 75.0
    return round((len(matched_skills) / max(1, len(required_skills))) * 100, 1)


def _competencies(required_skills: list[str], missing_skills: list[str]) -> list[dict[str, Any]]:
    ordered = missing_skills + [skill for skill in required_skills if skill not in missing_skills]
    if not ordered:
        ordered = ["Communication", "Problem Solving", "Ownership"]
    weights = _renormalize([2.0 if skill in missing_skills else 1.0 for skill in ordered[:6]])
    return [
        {
            "name": skill,
            "weight": weight,
            "reason": "Skill gap cần probe" if skill in missing_skills else "Kỹ năng cần xác minh bằng evidence",
        }
        for skill, weight in zip(ordered[:6], weights, strict=False)
    ]


def _strengths(section_scores: dict[str, float], matched_skills: list[str], cv_data: dict[str, Any]) -> list[str]:
    strengths: list[str] = []
    if matched_skills:
        strengths.append(f"Khớp kỹ năng mục tiêu: {', '.join(matched_skills[:5])}.")
    if section_scores["impact"] >= 70:
        strengths.append("CV có nhiều mô tả theo hướng kết quả/impact.")
    if _project_names(cv_data):
        strengths.append("Có project để khai thác sâu trong phỏng vấn.")
    if section_scores["structure"] >= 80:
        strengths.append("Cấu trúc CV tương đối đầy đủ cho ATS.")
    return strengths[:5]


def _issues(section_scores: dict[str, float], missing_skills: list[str], cv_data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if missing_skills:
        issues.append(f"Thiếu hoặc chưa thể hiện rõ: {', '.join(missing_skills[:6])}.")
    if section_scores["impact"] < 60:
        issues.append("Nhiều bullet còn thiếu số liệu, kết quả đo lường hoặc động từ hành động mạnh.")
    if section_scores["profile"] < 70:
        issues.append("Thông tin hồ sơ/summary chưa đủ mạnh để nhà tuyển dụng nắm nhanh định vị ứng viên.")
    if not _project_names(cv_data) and not cv_data.get("experience"):
        issues.append("Thiếu project nổi bật để chứng minh năng lực thực tế.")
    if section_scores["experience"] < 55:
        issues.append("Kinh nghiệm làm việc chưa đủ chi tiết hoặc thiếu bối cảnh vai trò.")
    return issues[:6]


def _interview_focus(missing_skills: list[str], section_scores: dict[str, float], cv_data: dict[str, Any]) -> list[str]:
    focus = [f"Làm rõ mức độ thành thạo {skill} bằng ví dụ thực tế." for skill in missing_skills[:3]]
    if section_scores["impact"] < 70:
        focus.append("Yêu cầu ứng viên kể theo STAR để kiểm chứng ownership và kết quả đo lường.")
    projects = _project_names(cv_data)
    if projects:
        focus.append(f"Đào sâu project '{projects[0]}' về vai trò cá nhân, trade-off và kết quả.")
    return focus[:5]


def _extract_cv_skills(cv_data: dict[str, Any], flat_text: str) -> list[str]:
    values: list[str] = []
    skills_matrix = cv_data.get("skills_matrix")
    if isinstance(skills_matrix, dict):
        for items in skills_matrix.values():
            if isinstance(items, list):
                values.extend(str(item) for item in items if str(item).strip())
    for section in ("experience", "projects"):
        entries = cv_data.get(section)
        if isinstance(entries, list):
            for entry in entries:
                if isinstance(entry, dict) and isinstance(entry.get("tech_stack"), list):
                    values.extend(str(item) for item in entry["tech_stack"] if str(item).strip())
    for canonical in _TECH_SKILLS:
        if skill_present(canonical, flat_text):
            values.append(canonical.title() if canonical != "ci/cd" else "CI/CD")
    return _dedupe(values)


def _extract_jd_skills(jd_data: dict[str, Any]) -> list[str]:
    values: list[str] = []
    requirements = jd_data.get("requirements")
    if isinstance(requirements, dict):
        for key in ("skills", "required_skills", "mandatory_skills", "nice_to_have", "technologies"):
            items = requirements.get(key)
            if isinstance(items, list):
                values.extend(str(item) for item in items if str(item).strip())
            elif isinstance(items, str):
                values.extend(_split_skill_text(items))
    text = " ".join(str(jd_data.get(key) or "") for key in ("title", "description", "raw_text"))
    for canonical in _TECH_SKILLS:
        if skill_present(canonical, text):
            values.append(canonical.title() if canonical != "ci/cd" else "CI/CD")
    return _dedupe(values)


def _flatten_cv(cv_data: dict[str, Any]) -> str:
    parts: list[str] = []
    for value in cv_data.values():
        parts.append(_stringify(value))
    return " ".join(parts)


def _stringify(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_stringify(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_stringify(item) for item in value)
    return str(value or "")


def _bullet_texts(cv_data: dict[str, Any]) -> list[str]:
    bullets: list[str] = []
    for section in ("experience", "projects"):
        entries = cv_data.get(section)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            for key in ("descriptions", "key_impacts"):
                items = entry.get(key)
                if isinstance(items, list):
                    bullets.extend(str(item) for item in items if str(item).strip())
            if section == "projects" and str(entry.get("description") or "").strip():
                bullets.append(str(entry["description"]))
    return bullets


def _quantified_bullet_count(cv_data: dict[str, Any]) -> int:
    return sum(1 for bullet in _bullet_texts(cv_data) if _has_metric(bullet))


def _recent_roles(cv_data: dict[str, Any]) -> list[str]:
    roles: list[str] = []
    for item in cv_data.get("experience", []) if isinstance(cv_data.get("experience"), list) else []:
        if isinstance(item, dict):
            title = str(item.get("title") or "").strip()
            company = str(item.get("company") or "").strip()
            if title and company:
                roles.append(f"{title} at {company}")
            elif title:
                roles.append(title)
    return roles[:5]


def _project_names(cv_data: dict[str, Any]) -> list[str]:
    projects = cv_data.get("projects")
    if not isinstance(projects, list):
        return []
    return [str(item.get("name")).strip() for item in projects if isinstance(item, dict) and item.get("name")][:5]


def _first_text(cv_data: dict[str, Any], keys: tuple[str, ...], max_chars: int) -> str:
    for key in keys:
        value = cv_data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:max_chars]
    return ""


def _split_skill_text(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[,;/\n|]+", value) if part.strip()]


def _contains_alias(text: str, alias: str) -> bool:
    escaped = re.escape(alias.lower())
    if re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text):
        return True
    return alias.lower() in text if any(ch in alias for ch in ".#/+") else False


def _has_metric(text: str) -> bool:
    return bool(re.search(r"(\d+%|\d+\s*(x|k|m|triệu|nghìn|users?|requests?|ms|s|hours?|giờ))", text.lower()))


def _has_action_verb(text: str) -> bool:
    lower = text.lower()
    return any(verb in lower for verb in _ACTION_VERBS)


def _has_vague_term(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in _VAGUE_TERMS)


def _renormalize(raw_weights: list[float]) -> list[float]:
    total = sum(max(0.1, weight) for weight in raw_weights) or 1.0
    weights = [round(max(0.1, weight) / total, 2) for weight in raw_weights]
    diff = round(1.0 - sum(weights), 2)
    if weights:
        weights[0] = round(weights[0] + diff, 2)
    return weights


def _grade(score: float) -> str:
    if score >= 85:
        return "excellent"
    if score >= 70:
        return "strong"
    if score >= 55:
        return "needs_work"
    return "weak"


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        clean = str(value).strip()
        key = clean.lower()
        if clean and key not in seen:
            seen.add(key)
            output.append(clean)
    return output

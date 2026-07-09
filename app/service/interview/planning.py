"""Interview planning helpers for CV-first live interviews.

The reference project creates a plan/evaluation brief before the live room
starts. This module keeps that idea deterministic so the product works even
when the LLM service is unavailable, while still giving the interviewer and
scorecard enough structure to stay grounded in the CV/JD.
"""

from __future__ import annotations

import json
import re
from typing import Any

from app.models.job_listing import JobListing
from app.service.cv_analysis.scorecard import build_cv_scorecard
from app.service.interview.scoring import DEFAULT_COMPETENCY_WEIGHTS

IT_ROLE_OPTIONS = [
    "Frontend Developer",
    "Backend Developer",
    "Fullstack Developer",
    "AI Engineer",
    "Data Analyst",
    "Data Scientist",
    "DevOps Engineer",
    "QA Engineer",
    "Mobile Developer",
    "Software Engineer Intern",
    "Fresher Software Engineer",
]

_IT_ROLE_KEYWORDS = {
    "frontend": "Frontend Developer",
    "front-end": "Frontend Developer",
    "react": "Frontend Developer",
    "backend": "Backend Developer",
    "back-end": "Backend Developer",
    "api": "Backend Developer",
    "fullstack": "Fullstack Developer",
    "full-stack": "Fullstack Developer",
    "ai": "AI Engineer",
    "machine learning": "AI Engineer",
    "ml": "AI Engineer",
    "data analyst": "Data Analyst",
    "business intelligence": "Data Analyst",
    "data scientist": "Data Scientist",
    "devops": "DevOps Engineer",
    "sre": "DevOps Engineer",
    "qa": "QA Engineer",
    "tester": "QA Engineer",
    "testing": "QA Engineer",
    "mobile": "Mobile Developer",
    "android": "Mobile Developer",
    "ios": "Mobile Developer",
    "intern": "Software Engineer Intern",
    "fresher": "Fresher Software Engineer",
    "software": "Fresher Software Engineer",
}


def job_listing_to_jd_data(job: JobListing | None) -> dict[str, Any]:
    """Convert a JobListing ORM object into compact JD context."""
    if job is None:
        return {}
    return {
        "job_listing_id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "requirements": job.requirements or {},
        "salary_range": job.salary_range,
        "source": job.source,
        "source_url": job.source_url,
    }


def build_manual_jd_data(
    *,
    job_title: str | None = None,
    jd_text: str | None = None,
    jd_url: str | None = None,
) -> dict[str, Any]:
    """Build JD context from setup form fields."""
    data: dict[str, Any] = {}
    if job_title and job_title.strip():
        data["title"] = job_title.strip()
    if jd_text and jd_text.strip():
        data["description"] = jd_text.strip()
        data["raw_text"] = jd_text.strip()
    if jd_url and jd_url.strip():
        data["source_url"] = jd_url.strip()
    return data


def infer_job_title(cv_data: dict[str, Any], jd_data: dict[str, Any] | None = None) -> str:
    """Infer a target interview title from JD first, then CV."""
    jd_data = jd_data or {}
    for key in ("title", "job_title", "role"):
        value = jd_data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    personal_info = cv_data.get("personal_info")
    if isinstance(personal_info, dict):
        for key in ("title", "headline", "desired_role"):
            value = personal_info.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    experiences = cv_data.get("experience")
    if isinstance(experiences, list):
        for experience in experiences:
            if isinstance(experience, dict):
                value = experience.get("title")
                if isinstance(value, str) and value.strip():
                    return value.strip()

    return "CV Interview"


def normalise_it_role(job_title: str | None) -> str:
    """Keep interview scope inside IT/software/data roles."""
    title = (job_title or "").strip()
    if not title:
        return "Fresher Software Engineer"

    lower = title.lower()
    for option in IT_ROLE_OPTIONS:
        if option.lower() == lower:
            return option
    for keyword, role in _IT_ROLE_KEYWORDS.items():
        if keyword in lower:
            return role
    return "Fresher Software Engineer"


def build_interview_plan(
    *,
    cv_data: dict[str, Any],
    jd_data: dict[str, Any] | None = None,
    job_title: str | None = None,
    mode: str = "practice",
    focus_area: str | None = None,
    duration_minutes: int = 5,
) -> dict[str, Any]:
    """Create a product-ready plan and evaluation brief for a live interview."""
    jd_data = jd_data or {}
    target_role = normalise_it_role((job_title or "").strip() or infer_job_title(cv_data, jd_data))
    candidate_name = _candidate_name(cv_data)
    cv_skills = _extract_cv_skills(cv_data)
    jd_skills = _extract_jd_skills(jd_data)
    cv_scorecard = build_cv_scorecard(
        cv_data,
        target_job_title=target_role,
        target_industry="technology",
        jd_data=jd_data,
    )
    must_have_skills = cv_scorecard.get("required_skills") or jd_skills[:8] or cv_skills[:8]
    gaps = cv_scorecard.get("missing_skills") or [
        skill for skill in must_have_skills if _normalise(skill) not in {_normalise(s) for s in cv_skills}
    ]
    competencies = cv_scorecard.get("competencies") or [
        {
            "name": name,
            "weight": weight,
            "reason": _competency_description(name),
        }
        for name, weight in DEFAULT_COMPETENCY_WEIGHTS.items()
    ]

    question_plan = _build_question_plan(
        target_role=target_role,
        cv_data=cv_data,
        must_have_skills=must_have_skills,
        gaps=gaps,
        focus_area=focus_area,
        duration_minutes=duration_minutes,
    )

    return {
        "version": "cv_interview_v1",
        "target_role": target_role,
        "candidate_name": candidate_name,
        "mode": mode,
        "duration_minutes": duration_minutes,
        "focus_area": focus_area or "",
        "must_have_skills": must_have_skills,
        "skill_gaps_to_probe": gaps[:6],
        "cv_scorecard": cv_scorecard,
        "cv_snapshot": _cv_snapshot(cv_data),
        "jd_snapshot": _jd_snapshot(jd_data),
        "question_plan": question_plan,
        "evaluation_brief": {
            "instruction": (
                "Chấm điểm dựa trên evidence trong transcript, CV và JD. "
                "Nếu không có evidence cho một năng lực, chấm thấp và ghi rõ không quan sát được."
            ),
            "competencies": [
                {
                    "name": item.get("name", ""),
                    "weight": item.get("weight", 0),
                    "what_good_looks_like": item.get("reason") or _competency_description(item.get("name", "")),
                }
                for item in competencies
            ],
            "recommendation_thresholds": {
                "strong_hire": ">= 4.3",
                "hire": "3.5 - 4.29",
                "lean_hire": "2.8 - 3.49",
                "no_hire": "1.8 - 2.79",
                "strong_no_hire": "< 1.8",
            },
        },
    }


def plan_for_prompt(plan: dict[str, Any]) -> str:
    """Render a compact plan string for the interviewer system prompt."""
    if not plan:
        return "(Chưa có interview plan chi tiết.)"
    safe = {
        "target_role": plan.get("target_role", ""),
        "focus_area": plan.get("focus_area", ""),
        "must_have_skills": plan.get("must_have_skills", [])[:8],
        "skill_gaps_to_probe": plan.get("skill_gaps_to_probe", [])[:6],
        "question_plan": plan.get("question_plan", [])[:8],
        "evaluation_competencies": plan.get("evaluation_brief", {}).get("competencies", []),
    }
    return json.dumps(safe, ensure_ascii=False, indent=2)


def _candidate_name(cv_data: dict[str, Any]) -> str:
    personal_info = cv_data.get("personal_info")
    if isinstance(personal_info, dict):
        value = personal_info.get("name")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Ứng viên"


def _recent_roles(cv_data: dict[str, Any]) -> list[str]:
    roles: list[str] = []
    experiences = cv_data.get("experience")
    if not isinstance(experiences, list):
        return roles
    for item in experiences:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        company = str(item.get("company") or "").strip()
        if title and company:
            roles.append(f"{title} tại {company}")
        elif title:
            roles.append(title)
    return roles


def _build_question_plan(
    *,
    target_role: str,
    cv_data: dict[str, Any],
    must_have_skills: list[str],
    gaps: list[str],
    focus_area: str | None,
    duration_minutes: int,
) -> list[dict[str, Any]]:
    roles = _recent_roles(cv_data)
    projects = _project_names(cv_data)
    core_skill = must_have_skills[0] if must_have_skills else "kỹ năng chính trong CV"
    gap_skill = gaps[0] if gaps else core_skill
    main_project = projects[0] if projects else "một dự án nổi bật trong CV"
    recent_role = roles[0] if roles else target_role

    questions: list[dict[str, Any]] = [
        {
            "stage": "warmup",
            "goal": "Mở đầu và xác nhận định hướng nghề nghiệp",
            "question": (
                "Bạn có thể giới thiệu ngắn gọn về bản thân và phần kinh nghiệm "
                f"liên quan nhất tới vị trí {target_role} không?"
            ),
        },
        {
            "stage": "cv_deep_dive",
            "goal": "Kiểm chứng kinh nghiệm nổi bật trong CV",
            "question": (
                f"Trong vai trò {recent_role}, trách nhiệm hoặc thành tựu nào "
                "thể hiện rõ nhất năng lực của bạn?"
            ),
        },
        {
            "stage": "project_deep_dive",
            "goal": "Đánh giá ownership và impact qua dự án thực tế",
            "question": (
                f"Trong {main_project}, bạn trực tiếp chịu trách nhiệm phần nào "
                "và kết quả quan trọng nhất đạt được là gì?"
            ),
        },
        {
            "stage": "technical_depth",
            "goal": "Đào sâu kỹ năng cốt lõi",
            "question": (
                f"Bạn đã dùng {core_skill} trong tình huống thực tế nào, "
                "và bạn ra quyết định kỹ thuật ra sao?"
            ),
        },
        {
            "stage": "jd_fit",
            "goal": "Kiểm tra mức độ phù hợp với JD",
            "question": (
                f"Vị trí này cần {gap_skill}. Bạn có kinh nghiệm liên quan "
                "hoặc kế hoạch bù đắp khoảng trống này như thế nào?"
            ),
        },
        {
            "stage": "communication",
            "goal": "Quan sát cách diễn đạt và xử lý tình huống mơ hồ",
            "question": (
                "Khi yêu cầu thay đổi hoặc chưa rõ, bạn thường làm rõ vấn đề "
                "và phối hợp với team như thế nào?"
            ),
        },
        {
            "stage": "wrap_up",
            "goal": "Kết thúc và cho ứng viên bổ sung evidence",
            "question": (
                "Có điểm mạnh, dự án hoặc kinh nghiệm nào trong CV bạn muốn "
                "nhấn mạnh thêm trước khi kết thúc không?"
            ),
        },
    ]

    if focus_area and focus_area.strip():
        questions.insert(
            3,
            {
                "stage": "focus_area",
                "goal": "Đào sâu trọng tâm do người dùng chọn",
                "question": (
                    f"Bạn hãy nói kỹ hơn về {focus_area.strip()} và một ví dụ cụ thể "
                    "bạn đã xử lý trong công việc."
                ),
            },
        )

    if duration_minutes <= 3:
        return questions[:4]
    if duration_minutes <= 5:
        return questions[:6]
    return questions


def _competency_description(name: str) -> str:
    descriptions = {
        "CV-JD Fit": "Kinh nghiệm và kỹ năng trong CV khớp với JD hoặc mục tiêu vị trí.",
        "Technical Depth": "Câu trả lời có ví dụ thực tế, quyết định kỹ thuật, trade-off và kết quả rõ.",
        "STAR Clarity": "Ứng viên trình bày đủ Situation, Task, Action, Result và tránh trả lời chung chung.",
        "Communication": "Diễn đạt mạch lạc, trả lời đúng trọng tâm và biết làm rõ vấn đề.",
        "Professional Presence": "Tác phong ổn định, camera/âm thanh rõ, ít tín hiệu mất tập trung.",
    }
    return descriptions.get(name, "")


def _cv_snapshot(cv_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": _first_text(cv_data, ("summary", "raw_text"), 800),
        "recent_roles": _recent_roles(cv_data),
        "skills": _extract_cv_skills(cv_data)[:12],
        "projects": _project_names(cv_data)[:5],
    }


def _jd_snapshot(jd_data: dict[str, Any]) -> dict[str, Any]:
    if not jd_data:
        return {}
    requirements = jd_data.get("requirements") if isinstance(jd_data.get("requirements"), dict) else {}
    return {
        "title": jd_data.get("title") or jd_data.get("job_title") or "",
        "company": jd_data.get("company") or "",
        "location": jd_data.get("location") or "",
        "description": _first_text(jd_data, ("description", "raw_text"), 1200),
        "requirements": requirements,
        "skills": _extract_jd_skills(jd_data)[:12],
        "source_url": jd_data.get("source_url") or "",
    }


def _build_question_plan(
    *,
    target_role: str,
    cv_data: dict[str, Any],
    must_have_skills: list[str],
    gaps: list[str],
    focus_area: str | None,
    duration_minutes: int,
) -> list[dict[str, Any]]:
    roles = _recent_roles(cv_data)
    projects = _project_names(cv_data)
    core_skill = must_have_skills[0] if must_have_skills else "kỹ năng chính trong CV"
    gap_skill = gaps[0] if gaps else core_skill
    main_project = projects[0] if projects else "một dự án nổi bật trong CV"
    recent_role = roles[0] if roles else target_role

    questions: list[dict[str, Any]] = [
        {
            "stage": "warmup",
            "goal": "Mở đầu và xác nhận mục tiêu nghề nghiệp",
            "question": (
                "Bạn có thể giới thiệu ngắn gọn về bản thân và kinh nghiệm "
                f"phù hợp với vị trí {target_role} không?"
            ),
        },
        {
            "stage": "cv_deep_dive",
            "goal": "Kiểm chứng kinh nghiệm nổi bật trong CV",
            "question": (
                f"Trong vai trò {recent_role}, thành tựu hoặc trách nhiệm nào "
                "thể hiện rõ nhất năng lực của bạn?"
            ),
        },
        {
            "stage": "project_deep_dive",
            "goal": "Đánh giá ownership và impact qua dự án thực tế",
            "question": (
                f"Trong {main_project}, bạn trực tiếp chịu trách nhiệm phần nào "
                "và kết quả quan trọng nhất đạt được là gì?"
            ),
        },
        {
            "stage": "technical_depth",
            "goal": "Đào sâu kỹ thuật/kỹ năng cốt lõi",
            "question": (
                f"Bạn đã sử dụng {core_skill} trong tình huống thực tế nào, "
                "và bạn ra quyết định kỹ thuật ra sao?"
            ),
        },
        {
            "stage": "jd_fit",
            "goal": "Kiểm tra mức độ phù hợp với yêu cầu vị trí",
            "question": (
                f"Vị trí này cần {gap_skill}. Bạn có kinh nghiệm liên quan "
                "hoặc kế hoạch bù đắp khoảng trống này như thế nào?"
            ),
        },
        {
            "stage": "communication",
            "goal": "Quan sát cách diễn đạt và phản biện",
            "question": (
                "Khi gặp yêu cầu mơ hồ hoặc thay đổi giữa chừng, "
                "bạn thường làm rõ và phối hợp với team như thế nào?"
            ),
        },
        {
            "stage": "wrap_up",
            "goal": "Kết thúc và cho ứng viên bổ sung",
            "question": (
                "Có điểm mạnh, dự án hoặc kinh nghiệm nào trong CV bạn muốn "
                "nhấn mạnh thêm trước khi kết thúc không?"
            ),
        },
    ]

    if focus_area and focus_area.strip():
        questions.insert(
            3,
            {
                "stage": "focus_area",
                "goal": "Đào sâu trọng tâm do người dùng chọn",
                "question": f"Bạn hãy nói kỹ hơn về {focus_area.strip()} và ví dụ cụ thể bạn đã xử lý trong công việc.",
            },
        )

    if duration_minutes <= 3:
        return questions[:4]
    if duration_minutes <= 5:
        return questions[:6]
    return questions


def _extract_cv_skills(cv_data: dict[str, Any]) -> list[str]:
    values: list[str] = []
    skills_matrix = cv_data.get("skills_matrix")
    if isinstance(skills_matrix, dict):
        for key in ("languages", "frameworks", "tools", "soft_skills"):
            items = skills_matrix.get(key)
            if isinstance(items, list):
                values.extend(str(item) for item in items if str(item).strip())

    for section in ("experience", "projects"):
        entries = cv_data.get(section)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, dict) and isinstance(entry.get("tech_stack"), list):
                values.extend(str(item) for item in entry["tech_stack"] if str(item).strip())

    return _dedupe(values)


def _extract_jd_skills(jd_data: dict[str, Any]) -> list[str]:
    values: list[str] = []
    requirements = jd_data.get("requirements")
    if isinstance(requirements, dict):
        for key in ("skills", "required_skills", "nice_to_have", "technologies"):
            items = requirements.get(key)
            if isinstance(items, list):
                values.extend(str(item) for item in items if str(item).strip())
            elif isinstance(items, str):
                values.extend(_split_skill_text(items))

    text = " ".join(
        str(jd_data.get(key) or "")
        for key in ("title", "description", "raw_text")
    )
    values.extend(_guess_skills_from_text(text))
    return _dedupe(values)


def _guess_skills_from_text(text: str) -> list[str]:
    known = [
        "Python",
        "Java",
        "JavaScript",
        "TypeScript",
        "React",
        "Node.js",
        "FastAPI",
        "Django",
        "Spring",
        "PostgreSQL",
        "MySQL",
        "MongoDB",
        "Redis",
        "Docker",
        "Kubernetes",
        "AWS",
        "Azure",
        "GCP",
        "Machine Learning",
        "NLP",
        "LLM",
        "Data Analysis",
        "Agile",
        "CI/CD",
    ]
    lower = text.lower()
    return [skill for skill in known if skill.lower() in lower]


def _split_skill_text(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[,;/\n]+", value) if part.strip()]


def _recent_roles(cv_data: dict[str, Any]) -> list[str]:
    roles: list[str] = []
    experiences = cv_data.get("experience")
    if not isinstance(experiences, list):
        return roles
    for item in experiences:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        company = str(item.get("company") or "").strip()
        if title and company:
            roles.append(f"{title} tại {company}")
        elif title:
            roles.append(title)
    return roles


def _project_names(cv_data: dict[str, Any]) -> list[str]:
    projects = cv_data.get("projects")
    if not isinstance(projects, list):
        return []
    names = []
    for item in projects:
        if isinstance(item, dict) and str(item.get("name") or "").strip():
            names.append(str(item["name"]).strip())
    return names


def _first_text(data: dict[str, Any], keys: tuple[str, ...], limit: int) -> str:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:limit]
    return ""


def _normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9+#]+", "", value.lower())


def _dedupe(values: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = value.strip()
        key = _normalise(item)
        if not item or key in seen:
            continue
        output.append(item)
        seen.add(key)
    return output


def _competency_description(name: str) -> str:
    descriptions = {
        "CV-JD Fit": "Kinh nghiệm và kỹ năng trong CV khớp với yêu cầu JD hoặc mục tiêu vị trí.",
        "Technical Depth": "Câu trả lời có ví dụ thực tế, quyết định kỹ thuật, trade-off và kết quả rõ.",
        "STAR Clarity": "Ứng viên trình bày đủ Situation, Task, Action, Result, tránh trả lời chung chung.",
        "Communication": "Diễn đạt mạch lạc, trả lời đúng trọng tâm, biết làm rõ vấn đề.",
        "Professional Presence": "Tác phong ổn định, camera/âm thanh rõ, ít tín hiệu mất tập trung.",
    }
    return descriptions.get(name, "")


def _candidate_name(cv_data: dict[str, Any]) -> str:
    personal_info = cv_data.get("personal_info")
    if isinstance(personal_info, dict):
        value = personal_info.get("name")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Ứng viên"

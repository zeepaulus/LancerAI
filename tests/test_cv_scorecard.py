from app.service.cv_analysis.scorecard import build_cv_scorecard, skill_present


def test_cv_scorecard_detects_skill_gaps_and_focus() -> None:
    cv = {
        "personal_info": {"name": "An", "email": "an@example.com", "phone": "0909", "linkedin": "in/an"},
        "summary": "Backend engineer with Python and FastAPI experience.",
        "experience": [
            {
                "company": "Acme",
                "title": "Backend Engineer",
                "period": "2022-2024",
                "descriptions": ["Built FastAPI services serving 10k users."],
                "key_impacts": ["Reduced API latency by 35%."],
                "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
            }
        ],
        "projects": [{"name": "API Platform", "description": "Dockerized backend service.", "tech_stack": ["Docker"]}],
        "skills_matrix": {"languages": ["Python"], "frameworks": ["FastAPI"], "tools": ["Docker"]},
        "education": [{"school": "University"}],
    }
    jd = {
        "title": "Backend Engineer",
        "description": "Need Python, FastAPI, PostgreSQL, Redis, Kubernetes.",
    }

    scorecard = build_cv_scorecard(cv, target_job_title="Backend Engineer", jd_data=jd)

    assert scorecard["overall_score"] > 60
    assert "Python" in scorecard["matched_skills"]
    assert "Redis" in scorecard["missing_skills"]
    assert scorecard["interview_focus"]


def test_skill_present_is_alias_aware() -> None:
    assert skill_present("Kubernetes", "Deployed services on k8s.")
    assert skill_present("PostgreSQL", "Used postgres for reporting.")

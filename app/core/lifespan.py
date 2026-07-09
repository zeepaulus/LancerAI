"""FastAPI application lifespan."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logger import get_logger
from app.core.settings import get_settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    s = get_settings()
    logger.info("[startup] env=%s debug=%s", s.app_env, s.app_debug)

    if not s.app_debug and not s.allowed_origins:
        logger.warning("[CORS] allowed_origins is empty — all cross-origin requests will be rejected.")

    strict_db_startup = s.app_env in ("production", "staging")

    from sqlalchemy import text

    from app.core.database import get_engine

    try:
        async with get_engine().begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("[startup] database connection OK")
    except Exception as e:
        logger.error("[startup] database connection FAILED: %s", e)
        if strict_db_startup:
            raise RuntimeError(
                "Database unreachable during startup — refusing to boot in "
                f"app_env={s.app_env!r}. Fix DATABASE_URL connectivity."
            ) from e

    try:
        from app.core.providers.connectors import get_vector_repository

        await asyncio.get_running_loop().run_in_executor(None, get_vector_repository)
        logger.info("[startup] vector repository warmed up")
    except Exception as e:
        logger.warning("[startup] vector repository warm-up failed: %s", e)

    # ── Seed Dummy Job Listings ──────────────────────────────────────────────
    try:
        from sqlalchemy import select, func
        from app.core.database import _get_session_factory
        from app.models.job_listing import JobListing
        from app.workers.crawler_worker import _async_save_job_listings

        session_factory = _get_session_factory()
        async with session_factory() as session:
            count_stmt = select(func.count()).select_from(JobListing)
            count_res = await session.execute(count_stmt)
            count = count_res.scalar() or 0
            if count == 0:
                logger.info("[startup] job_listings table is empty. Seeding dummy IT jobs...")
                dummy_jobs = [
                    {
                        "source": "topcv",
                        "source_url": "https://www.topcv.vn/jobs/python-fastapi-backend-developer",
                        "title": "Python/FastAPI Backend Developer",
                        "company": "LancerAI Corp",
                        "location": "Hồ Chí Minh",
                        "salary_range": "20,000,000 - 35,000,000 VND",
                        "description": "Chúng tôi đang tìm kiếm lập trình viên Python phát triển API sử dụng FastAPI/Django. Thiết kế cơ sở dữ liệu PostgreSQL và tích hợp các LLM AI APIs.",
                        "requirements": {
                            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git", "RESTful API"],
                            "raw_requirements": "Có ít nhất 2 năm kinh nghiệm làm việc với Python, hiểu biết tốt về database SQL và lập trình bất đồng bộ (asyncio).",
                            "benefits": "Bảo hiểm đầy đủ, thưởng tháng 13, cấp MacBook Pro làm việc.",
                            "tags": ["Python", "FastAPI", "Backend"]
                        },
                        "experience_level": "Junior/Middle",
                        "job_type": "Full-time"
                    },
                    {
                        "source": "topcv",
                        "source_url": "https://www.topcv.vn/jobs/reactjs-typescript-frontend-developer",
                        "title": "ReactJS/TypeScript Frontend Developer",
                        "company": "LancerAI Corp",
                        "location": "Hà Nội",
                        "salary_range": "18,000,000 - 30,000,000 VND",
                        "description": "Phát triển giao diện ứng dụng web luyện phỏng vấn AI với ReactJS, TypeScript và Tailwind CSS. Kết nối các API WebSockets realtime.",
                        "requirements": {
                            "skills": ["React", "TypeScript", "Tailwind CSS", "Redux", "WebSockets", "Git"],
                            "raw_requirements": "Thành thạo ReactJS, TypeScript. Có kinh nghiệm tối ưu hóa frontend performance và làm việc với WebSocket stream.",
                            "benefits": "Thưởng dự án, bảo hiểm sức khỏe cao cấp, làm việc hybrid.",
                            "tags": ["React", "TypeScript", "Frontend"]
                        },
                        "experience_level": "Junior/Middle",
                        "job_type": "Full-time"
                    },
                    {
                        "source": "topcv",
                        "source_url": "https://www.topcv.vn/jobs/devops-cloud-engineer",
                        "title": "DevOps / Cloud Platform Engineer",
                        "company": "LancerAI Corp",
                        "location": "Hồ Chí Minh / Remote",
                        "salary_range": "30,000,000 - 50,000,000 VND",
                        "description": "Quản lý hạ tầng đám mây AWS, CI/CD pipeline sử dụng GitHub Actions. Triển khai các containerized microservices qua Kubernetes/Docker.",
                        "requirements": {
                            "skills": ["AWS", "Docker", "Kubernetes", "CI/CD", "Terraform", "Nginx"],
                            "raw_requirements": "Kinh nghiệm trên 3 năm triển khai ứng dụng lên AWS, thiết lập hệ thống log Prometheus/Grafana, tự động hóa script Bash/Python.",
                            "benefits": "Làm việc remote, nghỉ phép 15 ngày/năm, xét tăng lương 2 lần/năm.",
                            "tags": ["DevOps", "AWS", "Cloud"]
                        },
                        "experience_level": "Senior",
                        "job_type": "Full-time"
                    },
                    {
                        "source": "topcv",
                        "source_url": "https://www.topcv.vn/jobs/qa-qc-automation-test-engineer",
                        "title": "QA/QC Automation Test Engineer",
                        "company": "LancerAI Corp",
                        "location": "Đà Nẵng",
                        "salary_range": "15,000,000 - 25,000,000 VND",
                        "description": "Xây dựng các kịch bản kiểm thử tự động (Automation Testing) cho web/API. Sử dụng Selenium, Playwright hoặc Cypress để chạy kiểm thử hồi quy.",
                        "requirements": {
                            "skills": ["Selenium", "Playwright", "Cypress", "Python", "API Testing", "Git"],
                            "raw_requirements": "Kinh nghiệm viết test suite tự động bằng Python/JS. Có tư duy logic tốt, biết lập kế hoạch test plan và viết tài liệu QC.",
                            "benefits": "Cấp thiết bị test, lớp học tiếng Anh miễn phí, teambuilding hàng quý.",
                            "tags": ["QA", "QC", "Automation"]
                        },
                        "experience_level": "Junior/Middle",
                        "job_type": "Full-time"
                    },
                    {
                        "source": "topcv",
                        "source_url": "https://www.topcv.vn/jobs/data-analyst",
                        "title": "Data Analyst (SQL / PowerBI)",
                        "company": "LancerAI Corp",
                        "location": "Hồ Chí Minh",
                        "salary_range": "16,000,000 - 28,000,000 VND",
                        "description": "Phân tích số liệu người dùng, xây dựng dashboard trực quan phục vụ quyết định kinh doanh. Viết các câu lệnh SQL tối ưu truy vấn dữ liệu lớn.",
                        "requirements": {
                            "skills": ["SQL", "PowerBI", "Python", "Excel", "Data Analysis", "Statistics"],
                            "raw_requirements": "Kinh nghiệm phân tích dữ liệu, thành thạo SQL (Join, Subquery, Window function). Biết sử dụng PowerBI và thư viện Pandas.",
                            "benefits": "Được đào tạo bài bản, môi trường cởi mở, cơ hội thăng tiến lên Data Engineer.",
                            "tags": ["Data", "SQL", "Analyst"]
                        },
                        "experience_level": "Junior/Middle",
                        "job_type": "Full-time"
                    }
                ]
                added, updated, skipped = await _async_save_job_listings(dummy_jobs)
                logger.info("[startup] Seeding complete: added=%d, updated=%d, skipped=%d", added, updated, skipped)
            else:
                logger.info("[startup] job_listings table is already seeded (count=%d)", count)
    except Exception as e:
        logger.error("[startup] Seeding dummy jobs failed: %s", e, exc_info=True)

    yield
    logger.info("[shutdown] application stopped")

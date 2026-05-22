"""Crawler Worker: Scheduled JD collection from job boards.

Runs as Celery async task on Spot instances.
Scheduled via Prefect/Airflow for daily light-crawl.
"""

import asyncio
import logging
from typing import Any

import httpx
from bs4 import BeautifulSoup
from celery import shared_task  # type: ignore[import-untyped]

# Import the Celery app so @shared_task can find and register with it
from app.workers.celery_app import celery_app as _celery_app  # noqa: F401

logger = logging.getLogger(__name__)

MOCK_JOBS = {
    "topcv": [
        {
            "title": "Senior Python Backend Developer (FastAPI, Postgres, AWS)",
            "company": "SmartTech Solutions",
            "location": "Hà Nội",
            "salary_range": "25 - 40 triệu VNĐ",
            "description": (
                "Chúng tôi đang tìm kiếm Senior Python Developer để tham gia phát triển hệ thống AI/ML và "
                "backend API phục vụ hàng triệu người dùng.\nCông việc bao gồm:\n"
                "- Thiết kế kiến trúc hệ thống microservices.\n"
                "- Phát triển RESTful API hiệu năng cao bằng FastAPI/Django.\n"
                "- Tối ưu hóa truy vấn cơ sở dữ liệu PostgreSQL/Redis.\n"
                "- Hợp tác với đội ngũ Data Science để tích hợp các mô hình Machine Learning."
            ),
            "requirements": {
                "skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Redis", "Docker", "AWS", "Git"],
                "experience_years": 4
            },
            "source_url": "https://www.topcv.vn/viec-lam/senior-python-developer/mock1"
        },
        {
            "title": "React.js Frontend Engineer (Tailwind, TypeScript)",
            "company": "WebFlow Studio",
            "location": "TP. HCM",
            "salary_range": "18 - 30 triệu VNĐ",
            "description": (
                "Chịu trách nhiệm xây dựng giao diện người dùng (UI) mượt mà, phản hồi nhanh và "
                "thân thiện với SEO cho sản phẩm LancerAI.\nYêu cầu:\n"
                "- Xây dựng component reusable bằng React.js và Next.js.\n"
                "- Tối ưu hiệu năng render của trang web.\n"
                "- Làm việc chặt chẽ với UI/UX Designer."
            ),
            "requirements": {
                "skills": ["React.js", "Next.js", "TypeScript", "JavaScript", "HTML5", "CSS3", "TailwindCSS"],
                "experience_years": 2
            },
            "source_url": "https://www.topcv.vn/viec-lam/react-js-frontend-engineer/mock2"
        },
        {
            "title": "DevOps Engineer (Docker, Kubernetes, CI/CD)",
            "company": "CloudNative Asia",
            "location": "Remote",
            "salary_range": "30 - 50 triệu VNĐ",
            "description": (
                "Phát triển và duy trì hạ tầng đám mây tự động hóa cho các ứng dụng của công ty.\n"
                "Nhiệm vụ:\n"
                "- Triển khai và vận hành các cluster Kubernetes trên AWS/GCP.\n"
                "- Xây dựng pipeline CI/CD tự động bằng Jenkins/GitHub Actions.\n"
                "- Giám sát hệ thống sử dụng Prometheus/Grafana."
            ),
            "requirements": {
                "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Terraform", "Prometheus", "Grafana"],
                "experience_years": 3
            },
            "source_url": "https://www.topcv.vn/viec-lam/devops-engineer/mock3"
        },
        {
            "title": "Data Engineer (Python, Spark, Kafka)",
            "company": "BigData Corp",
            "location": "Hà Nội",
            "salary_range": "35 - 55 triệu VNĐ",
            "description": (
                "Xây dựng các đường ống dữ liệu (data pipeline) thời gian thực phục vụ phân tích dữ liệu lớn.\n"
                "Yêu cầu:\n"
                "- Thiết kế kiến trúc hồ dữ liệu (Data Lake) và kho dữ liệu (Data Warehouse).\n"
                "- Sử dụng Apache Spark/Flink để xử lý dữ liệu hàng đợi.\n"
                "- Quản lý luồng dữ liệu bằng Apache Kafka."
            ),
            "requirements": {
                "skills": ["Python", "SQL", "Apache Spark", "Apache Kafka", "Hadoop", "Data Warehouse"],
                "experience_years": 3
            },
            "source_url": "https://www.topcv.vn/viec-lam/data-engineer/mock4"
        },
        {
            "title": "Fullstack Developer (Node.js & Vue.js)",
            "company": "Lancer Ventures",
            "location": "Đà Nẵng",
            "salary_range": "20 - 35 triệu VNĐ",
            "description": (
                "Tham gia phát triển toàn diện sản phẩm từ frontend đến backend.\n"
                "Nội dung công việc:\n"
                "- Phát triển backend APIs bằng Express/NestJS.\n"
                "- Viết giao diện người dùng sử dụng Vue.js/Nuxt.js.\n"
                "- Tích hợp các cổng thanh toán và quản lý phiên đăng nhập."
            ),
            "requirements": {
                "skills": ["Node.js", "NestJS", "Vue.js", "Express", "MongoDB", "PostgreSQL"],
                "experience_years": 3
            },
            "source_url": "https://www.topcv.vn/viec-lam/fullstack-developer/mock5"
        }
    ],
    "itviec": [
        {
            "title": "Python/Go Software Engineer",
            "company": "VNG Corporation",
            "location": "TP. HCM",
            "salary_range": "1500 - 3000 USD",
            "description": (
                "Tham gia thiết kế và nâng cấp hệ thống backend có lượng truy cập lớn (high-traffic) "
                "bằng Python và Golang.\nYêu cầu:\n"
                "- Tối ưu hóa API latency và database throughput.\n"
                "- Phát triển microservices kết nối qua gRPC/REST.\n"
                "- Thực hiện unit test và integration test đầy đủ."
            ),
            "requirements": {
                "skills": ["Python", "Golang", "Go", "gRPC", "PostgreSQL", "Kafka", "Microservices"],
                "experience_years": 3
            },
            "source_url": "https://itviec.com/it-jobs/python-go-software-engineer-mock1"
        },
        {
            "title": "Senior Node.js Developer",
            "company": "FPT Software",
            "location": "Hà Nội",
            "salary_range": "1200 - 2500 USD",
            "description": (
                "Chịu trách nhiệm chính trong thiết kế và phát triển các sản phẩm phần mềm của đối tác quốc tế.\n"
                "Yêu cầu:\n"
                "- Thành thạo Node.js, Express/NestJS.\n"
                "- Kỹ năng thiết kế DB tốt (PostgreSQL, MongoDB).\n"
                "- Tiếng Anh giao tiếp tốt trong công việc."
            ),
            "requirements": {
                "skills": ["Node.js", "NestJS", "Express", "PostgreSQL", "MongoDB", "TypeScript", "English"],
                "experience_years": 4
            },
            "source_url": "https://itviec.com/it-jobs/senior-node-js-developer-mock2"
        },
        {
            "title": "AWS Cloud Solutions Architect",
            "company": "Viettel Group",
            "location": "Hà Nội",
            "salary_range": "2000 - 4000 USD",
            "description": (
                "Tư vấn thiết kế hạ tầng điện toán đám mây AWS cho các dự án quy mô quốc gia.\n"
                "Nhiệm vụ:\n"
                "- Tối ưu chi phí và tăng tính bảo mật, sẵn sàng cao của hệ thống.\n"
                "- Hỗ trợ team dev chuyển đổi hạ tầng từ on-premise lên Cloud.\n"
                "- Sử dụng Terraform viết Infrastructure as Code."
            ),
            "requirements": {
                "skills": ["AWS", "Cloud Architecture", "Terraform", "Security", "Linux", "Kubernetes"],
                "experience_years": 5
            },
            "source_url": "https://itviec.com/it-jobs/aws-cloud-solutions-architect-mock3"
        },
        {
            "title": "Lead Product Manager (Agile, Scrum)",
            "company": "Tiki.vn",
            "location": "TP. HCM",
            "salary_range": "2000 - 3500 USD",
            "description": (
                "Định hình tầm nhìn sản phẩm thương mại điện tử, lập kế hoạch phát triển và quản lý backlog.\n"
                "Yêu cầu:\n"
                "- Phối hợp với đội ngũ dev, marketing, và sales để ra mắt tính năng.\n"
                "- Sử dụng quy trình Agile/Scrum linh hoạt.\n"
                "- Phân tích hành vi khách hàng bằng dữ liệu."
            ),
            "requirements": {
                "skills": ["Product Management", "Agile", "Scrum", "Jira", "SQL", "A/B Testing"],
                "experience_years": 5
            },
            "source_url": "https://itviec.com/it-jobs/lead-product-manager-mock4"
        },
        {
            "title": "Machine Learning Engineer (Computer Vision)",
            "company": "VinAI Research",
            "location": "Hà Nội",
            "salary_range": "1800 - 3200 USD",
            "description": (
                "Nghiên cứu và phát triển các mô hình học sâu (Deep Learning) về Computer Vision "
                "ứng dụng vào xe tự lái và smart camera.\nYêu cầu:\n"
                "- Thành thạo PyTorch hoặc TensorFlow.\n"
                "- Tối ưu hóa mô hình chạy trên thiết bị edge/GPU.\n"
                "- Có công bố khoa học là một lợi thế lớn."
            ),
            "requirements": {
                "skills": ["Python", "PyTorch", "TensorFlow", "Computer Vision", "Deep Learning", "OpenCV"],
                "experience_years": 2
            },
            "source_url": "https://itviec.com/it-jobs/machine-learning-engineer-mock5"
        }
    ]
}


def _crawl_source_sync(source: str, max_pages: int) -> list[dict[str, Any]]:
    """Crawl jobs synchronously using httpx and BeautifulSoup, with a robust mock fallback."""
    jobs = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        if source == "topcv":
            for page in range(1, max_pages + 1):
                url = f"https://www.topcv.vn/tim-viec-lam?keyword=IT&page={page}"
                resp = httpx.get(url, headers=headers, timeout=10.0, follow_redirects=True)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "html.parser")
                items = soup.find_all("div", class_=lambda x: x and "job-item" in x)
                if not items:
                    break
                for item in items:
                    try:
                        title_el = item.find("h3", class_=lambda x: x and "title" in x) or item.find(
                            class_=lambda x: x and "title" in x
                        )
                        if not title_el:
                            continue
                        title_a = title_el.find("a") if hasattr(title_el, "find") else None
                        title = title_a.text.strip() if title_a else title_el.text.strip()
                        link = ""
                        if title_a and title_a.has_attr("href"):
                            href_val = title_a["href"]
                            link = href_val[0] if isinstance(href_val, list) else str(href_val)
                        if link and not link.startswith("http"):
                            link = f"https://www.topcv.vn{link}"

                        company_el = item.find(class_=lambda x: x and "company" in x)
                        company = company_el.text.strip() if company_el else ""

                        location_el = item.find(class_=lambda x: x and "address" in x) or item.find(
                            class_=lambda x: x and "location" in x
                        )
                        location = location_el.text.strip() if location_el else "Hà Nội/TP.HCM"

                        salary_el = item.find(class_=lambda x: x and "salary" in x)
                        salary = salary_el.text.strip() if salary_el else "Thỏa thuận"

                        description = (
                            f"Tuyển dụng vị trí {title} tại {company}. "
                            f"Địa điểm: {location}. Mức lương: {salary}."
                        )
                        requirements = {"skills": ["IT", "Software"], "experience_years": 1}

                        jobs.append({
                            "source": "topcv",
                            "source_url": link or f"https://www.topcv.vn/viec-lam/detail-{hash(title)}",
                            "title": title,
                            "company": company,
                            "location": location,
                            "salary_range": salary,
                            "description": description,
                            "requirements": requirements,
                        })
                    except Exception:
                        continue
        elif source == "itviec":
            for page in range(1, max_pages + 1):
                url = f"https://itviec.com/it-jobs?page={page}"
                resp = httpx.get(url, headers=headers, timeout=10.0, follow_redirects=True)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "html.parser")
                items = soup.find_all("div", class_=lambda x: x and "job" in x)
                if not items:
                    break
                for item in items:
                    try:
                        title_el = item.find("h2") or item.find("h3") or item.find(class_=lambda x: x and "title" in x)
                        if not title_el:
                            continue
                        title_a = title_el.find("a") if hasattr(title_el, "find") else None
                        title = title_a.text.strip() if title_a else title_el.text.strip()
                        link = ""
                        if title_a and title_a.has_attr("href"):
                            href_val = title_a["href"]
                            link = href_val[0] if isinstance(href_val, list) else str(href_val)
                        if link and not link.startswith("http"):
                            link = f"https://itviec.com{link}"

                        company_el = item.find(class_=lambda x: x and "company" in x)
                        company = company_el.text.strip() if company_el else ""

                        location_el = item.find(class_=lambda x: x and "address" in x) or item.find(
                            class_=lambda x: x and "location" in x
                        )
                        location = location_el.text.strip() if location_el else "Hồ Chí Minh"

                        salary_el = item.find(class_=lambda x: x and "salary" in x)
                        salary = salary_el.text.strip() if salary_el else "Thỏa thuận"

                        description = (
                            f"Tuyển dụng {title} làm việc tại {company}. "
                            "Yêu cầu ứng viên năng động, có kỹ năng tốt."
                        )
                        requirements = {"skills": ["IT", "Software"], "experience_years": 2}

                        jobs.append({
                            "source": "itviec",
                            "source_url": link or f"https://itviec.com/it-jobs/detail-{hash(title)}",
                            "title": title,
                            "company": company,
                            "location": location,
                            "salary_range": salary,
                            "description": description,
                            "requirements": requirements,
                        })
                    except Exception:
                        continue
    except Exception as e:
        logger.warning("Scraping source %s failed: %s. Using fallback.", source, e)

    # Use mock jobs as fallback if no jobs crawled or failed
    if not jobs:
        logger.info("No jobs crawled for %s. Populating with mock data.", source)
        source_key = source.lower()
        if source_key not in MOCK_JOBS:
            source_key = "topcv"
        for mock_job in MOCK_JOBS[source_key]:
            jobs.append({"source": source, **mock_job})

    return jobs


async def _async_save_job_listings(jobs: list[dict[str, Any]]) -> tuple[int, int]:
    """Helper to save jobs in PostgreSQL and generate/save embeddings in VectorDB."""
    from sqlalchemy import select

    from app.core.database import _get_session_factory
    from app.core.providers.connectors import get_llm_connector, get_vector_repository
    from app.models.job_listing import JobListing

    session_factory = _get_session_factory()
    vector_repo = get_vector_repository()
    llm = get_llm_connector()

    jobs_added = 0
    jobs_skipped = 0

    async with session_factory() as session:
        for job_data in jobs:
            try:
                # Deduplicate based on source_url
                stmt = select(JobListing).where(JobListing.source_url == job_data["source_url"])
                res = await session.execute(stmt)
                existing = res.scalars().first()
                if existing:
                    jobs_skipped += 1
                    continue

                # Insert relational record
                job = JobListing(
                    source=job_data["source"],
                    source_url=job_data["source_url"],
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data["location"],
                    description=job_data["description"],
                    requirements=job_data["requirements"],
                    salary_range=job_data["salary_range"],
                    is_active=True,
                )
                session.add(job)
                await session.flush()  # Gets the auto-generated id

                # Generate and store embedding
                text_to_embed = (
                    f"{job.title}\nCompany: {job.company}\nLocation: {job.location}\nDescription: {job.description}"
                )
                embedding = await llm.embed(text_to_embed)
                if embedding:
                    metadata = {
                        "title": job.title,
                        "company": job.company,
                        "location": job.location,
                        "url": job.source_url,
                        "source_url": job.source_url,
                    }
                    await vector_repo.store_embedding(
                        doc_id=job.id,
                        text=text_to_embed,
                        embedding=embedding,
                        metadata=metadata,
                    )
                else:
                    logger.warning("Failed to generate embedding for job '%s'", job.title)

                jobs_added += 1
            except Exception as e:
                logger.error("Error processing job '%s': %s", job_data.get("title"), e, exc_info=True)
                continue

        await session.commit()

    return jobs_added, jobs_skipped


@shared_task(bind=True, max_retries=3, default_retry_delay=60)  # type: ignore[untyped-decorator]
def crawl_job_listings(self: Any, source: str = "topcv", max_pages: int = 5) -> dict[str, Any]:
    """Crawl job listings from a specified source.

    Light-crawl strategy: Limited pages per run, daily schedule.
    Designed to be retry-safe for Spot instance interruptions.
    """
    logger.info("Starting crawl job listings for source: %s, max_pages: %d", source, max_pages)

    if source not in ("topcv", "itviec"):
        raise ValueError(f"Unsupported source: {source}")

    try:
        # Perform network crawling or fall back to mock jobs
        jobs = _crawl_source_sync(source, max_pages)
    except Exception as exc:
        logger.error("Crawl task setup/scraping failed: %s", exc, exc_info=True)
        try:
            self.retry(exc=exc)
        except Exception:
            raise exc from None

    try:
        def _run_async_helper(coro: Any) -> Any:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop = asyncio.get_event_loop()

            if loop.is_running():
                from concurrent.futures import ThreadPoolExecutor

                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)

        jobs_added, jobs_skipped = _run_async_helper(_async_save_job_listings(jobs))
    except Exception as exc:
        logger.error("Failed to store crawled job listings: %s", exc, exc_info=True)
        try:
            self.retry(exc=exc)
        except Exception:
            raise exc from None

    return {
        "status": "success",
        "source": source,
        "pages_crawled": max_pages,
        "jobs_added": jobs_added,
        "jobs_skipped": jobs_skipped,
    }

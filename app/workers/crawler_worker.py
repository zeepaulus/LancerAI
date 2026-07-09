"""Polite job listing crawler for public IT job boards."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from typing import Any
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)

TOPCV_BASE_URL = "https://www.topcv.vn/tim-viec-lam-moi-nhat"
TOPCV_QUERY_PARAMS = {
    "company_field": "1",
    "type_keyword": "1",
    "sba": "1",
    "saturday_status": "0",
}
TOPCV_APPROVED_SOURCE_URL = f"{TOPCV_BASE_URL}?{urlencode(TOPCV_QUERY_PARAMS)}"
TOPCV_HOST = "www.topcv.vn"
CRAWLER_USER_AGENT = "LancerAIJobCrawler/1.0 (+https://lancerai.local; public IT job indexing)"
REQUEST_DELAY_SECONDS = 1.5
REQUEST_TIMEOUT_SECONDS = 12.0
BLOCKED_STATUS_CODES = {401, 403, 429}
MAX_DETAIL_LINKS_PER_PAGE = 15

IT_KEYWORDS = {
    "ai",
    "api",
    "aws",
    "backend",
    "cloud",
    "data",
    "database",
    "devops",
    "docker",
    "fastapi",
    "frontend",
    "fullstack",
    "full-stack",
    "java",
    "javascript",
    "kubernetes",
    "machine learning",
    "mobile",
    "node",
    "php",
    "python",
    "qa",
    "react",
    "software",
    "sql",
    "tester",
    "testing",
    "typescript",
}

SKILL_DICTIONARY = [
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "C#",
    "Go",
    "PHP",
    "React",
    "Vue",
    "Angular",
    "Node.js",
    "Express",
    "NestJS",
    "FastAPI",
    "Django",
    "Flask",
    "Spring",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Redis",
    "SQL",
    "Docker",
    "Kubernetes",
    "AWS",
    "GCP",
    "Azure",
    "Linux",
    "CI/CD",
    "Git",
    "REST API",
    "GraphQL",
    "Kafka",
    "RabbitMQ",
    "Spark",
    "Airflow",
    "Pandas",
    "PyTorch",
    "TensorFlow",
    "Playwright",
    "Selenium",
    "Cypress",
    "Jenkins",
    "Terraform",
]

SECTION_STOP_HEADINGS = {
    "mo ta cong viec",
    "yeu cau ung vien",
    "yeu cau",
    "quyen loi",
    "dia diem lam viec",
    "thoi gian lam viec",
    "cach thuc ung tuyen",
    "requirements",
    "benefits",
    "job description",
    "location",
    "salary",
}


class TopCVBlockedError(RuntimeError):
    """Raised when TopCV returns a status that should stop crawling."""


def build_topcv_search_url(page: int) -> str:
    """Build the approved TopCV latest-jobs URL while preserving source params."""
    safe_page = max(1, int(page or 1))
    query = dict(TOPCV_QUERY_PARAMS)
    query["page"] = str(safe_page)
    return urlunparse(("https", TOPCV_HOST, "/tim-viec-lam-moi-nhat", "", urlencode(query), ""))


def validate_topcv_source_url(url: str) -> bool:
    """Validate that a URL matches the approved TopCV path and query params."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != TOPCV_HOST or parsed.path != "/tim-viec-lam-moi-nhat":
        return False

    query = parse_qs(parsed.query)
    for key, value in TOPCV_QUERY_PARAMS.items():
        if query.get(key, [None])[0] != value:
            return False

    page_values = query.get("page", [])
    return not page_values or all(value.isdigit() and int(value) >= 1 for value in page_values)


def clean_text(value: Any) -> str:
    """Collapse whitespace and strip invisible noise."""
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _clean_text(value: Any) -> str:
    return clean_text(value)


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _norm(value: str) -> str:
    return _strip_accents(clean_text(value)).lower()


def _first_text(soup: BeautifulSoup, selectors: list[str]) -> str:
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            text = clean_text(element.get_text(" "))
            if text:
                return text
    return ""


def _topcv_headers() -> dict[str, str]:
    return {
        "User-Agent": CRAWLER_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "vi,en-US;q=0.8,en;q=0.6",
    }


def _looks_blocked_html(html: str) -> bool:
    marker = _norm(html[:5000])
    blocked_markers = (
        "captcha",
        "cloudflare",
        "access denied",
        "forbidden",
        "xac minh",
        "verify you are human",
        "security check",
    )
    return any(item in marker for item in blocked_markers)


def _canonical_topcv_job_url(href: str) -> str:
    if not href:
        return ""
    absolute = urljoin("https://www.topcv.vn", href.strip())
    parsed = urlparse(absolute)
    if parsed.scheme not in {"http", "https"} or parsed.netloc != TOPCV_HOST:
        return ""
    if "/viec-lam/" not in parsed.path or parsed.path in {"/viec-lam", "/viec-lam/"}:
        return ""
    return urlunparse(("https", TOPCV_HOST, parsed.path, "", "", ""))


def _is_action_anchor(anchor: Any) -> bool:
    href = str(anchor.get("href", ""))
    classes = " ".join(anchor.get("class", []) or [])
    text = anchor.get_text(" ")
    marker = _norm(f"{href} {classes} {text}")
    action_words = ("ung tuyen", "apply", "save", "luu tin", "quick-view", "quick view", "xem nhanh")
    return any(word in marker for word in action_words) and len(clean_text(text)) < 40


def extract_topcv_listing_links(html: str) -> list[str]:
    """Extract likely public TopCV job detail links from a listing page."""
    soup = BeautifulSoup(html or "", "html.parser")
    links: list[str] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        if _is_action_anchor(anchor):
            continue
        url = _canonical_topcv_job_url(str(anchor.get("href", "")))
        if not url or url in seen:
            continue
        seen.add(url)
        links.append(url)

    return links


def _nearest_job_container(anchor: Any) -> Any:
    return anchor.find_parent(["article", "li", "section"]) or anchor.find_parent("div")


def _container_hint(container: Any, selectors: list[str]) -> str:
    if not container:
        return ""
    return _first_text(container, selectors)


def parse_salary(text: str) -> str:
    normalized = clean_text(text)
    patterns = [
        r"(?:muc luong|salary)\s*:?\s*([^|;\n]+)",
        r"(thuong luong|thoa thuan|negotiable)",
        r"(\d[\d.,]*\s*-\s*\d[\d.,]*\s*(?:trieu|million|usd|vnd|d))",
        r"(toi\s+\d[\d.,]*\s*(?:trieu|million|usd|vnd|d))",
        r"(up to\s+\d[\d.,]*\s*(?:usd|vnd|d|million))",
    ]
    ascii_text = _norm(normalized)
    for pattern in patterns:
        match = re.search(pattern, ascii_text, re.IGNORECASE)
        if match:
            return clean_text(match.group(1))
    return ""


def parse_location(text: str) -> str:
    normalized = clean_text(text)
    ascii_text = _norm(normalized)
    locations = [
        ("Ha Noi", "ha noi"),
        ("Ho Chi Minh", "ho chi minh"),
        ("Da Nang", "da nang"),
        ("Can Tho", "can tho"),
        ("Binh Duong", "binh duong"),
        ("Dong Nai", "dong nai"),
        ("Remote", "remote"),
        ("Toan quoc", "toan quoc"),
    ]
    for label, marker in locations:
        if marker in ascii_text:
            return label
    labeled = re.search(r"(?:dia diem|location)\s*:?\s*([^|;\n]+)", ascii_text, re.IGNORECASE)
    return clean_text(labeled.group(1)) if labeled else ""


def parse_company(soup: BeautifulSoup) -> str:
    json_ld = extract_json_ld_jobposting(soup)
    hiring_org = json_ld.get("hiringOrganization") if json_ld else None
    if isinstance(hiring_org, dict):
        company = clean_text(hiring_org.get("name"))
        if company:
            return company
    if isinstance(hiring_org, str):
        company = clean_text(hiring_org)
        if company:
            return company
    return _first_text(
        soup,
        [
            "[class*='company-name']",
            "[class*='company'] a",
            "a[href*='/cong-ty/']",
            "[class*='company']",
        ],
    )


def _extract_labeled_text(soup: BeautifulSoup, labels: list[str]) -> str:
    page_text = soup.get_text("\n")
    lines = [clean_text(line) for line in page_text.splitlines()]
    lines = [line for line in lines if line]
    normalized_labels = [_norm(label).rstrip(":") for label in labels]

    for index, line in enumerate(lines):
        normalized_line = _norm(line).rstrip(":")
        for label in normalized_labels:
            if normalized_line == label or normalized_line.startswith(f"{label}:"):
                inline = line.split(":", 1)[1].strip() if ":" in line else ""
                if inline:
                    return inline

                collected: list[str] = []
                for next_line in lines[index + 1 :]:
                    normalized_next = _norm(next_line).rstrip(":")
                    if normalized_next in SECTION_STOP_HEADINGS:
                        break
                    collected.append(next_line)
                    if len(" ".join(collected)) > 2000:
                        break
                return clean_text(" ".join(collected))
    return ""


def section_after_heading(soup: BeautifulSoup, headings: list[str], max_chars: int = 4000) -> str:
    text = _extract_labeled_text(soup, headings)
    return text[:max_chars] if text else ""


def parse_requirements_section(soup: BeautifulSoup) -> str:
    return section_after_heading(soup, ["Yeu cau ung vien", "Yeu cau", "Requirements", "Qualifications"])


def parse_benefits_section(soup: BeautifulSoup) -> str:
    return section_after_heading(soup, ["Quyen loi", "Benefits", "Phuc loi"])


def _html_to_text(value: Any) -> str:
    if not value:
        return ""
    return clean_text(BeautifulSoup(str(value), "html.parser").get_text(" "))


def _iter_json_ld_nodes(data: Any) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    if isinstance(data, dict):
        nodes.append(data)
        graph = data.get("@graph")
        if isinstance(graph, list):
            for item in graph:
                nodes.extend(_iter_json_ld_nodes(item))
    elif isinstance(data, list):
        for item in data:
            nodes.extend(_iter_json_ld_nodes(item))
    return nodes


def extract_json_ld_jobposting(soup: BeautifulSoup) -> dict[str, Any]:
    """Return schema.org JobPosting data when the page exposes it."""
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = script.string or script.get_text()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for node in _iter_json_ld_nodes(payload):
            node_type = node.get("@type")
            types = node_type if isinstance(node_type, list) else [node_type]
            if any(str(item).lower() == "jobposting" for item in types if item):
                return node
    return {}


def _json_ld_location(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(filter(None, (_json_ld_location(item) for item in value)))
    if isinstance(value, dict):
        address = value.get("address", value)
        if isinstance(address, dict):
            parts = [
                address.get("streetAddress"),
                address.get("addressLocality"),
                address.get("addressRegion"),
                address.get("addressCountry"),
            ]
            return clean_text(", ".join(str(part) for part in parts if part))
        return clean_text(address)
    return clean_text(value)


def _json_ld_salary(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(filter(None, (_json_ld_salary(item) for item in value)))
    if not isinstance(value, dict):
        return clean_text(value)

    currency = value.get("currency") or value.get("salaryCurrency") or ""
    salary_value = value.get("value")
    if isinstance(salary_value, dict):
        min_value = salary_value.get("minValue")
        max_value = salary_value.get("maxValue")
        unit = salary_value.get("unitText") or ""
        single = salary_value.get("value")
        if min_value and max_value:
            return clean_text(f"{min_value} - {max_value} {currency} {unit}")
        if single:
            return clean_text(f"{single} {currency} {unit}")
    return clean_text(value.get("value") or "")


def extract_topcv_job_cards(html: str) -> list[dict[str, Any]]:
    """Parse listing-page cards without depending on one TopCV class name."""
    soup = BeautifulSoup(html or "", "html.parser")
    jobs: list[dict[str, Any]] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        if _is_action_anchor(anchor):
            continue
        source_url = _canonical_topcv_job_url(str(anchor.get("href", "")))
        if not source_url or source_url in seen:
            continue

        title = clean_text(anchor.get_text(" "))
        if len(title) < 4:
            continue

        container = _nearest_job_container(anchor)
        container_text = clean_text(container.get_text(" ")) if container else title
        company = _container_hint(container, ["[class*='company-name']", "[class*='company'] a", "[class*='company']"])
        location = _container_hint(
            container,
            ["[class*='address']", "[class*='location']"],
        ) or parse_location(container_text)
        salary = _container_hint(container, ["[class*='salary']"]) or parse_salary(container_text)
        tags = infer_it_role_tags(f"{title} {container_text}")

        seen.add(source_url)
        jobs.append(
            normalize_job_listing(
                {
                    "source": "topcv",
                    "source_url": source_url,
                    "title": title,
                    "company": company,
                    "location": location,
                    "salary_range": salary,
                    "description": container_text[:3000],
                    "requirements": {
                        "skills": tags,
                        "raw_requirements": container_text[:2000],
                        "tags": tags,
                    },
                    "experience_level": infer_experience_level(container_text),
                    "job_type": infer_job_type(container_text),
                }
            )
        )

    return jobs


def parse_topcv_job_card(card: Any) -> dict[str, Any]:
    """Best-effort parser for callers that already selected a listing card."""
    title_el = card.select_one("h3 a[href*='/viec-lam/'], h2 a[href*='/viec-lam/'], a[href*='/viec-lam/']")
    href = str(title_el.get("href", "")) if title_el else ""
    source_url = _canonical_topcv_job_url(href)
    title = clean_text(title_el.get_text(" ")) if title_el else ""
    container_text = clean_text(card.get_text(" "))
    tags = infer_it_role_tags(f"{title} {container_text}")
    return normalize_job_listing(
        {
            "source": "topcv",
            "source_url": source_url,
            "title": title,
            "company": _container_hint(card, ["[class*='company-name']", "[class*='company'] a", "[class*='company']"]),
            "location": _container_hint(
                card,
                ["[class*='address']", "[class*='location']"],
            )
            or parse_location(container_text),
            "salary_range": _container_hint(card, ["[class*='salary']"]) or parse_salary(container_text),
            "description": container_text[:3000],
            "requirements": {"skills": tags, "raw_requirements": container_text[:2000], "tags": tags},
            "experience_level": infer_experience_level(container_text),
            "job_type": infer_job_type(container_text),
        }
    )


def _parse_topcv_cards(html: str) -> list[dict[str, Any]]:
    return extract_topcv_job_cards(html)


def _parse_topcv_anchor_jobs(html: str) -> list[dict[str, Any]]:
    return extract_topcv_job_cards(html)


def fetch_listing_html_static(client: httpx.Client, url: str) -> tuple[str, int]:
    """Fetch one public listing page through static HTTP."""
    response = client.get(url, follow_redirects=True)
    if response.status_code in BLOCKED_STATUS_CODES:
        raise TopCVBlockedError(f"TopCV blocked listing request ({response.status_code})")
    response.raise_for_status()
    return response.text, response.status_code


def fetch_topcv_job_detail(client: httpx.Client, url: str) -> str:
    """Fetch a public TopCV detail page without bypassing protections."""
    html, _status = fetch_detail_html_static(client, url)
    return html


def fetch_detail_html_static(client: httpx.Client, url: str) -> tuple[str, int]:
    """Fetch one public detail page through static HTTP."""
    response = client.get(url, follow_redirects=True)
    if response.status_code in BLOCKED_STATUS_CODES:
        raise TopCVBlockedError(f"TopCV blocked detail request ({response.status_code})")
    response.raise_for_status()
    return response.text, response.status_code


def _fetch_html_playwright(url: str, wait_selector: str | None = None) -> str:
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        logger.warning("[TopCV crawler] Playwright unavailable: %s", exc)
        return ""

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(user_agent=CRAWLER_USER_AGENT, locale="vi-VN")
            page.goto(url, wait_until="networkidle", timeout=REQUEST_TIMEOUT_SECONDS * 1000)
            if wait_selector:
                try:
                    page.wait_for_selector(wait_selector, timeout=5000)
                except PlaywrightTimeoutError:
                    logger.info("[TopCV crawler] Playwright selector not found: %s", wait_selector)
            html = page.content()
            browser.close()
            return html
    except Exception as exc:
        logger.warning("[TopCV crawler] Playwright fallback failed for %s: %s", url, exc)
        return ""


def fetch_listing_html_playwright(url: str) -> str:
    """Optional rendered-HTML fallback for listing pages."""
    return _fetch_html_playwright(url, "a[href*='/viec-lam/']")


def fetch_detail_html_playwright(url: str) -> str:
    """Optional rendered-HTML fallback for detail pages."""
    return _fetch_html_playwright(url, "h1")


def get_listing_html(client: httpx.Client, url: str) -> tuple[str, str, int | None]:
    """Fetch listing HTML; use Playwright only when static HTML has no job links."""
    html, status_code = fetch_listing_html_static(client, url)
    if _looks_blocked_html(html):
        raise TopCVBlockedError("TopCV returned a challenge or blocked listing page")
    if extract_topcv_listing_links(html):
        return html, "static", status_code

    rendered = fetch_listing_html_playwright(url)
    if rendered and extract_topcv_listing_links(rendered):
        return rendered, "playwright", status_code
    return html, "static-empty", status_code


def get_detail_html(client: httpx.Client, url: str) -> tuple[str, str, int | None]:
    """Fetch detail HTML; use Playwright only when static HTML looks too thin."""
    html, status_code = fetch_detail_html_static(client, url)
    if _looks_blocked_html(html):
        raise TopCVBlockedError("TopCV returned a challenge or blocked detail page")
    parsed = parse_topcv_job_detail(html, url)
    if parsed.get("title") and (parsed.get("description") or parsed.get("requirements", {}).get("raw_requirements")):
        return html, "static", status_code

    rendered = fetch_detail_html_playwright(url)
    if rendered:
        return rendered, "playwright", status_code
    return html, "static-thin", status_code


def parse_topcv_job_detail(html: str, source_url: str = "") -> dict[str, Any]:
    """Parse detail page into a normalized partial job listing."""
    soup = BeautifulSoup(html or "", "html.parser")
    json_ld = extract_json_ld_jobposting(soup)

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = clean_text(json_ld.get("title") or json_ld.get("name")) if json_ld else ""
    title = title or _first_text(
        soup,
        [
            "h1",
            "[class*='job-detail'] [class*='title']",
            "[class*='job-title']",
            "[class*='title']",
        ],
    )

    hiring_org = json_ld.get("hiringOrganization") if json_ld else None
    if isinstance(hiring_org, dict):
        company = clean_text(hiring_org.get("name"))
    elif isinstance(hiring_org, str):
        company = clean_text(hiring_org)
    else:
        company = ""
    company = company or parse_company(soup)
    location = _json_ld_location(json_ld.get("jobLocation")) if json_ld else ""
    location = location or _extract_labeled_text(soup, ["Dia diem", "Location", "Noi lam viec"])
    location = location or _first_text(soup, ["[class*='address']", "[class*='location']"])

    salary = _json_ld_salary(json_ld.get("baseSalary")) if json_ld else ""
    salary = salary or _extract_labeled_text(soup, ["Muc luong", "Salary"])
    salary = salary or _first_text(soup, ["[class*='salary']"])

    description = _html_to_text(json_ld.get("description")) if json_ld else ""
    raw_text = clean_text(soup.get_text(" "))
    description = description or section_after_heading(soup, ["Mo ta cong viec", "Job description"], 12000)
    description = description or raw_text[:12000]

    requirements_text = _html_to_text(json_ld.get("qualifications") or json_ld.get("skills")) if json_ld else ""
    requirements_text = requirements_text or parse_requirements_section(soup)
    benefits_text = _html_to_text(json_ld.get("jobBenefits")) if json_ld else ""
    benefits_text = benefits_text or parse_benefits_section(soup)

    employment_type = json_ld.get("employmentType") if json_ld else None
    if isinstance(employment_type, list):
        employment_type = ", ".join(str(item) for item in employment_type)

    tags = infer_it_role_tags(f"{title} {description} {requirements_text}")
    experience_text = clean_text(json_ld.get("experienceRequirements")) if json_ld else ""
    experience_text = experience_text or raw_text

    return normalize_job_listing(
        {
            "source": "topcv",
            "source_url": source_url,
            "title": title,
            "company": company,
            "location": location or parse_location(raw_text),
            "salary_range": salary or parse_salary(raw_text),
            "description": description,
            "requirements": {
                "skills": tags,
                "experience_years": _infer_experience_years(experience_text),
                "raw_requirements": requirements_text[:4000],
                "benefits": benefits_text[:2500],
                "tags": tags,
            },
            "experience_level": infer_experience_level(f"{title} {experience_text}"),
            "job_type": infer_job_type(clean_text(employment_type) or raw_text),
        }
    )


def infer_it_role_tags(text: str) -> list[str]:
    normalized = _norm(text)
    tags = [skill for skill in SKILL_DICTIONARY if _norm(skill) in normalized]
    if "frontend" in normalized or "front-end" in normalized:
        tags.append("Frontend")
    if "backend" in normalized or "back-end" in normalized:
        tags.append("Backend")
    if "fullstack" in normalized or "full-stack" in normalized:
        tags.append("Fullstack")
    if "devops" in normalized:
        tags.append("DevOps")
    if "tester" in normalized or re.search(r"\bqa\b", normalized):
        tags.append("QA")
    if "data engineer" in normalized:
        tags.append("Data Engineer")
    return sorted(set(tags))


def infer_experience_level(text: str) -> str | None:
    normalized = _norm(text)
    if any(word in normalized for word in ["intern", "thuc tap"]):
        return "Intern"
    if any(word in normalized for word in ["fresher", "graduate", "moi ra truong"]):
        return "Fresher"
    if "junior" in normalized:
        return "Junior"
    if any(word in normalized for word in ["middle", "mid-level", "mid level"]):
        return "Middle"
    if any(word in normalized for word in ["senior", "lead", "principal", "architect"]):
        return "Senior"

    years = _infer_experience_years(normalized)
    if years is None:
        return None
    if years >= 5:
        return "Senior"
    if years >= 3:
        return "Middle"
    if years >= 1:
        return "Junior"
    return None


def infer_job_type(text: str) -> str | None:
    normalized = _norm(text)
    if "part-time" in normalized or "part time" in normalized:
        return "Part-time"
    if "remote" in normalized:
        return "Remote"
    if "hybrid" in normalized:
        return "Hybrid"
    if any(marker in normalized for marker in ["full-time", "full time", "full_time", "toan thoi gian"]):
        return "Full-time"
    return None


def _infer_experience_years(text: str) -> int | None:
    normalized = _norm(text)
    matches = re.findall(r"(\d+)\+?\s*(?:nam|year|years)", normalized)
    if not matches:
        return None
    return max(int(value) for value in matches[:4])


def _is_it_job(job: dict[str, Any]) -> bool:
    requirements = job.get("requirements", {}) or {}
    text = " ".join(
        [
            str(job.get("title", "")),
            str(job.get("description", "")),
            str(requirements.get("raw_requirements", "")),
            " ".join(requirements.get("skills", []) or []),
        ]
    )
    normalized = _norm(text)
    return bool(infer_it_role_tags(text)) or any(keyword in normalized for keyword in IT_KEYWORDS)


def normalize_job_listing(job: dict[str, Any]) -> dict[str, Any]:
    requirements = job.get("requirements") or {}
    description = clean_text(job.get("description"))
    requirement_text = clean_text(requirements.get("raw_requirements"))
    source_text = f"{description} {requirement_text}"
    tags = requirements.get("tags") or requirements.get("skills") or infer_it_role_tags(source_text)
    skills = requirements.get("skills") or infer_it_role_tags(f"{description} {requirement_text}")
    return {
        "source": clean_text(job.get("source")) or "topcv",
        "source_url": clean_text(job.get("source_url")),
        "title": clean_text(job.get("title")),
        "company": clean_text(job.get("company")),
        "location": clean_text(job.get("location")),
        "salary_range": clean_text(job.get("salary_range")),
        "description": description,
        "requirements": {
            "skills": sorted(set(skills)),
            "experience_years": requirements.get("experience_years") or _infer_experience_years(description),
            "raw_requirements": requirement_text,
            "benefits": clean_text(requirements.get("benefits")),
            "tags": sorted(set(tags)),
        },
        "experience_level": job.get("experience_level")
        or infer_experience_level(f"{job.get('title', '')} {description}"),
        "job_type": job.get("job_type") or infer_job_type(description),
        "is_active": True,
    }


def _crawl_topcv_sync(max_pages: int) -> tuple[list[dict[str, Any]], str]:
    """Crawl TopCV listing/detail pages politely; return jobs and status message."""
    if not validate_topcv_source_url(TOPCV_APPROVED_SOURCE_URL):
        raise ValueError("Approved TopCV source URL failed validation")

    jobs_by_url: dict[str, dict[str, Any]] = {}
    statuses: list[str] = []
    safe_pages = max(1, min(int(max_pages or 1), 5))

    try:
        with httpx.Client(headers=_topcv_headers(), timeout=REQUEST_TIMEOUT_SECONDS) as client:
            for page in range(1, safe_pages + 1):
                list_url = build_topcv_search_url(page)
                try:
                    listing_html, mode, status_code = get_listing_html(client, list_url)
                except TopCVBlockedError as exc:
                    statuses.append(f"blocked:{exc}")
                    logger.warning("[TopCV crawler] Stopping crawl: %s", exc)
                    break

                statuses.append(f"page={page}:status={status_code}:mode={mode}")
                card_jobs = extract_topcv_job_cards(listing_html)
                for job in card_jobs:
                    if job.get("source_url"):
                        jobs_by_url[job["source_url"]] = job

                detail_links = extract_topcv_listing_links(listing_html)[:MAX_DETAIL_LINKS_PER_PAGE]
                if not detail_links:
                    logger.info("[TopCV crawler] No job links found on page %s", page)

                for link in detail_links:
                    time.sleep(REQUEST_DELAY_SECONDS)
                    try:
                        detail_html, detail_mode, _detail_status = get_detail_html(client, link)
                        detail_job = parse_topcv_job_detail(detail_html, link)
                        if detail_job.get("source_url") and detail_job.get("title"):
                            jobs_by_url[detail_job["source_url"]] = {
                                **jobs_by_url.get(detail_job["source_url"], {}),
                                **detail_job,
                            }
                            statuses.append(f"detail={detail_mode}")
                    except TopCVBlockedError as exc:
                        statuses.append(f"detail-blocked:{exc}")
                        logger.warning("[TopCV crawler] Stopping detail crawl: %s", exc)
                        break
                    except Exception as exc:
                        logger.info("[TopCV crawler] Skipping detail %s: %s", link, exc)

                time.sleep(REQUEST_DELAY_SECONDS)
    except Exception as exc:
        logger.warning("[TopCV crawler] Live crawl failed: %s", exc)
        statuses.append(f"failed:{exc.__class__.__name__}")

    jobs = [job for job in jobs_by_url.values() if job.get("title") and _is_it_job(job)]
    if not jobs:
        statuses.append("empty")
    return jobs, ";".join(statuses) or "not-run"


def _crawl_source_sync(source: str, max_pages: int) -> tuple[list[dict[str, Any]], str]:
    if source == "topcv":
        return _crawl_topcv_sync(max_pages=max_pages)
    return [], "unsupported-source"


async def _try_store_embedding(job: Any) -> bool:
    """Best-effort embedding storage; failures do not affect saved jobs."""
    try:
        from app.core.providers.connectors import get_llm_connector, get_vector_repository

        llm = get_llm_connector()
        vector_repo = get_vector_repository()
        text_to_embed = (
            f"{job.title}\nCompany: {job.company}\nLocation: {job.location}\n"
            f"Salary: {job.salary_range}\nDescription: {job.description}\n"
            f"Requirements: {job.requirements}"
        )
        embedding = await llm.embed(text_to_embed[:4000])
        if not embedding:
            logger.warning("[TopCV crawler] Empty embedding for job_id=%s", job.id)
            return False
        await vector_repo.store_embedding(
            doc_id=job.id,
            text=text_to_embed,
            embedding=embedding,
            metadata={
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "url": job.source_url,
                "source_url": job.source_url,
                "source": job.source,
            },
        )
        return True
    except Exception as exc:
        logger.warning("[TopCV crawler] Embedding skipped for job_id=%s: %s", getattr(job, "id", ""), exc)
        return False


async def _async_save_job_listings(jobs: list[dict[str, Any]]) -> tuple[int, int, int]:
    """Save jobs and embeddings; update existing rows by source_url."""
    from sqlalchemy import select

    from app.core.database import _get_session_factory
    from app.models.job_listing import JobListing

    session_factory = _get_session_factory()
    jobs_added = 0
    jobs_updated = 0
    jobs_skipped = 0
    now = datetime.now(UTC)

    async with session_factory() as session:
        for raw_job_data in jobs:
            try:
                job_data = normalize_job_listing(raw_job_data)
                if not job_data.get("source_url") or not job_data.get("title"):
                    jobs_skipped += 1
                    continue

                stmt = select(JobListing).where(JobListing.source_url == job_data["source_url"])
                res = await session.execute(stmt)
                existing = res.scalars().first()

                if existing:
                    existing.source = job_data["source"]
                    existing.title = job_data["title"]
                    existing.company = job_data["company"]
                    existing.location = job_data["location"]
                    existing.description = job_data["description"]
                    existing.requirements = job_data["requirements"]
                    existing.salary_range = job_data["salary_range"]
                    existing.experience_level = job_data["experience_level"]
                    existing.job_type = job_data["job_type"]
                    existing.is_active = True
                    existing.crawled_at = now
                    existing.updated_at = now
                    job = existing
                    jobs_updated += 1
                else:
                    job = JobListing(
                        source=job_data["source"],
                        source_url=job_data["source_url"],
                        title=job_data["title"],
                        company=job_data["company"],
                        location=job_data["location"],
                        description=job_data["description"],
                        requirements=job_data["requirements"],
                        salary_range=job_data["salary_range"],
                        experience_level=job_data["experience_level"],
                        job_type=job_data["job_type"],
                        is_active=True,
                        crawled_at=now,
                        updated_at=now,
                    )
                    session.add(job)
                    await session.flush()
                    jobs_added += 1

                await session.commit()
                await _try_store_embedding(job)
            except Exception as exc:
                await session.rollback()
                logger.error(
                    "[TopCV crawler] Error processing job %r: %s",
                    raw_job_data.get("title"),
                    exc,
                    exc_info=True,
                )
                jobs_skipped += 1
                continue

    return jobs_added, jobs_updated, jobs_skipped


def _run_async_helper(coro: Any) -> Any:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()


def _normalize_crawl_result(result: Any) -> tuple[list[dict[str, Any]], str]:
    """Accept both the current crawler result and the legacy jobs-only shape."""
    if isinstance(result, tuple) and len(result) == 2:
        jobs, crawl_status = result
        return list(jobs or []), str(crawl_status or "ok")

    return list(result or []), "legacy"


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=120,
    name="app.workers.crawler_worker.crawl_job_listings",
)
def crawl_job_listings(self: Any, source: str = "topcv", max_pages: int = 5) -> dict[str, Any]:
    """Crawl public IT job listings from a supported source."""
    logger.info("Starting crawl job listings for source=%s max_pages=%d", source, max_pages)

    if source not in {"topcv"}:
        raise ValueError(f"Unsupported source: {source}")

    try:
        jobs, crawl_status = _normalize_crawl_result(_crawl_source_sync(source, max_pages))
        jobs_added, jobs_updated, jobs_skipped = _run_async_helper(_async_save_job_listings(jobs))
    except Exception as exc:
        logger.error("Crawl task failed: %s", exc, exc_info=True)
        try:
            self.retry(exc=exc)
        except Exception:
            raise exc from None

    return {
        "status": "success",
        "crawl_status": crawl_status,
        "source": source,
        "approved_source_url": TOPCV_APPROVED_SOURCE_URL,
        "pages_crawled": max_pages,
        "jobs_seen": len(jobs),
        "jobs_added": jobs_added,
        "jobs_updated": jobs_updated,
        "jobs_skipped": jobs_skipped,
    }


def _smoke_topcv_crawler() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    page_url = build_topcv_search_url(1)
    print(f"approved_url_valid={validate_topcv_source_url(TOPCV_APPROVED_SOURCE_URL)}")
    print(f"page_1_url={page_url}")
    print(f"page_1_url_valid={validate_topcv_source_url(page_url)}")

    with httpx.Client(headers=_topcv_headers(), timeout=REQUEST_TIMEOUT_SECONDS) as client:
        try:
            listing_html, status_code = fetch_listing_html_static(client, page_url)
            print(f"listing_status_code={status_code}")
        except TopCVBlockedError as exc:
            print(f"listing_blocked={exc}")
            return 2
        except Exception as exc:
            print(f"listing_error={exc.__class__.__name__}: {exc}")
            return 1

        links = extract_topcv_listing_links(listing_html)
        print(f"links_found={len(links)}")
        if not links:
            rendered = fetch_listing_html_playwright(page_url)
            rendered_links = extract_topcv_listing_links(rendered) if rendered else []
            print(f"playwright_links_found={len(rendered_links)}")
            links = rendered_links

        if not links:
            return 0

        detail_url = links[0]
        print(f"detail_url={detail_url}")
        try:
            detail_html, detail_status = fetch_detail_html_static(client, detail_url)
            print(f"detail_status_code={detail_status}")
        except TopCVBlockedError as exc:
            print(f"detail_blocked={exc}")
            return 2
        except Exception as exc:
            print(f"detail_error={exc.__class__.__name__}: {exc}")
            return 1

        parsed = parse_topcv_job_detail(detail_html, detail_url)
        print(
            "parsed_job="
            + json.dumps(
                {
                    "title": parsed.get("title"),
                    "company": parsed.get("company"),
                    "location": parsed.get("location"),
                    "salary_range": parsed.get("salary_range"),
                    "experience_level": parsed.get("experience_level"),
                    "job_type": parsed.get("job_type"),
                    "skills": parsed.get("requirements", {}).get("skills", []),
                },
                ensure_ascii=False,
            )
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Safe TopCV crawler utilities.")
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Fetch one listing page and one detail page without saving.",
    )
    args = parser.parse_args()
    if args.smoke:
        return _smoke_topcv_crawler()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

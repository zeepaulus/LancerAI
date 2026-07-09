from bs4 import BeautifulSoup

from app.workers.crawler_worker import (
    TOPCV_APPROVED_SOURCE_URL,
    build_topcv_search_url,
    extract_json_ld_jobposting,
    extract_topcv_listing_links,
    parse_topcv_job_detail,
    validate_topcv_source_url,
)


def test_topcv_url_builder_preserves_approved_params() -> None:
    page_1 = build_topcv_search_url(1)
    page_2 = build_topcv_search_url(2)

    assert validate_topcv_source_url(TOPCV_APPROVED_SOURCE_URL)
    assert validate_topcv_source_url(page_1)
    assert validate_topcv_source_url(page_2)
    assert "company_field=1" in page_1
    assert "type_keyword=1" in page_1
    assert "sba=1" in page_1
    assert "saturday_status=0" in page_1
    assert "page=1" in page_1
    assert "page=2" in page_2


def test_extract_topcv_listing_links_filters_actions_and_dedupes() -> None:
    html = """
    <a href="/viec-lam/backend-python-dev-j123.html">Backend Python Developer</a>
    <a href="/viec-lam/backend-python-dev-j123.html#apply">Backend Python Developer</a>
    <a class="btn-apply" href="/viec-lam/backend-python-dev-j123.html">Apply</a>
    <a href="/viec-lam/">Jobs</a>
    <a href="https://other.example/viec-lam/fake">Fake</a>
    """

    assert extract_topcv_listing_links(html) == ["https://www.topcv.vn/viec-lam/backend-python-dev-j123.html"]


def test_parse_detail_prefers_json_ld_jobposting() -> None:
    html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "JobPosting",
          "title": "Senior Backend Engineer",
          "description": "<p>Build Python FastAPI services.</p>",
          "hiringOrganization": {"@type": "Organization", "name": "Acme Tech"},
          "jobLocation": {"address": {"addressLocality": "Ha Noi", "addressCountry": "VN"}},
          "baseSalary": {"currency": "USD", "value": {"minValue": 2000, "maxValue": 3500}},
          "employmentType": "FULL_TIME",
          "qualifications": "Python, FastAPI, SQL. 5 years experience.",
          "jobBenefits": "Health insurance"
        }
        </script>
      </head>
      <body><h1>Fallback title</h1></body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")
    assert extract_json_ld_jobposting(soup)["title"] == "Senior Backend Engineer"

    parsed = parse_topcv_job_detail(html, "https://www.topcv.vn/viec-lam/senior-backend-j123.html")
    assert parsed["title"] == "Senior Backend Engineer"
    assert parsed["company"] == "Acme Tech"
    assert "Ha Noi" in parsed["location"]
    assert parsed["experience_level"] == "Senior"
    assert "Python" in parsed["requirements"]["skills"]

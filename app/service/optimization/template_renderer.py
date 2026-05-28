"""CV template rendering — JSON projection and PDF generation."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.llm_connector import LLMConnector

logger = logging.getLogger(__name__)

_ALLOWED_TEMPLATES = {"harvard", "modern", "minimal", "creative"}

_RENDER_SYSTEM = """Bạn là chuyên gia trình bày CV chuyên nghiệp.
Nhiệm vụ: Sắp xếp lại dữ liệu CV theo định dạng của template được yêu cầu.
Trả về JSON hợp lệ (không markdown) phù hợp với template, giữ nguyên tất cả thông tin.
Điều chỉnh thứ tự section và cách trình bày nhưng KHÔNG thêm/bớt nội dung."""

# Minimal Jinja2 HTML template strings per layout style
_HTML_TEMPLATES: dict[str, str] = {
    "harvard": """<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8">
<style>
  body { font-family: "Times New Roman", serif; margin: 40px; color: #000; font-size: 11pt; }
  h1 { text-align: center; font-size: 16pt; margin-bottom: 2px; }
  .contact { text-align: center; font-size: 10pt; margin-bottom: 12px; }
  h2 {
    font-size: 12pt; border-bottom: 1px solid #000; margin-top: 14px;
    text-transform: uppercase; letter-spacing: 1px;
  }
  .entry { margin: 6px 0; }
  .entry-header { display: flex; justify-content: space-between; font-weight: bold; }
  ul { margin: 2px 0 6px 18px; }
  li { margin-bottom: 2px; }
</style></head><body>
{{ content }}
</body></html>""",
    "modern": """<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8">
<style>
  body { font-family: "Arial", sans-serif; margin: 0; color: #222; font-size: 10pt; }
  .sidebar {
    background: #2d3e50; color: #fff; width: 220px; float: left;
    min-height: 100vh; padding: 24px 16px; box-sizing: border-box;
  }
  .main { margin-left: 252px; padding: 24px; }
  h1 { color: #fff; font-size: 18pt; margin-bottom: 4px; }
  h2 { color: #2d3e50; font-size: 12pt; border-left: 4px solid #2d3e50; padding-left: 8px; margin-top: 16px; }
  .entry-header { display: flex; justify-content: space-between; font-weight: bold; }
  ul { margin: 2px 0 6px 18px; }
</style></head><body>
{{ content }}
</body></html>""",
    "minimal": """<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8">
<style>
  body { font-family: "Helvetica Neue", sans-serif; margin: 50px; color: #333; font-size: 10pt; line-height: 1.5; }
  h1 { font-size: 22pt; font-weight: 300; margin-bottom: 4px; }
  h2 {
    font-size: 11pt; font-weight: 600; text-transform: uppercase;
    color: #888; letter-spacing: 2px; margin-top: 20px;
  }
  hr { border: none; border-top: 1px solid #eee; margin: 6px 0; }
  .entry-header { display: flex; justify-content: space-between; font-weight: 600; }
  ul { margin: 2px 0 8px 16px; }
</style></head><body>
{{ content }}
</body></html>""",
    "creative": """<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8">
<style>
  body { font-family: "Georgia", serif; margin: 40px; color: #1a1a2e; font-size: 10pt; }
  h1 { font-size: 26pt; color: #e94560; margin-bottom: 0; }
  .subtitle { color: #0f3460; font-size: 12pt; margin-top: 2px; }
  h2 { font-size: 12pt; color: #e94560; margin-top: 18px; border-bottom: 2px solid #e94560; }
  .entry-header { display: flex; justify-content: space-between; font-weight: bold; color: #0f3460; }
  ul { margin: 2px 0 6px 18px; }
</style></head><body>
{{ content }}
</body></html>""",
}


class CVTemplateRenderer:
    """Renders structured CV data into named templates (JSON and PDF)."""

    def __init__(self, llm_connector: LLMConnector) -> None:
        self._llm = llm_connector

    async def render_cv(self, cv_data: dict[str, Any], template: str = "harvard") -> dict[str, Any]:
        """Project CV data into a named template via the LLM.

        Validates the template name, asks the LLM to reorder/format sections
        according to the template's conventions, and returns the structured dict.
        """
        if template not in _ALLOWED_TEMPLATES:
            raise ValueError(
                f"Unknown template '{template}'. Allowed: {sorted(_ALLOWED_TEMPLATES)}"
            )

        cv_json = json.dumps(cv_data, ensure_ascii=False)[:5000]

        prompt = f"""Template: {template}

Dữ liệu CV:
{cv_json}

Sắp xếp lại dữ liệu CV theo phong cách template "{template}":
- harvard: Thứ tự truyền thống (Education → Experience → Skills)
- modern: Nổi bật Skills và Projects trước
- minimal: Loại bỏ thông tin ít quan trọng, giữ cô đọng
- creative: Nhấn mạnh Projects và tính cá nhân

Trả về JSON với cùng schema nhưng thứ tự section phù hợp với template:"""

        raw = await self._llm.generate(
            prompt,
            system=_RENDER_SYSTEM,
            use_cloud=bool(self._llm._cloud_api_key),
            json_mode=True,
        )
        raw = raw.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:]).rstrip("`").strip()

        try:
            rendered: dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("[TemplateRenderer] JSON parse failed — returning original cv_data")
            rendered = cv_data

        return {"template": template, **rendered}

    async def render_pdf(self, cv_data: dict[str, Any], template: str = "harvard") -> bytes:
        """Render the chosen template to a PDF byte stream.

        Calls ``render_cv`` to get the ordered data, then builds an HTML
        document and converts it to PDF via WeasyPrint.

        Falls back to a raw JSON bytes response if WeasyPrint is unavailable.
        """
        rendered = await self.render_cv(cv_data, template)
        html_content = _build_html(rendered, template)

        try:
            from weasyprint import HTML  # type: ignore[import-untyped]

            pdf_bytes: bytes = HTML(string=html_content).write_pdf()
            logger.info("[TemplateRenderer] PDF generated via WeasyPrint (%d bytes)", len(pdf_bytes))
            return pdf_bytes
        except ImportError:
            logger.warning("[TemplateRenderer] WeasyPrint not installed — returning JSON bytes as fallback")
            return json.dumps(rendered, ensure_ascii=False, indent=2).encode("utf-8")
        except Exception as exc:
            logger.error("[TemplateRenderer] WeasyPrint render failed: %s", exc)
            raise


def _build_html(cv_data: dict[str, Any], template: str) -> str:
    """Build an HTML string from CV data using the named template layout."""
    pi = cv_data.get("personal_info", {})
    name = pi.get("name", "Ứng viên")
    email = pi.get("email", "")
    phone = pi.get("phone", "")
    linkedin = pi.get("linkedin", "")
    location = pi.get("location", "")

    contact_parts = [p for p in [email, phone, linkedin, location] if p]
    contact_line = " | ".join(contact_parts)

    sections_html = _build_sections_html(cv_data)

    if template in ("modern",):
        # Two-column layout: sidebar left, main content right
        sidebar_skills = _build_skills_sidebar(cv_data)
        content = f"""
<div class="sidebar">
  <h1>{name}</h1>
  <p style="font-size:9pt;color:#aad">{contact_line}</p>
  {sidebar_skills}
</div>
<div class="main">
  {sections_html}
</div>"""
    else:
        content = f"""
<h1>{name}</h1>
<div class="contact">{contact_line}</div>
{sections_html}"""

    base_html = _HTML_TEMPLATES.get(template, _HTML_TEMPLATES["minimal"])
    return base_html.replace("{{ content }}", content)


def _build_sections_html(cv_data: dict[str, Any]) -> str:
    """Convert CV dict sections into HTML blocks."""
    html_parts: list[str] = []

    # Education
    education_list: list[dict[str, Any]] = cv_data.get("education", [])
    if education_list:
        html_parts.append("<h2>Học vấn</h2>")
        for edu in education_list:
            school = edu.get("school", "")
            degree = edu.get("degree", "")
            major = edu.get("major", "")
            period = edu.get("period", "")
            gpa = edu.get("gpa", "")
            gpa_str = f" — GPA: {gpa}" if gpa else ""
            html_parts.append(
                f'<div class="entry"><div class="entry-header"><span>{school}</span><span>{period}</span></div>'
                f"<div>{degree} — {major}{gpa_str}</div></div>"
            )

    # Experience
    experience_list: list[dict[str, Any]] = cv_data.get("experience", [])
    if experience_list:
        html_parts.append("<h2>Kinh nghiệm làm việc</h2>")
        for exp in experience_list:
            company = exp.get("company", "")
            title = exp.get("title", "")
            period = exp.get("period", "")
            impacts: list[str] = exp.get("key_impacts", []) or exp.get("descriptions", [])
            html_parts.append(
                f'<div class="entry"><div class="entry-header">'
                f"<span>{title} — {company}</span><span>{period}</span></div>"
            )
            if impacts:
                items = "".join(f"<li>{item}</li>" for item in impacts)
                html_parts.append(f"<ul>{items}</ul>")
            html_parts.append("</div>")

    # Projects
    projects_list: list[dict[str, Any]] = cv_data.get("projects", [])
    if projects_list:
        html_parts.append("<h2>Dự án</h2>")
        for proj in projects_list:
            name = proj.get("name", "")
            role = proj.get("role", "")
            tech = ", ".join(proj.get("tech_stack", [])[:8])
            desc = proj.get("description", "")
            html_parts.append(
                f'<div class="entry"><div class="entry-header"><span>{name}</span><span>{role}</span></div>'
                f"<div>{desc}</div>"
                f"<div style='font-style:italic;color:#666'>Tech: {tech}</div></div>"
            )

    # Skills (non-modern templates)
    skills: dict[str, Any] = cv_data.get("skills_matrix", {})
    all_skills = (
        skills.get("languages", [])
        + skills.get("frameworks", [])
        + skills.get("tools", [])
    )
    if all_skills:
        html_parts.append("<h2>Kỹ năng</h2>")
        html_parts.append(f"<p>{', '.join(all_skills[:30])}</p>")

    # Certifications
    certs: list[str] = cv_data.get("certifications", [])
    if certs:
        html_parts.append("<h2>Chứng chỉ</h2>")
        html_parts.append("<ul>" + "".join(f"<li>{c}</li>" for c in certs) + "</ul>")

    return "\n".join(html_parts)


def _build_skills_sidebar(cv_data: dict[str, Any]) -> str:
    """Build a sidebar-friendly skills section for the modern template."""
    skills: dict[str, Any] = cv_data.get("skills_matrix", {})
    html_parts: list[str] = []
    for category, label in [
        ("languages", "Ngôn ngữ"),
        ("frameworks", "Framework"),
        ("tools", "Công cụ"),
        ("soft_skills", "Kỹ năng mềm"),
    ]:
        items: list[str] = skills.get(category, [])
        if items:
            html_parts.append(f"<p style='font-weight:bold;margin-bottom:2px'>{label}</p>")
            html_parts.append(
                "<ul style='margin:0 0 8px 12px;color:#cde'>"
                + "".join(f"<li>{i}</li>" for i in items[:10])
                + "</ul>"
            )
    return "\n".join(html_parts)

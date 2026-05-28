"""LancerAI — End-to-End Test Script
Sử dụng file CV thực để test toàn bộ flow:
  1. Đăng ký user
  2. Đăng nhập lấy token
  3. Upload CV PDF → Extraction (LLM parse)
  4. Tối ưu CV (Optimization agent)
  5. Job Matching
  6. Tạo phiên phỏng vấn (Interview session)

Chạy: python test_with_real_cv.py
Yêu cầu: server đang chạy trên http://localhost:8000
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# Fix encoding issue on Windows console/redirects
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

import httpx

BASE_URL = "http://localhost:8000/api/v1"
CV_FILE = Path(__file__).parent / "CV _PhamNgocDuy.pdf"

# Test credentials
TEST_EMAIL = "phamngocuy.test@lancerai.local"
TEST_PASSWORD = "TestPass123!"
TEST_NAME = "Phạm Ngọc Duy"

# ─────────────────────────────────────────────────────────────────────────────

def sep(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def ok(label: str, data: object = None) -> None:
    print(f"  ✅ {label}")
    if data:
        if isinstance(data, dict):
            for k, v in list(data.items())[:6]:
                val = str(v)[:80] + "…" if len(str(v)) > 80 else str(v)
                print(f"     {k}: {val}")
        else:
            print(f"     {str(data)[:200]}")


def fail(label: str, resp: httpx.Response) -> None:
    print(f"  ❌ {label}")
    print(f"     Status: {resp.status_code}")
    try:
        print(f"     Body:   {resp.json()}")
    except Exception:
        print(f"     Body:   {resp.text[:200]}")


def check_server() -> bool:
    sep("0. Kiểm tra server")
    try:
        r = httpx.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        if r.status_code == 200:
            ok("Server đang chạy", r.json())
            return True
        fail("Server trả lỗi", r)
        return False
    except httpx.ConnectError:
        print("  ❌ Không kết nối được http://localhost:8000")
        print("     → Chạy trước: uvicorn app.main:app --reload")
        return False


def register_and_login(client: httpx.Client) -> str | None:
    sep("1. Đăng ký + Đăng nhập")

    # Register (ignore 409 = user already exists)
    r = client.post(f"{BASE_URL}/auth/signup", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "display_name": TEST_NAME,
    })
    if r.status_code in (200, 201):
        ok("Đăng ký thành công")
    elif r.status_code == 409 or (r.status_code == 400 and "already registered" in r.text):
        ok("User đã tồn tại, tiếp tục đăng nhập")
    else:
        fail("Đăng ký thất bại", r)
        return None

    # Login
    r = client.post(f"{BASE_URL}/auth/login", json={
        "identifier": TEST_EMAIL,
        "password": TEST_PASSWORD,
    })
    if r.status_code != 200:
        fail("Đăng nhập thất bại", r)
        return None

    data = r.json()
    token = data.get("access_token")
    ok("Đăng nhập thành công", {"access_token": token[:30] + "…", "user": data.get("user", {}).get("email")})
    return token


def upload_cv(client: httpx.Client, token: str) -> str | None:
    sep("2. Upload CV — Extraction")

    if not CV_FILE.exists():
        print(f"  ❌ Không tìm thấy file: {CV_FILE}")
        return None

    file_size_kb = CV_FILE.stat().st_size // 1024
    print(f"  📄 File: {CV_FILE.name} ({file_size_kb} KB)")
    print("  ⏳ Đang upload và phân tích CV bằng LLM (có thể mất 15-30s)…")

    start = time.time()
    with open(CV_FILE, "rb") as f:
        r = client.post(
            f"{BASE_URL}/extraction/cvs",
            files={"file": ("CV_PhamNgocDuy.pdf", f, "application/pdf")},
            headers={"Authorization": f"Bearer {token}"},
            timeout=300,
        )
    elapsed = time.time() - start

    if r.status_code != 201:
        fail("Upload CV thất bại", r)
        return None

    data = r.json()
    cv_id = data.get("cv_id") or data.get("id")
    personal = data.get("personal_info", {})

    ok(f"CV extracted trong {elapsed:.1f}s", {
        "cv_id": cv_id,
        "name": personal.get("name"),
        "email": personal.get("email"),
        "phone": personal.get("phone"),
        "education": f"{len(data.get('education', []))} mục",
        "experience": f"{len(data.get('experience', []))} mục",
        "skills": str(data.get("skills_matrix", {}))[:100],
    })

    # Pretty-print full JSON
    print("\n  📋 Toàn bộ dữ liệu extracted:")
    print(json.dumps(data, ensure_ascii=False, indent=4)[:3000])

    return cv_id


def optimize_cv(client: httpx.Client, token: str, cv_id: str) -> dict | None:
    sep("3. Tối ưu CV — Optimization Agent")

    target_job_title = "Senior Python Backend Developer"
    print(f"  🎯 Role: {target_job_title}")
    print("  ⏳ Đang phân tích và tối ưu (30-60s do LLM agents)…")

    start = time.time()
    r = client.post(
        f"{BASE_URL}/optimization/cvs/{cv_id}/optimizations",
        json={
            "target_job_title": target_job_title,
            "target_industry": "technology",
            "mode": "standard"
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=300,
    )
    elapsed = time.time() - start

    if r.status_code != 200:
        fail("Optimization thất bại", r)
        return None

    data = r.json()
    ok(f"Optimization hoàn thành trong {elapsed:.1f}s", {
        "audit_score": data.get("audit_score"),
        "cv_id": data.get("cv_id"),
        "optimized_data_sections": list((data.get("optimized_data") or {}).keys()),
    })
    return data


def match_jobs(client: httpx.Client, token: str, cv_id: str) -> dict | None:
    sep("4. Job Matching")

    jd_text = (
        "Senior Python Backend Developer (FastAPI, PostgreSQL, AWS). "
        "Yêu cầu 3+ năm kinh nghiệm, thành thạo RESTful API, Docker, CI/CD."
    )
    print(f"  🎯 JD để matching: {jd_text[:80]}…")
    print("  ⏳ Đang chạy Hybrid Matching (frequency, position, semantic)…")
    start = time.time()
    r = client.post(
        f"{BASE_URL}/jobs/matches",
        json={
            "cv_id": cv_id,
            "jd_text": jd_text
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=300,
    )
    elapsed = time.time() - start

    if r.status_code not in (200, 201):
        fail("Job matching thất bại", r)
        return None

    data = r.json()
    ok(f"Matching hoàn thành trong {elapsed:.1f}s", {
        "overall_score": data.get("overall_score"),
        "semantic_score": data.get("semantic_score"),
        "frequency_score": data.get("frequency_score"),
        "position_score": data.get("position_score"),
        "missing_skills_count": len(data.get("missing_skills", [])),
    })
    return data


def get_recommendations(client: httpx.Client, token: str, cv_id: str) -> list | None:
    sep("4b. Job Recommendations")
    print("  ⏳ Đang lấy danh sách job gợi ý từ database…")
    start = time.time()
    r = client.get(
        f"{BASE_URL}/jobs/recommendations/{cv_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,
    )
    elapsed = time.time() - start

    if r.status_code != 200:
        fail("Lấy gợi ý job thất bại", r)
        return None

    data = r.json()
    ok(f"Lấy gợi ý hoàn thành trong {elapsed:.1f}s — {len(data)} kết quả", {
        "count": len(data),
        "results": str(data)[:200],
    })
    return data


def create_interview(client: httpx.Client, token: str, cv_id: str) -> dict | None:
    sep("5. Tạo phiên phỏng vấn")

    print("  ⏳ Khởi tạo phiên phỏng vấn AI…")
    r = client.post(
        f"{BASE_URL}/interview/sessions",
        json={
            "cv_id": cv_id,
            "mode": "practice",
            "total_questions": 3,
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=300,
    )

    if r.status_code not in (200, 201):
        fail("Tạo phiên phỏng vấn thất bại", r)
        return None

    data = r.json()
    session_id = data.get("session_id") or data.get("id")
    ok("Phiên phỏng vấn đã tạo", {
        "session_id": session_id,
        "mode": data.get("mode"),
        "first_question": str(data.get("question") or data.get("message") or "")[:100],
    })
    return data


# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    print("\n🚀 LancerAI End-to-End Test — CV: Phạm Ngọc Duy")
    print(f"   Target server: {BASE_URL}")
    print(f"   CV file: {CV_FILE}")

    if not check_server():
        sys.exit(1)

    with httpx.Client(timeout=120) as client:
        # Step 1: Auth
        token = register_and_login(client)
        if not token:
            sys.exit(1)

        # Step 2: Upload CV
        cv_id = upload_cv(client, token)
        if not cv_id:
            sys.exit(1)

        # Step 3: Optimize CV
        optimize_cv(client, token, cv_id)

        # Step 4: Job Match
        match_jobs(client, token, cv_id)

        # Step 4b: Recommendations
        get_recommendations(client, token, cv_id)

        # Step 5: Interview
        create_interview(client, token, cv_id)

    sep("✅ Hoàn thành End-to-End Test")
    print("  Tất cả chức năng đã được kiểm tra với CV thực.")
    print()


if __name__ == "__main__":
    main()
